"""Shared authorization and lifecycle behavior for production connectors."""

from __future__ import annotations

import json
from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Mapping

from seo_os.authorization import AuthorizationError, AuthorizationGrant, require_manifest
from seo_os.datasets import CanonicalDataset
from seo_os.ingestion.pipeline import persist_acquisition, persist_failure
from seo_os.ingestion.quality import QualityIssue
from seo_os.security.redaction import redact_mapping, redact_text
from seo_os.secrets import EnvironmentSecretResolver, SecretResolver, SecretUnavailableError

from .base import (
    AcquisitionRequest,
    Connector,
    ConnectorContext,
    ConnectorError,
    ConnectorResult,
    ProbeResult,
)
from .transport import HttpTransport, UrllibJsonTransport


@dataclass(frozen=True, slots=True)
class ProviderBatch:
    dataset_type: str
    records: tuple[Mapping[str, Any], ...]
    raw_payload: Mapping[str, Any] | bytes
    raw_media_type: str = "application/json"
    dimensions: tuple[str, ...] = ()
    metrics: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)
    rejected_records: tuple[Mapping[str, Any], ...] = ()
    extra_quality_issues: tuple[QualityIssue, ...] = ()
    truncated: bool = False
    partial_api_result: bool = False
    screenshot_evidence: bool = False
    missing_field_data: bool = False


class ManagedReadOnlyConnector(Connector):
    default_acquisition_method = "api"
    credential_optional = False

    def __init__(
        self,
        *,
        transport: HttpTransport | None = None,
        secret_resolver: SecretResolver | None = None,
    ) -> None:
        self.transport = transport or UrllibJsonTransport()
        self.secret_resolver = secret_resolver or EnvironmentSecretResolver()

    def acquisition_method(self, request: AcquisitionRequest) -> str:
        return str(request.filters.get("acquisition_method", self.default_acquisition_method))

    def authorization_fields(self, request: AcquisitionRequest) -> tuple[str, ...]:
        return ()

    def probe(self, context: ConnectorContext) -> ProbeResult:
        try:
            manifest = require_manifest(context.authorization_manifest)
            if manifest.payload["status"] != "active":
                return ProbeResult(True, False, self.capabilities.acquisition_methods, ("Authorization is not active",))
            if manifest.payload["project_id"] != context.project_id or manifest.payload["authorization_id"] != context.authorization_id:
                return ProbeResult(True, False, self.capabilities.acquisition_methods, ("Authorization context does not match",))
            expires_at = manifest.payload.get("expires_at")
            if expires_at:
                expiry = datetime.fromisoformat(str(expires_at).replace("Z", "+00:00"))
                requested_at = context.requested_at if context.requested_at.tzinfo else context.requested_at.replace(tzinfo=UTC)
                if expiry <= requested_at.astimezone(expiry.tzinfo or UTC):
                    return ProbeResult(True, False, self.capabilities.acquisition_methods, ("Authorization has expired",))
            entries = [
                item for item in manifest.payload["connectors"]
                if item["provider"] == self.capabilities.provider
                and item["access_mode"] == "read-only"
                and item.get("allowed_record_types")
                and item["authentication_method"] in self.capabilities.authentication_methods
            ]
            if not entries:
                return ProbeResult(True, False, self.capabilities.acquisition_methods, ("No active provider grant",))
            credentials_ready = any(_entry_is_ready(item, self.secret_resolver) for item in entries)
            return ProbeResult(True, credentials_ready, self.capabilities.acquisition_methods, (() if credentials_ready else ("Referenced secret unavailable",)))
        except (AuthorizationError, ValueError):
            return ProbeResult(True, False, self.capabilities.acquisition_methods, ("Authorization manifest invalid or inactive",))

    def collect(self, context: ConnectorContext, request: AcquisitionRequest) -> ConnectorResult:
        method = self.acquisition_method(request)
        request_envelope = {
            "source": request.source,
            "record_type": request.record_type,
            "resource_id": request.resource_id,
            "fields": request.fields,
            "filters": request.filters,
        }
        if _text_redaction_changes(request_envelope):
            raise ConnectorError(
                "privacy_quarantine",
                "Acquisition request contains credential-like material and was not executed",
            )
        if request.source != self.capabilities.provider:
            raise ConnectorError("source_mismatch", "Request source does not match connector provider")
        if request.record_type not in self.capabilities.supported_record_types:
            raise ConnectorError("unsupported_record_type", "Connector does not support the requested record type")
        if method not in self.capabilities.acquisition_methods:
            raise ConnectorError("unsupported_acquisition_method", "Connector does not support the acquisition method")
        scope_fields = tuple(dict.fromkeys((*request.fields, *self.authorization_fields(request))))
        try:
            grant = require_manifest(context.authorization_manifest).authorize(
                project_id=context.project_id,
                authorization_id=context.authorization_id,
                provider=self.capabilities.provider,
                acquisition_method=method,
                record_type=request.record_type,
                resource_id=request.resource_id,
                fields=scope_fields,
                start_date=request.start_date,
                end_date=request.end_date,
                at=context.requested_at,
            )
        except AuthorizationError as exc:
            raise ConnectorError(exc.code, str(exc)) from None
        if grant.authentication_method not in self.capabilities.authentication_methods:
            raise ConnectorError(
                "unsupported_authentication",
                "Authorization uses an authentication method this connector does not implement",
            )
        if context.approved_resource_ids and request.resource_id not in context.approved_resource_ids:
            raise ConnectorError("resource_not_authorized", "Resource is outside the execution context")
        if context.credential_reference and context.credential_reference != grant.credential_reference:
            raise ConnectorError("credential_reference_mismatch", "Credential reference differs from authorization")

        try:
            batch = self.collect_authorized(context, request, grant)
            if isinstance(batch.raw_payload, Mapping):
                original = json.dumps(batch.raw_payload, sort_keys=True, default=str)
                redacted = json.dumps(redact_mapping(batch.raw_payload), sort_keys=True, default=str)
                if redacted != original:
                    raise ConnectorError(
                        "privacy_quarantine",
                        "Provider payload contained sensitive material and was not retained",
                    )
            if _text_redaction_changes(
                {"metadata": batch.metadata, "records": batch.records, "rejected_records": batch.rejected_records}
            ):
                raise ConnectorError(
                    "privacy_quarantine",
                    "Normalized provider data contained credential-like material and was not retained",
                )
            raw_content = batch.raw_payload if isinstance(batch.raw_payload, bytes) else (json.dumps(batch.raw_payload, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
            retrieved_at = (
                context.requested_at.astimezone(UTC)
                if context.requested_at.tzinfo
                else context.requested_at.replace(tzinfo=UTC)
            )
            provenance = dict(batch.metadata)
            provider_timestamp = _metadata_datetime(provenance.pop("retrieved_at", None))
            if provider_timestamp is not None:
                provenance["provider_timestamp"] = provider_timestamp.isoformat().replace("+00:00", "Z")
            period = {"start_date": request.start_date, "end_date": request.end_date} if request.start_date and request.end_date else None
            dataset = CanonicalDataset(
                dataset_type=batch.dataset_type, source=self.capabilities.provider,
                resource_id=request.resource_id, retrieved_at=retrieved_at, period=period,
                dimensions=batch.dimensions, metrics=batch.metrics,
                limitations=batch.limitations, provenance=provenance, records=batch.records,
            )
            return persist_acquisition(
                context=context, request=request, acquisition_method=method, dataset=dataset,
                raw_content=raw_content, raw_media_type=batch.raw_media_type,
                rejected_records=batch.rejected_records, extra_quality_issues=batch.extra_quality_issues,
                truncated=batch.truncated, partial_api_result=batch.partial_api_result,
                screenshot_evidence=batch.screenshot_evidence, missing_field_data=batch.missing_field_data,
            )
        except SecretUnavailableError:
            error = ConnectorError("credential_unavailable", "Referenced credential is unavailable")
        except ConnectorError as exc:
            error = exc
        except Exception:
            error = ConnectorError("connector_failure", "Connector failed while processing provider data")
        return persist_failure(
            context=context, request=request, source=self.capabilities.provider,
            acquisition_method=method, category=error.category, message=str(error),
            retryable=error.retryable,
        )

    def resolve_credential(self, grant: AuthorizationGrant) -> str | None:
        if not grant.credential_reference:
            if self.credential_optional:
                return None
            raise SecretUnavailableError("Authorization has no credential reference")
        return self.secret_resolver.resolve(grant.credential_reference)

    @abstractmethod
    def collect_authorized(
        self, context: ConnectorContext, request: AcquisitionRequest, grant: AuthorizationGrant
    ) -> ProviderBatch:
        """Collect and normalize after the common scope gate succeeds."""


def _metadata_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
    except ValueError:
        return None


def _entry_is_ready(entry: Mapping[str, Any], resolver: SecretResolver) -> bool:
    authentication_method = entry["authentication_method"]
    requires_secret = authentication_method in {"oauth2", "service-account", "api-key", "environment-secret"}
    reference = entry.get("credential_reference")
    if requires_secret:
        return isinstance(reference, str) and resolver.available(reference)
    return reference in (None, "") or (isinstance(reference, str) and resolver.available(reference))


def _text_redaction_changes(value: Any) -> bool:
    serialized = json.dumps(value, sort_keys=True, default=str)
    return redact_text(serialized) != serialized
