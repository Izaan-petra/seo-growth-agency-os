"""Read-only Ahrefs API/export/screenshot/public-fallback adapter."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Mapping

from seo_os.authorization import AuthorizationGrant
from seo_os.ingestion.quality import QualityIssue, QualityStatus

from .base import AcquisitionRequest, ConnectorCapabilities, ConnectorContext, ConnectorError
from .managed import ManagedReadOnlyConnector, ProviderBatch
from .tabular import parse_authorized_tabular


REPORTS = {
    "ahrefs-organic-keywords": ("organic-keywords", "keywords", "ahrefs-keyword-ranking"),
    "ahrefs-top-pages": ("top-pages", "pages", "ahrefs-keyword-ranking"),
    "ahrefs-backlinks": ("all-backlinks", "backlinks", "ahrefs-backlink-refdomain"),
    "ahrefs-referring-domains": ("refdomains", "refdomains", "ahrefs-backlink-refdomain"),
}
REQUIRED_REPORT_FIELDS = {
    "ahrefs-organic-keywords": {"keyword"},
    "ahrefs-top-pages": {"url"},
    "ahrefs-backlinks": {"url_from", "url_to"},
    "ahrefs-referring-domains": {"domain"},
}
SAFE_FIELD = re.compile(r"^[a-z][a-z0-9_]{0,127}$")


class AhrefsConnector(ManagedReadOnlyConnector):
    @property
    def capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            provider="ahrefs",
            acquisition_methods=("api", "export", "screenshot", "public-research"),
            authentication_methods=("api-key", "environment-secret", "user-export", "user-screenshot", "none"),
            supported_record_types=tuple(REPORTS),
        )

    def authorization_fields(self, request: AcquisitionRequest) -> tuple[str, ...]:
        mapping = request.filters.get("field_mapping", {})
        return tuple(str(value) for value in mapping.values()) if isinstance(mapping, Mapping) else ()

    def collect_authorized(
        self, context: ConnectorContext, request: AcquisitionRequest, grant: AuthorizationGrant
    ) -> ProviderBatch:
        missing_required = REQUIRED_REPORT_FIELDS[request.record_type] - set(request.fields)
        if missing_required:
            raise ConnectorError("missing_required_field", f"Ahrefs report requires: {', '.join(sorted(missing_required))}")
        method = self.acquisition_method(request)
        if method == "api":
            return self._collect_api(request, grant)
        if method == "export":
            return self._collect_export(context, request)
        if method == "screenshot":
            return self._collect_screenshot(context, request)
        return ProviderBatch(
            dataset_type=REPORTS[request.record_type][2], records=(),
            raw_payload={"mode": "public-research", "target": request.resource_id, "report": request.record_type},
            dimensions=(), metrics=(),
            limitations=("Ahrefs API and user-provided evidence were unavailable; only declared public research fallback is permitted.", "No Ahrefs values were inferred or fabricated."),
            metadata={"report": request.record_type, "target": request.resource_id, "acquisition_mode": "public-research", "third_party_estimate": True},
            missing_field_data=True,
        )

    def _collect_api(self, request: AcquisitionRequest, grant: AuthorizationGrant) -> ProviderBatch:
        endpoint_name, response_key, dataset_type = REPORTS[request.record_type]
        if any(SAFE_FIELD.fullmatch(field) is None for field in request.fields):
            raise ConnectorError("unsupported_field", "Ahrefs select fields must be safe API field identifiers")
        token = self.resolve_credential(grant)
        limit = _bounded_int(request.filters.get("limit", 1000), 1, 10000, "limit")
        mode = str(request.filters.get("target_mode", "subdomains"))
        if mode not in {"exact", "prefix", "domain", "subdomains"}:
            raise ConnectorError("unsupported_combination", "Ahrefs target mode is invalid")
        query: dict[str, Any] = {
            "target": request.resource_id, "mode": mode,
            "select": ",".join(request.fields), "limit": limit, "output": "json",
        }
        allowed_options = {"country", "date", "date_compared", "where", "order_by", "protocol", "aggregation", "history", "traffic_mode", "volume_mode"}
        for name in allowed_options:
            if name in request.filters:
                query[name] = request.filters[name]
        if endpoint_name in {"organic-keywords", "top-pages"}:
            query.setdefault("date", request.end_date)
            if not query.get("date"):
                raise ConnectorError("invalid_date_range", "Ahrefs organic reports require a report date")
        response = self.transport.request(
            "GET", f"https://api.ahrefs.com/v3/site-explorer/{endpoint_name}",
            headers={"Authorization": f"Bearer {token}"}, query=query,
        ).payload
        source_rows = response.get(response_key, [])
        if not isinstance(source_rows, list):
            raise ConnectorError("invalid_provider_response", "Ahrefs report rows must be an array")
        records: list[Mapping[str, Any]] = []
        for row in source_rows:
            if not isinstance(row, Mapping):
                raise ConnectorError("invalid_provider_response", "Ahrefs report row must be an object")
            selected = {field: row.get(field) for field in request.fields}
            selected["resource_id"] = request.resource_id
            if dataset_type == "ahrefs-keyword-ranking" and not selected.get("keyword"):
                selected["keyword"] = selected.get("top_keyword")
            selected["target"] = request.resource_id
            records.append(selected)
        capped = len(records) >= limit
        return ProviderBatch(
            dataset_type=dataset_type, records=tuple(records), raw_payload=response,
            dimensions=tuple(field for field in request.fields if field in {"keyword", "url", "keyword_country", "language", "date", "url_from", "url_to", "domain", "root_name_source"}),
            metrics=tuple(field for field in request.fields if field not in {"keyword", "url", "keyword_country", "language", "date", "url_from", "url_to", "domain", "root_name_source"}),
            limitations=("Ahrefs values are third-party estimates and must remain labeled as such.", "Ahrefs API units depend on selected fields and returned rows; this adapter requests only authorized fields."),
            metadata={"endpoint_report": endpoint_name, "target": request.resource_id, "target_mode": mode, "country": query.get("country"), "filters": query.get("where"), "date": query.get("date"), "fields": list(request.fields), "limit": limit, "returned_rows": len(records), "third_party_estimate": True},
            partial_api_result=capped,
        )

    def _collect_export(self, context: ConnectorContext, request: AcquisitionRequest) -> ProviderBatch:
        parsed = parse_authorized_tabular(context, request)
        dataset_type = REPORTS[request.record_type][2]
        records = []
        for item in parsed.records:
            record = dict(item["values"])
            record["source_row"] = item["source_row"]
            record["resource_id"] = request.resource_id
            record["target"] = request.resource_id
            if dataset_type == "ahrefs-keyword-ranking" and not record.get("keyword"):
                record["keyword"] = record.get("top_keyword")
            records.append(record)
        issues = ()
        if parsed.rejected:
            issues = (QualityIssue("rejected-rows", QualityStatus.WARNING, f"{len(parsed.rejected)} Ahrefs export rows were quarantined"),)
        return ProviderBatch(
            dataset_type=dataset_type, records=tuple(records), raw_payload=parsed.raw_content,
            raw_media_type=parsed.media_type, dimensions=tuple(parsed.headers),
            limitations=("Ahrefs export values are third-party estimates.",),
            metadata={"report": request.record_type, "target": request.resource_id, "target_mode": request.filters.get("target_mode"), "country": request.filters.get("country"), "filters": request.filters.get("where"), "date": request.end_date, "fields": list(parsed.headers), "limit": request.filters.get("row_limit"), "returned_rows": len(records), "third_party_estimate": True, "sheet": parsed.sheet, "encoding": parsed.encoding},
            rejected_records=parsed.rejected, extra_quality_issues=issues, truncated=parsed.truncated,
        )

    def _collect_screenshot(self, context: ConnectorContext, request: AcquisitionRequest) -> ProviderBatch:
        evidence = request.filters.get("evidence_manifest")
        visible_values = request.filters.get("visible_values")
        if not isinstance(evidence, Mapping) or not isinstance(visible_values, list):
            raise ConnectorError("invalid_screenshot_evidence", "Screenshot mode requires an evidence manifest and explicit visible_values")
        required = {"relative_path", "checksum_sha256", "captured_at", "report", "target", "visible_fields"}
        if not required.issubset(evidence) or evidence.get("target") != request.resource_id:
            raise ConnectorError("invalid_screenshot_evidence", "Screenshot evidence metadata is incomplete or targets another resource")
        relative = evidence["relative_path"]
        if not isinstance(relative, str):
            raise ConnectorError("invalid_screenshot_evidence", "Screenshot path is invalid")
        raw_root = (context.data_root / "raw").resolve()
        image_path = (raw_root / relative).resolve()
        try:
            image_path.relative_to(raw_root)
        except ValueError:
            raise ConnectorError("unsafe_path", "Screenshot path must remain under the raw data root") from None
        if not image_path.is_file() or hashlib.sha256(image_path.read_bytes()).hexdigest() != evidence["checksum_sha256"]:
            raise ConnectorError("invalid_screenshot_evidence", "Screenshot is missing or checksum validation failed")
        visible_fields = set(map(str, evidence["visible_fields"]))
        if not set(request.fields).issubset(visible_fields):
            raise ConnectorError("field_not_visible", "Requested screenshot fields are not visibly documented")
        records = []
        for index, value in enumerate(visible_values, start=1):
            if not isinstance(value, Mapping):
                raise ConnectorError("invalid_screenshot_evidence", "Visible screenshot values must be structured objects")
            record = {field: value.get(field) for field in request.fields}
            record.update({"source_row": index, "resource_id": request.resource_id, "target": request.resource_id})
            records.append(record)
        return ProviderBatch(
            dataset_type=REPORTS[request.record_type][2], records=tuple(records),
            raw_payload={"evidence_manifest": dict(evidence), "visible_values": visible_values},
            dimensions=tuple(request.fields),
            limitations=("Only values explicitly visible and recorded in the screenshot evidence manifest are represented.", "Screenshot evidence may be incomplete and Ahrefs values remain third-party estimates."),
            metadata={"report": evidence["report"], "target": request.resource_id, "captured_at": evidence["captured_at"], "screenshot_reference": relative, "visible_fields": sorted(visible_fields), "returned_rows": len(records), "third_party_estimate": True},
            screenshot_evidence=True,
        )


def _bounded_int(value: Any, minimum: int, maximum: int, name: str) -> int:
    if isinstance(value, bool):
        raise ConnectorError("invalid_limit", f"{name} must be an integer")
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ConnectorError("invalid_limit", f"{name} must be an integer") from None
    if not minimum <= parsed <= maximum:
        raise ConnectorError("invalid_limit", f"{name} must be between {minimum} and {maximum}")
    return parsed
