"""Deterministic keyword normalization, intent, clustering, cannibalization, and mapping."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping, Sequence

from seo_os.schemas import validate_instance

from .common import as_number, lexical_overlap, normalize_query, stable_id, values
from .framework import FindingDraft, ProcedureError, ProcedureSpec, build_output, prepare_inputs


SPEC = ProcedureSpec(
    "keyword-intent-strategy", "1.0.0", "keyword-intent-strategy", "KEYWORD",
    minimum_any=("gsc-search-performance", "ahrefs-keyword-ranking", "generic-tabular-evidence"),
    optional_datasets=("gsc-search-performance", "ahrefs-keyword-ranking", "generic-tabular-evidence"),
    output_schemas=("specialist-finding", "keyword-cluster"),
)

INTENT_TERMS = {
    "transactional": {"buy", "order", "price", "coupon", "deal", "shop"},
    "commercial": {"best", "review", "reviews", "top", "alternative"},
    "comparison": {"vs", "versus", "compare", "comparison", "alternative"},
    "local": {"near", "local", "nearby"},
    "navigational": {"login", "contact", "website", "homepage"},
    "conversational": {"how", "what", "why", "when", "where", "can", "does"},
    "informational": {"guide", "tutorial", "ideas", "tips", "how", "what", "why"},
}


def classify_brand(query: str, brand_terms: Sequence[str]) -> str:
    normalized = normalize_query(query)
    terms = [normalize_query(term) for term in brand_terms if normalize_query(term)]
    if not terms:
        return "ambiguous"
    query_words = set(normalized.split())
    return "branded" if any(set(term.split()).issubset(query_words) for term in terms) else "non-branded"


def classify_intent(query: str, *, branded: bool = False) -> tuple[str, ...]:
    tokens = set(normalize_query(query).split())
    labels = {label for label, terms in INTENT_TERMS.items() if tokens & terms}
    if branded:
        labels.add("branded")
    if not labels:
        labels.add("informational")
    return tuple(sorted(labels))


def run_keyword_procedure(
    *, project_id: str, brief_id: str, datasets: Sequence[Mapping[str, Any]],
    approved_dataset_ids: Sequence[str], config: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    settings = dict(config or {})
    prepared = prepare_inputs(SPEC, project_id=project_id, brief_id=brief_id, datasets=datasets, approved_dataset_ids=approved_dataset_ids)
    brand_terms = tuple(map(str, settings.get("brand_terms", ())))
    market = str(settings.get("market", "Requires validation"))
    language = str(settings.get("language", "und"))
    threshold = float(settings.get("lexical_cluster_threshold", 0.5))
    observations: dict[str, dict[str, Any]] = {}
    for dataset in prepared.datasets:
        dataset_id = str(dataset["snapshot_id"])
        for raw in dataset.get("records", []):
            row = values(raw)
            original = row.get("query", row.get("keyword"))
            if not isinstance(original, str) or not normalize_query(original):
                continue
            normalized = normalize_query(original)
            item = observations.setdefault(normalized, {
                "originals": set(), "urls": defaultdict(set), "dataset_ids": set(),
                "clicks": 0.0, "impressions": 0.0, "position_weighted": 0.0,
                "position_weight": 0.0, "third_party_demand": [],
                "business_relevance": set(), "conversion_roles": set(),
            })
            item["originals"].add(original)
            item["dataset_ids"].add(dataset_id)
            url = row.get("page", row.get("url"))
            if url:
                period_key = str(row.get("date", dataset.get("period", {}).get("end_date", "aggregate")))
                item["urls"][str(url)].add(period_key)
            clicks = as_number(row.get("clicks")) or 0.0
            impressions = as_number(row.get("impressions")) or 0.0
            position = as_number(row.get("average_position", row.get("position")))
            item["clicks"] += clicks
            item["impressions"] += impressions
            if position is not None:
                weight = impressions or 1.0
                item["position_weighted"] += position * weight
                item["position_weight"] += weight
            volume = as_number(row.get("volume"))
            if volume is not None:
                item["third_party_demand"].append(volume)
            if row.get("business_relevance") not in (None, ""):
                item["business_relevance"].add(str(row["business_relevance"]).casefold())
            if row.get("conversion_role") not in (None, ""):
                item["conversion_roles"].add(str(row["conversion_role"]).casefold())
    if not observations:
        raise ProcedureError("No usable query or keyword rows are available")

    keys = sorted(observations)
    parent = {key: key for key in keys}

    def find(key: str) -> str:
        while parent[key] != key:
            parent[key] = parent[parent[key]]
            key = parent[key]
        return key

    def union(left: str, right: str) -> None:
        a, b = find(left), find(right)
        if a != b:
            parent[max(a, b)] = min(a, b)

    for index, left in enumerate(keys):
        for right in keys[index + 1:]:
            left_urls = set(observations[left]["urls"])
            right_urls = set(observations[right]["urls"])
            if lexical_overlap(left, right) >= threshold or bool(left_urls & right_urls):
                union(left, right)
    groups: dict[str, list[str]] = defaultdict(list)
    for key in keys:
        groups[find(key)].append(key)

    clusters: list[dict[str, Any]] = []
    drafts: list[FindingDraft] = []
    for root, queries in sorted(groups.items()):
        combined_urls: dict[str, set[str]] = defaultdict(set)
        dataset_ids: set[str] = set()
        total_clicks = total_impressions = weighted_position = position_weight = 0.0
        query_items = []
        intents: set[str] = set()
        demand_evidence: list[str] = []
        relevance_labels: set[str] = set()
        conversion_roles: set[str] = set()
        for query in sorted(queries):
            item = observations[query]
            brand = classify_brand(query, brand_terms)
            query_intents = classify_intent(query, branded=brand == "branded")
            intents.update(query_intents)
            dataset_ids.update(item["dataset_ids"])
            for url, periods in item["urls"].items():
                combined_urls[url].update(periods)
            total_clicks += item["clicks"]
            total_impressions += item["impressions"]
            weighted_position += item["position_weighted"]
            position_weight += item["position_weight"]
            if item["third_party_demand"]:
                demand_evidence.append(f"{query}: third-party volume {max(item['third_party_demand']):g}")
            if item["impressions"] or item["clicks"]:
                demand_evidence.append(f"{query}: {item['clicks']:g} clicks / {item['impressions']:g} impressions")
            relevance_labels.update(item["business_relevance"])
            conversion_roles.update(item["conversion_roles"])
            query_items.append({
                "original": sorted(item["originals"])[0], "normalized": query,
                "brand_classification": brand,
                "brand_confidence": "high" if brand_terms else "low",
                "intent_labels": list(query_intents),
                "intent_confidence": "medium" if any(set(normalize_query(query).split()) & terms for terms in INTENT_TERMS.values()) else "low",
                "evidence_references": sorted(item["dataset_ids"]),
            })
        stable_urls = sorted(combined_urls)
        consistent_multi = len(stable_urls) > 1 and all(len(combined_urls[url]) >= 2 for url in stable_urls)
        cannibalization = "confirmed" if consistent_multi else "possible" if len(stable_urls) > 1 else "none"
        average_position = weighted_position / position_weight if position_weight else None
        ctr = total_clicks / total_impressions if total_impressions else None
        business_excluded = bool(relevance_labels) and relevance_labels.issubset({"low", "none", "irrelevant"})
        if business_excluded:
            decision = "unresolved"
        elif cannibalization in {"possible", "confirmed"}:
            decision = "consolidate"
        elif stable_urls and average_position is not None and 4 < average_position <= 20 and ctr is not None and ctr < float(settings.get("low_ctr_threshold", 0.03)):
            decision = "refresh-existing"
        elif stable_urls:
            decision = "existing-page-fit"
        elif demand_evidence:
            decision = "create-new"
        else:
            decision = "unresolved"
        cluster_id = stable_id("KEYWORD", project_id, root, queries, stable_urls)
        cluster = {
            "schema_version": "1.0.0", "cluster_id": cluster_id, "project_id": project_id,
            "topic": root, "market": market, "language": language,
            "intent": sorted(intents), "queries": query_items,
            "target_mapping": {
                "state": "existing" if stable_urls else "proposed" if decision == "create-new" else "unmapped",
                "url": stable_urls[0] if len(stable_urls) == 1 else None,
                "page_type": str(settings.get("default_page_type", "requires-review")),
                "cannibalization": cannibalization,
                "decision": decision,
            },
            "demand_evidence": demand_evidence,
            "competition_evidence": ["SERP evidence required for competitive feasibility"] if not prepared.of_type("generic-tabular-evidence") else ["Approved generic/SERP evidence available"],
            "business_evidence": {"relevance_labels": sorted(relevance_labels), "conversion_roles": sorted(conversion_roles)},
            "confidence": "low" if not brand_terms or prepared.degraded else "high" if prepared.of_type("gsc-search-performance") else "medium",
        }
        validate_instance("keyword-cluster", cluster)
        clusters.append(cluster)
        if cannibalization != "none":
            drafts.append(FindingDraft(
                "cannibalization", f"Cluster {root} has {len(stable_urls)} ranking URLs with {cannibalization} persistence evidence.",
                f"{cannibalization}-cannibalization", "Review intent and consolidate or differentiate competing page targets where overlap is confirmed.",
                tuple(sorted(dataset_ids)), tuple(stable_urls), inference="Multiple URLs may be competing; a multi-URL query alone is not treated as confirmed cannibalization.",
                impact="high" if cannibalization == "confirmed" else "medium",
                requires_validation=("Validate page intent, canonical state, and period consistency before consolidation.",),
                dependencies=("seo-content-strategy", "technical-seo"),
            ))
        if decision in {"refresh-existing", "create-new"}:
            drafts.append(FindingDraft(
                "page-mapping", f"Cluster {root} is classified as {decision} from approved performance and page-overlap evidence.",
                decision, "Use the cluster record as input to content strategy; do not convert it into an unsupported traffic forecast.",
                tuple(sorted(dataset_ids)), tuple(stable_urls), finding_type="opportunity", impact="medium",
                requires_validation=("Confirm business relevance, conversion role, and current SERP format before execution.",),
                dependencies=("competitor-serp-analysis", "seo-content-strategy"),
            ))
    return build_output(prepared, drafts, artifacts={"keyword_clusters": clusters, "normalization": {"unicode": "NFKC", "case": "casefold", "lexical_threshold": threshold}})
