from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from seo_os.ingestion import deterministic_snapshot_id


FIXTURES = Path(__file__).parents[1] / "fixtures" / "procedures"


def snapshot(
    dataset_type: str,
    records: list[Mapping[str, Any]],
    *,
    source: str | None = None,
    period: Mapping[str, str] | None = None,
    quality: str = "pass",
    name: str = "fixture",
    limitations: list[str] | None = None,
) -> dict[str, Any]:
    resolved_source = source or {
        "gsc-search-performance": "gsc",
        "ga4-organic-landing-performance": "ga4",
        "ahrefs-keyword-ranking": "ahrefs",
        "ahrefs-backlink-refdomain": "ahrefs",
        "psi-lab-performance": "pagespeed-insights",
        "crux-field-performance": "crux",
    }.get(dataset_type, "public-research")
    base = {
        "schema_version": "1.0.0", "ingestion_id": f"ingestion-{name}", "project_id": "PROJECT-FIXTURE",
        "source": resolved_source, "dataset_type": dataset_type, "resource_id": f"resource-{name}",
        "retrieved_at": "2026-09-03T00:00:00Z", "period": dict(period) if period else None,
        "dimensions": [], "metrics": [], "limitations": list(limitations or []),
        "provenance": {"fixture": True, "provider_timestamp": "2026-09-02T23:00:00Z"},
        "quality": {"status": quality}, "records": [dict(row) for row in records],
    }
    return {"snapshot_id": deterministic_snapshot_id(base), **base}


def load_scenario(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def scenario_snapshots(name: str) -> list[dict[str, Any]]:
    definition = load_scenario(name)
    return [snapshot(**item) for item in definition["datasets"]]
