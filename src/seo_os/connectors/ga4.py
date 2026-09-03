"""Read-only Google Analytics 4 Data API adapter."""

from __future__ import annotations

import re
from typing import Any, Mapping

from seo_os.authorization import AuthorizationGrant

from .base import AcquisitionRequest, ConnectorCapabilities, ConnectorContext, ConnectorError
from .managed import ManagedReadOnlyConnector, ProviderBatch


REVENUE_METRICS = {"totalRevenue", "purchaseRevenue", "grossPurchaseRevenue", "refundAmount"}


class GoogleAnalytics4Connector(ManagedReadOnlyConnector):
    @property
    def capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            provider="ga4",
            acquisition_methods=("api",),
            authentication_methods=("oauth2", "environment-secret"),
            supported_record_types=("ga4-organic-landing-performance",),
        )

    def authorization_fields(self, request: AcquisitionRequest) -> tuple[str, ...]:
        fields = _filter_field_names(request.filters.get("dimension_filter"))
        if request.filters.get("dimension_filter") is None:
            fields.add("sessionDefaultChannelGroup")
        return tuple(sorted(fields))

    def collect_authorized(
        self, context: ConnectorContext, request: AcquisitionRequest, grant: AuthorizationGrant
    ) -> ProviderBatch:
        if not request.start_date or not request.end_date:
            raise ConnectorError("invalid_date_range", "GA4 requires start and end dates")
        property_path = request.resource_id if request.resource_id.startswith("properties/") else f"properties/{request.resource_id}"
        if re.fullmatch(r"properties/[0-9]+", property_path) is None:
            raise ConnectorError("invalid_resource", "GA4 property must be a numeric property ID")
        token = self.resolve_credential(grant)
        headers = {"Authorization": f"Bearer {token}"}
        metadata_response = self.transport.request(
            "GET", f"https://analyticsdata.googleapis.com/v1beta/{property_path}/metadata", headers=headers
        ).payload
        dimension_metadata = _metadata_by_name(metadata_response.get("dimensions"), "dimension")
        metric_metadata = _metadata_by_name(metadata_response.get("metrics"), "metric")
        unknown = set(request.fields) - set(dimension_metadata) - set(metric_metadata)
        if unknown:
            raise ConnectorError("unsupported_field", f"GA4 metadata does not support: {', '.join(sorted(unknown))}")
        dimensions = tuple(field for field in request.fields if field in dimension_metadata)
        metrics = tuple(field for field in request.fields if field in metric_metadata)
        if not metrics:
            raise ConnectorError("unsupported_combination", "GA4 report requires at least one metric")

        custom_filter = request.filters.get("dimension_filter")
        dimension_filter = custom_filter or {
            "filter": {
                "fieldName": "sessionDefaultChannelGroup",
                "stringFilter": {"matchType": "EXACT", "value": "Organic Search", "caseSensitive": False},
            }
        }
        filter_fields = _filter_field_names(dimension_filter)
        if custom_filter is not None:
            organic_definition = request.filters.get("organic_channel_definition")
            if not isinstance(organic_definition, str) or not organic_definition.strip():
                raise ConnectorError("organic_definition_required", "A custom GA4 filter requires an explicit organic channel definition")
            if not filter_fields.intersection({"sessionDefaultChannelGroup", "sessionMedium", "sessionSource"}):
                raise ConnectorError("organic_filter_required", "GA4 organic landing data must filter a session-scoped organic acquisition dimension")
        unsupported_filters = filter_fields - set(dimension_metadata)
        if unsupported_filters:
            raise ConnectorError("unsupported_combination", f"GA4 filter uses unsupported dimensions: {', '.join(sorted(unsupported_filters))}")

        compatibility_body = {
            "dimensions": [{"name": name} for name in dimensions],
            "metrics": [{"name": name} for name in metrics],
            "dimensionFilter": dimension_filter,
        }
        compatibility_response = self.transport.request(
            "POST", f"https://analyticsdata.googleapis.com/v1beta/{property_path}:checkCompatibility",
            headers=headers, json_body=compatibility_body,
        ).payload
        incompatible = _incompatible_fields(compatibility_response)
        if incompatible:
            raise ConnectorError(
                "unsupported_combination",
                f"GA4 reports incompatible fields: {', '.join(sorted(incompatible))}",
            )

        page_size = _bounded_int(request.filters.get("row_limit", 100000), 1, 250000, "row_limit")
        max_rows = _bounded_int(request.filters.get("max_rows", 250000), 1, 1000000, "max_rows")
        expected_currency = request.filters.get("expected_currency")
        if expected_currency is not None and (not isinstance(expected_currency, str) or re.fullmatch(r"[A-Z]{3}", expected_currency) is None):
            raise ConnectorError("invalid_currency", "Expected currency must be an ISO 4217 three-letter code")
        if set(metrics) & REVENUE_METRICS and not expected_currency:
            raise ConnectorError("currency_required", "Revenue acquisition requires an explicitly authorized expected_currency")

        rows: list[Mapping[str, Any]] = []
        raw_pages: list[Mapping[str, Any]] = []
        response_metadata: Mapping[str, Any] = {}
        total_count: int | None = None
        last_page_had_rows = False
        offset = 0
        while offset < max_rows:
            limit = min(page_size, max_rows - offset)
            body: dict[str, Any] = {
                "dimensions": [{"name": name} for name in dimensions],
                "metrics": [{"name": name} for name in metrics],
                "dateRanges": [{"startDate": request.start_date, "endDate": request.end_date}],
                "dimensionFilter": dimension_filter,
                "offset": str(offset),
                "limit": str(limit),
                "returnPropertyQuota": True,
            }
            if expected_currency:
                body["currencyCode"] = expected_currency
            response = self.transport.request(
                "POST", f"https://analyticsdata.googleapis.com/v1beta/{property_path}:runReport",
                headers=headers, json_body=body,
            ).payload
            raw_pages.append(response)
            page_metadata = response.get("metadata", {}) if isinstance(response.get("metadata", {}), Mapping) else {}
            response_metadata = {**response_metadata, **page_metadata}
            page_rows = response.get("rows", [])
            if not isinstance(page_rows, list):
                raise ConnectorError("invalid_provider_response", "GA4 rows must be an array")
            last_page_had_rows = bool(page_rows)
            if "rowCount" in response:
                try:
                    reported_count = int(response["rowCount"])
                except (TypeError, ValueError):
                    raise ConnectorError("invalid_provider_response", "GA4 rowCount must be numeric") from None
                if total_count is not None and reported_count != total_count:
                    raise ConnectorError("invalid_provider_response", "GA4 rowCount changed between pages")
                total_count = reported_count
            response_dimensions = [item.get("name") for item in response.get("dimensionHeaders", [])]
            response_metrics = [item.get("name") for item in response.get("metricHeaders", [])]
            if response_dimensions and response_dimensions != list(dimensions):
                raise ConnectorError("invalid_provider_response", "GA4 dimension headers differ from request")
            if response_metrics and response_metrics != list(metrics):
                raise ConnectorError("invalid_provider_response", "GA4 metric headers differ from request")
            for raw_row in page_rows:
                dimension_values = raw_row.get("dimensionValues", [])
                metric_values = raw_row.get("metricValues", [])
                if len(dimension_values) != len(dimensions) or len(metric_values) != len(metrics):
                    raise ConnectorError("invalid_provider_response", "GA4 row values do not match headers")
                record: dict[str, Any] = {
                    name: str(item.get("value", "")) for name, item in zip(dimensions, dimension_values)
                }
                for name, item in zip(metrics, metric_values):
                    record[name] = _metric_value(item.get("value"), metric_metadata[name].get("type"))
                if set(metrics) & REVENUE_METRICS:
                    record["currency"] = str(response_metadata.get("currencyCode") or expected_currency)
                record["resource_id"] = request.resource_id
                rows.append(record)
            offset += len(page_rows)
            if not page_rows or (total_count is not None and offset >= total_count) or len(page_rows) < limit:
                break

        limitations = [
            "GA4 sessions and GSC clicks have different definitions and must not be treated as equivalent.",
            "Attribution, consent, identity, and channel configuration can change reported organic performance.",
            "GA4 unique-user and session counts can be approximate.",
            "Consent modeling and processing freshness can affect GA4 results even when no explicit response flag is present.",
        ]
        if response_metadata.get("subjectToThresholding"):
            limitations.append("GA4 reported that privacy thresholding affected this result.")
        if response_metadata.get("samplingMetadatas"):
            limitations.append("GA4 reported sampling metadata for this result.")
        if response_metadata.get("dataLossFromOtherRow"):
            limitations.append("GA4 reported high-cardinality data loss into the (other) row.")
        if response_metadata.get("schemaRestrictionResponse"):
            limitations.append("GA4 applied active property data restrictions.")
        timezone_missing = not response_metadata.get("timeZone")
        if timezone_missing:
            limitations.append("GA4 did not return a property timezone, so date alignment requires validation.")
        capped = (
            (total_count is not None and len(rows) < total_count)
            or (total_count is None and len(rows) >= max_rows and last_page_had_rows)
        )
        metric_definitions = {
            name: {key: metric_metadata[name].get(key) for key in ("uiName", "description", "type", "category", "customDefinition") if key in metric_metadata[name]}
            for name in metrics
        }
        return ProviderBatch(
            dataset_type="ga4-organic-landing-performance", records=tuple(rows),
            raw_payload={"property": property_path, "metadata": metadata_response, "compatibility": compatibility_response, "report_pages": raw_pages},
            dimensions=dimensions, metrics=metrics, limitations=tuple(limitations),
            metadata={"property_id": request.resource_id, "timezone": response_metadata.get("timeZone"), "dimensions": list(dimensions), "metrics": list(metrics), "date_range": {"start_date": request.start_date, "end_date": request.end_date}, "filters": dimension_filter, "organic_channel_definition": request.filters.get("organic_channel_definition", "sessionDefaultChannelGroup exactly Organic Search"), "attribution_limitations": "Session-scoped acquisition dimensions reflect GA4 attribution configuration.", "metric_definition_metadata": metric_definitions, "returned_rows": len(rows), "provider_row_count": total_count, "expected_currency": expected_currency},
            partial_api_result=capped or bool(response_metadata.get("subjectToThresholding") or response_metadata.get("samplingMetadatas") or response_metadata.get("dataLossFromOtherRow")),
            missing_field_data=timezone_missing,
        )


def _metadata_by_name(value: Any, kind: str) -> dict[str, Mapping[str, Any]]:
    if not isinstance(value, list):
        raise ConnectorError("invalid_provider_response", f"GA4 {kind} metadata must be an array")
    result: dict[str, Mapping[str, Any]] = {}
    for item in value:
        if isinstance(item, Mapping) and isinstance(item.get("apiName"), str):
            result[item["apiName"]] = item
    return result


def _filter_field_names(value: Any) -> set[str]:
    names: set[str] = set()
    if isinstance(value, Mapping):
        if isinstance(value.get("fieldName"), str):
            names.add(value["fieldName"])
        for item in value.values():
            names.update(_filter_field_names(item))
    elif isinstance(value, list):
        for item in value:
            names.update(_filter_field_names(item))
    return names


def _incompatible_fields(payload: Mapping[str, Any]) -> set[str]:
    result: set[str] = set()
    for collection_name, metadata_name in (
        ("dimensionCompatibilities", "dimensionMetadata"),
        ("metricCompatibilities", "metricMetadata"),
    ):
        values = payload.get(collection_name, [])
        if not isinstance(values, list):
            raise ConnectorError("invalid_provider_response", "GA4 compatibility response is invalid")
        for item in values:
            if not isinstance(item, Mapping):
                raise ConnectorError("invalid_provider_response", "GA4 compatibility item is invalid")
            metadata = item.get(metadata_name, {})
            if item.get("compatibility") != "COMPATIBLE" and isinstance(metadata, Mapping) and isinstance(metadata.get("apiName"), str):
                result.add(metadata["apiName"])
    return result


def _metric_value(value: Any, metric_type: Any) -> int | float:
    text = str(value)
    try:
        if str(metric_type) in {"TYPE_INTEGER", "TYPE_SECONDS"} and re.fullmatch(r"-?[0-9]+", text):
            return int(text)
        return float(text)
    except ValueError:
        raise ConnectorError("invalid_provider_response", "GA4 metric value is not numeric") from None


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
