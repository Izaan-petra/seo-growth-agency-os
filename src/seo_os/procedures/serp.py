"""Deterministic competitor and SERP sampling procedure."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Mapping, Sequence

from .common import canonicalize_url, domain_of, normalize_query, values
from .framework import FindingDraft, ProcedureError, ProcedureSpec, build_output, prepare_inputs


SPEC = ProcedureSpec(
    "competitor-serp-analysis", "1.0.0", "competitor-serp-analysis", "SERP",
    minimum_any=("generic-tabular-evidence",), required_datasets=("generic-tabular-evidence",),
    output_schemas=("specialist-finding",),
)

REQUIRED_SAMPLE_FIELDS = {
    "query", "locale", "language", "device", "location", "timestamp",
    "search_engine", "position", "url", "result_type", "serp_features",
}


def classify_page_type(url: str, result_type: str, explicit: Any = None) -> str:
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip().casefold().replace("_", "-")
    lowered = canonicalize_url(url).casefold()
    declared = result_type.casefold().replace("_", "-")
    if declared not in {"organic", "web", "unknown"}:
        return declared
    rules = (("/products/", "product"), ("/product/", "product"), ("/collections/", "category"), ("/category/", "category"), ("/blog/", "article"), ("/articles/", "article"), ("/locations/", "location"), ("/services/", "service"))
    return next((label for token, label in rules if token in lowered), "unknown")


def run_serp_procedure(
    *, project_id: str, brief_id: str, datasets: Sequence[Mapping[str, Any]],
    approved_dataset_ids: Sequence[str], config: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    settings = dict(config or {})
    prepared = prepare_inputs(SPEC, project_id=project_id, brief_id=brief_id, datasets=datasets, approved_dataset_ids=approved_dataset_ids)
    minimum_results = int(settings.get("minimum_results_per_query", 3))
    recurrence_threshold = int(settings.get("competitor_recurrence_queries", 2))
    business_competitors = {str(item).casefold() for item in settings.get("business_competitors", [])}
    target_domain = str(settings.get("target_domain", "")).casefold()
    snapshots: list[dict[str, Any]] = []
    invalid_rows = 0
    for dataset in prepared.of_type("generic-tabular-evidence"):
        for record in dataset.get("records", []):
            row = values(record)
            if not REQUIRED_SAMPLE_FIELDS.issubset(row) or not isinstance(row.get("serp_features"), (list, tuple)):
                invalid_rows += 1
                continue
            try:
                position = int(row["position"])
            except (TypeError, ValueError):
                invalid_rows += 1
                continue
            result_type = str(row["result_type"])
            url = canonicalize_url(str(row["url"]))
            snapshots.append({
                "dataset_id": str(dataset["snapshot_id"]), "query": str(row["query"]),
                "normalized_query": normalize_query(str(row["query"])), "locale": str(row["locale"]),
                "language": str(row["language"]), "device": str(row["device"]),
                "location": str(row["location"]), "timestamp": str(row["timestamp"]),
                "search_engine": str(row["search_engine"]), "position": position,
                "url": url, "domain": domain_of(str(row["url"])),
                "result_type": result_type, "page_type": classify_page_type(url, result_type, row.get("page_type")), "serp_features": sorted(map(str, row["serp_features"])),
                "intent": str(row.get("intent", "unknown")),
            })
    if not snapshots:
        raise ProcedureError("No valid deterministic SERP sample rows are available")

    by_query: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in snapshots:
        by_query[row["normalized_query"]].append(row)
    under_sampled = sorted(query for query, rows in by_query.items() if len(rows) < minimum_results)
    domains_by_query = {query: {row["domain"] for row in rows if row["domain"] != target_domain} for query, rows in by_query.items()}
    domain_frequency = Counter(domain for domains in domains_by_query.values() for domain in domains)
    result_types = Counter(row["result_type"] for row in snapshots)
    page_types = Counter(row["page_type"] for row in snapshots)
    features = Counter(feature for row in snapshots for feature in row["serp_features"])
    intents = {query: Counter(row["intent"] for row in rows) for query, rows in by_query.items()}

    drafts: list[FindingDraft] = []
    all_dataset_ids = tuple(sorted({row["dataset_id"] for row in snapshots}))
    for domain, count in sorted(domain_frequency.items()):
        if count >= recurrence_threshold:
            competitor_type = "business-and-organic" if domain in business_competitors else "organic-only"
            drafts.append(FindingDraft(
                "competitor-recurrence", f"{domain} appears for {count} sampled queries.", competitor_type,
                "Use the recurring domain as comparative evidence for result format, coverage, and defensible differentiation—not as a traffic or market-share estimate.",
                all_dataset_ids, (domain,), finding_type="observation", impact="medium", effort="low",
                requires_validation=("Repeat a like-for-like SERP sample before using this observation in a later planning cycle.",),
            ))
    if result_types:
        result_type, count = sorted(result_types.items(), key=lambda item: (-item[1], item[0]))[0]
        drafts.append(FindingDraft(
            "result-format", f"{result_type} is the most frequent result type in the approved sample ({count}/{len(snapshots)} results).",
            "dominant-result-format", "Use this as intent-format evidence while requiring a genuinely differentiated page proposition.",
            all_dataset_ids, finding_type="observation", impact="medium", effort="low",
            requires_validation=("Confirm the format remains consistent across the configured market, device, and location sample.",),
        ))
    inconsistent = [query for query, counts in intents.items() if len([key for key, count in counts.items() if key != "unknown" and count]) > 1]
    if inconsistent:
        drafts.append(FindingDraft(
            "intent-consistency", f"{len(inconsistent)} sampled queries show multiple explicit intent labels.", "mixed-intent-sample",
            "Keep intent multi-label or split the query set until repeated evidence supports a stable page format.",
            all_dataset_ids, tuple(inconsistent), inference="Observed format variation may reflect mixed intent rather than a single winning template.",
            requires_validation=("Review the time-stamped result composition and query semantics.",),
        ))
    if under_sampled:
        drafts.append(FindingDraft(
            "sample-coverage", f"{len(under_sampled)} queries have fewer than the configured {minimum_results} results.", "limited-sample",
            "Collect a larger like-for-like sample before making strong recurrence or format conclusions.",
            all_dataset_ids, tuple(under_sampled), finding_type="validation-required", impact="low", effort="low", confidence="low",
            requires_validation=("Increase the sample without changing locale, language, device, location, or engine.",),
        ))
    by_dataset: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in snapshots:
        by_dataset[row["dataset_id"]].append(row)
    dataset_order = sorted(
        by_dataset,
        key=lambda dataset_id: (
            str(next(item for item in prepared.datasets if item["snapshot_id"] == dataset_id).get("retrieved_at", "")),
            dataset_id,
        ),
    )
    serp_diff: dict[str, Any] = {"status": "not-available", "reason": "At least two approved time-separated SERP snapshots are required."}
    if len(dataset_order) >= 2:
        previous_id, current_id = dataset_order[-2], dataset_order[-1]
        signature = lambda row: (row["normalized_query"], row["position"], row["url"], row["result_type"], tuple(row["serp_features"]))
        previous_rows = {signature(row) for row in by_dataset[previous_id]}
        current_rows = {signature(row) for row in by_dataset[current_id]}
        serp_diff = {
            "status": "available", "previous_dataset_id": previous_id, "current_dataset_id": current_id,
            "added": [list(item) for item in sorted(current_rows - previous_rows)],
            "removed": [list(item) for item in sorted(previous_rows - current_rows)],
            "interpretation": "Descriptive sample change only; recurring monitoring is not implemented.",
        }
    return build_output(prepared, drafts, artifacts={
        "serp_snapshot": sorted(snapshots, key=lambda row: (row["normalized_query"], row["position"], row["url"])),
        "domain_frequency": dict(sorted(domain_frequency.items())),
        "query_overlap": {domain: sorted(query for query, domains in domains_by_query.items() if domain in domains) for domain in sorted(domain_frequency)},
        "result_type_frequency": dict(sorted(result_types.items())),
        "page_type_frequency": dict(sorted(page_types.items())),
        "serp_feature_frequency": dict(sorted(features.items())),
        "opportunity_barrier_evidence": [
            {"serp_feature": feature, "observed_results": count, "classification": "barrier-or-format-requirement", "interpretation": "Observed composition only; feasibility requires business and specialist review."}
            for feature, count in sorted(features.items())
        ],
        "invalid_row_count": invalid_rows,
        "sample_configuration": {"minimum_results_per_query": minimum_results, "competitor_recurrence_queries": recurrence_threshold},
        "serp_diff": serp_diff,
    })
