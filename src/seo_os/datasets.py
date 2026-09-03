"""Typed canonical dataset envelope and Batch 2 dataset definitions."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class DatasetDefinition:
    name: str
    required_fields: tuple[str, ...]
    dimension_fields: tuple[str, ...]
    metric_fields: tuple[str, ...]
    duplicate_key_fields: tuple[str, ...]


DATASET_DEFINITIONS: Mapping[str, DatasetDefinition] = {
    "gsc-search-performance": DatasetDefinition(
        "gsc-search-performance", (),
        ("date", "query", "page", "country", "device", "searchAppearance"),
        ("clicks", "impressions", "ctr", "average_position"),
        ("date", "query", "page", "country", "device", "searchAppearance"),
    ),
    "ga4-organic-landing-performance": DatasetDefinition(
        "ga4-organic-landing-performance", (),
        ("date", "landingPage", "landingPagePlusQueryString", "sessionSource", "sessionMedium", "sessionDefaultChannelGroup", "country", "deviceCategory"),
        ("sessions", "totalUsers", "activeUsers", "engagedSessions", "engagementRate", "keyEvents", "conversions", "totalRevenue", "purchaseRevenue"),
        ("date", "landingPage", "landingPagePlusQueryString", "sessionSource", "sessionMedium", "country", "deviceCategory"),
    ),
    "ahrefs-keyword-ranking": DatasetDefinition(
        "ahrefs-keyword-ranking", (),
        ("keyword", "url", "keyword_country", "language", "date"),
        ("best_position", "position", "volume", "keyword_difficulty", "traffic"),
        ("keyword", "url", "keyword_country", "date"),
    ),
    "ahrefs-backlink-refdomain": DatasetDefinition(
        "ahrefs-backlink-refdomain", (),
        ("url_from", "url_to", "domain", "root_name_source", "target"),
        ("domain_rating", "domain_rating_source", "links_to_target", "traffic_domain"),
        ("url_from", "url_to", "domain", "target"),
    ),
    "psi-lab-performance": DatasetDefinition(
        "psi-lab-performance", ("requested_url", "final_url", "strategy", "fetch_time", "lighthouse_version"),
        ("requested_url", "final_url", "strategy"),
        ("performance_score",),
        ("requested_url", "strategy", "fetch_time"),
    ),
    "crux-field-performance": DatasetDefinition(
        "crux-field-performance", ("scope", "resource", "collection_period", "metrics"),
        ("scope", "resource", "form_factor"),
        (),
        ("scope", "resource", "form_factor"),
    ),
    "generic-tabular-evidence": DatasetDefinition(
        "generic-tabular-evidence", ("values", "source_row"), (), (), ("source_row",)
    ),
}


@dataclass(frozen=True, slots=True)
class CanonicalDataset:
    dataset_type: str
    source: str
    resource_id: str
    retrieved_at: datetime
    period: Mapping[str, str] | None
    dimensions: tuple[str, ...]
    metrics: tuple[str, ...]
    limitations: tuple[str, ...]
    provenance: Mapping[str, Any]
    records: tuple[Mapping[str, Any], ...]
    schema_version: str = "1.0.0"

    def __post_init__(self) -> None:
        if self.dataset_type not in DATASET_DEFINITIONS:
            raise ValueError(f"Unknown canonical dataset type: {self.dataset_type}")
        if not self.source or not self.resource_id:
            raise ValueError("Dataset source and resource are required")

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "schema_version": self.schema_version,
            "dataset_type": self.dataset_type,
            "source": self.source,
            "resource_id": self.resource_id,
            "retrieved_at": self.retrieved_at.isoformat().replace("+00:00", "Z"),
            "period": dict(self.period) if self.period else None,
            "dimensions": list(self.dimensions),
            "metrics": list(self.metrics),
            "limitations": list(self.limitations),
            "provenance": dict(self.provenance),
            "records": [dict(record) for record in self.records],
        }
        return json.loads(json.dumps(payload))
