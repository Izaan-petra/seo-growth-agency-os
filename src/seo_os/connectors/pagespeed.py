"""Read-only PageSpeed Insights v5 lab-diagnostics adapter."""

from __future__ import annotations

from typing import Any, Mapping
from urllib.parse import urlparse

from seo_os.authorization import AuthorizationGrant

from .base import AcquisitionRequest, ConnectorCapabilities, ConnectorContext, ConnectorError
from .managed import ManagedReadOnlyConnector, ProviderBatch


AUDIT_IDS = (
    "first-contentful-paint", "largest-contentful-paint", "total-blocking-time",
    "cumulative-layout-shift", "speed-index", "interactive",
)
SUPPORTED_FIELDS = {"performance_score", "final_url", "fetch_time", "lighthouse_version", "audit_ids", *AUDIT_IDS}


class PageSpeedInsightsConnector(ManagedReadOnlyConnector):
    credential_optional = True

    @property
    def capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            provider="pagespeed-insights", acquisition_methods=("api",),
            authentication_methods=("none", "api-key", "environment-secret"),
            supported_record_types=("psi-lab-performance",),
        )

    def authorization_fields(self, request: AcquisitionRequest) -> tuple[str, ...]:
        return ("final_url", "fetch_time", "lighthouse_version", "audit_ids")

    def collect_authorized(
        self, context: ConnectorContext, request: AcquisitionRequest, grant: AuthorizationGrant
    ) -> ProviderBatch:
        unknown = set(request.fields) - SUPPORTED_FIELDS
        if unknown:
            raise ConnectorError("unsupported_field", f"Unsupported PageSpeed fields: {', '.join(sorted(unknown))}")
        if not _http_url(request.resource_id):
            raise ConnectorError("invalid_resource", "PageSpeed resource must be an HTTP(S) URL")
        strategy = str(request.filters.get("strategy", "mobile"))
        if strategy not in {"mobile", "desktop"}:
            raise ConnectorError("unsupported_combination", "PageSpeed strategy must be mobile or desktop")
        key = self.resolve_credential(grant) if grant.credential_reference else None
        query = {"url": request.resource_id, "strategy": strategy, "category": "performance", "key": key}
        response = self.transport.request(
            "GET", "https://pagespeedonline.googleapis.com/pagespeedonline/v5/runPagespeed", query=query
        ).payload
        lighthouse = response.get("lighthouseResult")
        if not isinstance(lighthouse, Mapping):
            raise ConnectorError("invalid_provider_response", "PageSpeed response has no Lighthouse result")
        audits = lighthouse.get("audits", {})
        categories = lighthouse.get("categories", {})
        if not isinstance(audits, Mapping) or not isinstance(categories, Mapping):
            raise ConnectorError("invalid_provider_response", "PageSpeed Lighthouse sections are invalid")
        requested_audits = set(request.fields) & set(AUDIT_IDS)
        lab_metrics = {
            audit_id: {
                "numeric_value": audits[audit_id].get("numericValue"),
                "numeric_unit": audits[audit_id].get("numericUnit"),
                "score": audits[audit_id].get("score"),
                "display_value": audits[audit_id].get("displayValue"),
            }
            for audit_id in AUDIT_IDS
            if audit_id in requested_audits and isinstance(audits.get(audit_id), Mapping)
        }
        performance = categories.get("performance", {})
        record = {
            "requested_url": lighthouse.get("requestedUrl", request.resource_id),
            "final_url": lighthouse.get("finalUrl", request.resource_id),
            "strategy": strategy,
            "fetch_time": lighthouse.get("fetchTime"),
            "lighthouse_version": lighthouse.get("lighthouseVersion"),
            "performance_score": performance.get("score") if isinstance(performance, Mapping) else None,
            "lab_metrics": lab_metrics,
            "audit_ids": sorted(audits.keys()),
            "resource_id": request.resource_id,
        }
        if any(record[field] in (None, "") for field in ("fetch_time", "lighthouse_version", "final_url")):
            raise ConnectorError("invalid_provider_response", "PageSpeed result is missing required metadata")
        return ProviderBatch(
            dataset_type="psi-lab-performance", records=(record,), raw_payload=response,
            dimensions=("requested_url", "final_url", "strategy"),
            metrics=("performance_score", *tuple(lab_metrics)),
            limitations=(
                "PageSpeed Lighthouse metrics are controlled lab diagnostics, not field Core Web Vitals.",
                "A single Lighthouse run can vary with test conditions and should not be treated as a user-experience population.",
            ),
            metadata={"requested_url": request.resource_id, "final_url": record["final_url"], "strategy": strategy, "fetch_timestamp": record["fetch_time"], "lighthouse_version": record["lighthouse_version"], "audit_identifiers": sorted(audits.keys()), "evidence_class": "lab" , "retrieved_at": record["fetch_time"]},
        )


def _http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
