"""Authorization-manifest loading and minimum-scope enforcement."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Mapping

from seo_os.schemas import validate_instance


class AuthorizationError(ValueError):
    """A categorized authorization denial safe to expose to callers."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class AuthorizationGrant:
    connector_id: str
    provider: str
    acquisition_method: str
    resource_id: str
    allowed_fields: tuple[str, ...]
    credential_reference: str | None
    authentication_method: str
    purpose: str


@dataclass(frozen=True, slots=True)
class AuthorizationManifest:
    payload: Mapping[str, Any]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "AuthorizationManifest":
        copied = json.loads(json.dumps(payload))
        validate_instance("authorization-manifest", copied)
        return cls(copied)

    @classmethod
    def from_path(cls, path: str | Path) -> "AuthorizationManifest":
        with Path(path).open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, dict):
            raise AuthorizationError("invalid_manifest", "Authorization manifest must be an object")
        return cls.from_mapping(payload)

    def authorize(
        self,
        *,
        project_id: str,
        authorization_id: str,
        provider: str,
        acquisition_method: str,
        record_type: str,
        resource_id: str,
        fields: tuple[str, ...],
        start_date: str | None = None,
        end_date: str | None = None,
        at: datetime | None = None,
    ) -> AuthorizationGrant:
        now = at or datetime.now(UTC)
        try:
            requested_start = date.fromisoformat(start_date) if start_date else None
            requested_end = date.fromisoformat(end_date) if end_date else None
        except ValueError:
            raise AuthorizationError("invalid_date", "Requested dates must use YYYY-MM-DD") from None
        if requested_start and requested_end and requested_start > requested_end:
            raise AuthorizationError("invalid_date", "Requested start date must not follow end date")
        if self.payload["project_id"] != project_id:
            raise AuthorizationError("project_mismatch", "Authorization belongs to another project")
        if self.payload["authorization_id"] != authorization_id:
            raise AuthorizationError("authorization_mismatch", "Authorization identifier does not match")
        if self.payload["status"] != "active":
            raise AuthorizationError("authorization_inactive", "Authorization is not active")

        expires_at = self.payload.get("expires_at")
        if expires_at:
            expiry = datetime.fromisoformat(str(expires_at).replace("Z", "+00:00"))
            comparison = now if now.tzinfo else now.replace(tzinfo=UTC)
            if expiry <= comparison.astimezone(expiry.tzinfo or UTC):
                raise AuthorizationError("authorization_expired", "Authorization has expired")

        candidates = [
            entry
            for entry in self.payload["connectors"]
            if entry["provider"] == provider
            and acquisition_method in entry["acquisition_methods"]
            and resource_id in entry["resource_ids"]
        ]
        if not candidates:
            raise AuthorizationError(
                "resource_not_authorized",
                "Provider, acquisition method, or resource is not authorized",
            )

        requested = set(fields)
        for entry in candidates:
            allowed = set(entry["allowed_fields"])
            if not requested.issubset(allowed):
                continue
            allowed_record_types = entry.get("allowed_record_types", [])
            if record_type not in allowed_record_types:
                continue
            if not _date_within(start_date, entry.get("start_date"), lower=True):
                continue
            if not _date_within(end_date, entry.get("end_date"), lower=False):
                continue
            if entry["access_mode"] != "read-only":
                raise AuthorizationError("write_scope_rejected", "Only read-only authorization is allowed")
            return AuthorizationGrant(
                connector_id=entry["connector_id"],
                provider=provider,
                acquisition_method=acquisition_method,
                resource_id=resource_id,
                allowed_fields=tuple(entry["allowed_fields"]),
                credential_reference=entry.get("credential_reference"),
                authentication_method=entry["authentication_method"],
                purpose=entry["purpose"],
            )

        if not any(record_type in item.get("allowed_record_types", []) for item in candidates):
            raise AuthorizationError("operation_not_authorized", "Requested record type is not authorized")
        unauthorized = sorted(requested - set().union(*(set(item["allowed_fields"]) for item in candidates)))
        if unauthorized:
            raise AuthorizationError(
                "field_not_authorized", f"Requested fields are not authorized: {', '.join(unauthorized)}"
            )
        raise AuthorizationError("date_not_authorized", "Requested date range exceeds authorization")


def require_manifest(payload: Mapping[str, Any] | None) -> AuthorizationManifest:
    if payload is None:
        raise AuthorizationError("authorization_missing", "An active authorization manifest is required")
    return AuthorizationManifest.from_mapping(payload)


def _date_within(requested: str | None, boundary: str | None, *, lower: bool) -> bool:
    if requested is None or boundary is None:
        return True
    requested_date = date.fromisoformat(requested)
    boundary_date = date.fromisoformat(boundary)
    return requested_date >= boundary_date if lower else requested_date <= boundary_date
