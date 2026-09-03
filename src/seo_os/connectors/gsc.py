"""Read-only Google Search Console Search Analytics adapter."""

from __future__ import annotations

from typing import Any, Mapping
from urllib.parse import quote

from seo_os.authorization import AuthorizationGrant

from .base import AcquisitionRequest, ConnectorCapabilities, ConnectorContext, ConnectorError
from .managed import ManagedReadOnlyConnector, ProviderBatch


DIMENSIONS = {"date", "hour", "query", "page", "country", "device", "searchAppearance"}
METRICS = {"clicks", "impressions", "ctr", "average_position"}
SEARCH_TYPES = {"web", "image", "video", "news", "discover", "googleNews"}
AGGREGATIONS = {"auto", "byPage", "byProperty", "byNewsShowcasePanel"}
FILTER_OPERATORS = {"contains", "equals", "notContains", "notEquals", "includingRegex", "excludingRegex"}


class GoogleSearchConsoleConnector(ManagedReadOnlyConnector):
    @property
    def capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            provider="gsc",
            acquisition_methods=("api",),
            authentication_methods=("oauth2", "environment-secret"),
            supported_record_types=("gsc-search-performance",),
        )

    def authorization_fields(self, request: AcquisitionRequest) -> tuple[str, ...]:
        filters = request.filters.get("dimension_filters", ())
        return tuple(
            str(item.get("dimension"))
            for item in filters
            if isinstance(item, Mapping) and item.get("dimension")
        )

    def collect_authorized(
        self, context: ConnectorContext, request: AcquisitionRequest, grant: AuthorizationGrant
    ) -> ProviderBatch:
        if not request.start_date or not request.end_date:
            raise ConnectorError("invalid_date_range", "GSC requires start and end dates")
        unknown = set(request.fields) - DIMENSIONS - METRICS
        if unknown:
            raise ConnectorError("unsupported_field", f"Unsupported GSC fields: {', '.join(sorted(unknown))}")
        dimensions = tuple(field for field in request.fields if field in DIMENSIONS)
        if len(dimensions) != len(set(dimensions)):
            raise ConnectorError("unsupported_combination", "GSC dimensions cannot be repeated")

        search_type = str(request.filters.get("search_type", "web"))
        aggregation = str(request.filters.get("aggregation_type", "auto"))
        data_state = str(request.filters.get("data_state", "final"))
        if search_type not in SEARCH_TYPES or aggregation not in AGGREGATIONS or data_state not in {"final", "all", "hourly_all"}:
            raise ConnectorError("unsupported_combination", "Unsupported GSC search type, aggregation, or data state")
        dimension_filters = _validate_filters(request.filters.get("dimension_filters", ()))
        filter_dimensions = {item["dimension"] for item in dimension_filters}
        if aggregation == "byProperty" and ("page" in dimensions or "page" in filter_dimensions):
            raise ConnectorError("unsupported_combination", "GSC byProperty aggregation cannot group or filter by page")
        if data_state == "hourly_all" and "hour" not in dimensions:
            raise ConnectorError("unsupported_combination", "GSC hourly_all requires the hour dimension")

        token = self.resolve_credential(grant)
        page_size = _bounded_int(request.filters.get("row_limit", 25000), 1, 25000, "row_limit")
        max_rows = _bounded_int(request.filters.get("max_rows", 100000), 1, 1000000, "max_rows")
        endpoint = f"https://www.googleapis.com/webmasters/v3/sites/{quote(request.resource_id, safe='')}/searchAnalytics/query"
        rows: list[Mapping[str, Any]] = []
        raw_pages: list[Mapping[str, Any]] = []
        response_aggregation = aggregation
        start_row = 0
        while start_row < max_rows:
            limit = min(page_size, max_rows - start_row)
            body: dict[str, Any] = {
                "startDate": request.start_date,
                "endDate": request.end_date,
                "dimensions": list(dimensions),
                "type": search_type,
                "aggregationType": aggregation,
                "dataState": data_state,
                "rowLimit": limit,
                "startRow": start_row,
            }
            if dimension_filters:
                body["dimensionFilterGroups"] = [{"groupType": "and", "filters": dimension_filters}]
            response = self.transport.request("POST", endpoint, headers={"Authorization": f"Bearer {token}"}, json_body=body)
            raw_pages.append(response.payload)
            page_rows = response.payload.get("rows", [])
            if not isinstance(page_rows, list):
                raise ConnectorError("invalid_provider_response", "GSC rows must be an array")
            response_aggregation = str(response.payload.get("responseAggregationType", response_aggregation))
            for raw_row in page_rows:
                if not isinstance(raw_row, Mapping):
                    raise ConnectorError("invalid_provider_response", "GSC row must be an object")
                keys = raw_row.get("keys", [])
                if not isinstance(keys, list) or len(keys) != len(dimensions):
                    raise ConnectorError("invalid_provider_response", "GSC row dimension keys do not match the request")
                record = {name: value for name, value in zip(dimensions, keys)}
                if "clicks" in request.fields:
                    record["clicks"] = _number(raw_row.get("clicks"), "clicks")
                if "impressions" in request.fields:
                    record["impressions"] = _number(raw_row.get("impressions"), "impressions")
                if "ctr" in request.fields:
                    record["ctr"] = _number(raw_row.get("ctr"), "ctr")
                if "average_position" in request.fields:
                    record["average_position"] = _number(raw_row.get("position"), "position")
                record["resource_id"] = request.resource_id
                rows.append(record)
            start_row += len(page_rows)
            if not page_rows or len(page_rows) < limit:
                break

        capped = len(rows) >= max_rows and bool(raw_pages and raw_pages[-1].get("rows"))
        limitations = [
            "Search Analytics returns top rows and does not guarantee every underlying row.",
            "Anonymized queries and privacy filtering can make query totals differ from aggregate totals.",
            "Search Console dates use Pacific Time and may not align with GA4 property dates.",
        ]
        if data_state != "final":
            limitations.append("Fresh or hourly data can be partial and can change after retrieval.")
        return ProviderBatch(
            dataset_type="gsc-search-performance",
            records=tuple(rows),
            raw_payload={"request_metadata": {"property": request.resource_id, "dimensions": dimensions, "filters": dimension_filters, "aggregation_type": aggregation, "search_type": search_type, "start_date": request.start_date, "end_date": request.end_date}, "pages": raw_pages},
            dimensions=dimensions,
            metrics=tuple(field for field in request.fields if field in METRICS),
            limitations=tuple(limitations),
            metadata={"property": request.resource_id, "dimensions": list(dimensions), "filters": dimension_filters, "aggregation_mode": response_aggregation, "requested_dates": {"start_date": request.start_date, "end_date": request.end_date}, "returned_rows": len(rows), "row_limit": page_size, "max_rows": max_rows, "timezone": "America/Los_Angeles", "data_state": data_state},
            partial_api_result=capped,
        )


def _validate_filters(value: Any) -> list[dict[str, str]]:
    if value in (None, ()):
        return []
    if not isinstance(value, (list, tuple)):
        raise ConnectorError("invalid_filter", "GSC dimension_filters must be an array")
    result: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise ConnectorError("invalid_filter", "GSC filter must be an object")
        dimension = str(item.get("dimension", ""))
        operator = str(item.get("operator", "equals"))
        expression = item.get("expression")
        if dimension not in DIMENSIONS or operator not in FILTER_OPERATORS or not isinstance(expression, str):
            raise ConnectorError("invalid_filter", "GSC filter dimension, operator, or expression is invalid")
        result.append({"dimension": dimension, "operator": operator, "expression": expression})
    return result


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


def _number(value: Any, field: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ConnectorError("invalid_provider_response", f"GSC {field} is not numeric") from None
