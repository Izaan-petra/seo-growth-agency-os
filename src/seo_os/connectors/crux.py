"""Read-only Chrome UX Report current-record adapter."""

from __future__ import annotations

from datetime import date
from typing import Any, Mapping
from urllib.parse import urlparse

from seo_os.authorization import AuthorizationGrant

from .base import AcquisitionRequest, ConnectorCapabilities, ConnectorContext, ConnectorError
from .managed import ManagedReadOnlyConnector, ProviderBatch


ALLOWED_METRICS = {
    "cumulative_layout_shift", "first_contentful_paint", "interaction_to_next_paint",
    "largest_contentful_paint", "experimental_time_to_first_byte", "navigation_types",
    "round_trip_time", "largest_contentful_paint_resource_type",
    "largest_contentful_paint_image_time_to_first_byte", "largest_contentful_paint_image_resource_load_delay",
    "largest_contentful_paint_image_resource_load_duration", "largest_contentful_paint_image_element_render_delay",
}
FRACTION_METRICS = {"navigation_types", "largest_contentful_paint_resource_type"}


class ChromeUxReportConnector(ManagedReadOnlyConnector):
    @property
    def capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            provider="crux", acquisition_methods=("api",),
            authentication_methods=("api-key", "environment-secret"),
            supported_record_types=("crux-field-performance",),
        )

    def collect_authorized(
        self, context: ConnectorContext, request: AcquisitionRequest, grant: AuthorizationGrant
    ) -> ProviderBatch:
        if not _http_url(request.resource_id):
            raise ConnectorError("invalid_resource", "CrUX resource must be an HTTP(S) URL or origin")
        lookup = str(request.filters.get("lookup", "url"))
        if lookup not in {"url", "origin"}:
            raise ConnectorError("unsupported_combination", "CrUX lookup must be url or origin")
        parsed_resource = urlparse(request.resource_id)
        if lookup == "origin" and (parsed_resource.path not in {"", "/"} or parsed_resource.query or parsed_resource.fragment):
            raise ConnectorError("invalid_resource", "CrUX origin lookup requires a scheme-and-host origin without a path")
        form_factor = request.filters.get("form_factor")
        if form_factor is not None:
            form_factor = str(form_factor).upper()
            if form_factor not in {"PHONE", "TABLET", "DESKTOP"}:
                raise ConnectorError("unsupported_combination", "CrUX form factor is invalid")
        metrics = tuple(request.fields)
        unknown = set(metrics) - ALLOWED_METRICS
        if unknown:
            raise ConnectorError("unsupported_field", f"Unsupported CrUX metrics: {', '.join(sorted(unknown))}")
        key = self.resolve_credential(grant)
        body: dict[str, Any] = {lookup: request.resource_id, "metrics": list(metrics)}
        if form_factor:
            body["formFactor"] = form_factor
        try:
            response = self.transport.request(
                "POST", "https://chromeuxreport.googleapis.com/v1/records:queryRecord",
                query={"key": key}, json_body=body,
            ).payload
        except ConnectorError as exc:
            if exc.category != "data_unavailable":
                raise
            return ProviderBatch(
                dataset_type="crux-field-performance", records=(), raw_payload={"record": None},
                dimensions=("scope", "resource", "form_factor"), metrics=metrics,
                limitations=("CrUX has no field record for the requested URL/origin and form factor.",),
                metadata={"lookup": lookup, "resource": request.resource_id, "form_factor": form_factor, "evidence_class": "field"},
                missing_field_data=True,
            )
        record_payload = response.get("record")
        if not isinstance(record_payload, Mapping):
            raise ConnectorError("invalid_provider_response", "CrUX response has no record")
        collection_period = record_payload.get("collectionPeriod")
        raw_metrics = record_payload.get("metrics")
        if not isinstance(collection_period, Mapping) or not isinstance(raw_metrics, Mapping):
            raise ConnectorError("invalid_provider_response", "CrUX record metadata is invalid")
        _validate_collection_period(collection_period)
        normalized_metrics: dict[str, Any] = {}
        for name in metrics:
            metric = raw_metrics.get(name)
            if not isinstance(metric, Mapping):
                continue
            normalized_metrics[name] = {
                "p75": metric.get("percentiles", {}).get("p75") if isinstance(metric.get("percentiles", {}), Mapping) else None,
                "histogram": metric.get("histogram", []),
                "fractions": metric.get("fractions", {}),
            }
        key_payload = record_payload.get("key", {})
        resource = key_payload.get(lookup, request.resource_id) if isinstance(key_payload, Mapping) else request.resource_id
        record = {
            "scope": lookup, "resource": resource, "form_factor": form_factor,
            "collection_period": collection_period, "metrics": normalized_metrics,
            "resource_id": request.resource_id,
        }
        missing = len(normalized_metrics) < len(metrics) or any(
            name not in FRACTION_METRICS and normalized_metrics.get(name, {}).get("p75") is None
            for name in metrics
        )
        limitations = ["CrUX is aggregated field evidence over its reported rolling collection period."]
        if missing:
            limitations.append("One or more requested metrics had no field evidence for this record.")
        return ProviderBatch(
            dataset_type="crux-field-performance", records=(record,), raw_payload=response,
            dimensions=("scope", "resource", "form_factor"), metrics=metrics,
            limitations=tuple(limitations),
            metadata={"lookup": lookup, "resource": resource, "form_factor": form_factor, "collection_period": collection_period, "p75_metrics": sorted(normalized_metrics), "evidence_class": "field"},
            missing_field_data=missing,
        )


def _http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _validate_collection_period(value: Mapping[str, Any]) -> None:
    try:
        first = value["firstDate"]
        last = value["lastDate"]
        first_date = date(int(first["year"]), int(first["month"]), int(first["day"]))
        last_date = date(int(last["year"]), int(last["month"]), int(last["day"]))
    except (KeyError, TypeError, ValueError):
        raise ConnectorError("invalid_provider_response", "CrUX collection period is invalid") from None
    if first_date > last_date:
        raise ConnectorError("invalid_provider_response", "CrUX collection period is reversed")
