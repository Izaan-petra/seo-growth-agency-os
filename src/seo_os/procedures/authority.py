"""Deterministic backlink normalization, deduplication, qualification, and risk triage."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping, Sequence

from seo_os.schemas import validate_instance

from .common import as_bool, as_number, canonicalize_url, domain_of, stable_id, values
from .framework import FindingDraft, ProcedureError, ProcedureSpec, build_output, prepare_inputs


SPEC = ProcedureSpec(
    "authority-link-building", "1.0.0", "authority-link-building", "AUTH",
    minimum_any=("ahrefs-backlink-refdomain", "generic-tabular-evidence"),
    optional_datasets=("ahrefs-backlink-refdomain", "generic-tabular-evidence"),
    output_schemas=("specialist-finding", "backlink-prospect"),
)


def _score(value: Any, fallback: int = 3) -> int:
    number = as_number(value)
    return max(1, min(5, int(number))) if number is not None else fallback


def _opportunity(row: Mapping[str, Any]) -> str:
    explicit = str(row.get("opportunity_type", "")).strip().casefold().replace("_", "-").replace(" ", "-")
    allowed = {"reclamation", "lost-link-reclamation", "unlinked-mention", "broken-link", "broken-link-replacement", "resource-page", "resource", "competitor-intersect", "competitor-gap", "link-gap", "partner-association", "partnership", "expert-contribution", "digital-pr", "linkable-asset", "other"}
    if explicit in allowed:
        return explicit
    if as_bool(row.get("lost")):
        return "lost-link-reclamation"
    if as_bool(row.get("unlinked_mention")):
        return "unlinked-mention"
    if as_bool(row.get("broken_destination")):
        return "broken-link-replacement"
    if as_bool(row.get("resource_page")):
        return "resource-page"
    if row.get("linked_competitors"):
        return "competitor-gap"
    return "other"


def run_authority_procedure(
    *, project_id: str, brief_id: str, datasets: Sequence[Mapping[str, Any]],
    approved_dataset_ids: Sequence[str], config: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    settings = dict(config or {})
    prepared = prepare_inputs(SPEC, project_id=project_id, brief_id=brief_id, datasets=datasets, approved_dataset_ids=approved_dataset_ids)
    target_domain = str(settings.get("target_domain", "")).casefold()
    competitor_domains = {str(item).casefold() for item in settings.get("competitor_domains", [])}
    records: dict[tuple[str, str, str], dict[str, Any]] = {}
    duplicate_count = invalid_rows = 0
    domain_targets: dict[str, set[str]] = defaultdict(set)
    domain_destinations: dict[str, set[str]] = defaultdict(set)
    for dataset in prepared.datasets:
        dataset_id = str(dataset["snapshot_id"])
        for raw in dataset.get("records", []):
            row = dict(values(raw))
            source = row.get("url_from", row.get("source_url"))
            target = row.get("url_to", row.get("target_url"))
            if not isinstance(source, str) or not source.startswith("http") or not isinstance(target, str) or not target.startswith("http"):
                invalid_rows += 1
                continue
            source, target = canonicalize_url(source), canonicalize_url(target)
            domain = domain_of(source)
            key = (source, target, str(row.get("anchor", "")).strip().casefold())
            if key in records:
                duplicate_count += 1
                records[key]["dataset_ids"].add(dataset_id)
                continue
            row.update({"source_url": source, "target_url": target, "domain": domain, "dataset_ids": {dataset_id}})
            records[key] = row
            domain_targets[domain].add(target)
            domain_destinations[domain].add(domain_of(target))
            for linked_site in row.get("linked_sites", []) if isinstance(row.get("linked_sites"), list) else []:
                domain_destinations[domain].add(str(linked_site).casefold())
    if not records:
        raise ProcedureError("No valid backlink or referring-domain evidence rows are available")

    prospects: list[dict[str, Any]] = []
    drafts: list[FindingDraft] = []
    for key, row in sorted(records.items()):
        domain = row["domain"]
        risks: list[str] = []
        if as_bool(row.get("sitewide")) or len(domain_targets[domain]) >= int(settings.get("sitewide_target_threshold", 20)):
            risks.append("sitewide-pattern")
        if (as_number(row.get("outbound_links")) or 0) > int(settings.get("outbound_link_risk_threshold", 100)):
            risks.append("high-outbound-link-count")
        if as_bool(row.get("suspicious_network")):
            risks.append("suspected-link-network")
        if as_bool(row.get("pbn_pattern")):
            risks.append("possible-pbn-pattern")
        if as_bool(row.get("link_farm")):
            risks.append("possible-link-farm")
        if as_bool(row.get("irrelevant_directory")):
            risks.append("irrelevant-directory")
        if as_bool(row.get("paid_or_sponsored")):
            risks.append("paid-or-sponsored")
        if (as_number(row.get("sponsored_ratio")) or 0) > float(settings.get("sponsored_ratio_threshold", 0.5)):
            risks.append("excessive-sponsored-placement")
        if as_bool(row.get("exact_match_anchor_risk")):
            risks.append("exact-match-anchor-manipulation")
        if as_bool(row.get("automated_spam")):
            risks.append("automated-spam-environment")
        if as_bool(row.get("malware")):
            risks.append("malware-or-safety-risk")
        relevance = _score(row.get("topical_relevance"))
        audience = _score(row.get("audience_fit"))
        editorial = _score(row.get("editorial_quality"))
        plausibility = _score(row.get("traffic_plausibility"), 2 if as_number(row.get("traffic_domain")) is None else 3)
        geographic = _score(row.get("geographic_fit"))
        real_site = _score(row.get("real_site_plausibility"), editorial)
        organic_visibility = _score(row.get("organic_visibility_evidence"), plausibility)
        placement = _score(row.get("placement_relevance"), relevance)
        average = (relevance + audience + editorial + plausibility + geographic + real_site + organic_visibility + placement) / 8
        overall = "reject" if any(flag in risks for flag in {"suspected-link-network", "possible-pbn-pattern", "possible-link-farm", "malware-or-safety-risk", "automated-spam-environment"}) else "qualified" if average >= 4 and not risks else "review"
        opportunity = _opportunity(row)
        ids = tuple(sorted(row["dataset_ids"]))
        prospect = {
            "schema_version": "1.0.0", "prospect_id": stable_id("AUTH", project_id, *key), "project_id": project_id,
            "domain": domain, "source_url": row["source_url"], "evidence_references": list(ids),
            "qualification": {"topical_relevance": relevance, "audience_fit": audience, "editorial_quality": editorial, "traffic_plausibility": plausibility, "geographic_fit": geographic, "real_site_plausibility": real_site, "organic_visibility_evidence": organic_visibility, "placement_relevance": placement, "manipulation_risk": "high" if overall == "reject" else "medium" if risks else "low", "overall": overall},
            "risk_flags": sorted(risks), "target_page": row.get("target_url") if domain_of(row.get("target_url", "")) == target_domain or not target_domain else None,
            "linkable_asset": row.get("linkable_asset"), "opportunity_type": opportunity, "approval_status": "not-reviewed",
        }
        validate_instance("backlink-prospect", prospect)
        prospects.append(prospect)
        if opportunity != "other" or risks:
            drafts.append(FindingDraft(
                "authority-opportunity", f"{domain} is classified as {opportunity} with qualification {overall}" + (f" and flags {', '.join(sorted(risks))}" if risks else "") + ".",
                f"{opportunity}:{overall}", "Manually validate ownership, editorial legitimacy, relevance, contact context, and approval before preparing outreach.",
                ids, (row["source_url"],), inference="Third-party authority metrics are supporting evidence and are not treated as proof of quality.",
                finding_type="opportunity", impact="medium", effort="medium", confidence="low" if prepared.degraded else "medium",
                requires_validation=("Human qualification and approval are required; this procedure sends no outreach and acquires no links.",),
            ))
    return build_output(prepared, drafts, artifacts={
        "backlink_prospects": prospects, "duplicate_record_count": duplicate_count, "invalid_row_count": invalid_rows,
        "domain_target_counts": {domain: len(targets) for domain, targets in sorted(domain_targets.items())},
        "normalized_backlinks": [
            {
                "source_url": row["source_url"], "source_domain": row["domain"], "target_url": row["target_url"],
                "anchor": str(row.get("anchor", "")), "follow_state": row.get("follow_state", row.get("dofollow")),
                "first_seen": row.get("first_seen"), "last_seen": row.get("last_seen"),
                "third_party_metrics": {key: row.get(key) for key in ("domain_rating", "domain_rating_source", "traffic_domain") if row.get(key) is not None},
                "evidence_references": sorted(row["dataset_ids"]),
            }
            for _, row in sorted(records.items())
        ],
        "competitor_intersect": {
            domain: (
                "both" if target_domain in destinations and destinations.intersection(competitor_domains)
                else "target-only" if target_domain in destinations
                else "competitors-only" if destinations.intersection(competitor_domains)
                else "neither-configured-set"
            )
            for domain, destinations in sorted(domain_destinations.items())
        },
        "automation_boundary": "No outreach, contact enrichment, acquisition, disavow, or write action is performed.",
    })
