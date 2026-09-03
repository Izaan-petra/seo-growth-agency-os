"""Deterministic content inventory, action classification, and brief procedure."""

from __future__ import annotations

from datetime import date
from typing import Any, Mapping, Sequence

from seo_os.schemas import validate_instance

from .common import as_bool, as_number, canonicalize_url, parse_iso_date, percent_change, period_days, stable_id, values
from .framework import FindingDraft, ProcedureError, ProcedureSpec, build_output, prepare_inputs


SPEC = ProcedureSpec(
    "seo-content-strategy", "1.0.0", "seo-content-strategy", "CONTENT",
    minimum_any=("generic-tabular-evidence", "gsc-search-performance", "ga4-organic-landing-performance"),
    optional_datasets=("generic-tabular-evidence", "gsc-search-performance", "ga4-organic-landing-performance"),
    output_schemas=("specialist-finding", "content-action"),
)


def _action(row: Mapping[str, Any], *, today: date, stale_days: int, decline: float) -> tuple[str, list[str]]:
    signals: list[str] = []
    status = int(as_number(row.get("status_code")) or 200)
    indexable = as_bool(row.get("indexable"))
    duplicate = as_bool(row.get("duplicate")) is True
    cannibalization = str(row.get("cannibalization", "none"))
    business_role = str(row.get("business_role", "unknown"))
    conversions = as_number(row.get("conversions")) or 0
    current = as_number(row.get("current_clicks"))
    previous = as_number(row.get("comparable_clicks"))
    seasonal = as_bool(row.get("seasonal")) is True
    if 300 <= status < 400:
        return "redirect", [f"HTTP status {status}"]
    if duplicate or cannibalization in {"possible", "confirmed"}:
        return "consolidate", ["Duplicate or cannibalization evidence"]
    if (indexable is False or status >= 400) and conversions == 0 and business_role in {"none", "unknown", "low"}:
        return "remove-noindex-candidate", ["Non-indexable/error page without measured conversion or confirmed business role"]
    change = percent_change(current, previous) if current is not None and previous is not None else None
    if change is not None and change <= -decline and not seasonal:
        signals.append(f"Comparable-period clicks changed {change:.1%}")
        return "refresh", signals
    updated = row.get("last_updated")
    if isinstance(updated, str):
        try:
            age = (today - parse_iso_date(updated)).days
            if age >= stale_days:
                return "refresh", [f"Content age is {age} days"]
        except ValueError:
            return "requires-review", ["Invalid last_updated date"]
    return "retain", ["No deterministic refresh, consolidation, redirect, or removal rule fired"]


def run_content_procedure(
    *, project_id: str, brief_id: str, datasets: Sequence[Mapping[str, Any]],
    approved_dataset_ids: Sequence[str], config: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    settings = dict(config or {})
    prepared = prepare_inputs(SPEC, project_id=project_id, brief_id=brief_id, datasets=datasets, approved_dataset_ids=approved_dataset_ids)
    stale_days = int(settings.get("stale_days", 730))
    decline = float(settings.get("decline_threshold", 0.20))
    today = parse_iso_date(str(settings.get("as_of_date", "2026-09-03")))
    inventory: dict[str, dict[str, Any]] = {}
    source_ids: dict[str, set[str]] = {}
    gsc_periods: dict[str, dict[str, float]] = {}
    ga4_conversions: dict[str, float] = {}
    invalid_rows = 0
    for dataset in prepared.datasets:
        dataset_id = str(dataset["snapshot_id"])
        for record in dataset.get("records", []):
            row = dict(values(record))
            raw_url = row.get("url", row.get("page", row.get("landingPage")))
            if not isinstance(raw_url, str) or not raw_url.startswith(("http://", "https://", "/")):
                invalid_rows += 1
                continue
            url = canonicalize_url(raw_url) if raw_url.startswith("http") else raw_url
            merged = inventory.setdefault(url, {"url": url})
            for key, value in row.items():
                if value not in (None, ""):
                    merged[key] = value
            source_ids.setdefault(url, set()).add(dataset_id)
            if dataset["dataset_type"] == "gsc-search-performance":
                gsc_periods.setdefault(url, {}).setdefault(dataset_id, 0.0)
                gsc_periods[url][dataset_id] += as_number(row.get("clicks")) or 0.0
            if dataset["dataset_type"] == "ga4-organic-landing-performance":
                ga4_conversions[url] = ga4_conversions.get(url, 0.0) + (as_number(row.get("keyEvents", row.get("conversions"))) or 0.0)
    if not inventory and not settings.get("proposed_clusters"):
        raise ProcedureError("No valid page inventory or proposed cluster input is available")

    datasets_by_id = {str(item["snapshot_id"]): item for item in prepared.datasets}
    for url, total in ga4_conversions.items():
        inventory[url]["conversions"] = total
    for url, period_totals in gsc_periods.items():
        ordered = sorted(
            ((str(datasets_by_id[dataset_id].get("period", {}).get("end_date", "")), dataset_id, value) for dataset_id, value in period_totals.items()),
            reverse=True,
        )
        if ordered:
            inventory[url]["current_clicks"] = ordered[0][2]
        if len(ordered) >= 2:
            current_dataset = datasets_by_id[ordered[0][1]]
            previous_dataset = datasets_by_id[ordered[1][1]]
            if period_days(current_dataset.get("period")) == period_days(previous_dataset.get("period")):
                inventory[url]["comparable_clicks"] = ordered[1][2]

    actions: list[dict[str, Any]] = []
    briefs: list[dict[str, Any]] = []
    drafts: list[FindingDraft] = []
    for url, row in sorted(inventory.items()):
        action, signals = _action(row, today=today, stale_days=stale_days, decline=decline)
        ids = tuple(sorted(source_ids[url]))
        destination = row.get("redirect_to") if action == "redirect" else row.get("consolidate_into") if action == "consolidate" else None
        direction = {
            "retain": "Retain and monitor the page under the defined KPI cadence.",
            "refresh": "Refresh the page against its mapped intent, evidence gaps, and current result format.",
            "consolidate": "Validate intent overlap, then consolidate signals into one selected canonical destination.",
            "redirect": "Validate the destination and internal references for the existing redirect.",
            "remove-noindex-candidate": "Obtain business approval and dependency checks before removal or durable noindex treatment.",
            "requires-review": "Correct or supplement the source record before an execution decision.",
        }[action]
        action_record = {
            "schema_version": "1.0.0", "action_id": stable_id("CONTENT", project_id, url, action), "project_id": project_id,
            "action": action, "url": url, "destination_url": destination,
            "page_type": str(row.get("page_type", "requires-review")), "supporting_signals": signals,
            "recommended_direction": direction, "brief_reference": None,
            "internal_link_changes": ["Reconcile inbound links with the approved target state"] if action in {"consolidate", "redirect", "remove-noindex-candidate"} else [],
            "qa_requirements": ["Re-crawl affected URL and verify indexability, canonical, status, and internal links after approved implementation."],
            "confidence": "low" if action == "requires-review" or prepared.degraded else "medium",
        }
        if action in {"refresh", "create-new"}:
            brief_id_value = stable_id("BRIEF", project_id, url, action)
            action_record["brief_reference"] = brief_id_value
            briefs.append({
                "brief_id": brief_id_value, "target": url, "action": action,
                "audience": row.get("audience", "Requires validation"),
                "intent": row.get("intent", "Requires validation"),
                "required_evidence": list(row.get("required_evidence", [])) if isinstance(row.get("required_evidence"), list) else [],
                "internal_link_requirements": action_record["internal_link_changes"],
                "conversion_role": row.get("conversion_role", "Requires validation"),
                "qa": action_record["qa_requirements"],
            })
        validate_instance("content-action", action_record)
        actions.append(action_record)
        if action != "retain":
            drafts.append(FindingDraft(
                "content-action", f"{url} is classified as {action}: {signals[0]}", action, direction,
                ids, (url,), inference=None if action in {"redirect", "requires-review"} else "The deterministic signals support prioritizing review, not automatic publication or deletion.",
                finding_type="opportunity" if action in {"refresh", "create-new"} else "issue",
                impact="high" if action in {"consolidate", "redirect"} else "medium",
                requires_validation=tuple(action_record["qa_requirements"]), dependencies=("keyword-intent-strategy", "technical-seo"),
            ))

    all_ids = tuple(prepared.input_dataset_ids)
    for cluster in sorted(settings.get("proposed_clusters", []), key=lambda item: str(item.get("cluster_id", ""))):
        if cluster.get("target_mapping", {}).get("decision") != "create-new":
            continue
        target = str(cluster.get("topic", "requires-review"))
        record = {
            "schema_version": "1.0.0", "action_id": stable_id("CONTENT", project_id, cluster.get("cluster_id"), "create-new"),
            "project_id": project_id, "action": "create-new", "url": None, "destination_url": None,
            "page_type": str(cluster.get("target_mapping", {}).get("page_type", "requires-review")),
            "supporting_signals": [f"Keyword cluster {cluster.get('cluster_id')} has no approved existing target"],
            "recommended_direction": "Validate SERP format and business value, then create a differentiated page brief.",
            "brief_reference": stable_id("BRIEF", project_id, cluster.get("cluster_id")), "internal_link_changes": ["Define at least one relevant contextual internal-link source"],
            "qa_requirements": ["Validate intent, originality, evidence, indexability, canonical, and internal links before publication."],
            "confidence": "low" if prepared.degraded else "medium",
        }
        validate_instance("content-action", record)
        actions.append(record)
        briefs.append({"brief_id": record["brief_reference"], "target": target, "action": "create-new", "cluster_id": cluster.get("cluster_id"), "qa": record["qa_requirements"]})
        drafts.append(FindingDraft("new-content", record["supporting_signals"][0], "create-new", record["recommended_direction"], all_ids, finding_type="opportunity", dependencies=("competitor-serp-analysis", "keyword-intent-strategy")))

    return build_output(prepared, drafts, artifacts={"content_inventory": [inventory[key] for key in sorted(inventory)], "content_actions": actions, "content_briefs": briefs, "invalid_row_count": invalid_rows})
