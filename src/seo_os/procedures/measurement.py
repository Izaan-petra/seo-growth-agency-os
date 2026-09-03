"""Deterministic SEO KPI baselines and like-for-like comparison procedure."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping, Sequence

from seo_os.schemas import validate_instance

from .common import as_number, parse_iso_date, percent_change, stable_id, values
from .framework import FindingDraft, ProcedureError, ProcedureSpec, build_output, prepare_inputs


SPEC = ProcedureSpec(
    "seo-measurement", "1.0.0", "seo-measurement", "MEASURE",
    minimum_any=("gsc-search-performance", "ga4-organic-landing-performance", "ahrefs-keyword-ranking", "ahrefs-backlink-refdomain", "crux-field-performance"),
    optional_datasets=("gsc-search-performance", "ga4-organic-landing-performance", "ahrefs-keyword-ranking", "ahrefs-backlink-refdomain", "crux-field-performance"),
    output_schemas=("specialist-finding", "measurement-kpi"),
)

METRICS = {
    "gsc-search-performance": ("clicks", "impressions"),
    "ga4-organic-landing-performance": ("sessions", "totalUsers", "keyEvents", "conversions", "totalRevenue", "purchaseRevenue"),
    "ahrefs-keyword-ranking": ("traffic", "volume"),
    "ahrefs-backlink-refdomain": ("links_to_target",),
}


def _period(dataset: Mapping[str, Any]) -> tuple[str, str] | None:
    period = dataset.get("period")
    if not isinstance(period, Mapping):
        return None
    try:
        start, end = str(period["start_date"]), str(period["end_date"])
        if parse_iso_date(start) > parse_iso_date(end):
            return None
        return start, end
    except (KeyError, ValueError):
        return None


def run_measurement_procedure(
    *, project_id: str, brief_id: str, datasets: Sequence[Mapping[str, Any]],
    approved_dataset_ids: Sequence[str], config: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    settings = dict(config or {})
    prepared = prepare_inputs(SPEC, project_id=project_id, brief_id=brief_id, datasets=datasets, approved_dataset_ids=approved_dataset_ids)
    baselines: list[dict[str, Any]] = []
    series: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    limitations = list(prepared.limitations)
    for dataset in prepared.datasets:
        dataset_type = str(dataset["dataset_type"])
        period = _period(dataset)
        if dataset_type == "crux-field-performance":
            for record in dataset.get("records", []):
                collection = record.get("collection_period", {})
                try:
                    start, end = str(collection["first_date"]), str(collection["last_date"])
                    if parse_iso_date(start) > parse_iso_date(end):
                        raise ValueError
                except (KeyError, TypeError, ValueError):
                    limitations.append(f"Invalid CrUX collection period: {dataset['snapshot_id']}")
                    continue
                resource = str(record.get("resource", dataset["resource_id"]))
                form_factor = str(record.get("form_factor", "all"))
                metrics = record.get("metrics", {})
                if not isinstance(metrics, Mapping):
                    continue
                for metric, evidence in sorted(metrics.items()):
                    if not isinstance(evidence, Mapping):
                        continue
                    percentiles = evidence.get("percentiles", {})
                    value = as_number(evidence.get("p75", percentiles.get("p75") if isinstance(percentiles, Mapping) else None))
                    if value is None:
                        continue
                    name = f"{metric}_p75:{resource}:{form_factor}"
                    item = {"source": dataset_type, "metric": name, "value": value, "start_date": start, "end_date": end, "dataset_id": str(dataset["snapshot_id"]), "currency": None}
                    baselines.append(item)
                    series[(dataset_type, name)].append(item)
            continue
        if not period:
            limitations.append(f"Invalid or absent comparison period: {dataset['snapshot_id']}")
            continue
        start, end = period
        totals: dict[str, float] = defaultdict(float)
        position_numerator = position_denominator = 0.0
        for record in dataset.get("records", []):
            row = values(record)
            for metric in METRICS.get(dataset_type, ()):
                number = as_number(row.get(metric))
                if number is not None:
                    totals[metric] += number
            position = as_number(row.get("average_position"))
            impressions = as_number(row.get("impressions"))
            if position is not None and impressions is not None:
                position_numerator += position * impressions
                position_denominator += impressions
        if dataset_type == "gsc-search-performance":
            totals["ctr"] = totals["clicks"] / totals["impressions"] if totals["impressions"] else 0.0
            if position_denominator:
                totals["average_position"] = position_numerator / position_denominator
        if dataset_type == "ga4-organic-landing-performance":
            events = totals.get("keyEvents", totals.get("conversions", 0.0))
            totals["conversion_rate"] = events / totals["sessions"] if totals["sessions"] else 0.0
        for metric, value in sorted(totals.items()):
            item = {"source": dataset_type, "metric": metric, "value": value, "start_date": start, "end_date": end, "dataset_id": str(dataset["snapshot_id"]), "currency": dataset.get("provenance", {}).get("currency") if "Revenue" in metric else None}
            baselines.append(item)
            series[(dataset_type, metric)].append(item)
    if not baselines:
        raise ProcedureError("No dataset has a valid dated KPI baseline")

    kpis: list[dict[str, Any]] = []
    comparisons: list[dict[str, Any]] = []
    drafts: list[FindingDraft] = []
    threshold = float(settings.get("material_change_threshold", 0.20))
    for key, items in sorted(series.items()):
        source, metric = key
        ordered = sorted(items, key=lambda item: (item["end_date"], item["start_date"], item["dataset_id"]))
        latest = ordered[-1]
        comparison = "No equal-duration prior period supplied"
        if len(ordered) >= 2:
            previous = ordered[-2]
            current_days = (parse_iso_date(latest["end_date"]) - parse_iso_date(latest["start_date"])).days
            previous_days = (parse_iso_date(previous["end_date"]) - parse_iso_date(previous["start_date"])).days
            if current_days == previous_days:
                change = percent_change(latest["value"], previous["value"])
                mode = str(settings.get("comparison_mode", "previous-period"))
                if mode not in {"previous-period", "WoW", "MoM", "YoY", "pre/post"}:
                    raise ProcedureError(f"Unsupported comparison mode: {mode}")
                currency_mismatch = latest["currency"] and previous["currency"] and latest["currency"] != previous["currency"]
                if currency_mismatch:
                    comparisons.append({"source": source, "metric": metric, "current_dataset_id": latest["dataset_id"], "previous_dataset_id": previous["dataset_id"], "percent_change": None, "comparable": False, "reason": "Currency differs"})
                    comparison = f"{mode} unavailable because currency differs"
                    change = None
                else:
                    change = percent_change(latest["value"], previous["value"])
                    comparison = f"Like-for-like {mode}"
                    comparisons.append({"source": source, "metric": metric, "current_dataset_id": latest["dataset_id"], "previous_dataset_id": previous["dataset_id"], "percent_change": change, "comparable": True, "comparison_mode": mode})
                if change is not None and abs(change) >= threshold:
                    direction = "increase" if change > 0 else "decrease"
                    drafts.append(FindingDraft(
                        "material-change", f"{source} {metric} shows a {abs(change):.1%} {direction} across equal-duration supplied periods.", f"material-{direction}",
                        "Investigate dated releases, technical changes, query/page segments, seasonality, and measurement changes before assigning a cause.",
                        (previous["dataset_id"], latest["dataset_id"]), inference="The change is descriptive and does not establish causality.",
                        finding_type="observation", impact="medium", effort="low",
                        requires_validation=("Confirm period completeness, reporting delay, filters, timezone, currency, attribution, and seasonal comparability.",),
                    ))
            else:
                comparisons.append({"source": source, "metric": metric, "current_dataset_id": latest["dataset_id"], "previous_dataset_id": previous["dataset_id"], "percent_change": None, "comparable": False, "reason": "Unequal period lengths"})
        kpi = {
            "schema_version": "1.0.0", "kpi_id": stable_id("MEASURE", project_id, source, metric), "project_id": project_id,
            "name": f"{source}: {metric}", "business_question": f"How is {metric} changing within the explicitly scoped {source} evidence?",
            "definition": f"Provider-scoped {metric}; it is not substituted for a similarly named metric from another provider. GSC average position is an aggregate diagnostic, not a universal rank.",
            "formula": "CrUX provider p75" if source == "crux-field-performance" else "Sum source rows" if metric not in {"ctr", "conversion_rate", "average_position"} else {"ctr": "GSC clicks / GSC impressions", "conversion_rate": "GA4 key events / GA4 sessions", "average_position": "GSC impression-weighted average position"}[metric],
            "source": source, "grain": "supplied dataset period", "filters": dict(settings.get("filters", {})),
            "timezone": settings.get("timezone"), "currency": latest["currency"], "attribution": settings.get("attribution") if source.startswith("ga4") else None,
            "baseline": {"start_date": latest["start_date"], "end_date": latest["end_date"], "value": latest["value"], "comparison_rule": comparison},
            "thresholds": [f"Review absolute period-over-period change at or above {threshold:.0%}; threshold is configurable, not a forecast."],
            "cadence": str(settings.get("cadence", "monthly")),
            "limitations": sorted(set(limitations + list(settings.get("seasonality_warnings", [])) + ["Source reporting delay and attribution must be revalidated at review time."])),
        }
        validate_instance("measurement-kpi", kpi)
        kpis.append(kpi)
    return build_output(prepared, drafts, artifacts={
        "measurement_kpis": kpis, "baselines": sorted(baselines, key=lambda item: (item["source"], item["metric"], item["end_date"])),
        "comparisons": comparisons,
        "source_boundaries": {"gsc_clicks": "Google Search organic result clicks", "ga4_sessions": "Analytics organic sessions", "rule": "Never normalize GSC clicks as GA4 sessions."},
    })
