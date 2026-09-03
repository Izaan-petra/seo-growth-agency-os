"""Deterministic technical SEO classification and issue generation."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from seo_os.schemas import validate_instance
from seo_os.security import redact_mapping

from .common import as_bool, as_number, canonicalize_url, classify_cwv, domain_of, stable_id, values
from .framework import FindingDraft, ProcedureSpec, build_output, prepare_inputs


SPEC = ProcedureSpec(
    "technical-seo", "1.0.0", "technical-seo", "TECH",
    minimum_any=("generic-tabular-evidence", "crux-field-performance", "psi-lab-performance", "gsc-search-performance"),
    optional_datasets=("generic-tabular-evidence", "crux-field-performance", "psi-lab-performance", "gsc-search-performance"),
    output_schemas=("specialist-finding", "technical-issue"),
)


def classify_url(record: Mapping[str, Any]) -> tuple[str, ...]:
    row = values(record)
    status = int(as_number(row.get("status_code", row.get("status"))) or 0)
    url = str(row.get("url", ""))
    canonical = str(row.get("canonical", row.get("declared_canonical", "")) or "")
    meta = f"{row.get('meta_robots', '')} {row.get('x_robots_tag', '')}".casefold()
    classes: list[str] = []
    if 500 <= status <= 599:
        classes.append("5xx")
    elif 400 <= status <= 499:
        classes.append("4xx")
    elif 300 <= status <= 399:
        classes.append("redirect")
    else:
        if as_bool(row.get("robots_allowed")) is False:
            classes.append("blocked")
        if "noindex" in meta or as_bool(row.get("indexable")) is False:
            classes.append("noindex")
        if status == 200 and url and not classes:
            classes.append("indexable")
        elif not classes:
            classes.append("unknown")
    if url and canonical and canonicalize_url(url) != canonicalize_url(canonical):
        classes.append("canonicalized")
    if row.get("duplicate_group") or as_bool(row.get("duplicate")) is True:
        classes.append("duplicate-risk")
    if as_number(row.get("inlinks")) == 0 and not as_bool(row.get("is_homepage")):
        classes.append("orphan-risk")
    if as_bool(row.get("crawl_trap")) is True or len(str(row.get("url", "")).split("?", 1)) > 1 and str(row.get("url", "")).count("=") >= 3:
        classes.append("crawl-trap-risk")
    return tuple(classes)


def run_technical_procedure(
    *, project_id: str, brief_id: str, datasets: Sequence[Mapping[str, Any]],
    approved_dataset_ids: Sequence[str], config: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    settings = dict(config or {})
    prepared = prepare_inputs(
        SPEC, project_id=project_id, brief_id=brief_id,
        datasets=datasets, approved_dataset_ids=approved_dataset_ids,
    )
    drafts: list[FindingDraft] = []
    url_inventory: list[dict[str, Any]] = []
    rows: list[tuple[str, Mapping[str, Any]]] = []
    for dataset in prepared.of_type("generic-tabular-evidence"):
        for record in dataset.get("records", []):
            row = values(record)
            if row.get("url"):
                rows.append((str(dataset["snapshot_id"]), row))

    known_urls = {canonicalize_url(str(row["url"])) for _, row in rows if row.get("url")}
    status_by_url = {
        canonicalize_url(str(row["url"])): int(as_number(row.get("status_code", row.get("status"))) or 0)
        for _, row in rows if row.get("url")
    }
    redirect_map = {
        canonicalize_url(str(row["url"])): canonicalize_url(str(row.get("redirect_to", row.get("redirect_destination"))))
        for _, row in rows if row.get("url") and row.get("redirect_to", row.get("redirect_destination"))
    }
    max_depth = int(settings.get("max_crawl_depth", 4))
    for dataset_id, row in sorted(rows, key=lambda item: canonicalize_url(str(item[1]["url"]))):
        url = canonicalize_url(str(row["url"]))
        classes = classify_url(row)
        url_inventory.append({"url": url, "classifications": list(classes)})
        status = int(as_number(row.get("status_code", row.get("status"))) or 0)
        preferred_host = str(settings.get("preferred_host", "")).casefold()
        preferred_protocol = str(settings.get("preferred_protocol", "")).casefold()
        actual_host = domain_of(url)
        actual_protocol = url.split(":", 1)[0].casefold() if ":" in url else ""
        if (preferred_host and actual_host != preferred_host) or (preferred_protocol and actual_protocol != preferred_protocol):
            drafts.append(FindingDraft(
                "host-protocol", f"{url} does not match the configured preferred host/protocol.", "host-protocol-mismatch",
                "Align redirect, canonical, sitemap, and internal-link signals with the approved preferred origin.",
                (dataset_id,), (url,), impact="medium", effort="medium",
                requires_validation=("Retest all origin variants and the submitted sitemap after an approved change.",),
            ))
        if "4xx" in classes or "5xx" in classes:
            drafts.append(FindingDraft(
                "http-status", f"{url} returned HTTP {status}.", classes[0],
                "Restore a valid response or update internal references to an appropriate live destination.",
                (dataset_id,), (url,), impact="high" if "5xx" in classes else "medium", effort="medium",
                requires_validation=("Recrawl the URL and every known internal source link.",),
            ))
        if "blocked" in classes or "noindex" in classes:
            reason = "robots-blocked" if "blocked" in classes else "noindex"
            drafts.append(FindingDraft(
                "indexability", f"{url} is deterministically classified as {reason}.", reason,
                "Confirm whether exclusion is intentional; align crawl access, directives, canonical signals, and sitemap membership.",
                (dataset_id,), (url,), impact="high" if as_bool(row.get("in_sitemap")) else "medium",
                requires_validation=("Validate robots.txt and page/header directives with a fresh crawl.",),
            ))
        canonical = row.get("canonical", row.get("declared_canonical"))
        if canonical and canonicalize_url(str(canonical)) != url:
            drafts.append(FindingDraft(
                "canonical", f"{url} declares {canonicalize_url(str(canonical))} as canonical.", "declared-canonical-differs",
                "Verify the pages are duplicates and align internal links, sitemap inclusion, redirects, and canonical signals.",
                (dataset_id,), (url,), inference="The declared canonical may consolidate this URL, but Google selection is unverified.",
                requires_validation=("Use approved Search Console URL Inspection evidence before claiming Google-selected canonical.",),
            ))
        if as_bool(row.get("in_sitemap")) and (status != 200 or "noindex" in classes or "blocked" in classes or "canonicalized" in classes or "duplicate-risk" in classes):
            drafts.append(FindingDraft(
                "sitemap", f"Sitemap member {url} is not a clean indexable self-canonical HTTP 200 URL.", "invalid-sitemap-member",
                "Keep only preferred, indexable, self-canonical HTTP 200 URLs in the submitted sitemap.",
                (dataset_id,), (url,), impact="medium", effort="low",
                requires_validation=("Regenerate and validate the sitemap, then recrawl its URLs.",),
            ))
        if "orphan-risk" in classes:
            drafts.append(FindingDraft(
                "internal-links", f"{url} has zero recorded internal inlinks.", "orphan-candidate",
                "Confirm inventory coverage and add justified crawlable links from relevant pages if the URL is important.",
                (dataset_id,), (url,), inference="The URL is an orphan candidate; incomplete crawl scope may explain the zero count.",
                impact="high" if str(row.get("business_role", "")).casefold() in {"high", "primary", "conversion"} else "medium",
                requires_validation=("Recrawl from all approved seeds and compare sitemap and GSC evidence.",),
                dependencies=("keyword-intent-strategy", "seo-content-strategy"),
            ))
        if "duplicate-risk" in classes:
            drafts.append(FindingDraft(
                "duplicate-url", f"{url} has explicit duplicate-group evidence.", "duplicate-risk",
                "Validate content equivalence and align canonical, redirect, sitemap, and internal-link signals to one preferred URL where appropriate.",
                (dataset_id,), (url,), inference="Duplicate evidence requires canonical-target review; it does not prove Google's selected canonical.",
                impact="medium", effort="medium", requires_validation=("Compare rendered content and approved Search Console canonical evidence before consolidation.",),
            ))
        outlinks = row.get("internal_links", row.get("outlinks", []))
        if isinstance(outlinks, (list, tuple)):
            broken = sorted({canonicalize_url(str(destination)) for destination in outlinks if status_by_url.get(canonicalize_url(str(destination)), 0) >= 400})
            if broken:
                drafts.append(FindingDraft(
                    "broken-internal-destination", f"{url} links to {len(broken)} known 4xx/5xx internal destination(s).", "broken-internal-links",
                    "Update the internal references to verified live destinations or restore the intended pages.",
                    (dataset_id,), tuple([url, *broken]), impact="high", effort="low",
                    requires_validation=("Recrawl every source and destination after approved link changes.",),
                ))
        if "redirect" in classes and as_bool(row.get("redirect_relevance")) is False:
            drafts.append(FindingDraft(
                "inappropriate-redirect", f"{url} has an explicitly observed non-equivalent redirect destination.", "inappropriate-redirect",
                "Choose a genuinely equivalent replacement or return the appropriate terminal status.",
                (dataset_id,), (url,), impact="medium", effort="low",
                requires_validation=("Review the source/destination intent and retest the approved response.",),
            ))
        depth = as_number(row.get("crawl_depth", row.get("depth")))
        if depth is not None and depth > max_depth:
            drafts.append(FindingDraft(
                "crawl-depth", f"{url} was found at crawl depth {int(depth)}, above the configured threshold {max_depth}.", "excessive-depth",
                "Review structural and contextual link paths to reduce isolation for important pages.",
                (dataset_id,), (url,), impact="medium", effort="medium",
                requires_validation=("Recrawl after approved navigation or internal-link changes.",),
                dependencies=("seo-content-strategy",),
            ))
        if "crawl-trap-risk" in classes:
            drafts.append(FindingDraft(
                "crawl-trap", f"{url} matches the configured crawl-trap evidence rule.", "crawl-trap-risk",
                "Constrain unnecessary URL generation while preserving crawlable canonical pages.",
                (dataset_id,), (url,), confidence="medium",
                requires_validation=("Inspect parameter behavior, crawl paths, and server logs before applying controls.",),
            ))
        if as_bool(row.get("soft_404")) is True:
            drafts.append(FindingDraft(
                "soft-404", f"{url} has explicit soft-404 evidence.", "soft-404-evidence",
                "Return a meaningful page or an appropriate real 404/410 response.",
                (dataset_id,), (url,), confidence="medium",
                requires_validation=("Confirm using content inspection and approved Search Console evidence.",),
            ))

    for source, destination in sorted(redirect_map.items()):
        chain = [source]
        current = destination
        while current in redirect_map and current not in chain and len(chain) <= 20:
            chain.append(current)
            current = redirect_map[current]
        if current in chain:
            dataset_id = next(dataset_id for dataset_id, row in rows if canonicalize_url(str(row["url"])) == source)
            drafts.append(FindingDraft(
                "redirect-loop", f"Redirect traversal from {source} repeats {current}.", "redirect-loop",
                "Replace the loop with one direct redirect to a verified final destination.",
                (dataset_id,), tuple(chain), impact="critical", effort="medium",
                requires_validation=("Retest every hop until one non-redirecting final response is reached.",),
            ))
        elif len(chain) > 1:
            dataset_id = next(dataset_id for dataset_id, row in rows if canonicalize_url(str(row["url"])) == source)
            drafts.append(FindingDraft(
                "redirect-chain", f"Redirect traversal from {source} contains {len(chain)} redirecting URLs.", "redirect-chain",
                "Collapse the chain to one appropriate redirect where platform constraints permit.",
                (dataset_id,), tuple(chain), impact="medium", effort="medium",
                requires_validation=("Retest the original URL and final destination after the redirect map changes.",),
            ))

    cwv_results: list[dict[str, Any]] = []
    for dataset in prepared.of_type("crux-field-performance"):
        for record in dataset.get("records", []):
            resource = str(record.get("resource", dataset["resource_id"]))
            metrics = record.get("metrics", {})
            if not isinstance(metrics, Mapping):
                continue
            for metric, evidence in sorted(metrics.items()):
                if metric not in {"largest_contentful_paint", "interaction_to_next_paint", "cumulative_layout_shift"} or not isinstance(evidence, Mapping):
                    continue
                percentiles = evidence.get("percentiles", {})
                p75 = as_number(evidence.get("p75", percentiles.get("p75") if isinstance(percentiles, Mapping) else None))
                if p75 is None:
                    continue
                classification = classify_cwv(metric, p75)
                cwv_results.append({"resource": resource, "metric": metric, "p75": p75, "classification": classification, "evidence_class": "field"})
                if classification != "good":
                    drafts.append(FindingDraft(
                        f"cwv-{metric}", f"CrUX field p75 for {resource} is {p75:g} for {metric}.", f"field-cwv-{classification}",
                        "Diagnose representative templates with lab tooling, then validate improvements in subsequent field data.",
                        (str(dataset["snapshot_id"]),), (resource,), impact="high" if classification == "poor" else "medium",
                        requires_validation=("Validate against a later CrUX collection period; do not substitute a Lighthouse score.",),
                        dependencies=("seo-cro", "seo-measurement"),
                    ))

    lab_diagnostics = [
        {"resource": record.get("final_url", dataset["resource_id"]), "performance_score": record.get("performance_score"), "evidence_class": "lab"}
        for dataset in prepared.of_type("psi-lab-performance") for record in dataset.get("records", [])
    ]
    output = build_output(prepared, drafts, artifacts={"url_inventory": url_inventory, "core_web_vitals": cwv_results, "psi_lab_diagnostics": lab_diagnostics})
    issues: list[dict[str, Any]] = []
    draft_by_id = {stable_id("TECH", project_id, SPEC.procedure_id, SPEC.version, item.rule_id, item.affected_assets, item.classification): item for item in drafts}
    for finding in output["findings"]:
        draft = draft_by_id[finding["finding_id"]]
        issue = {
            "schema_version": "1.0.0", "issue_id": finding["finding_id"], "project_id": project_id,
            "rule_id": draft.rule_id, "observed_at": finding["evidence"][0]["observed_at"],
            "category": draft.classification, "affected_urls": list(draft.affected_assets),
            "expected_state": draft.recommendation, "actual_state": draft.observed_fact,
            "evidence_references": [item["reference"] for item in finding["evidence"]],
            "recommended_direction": draft.recommendation, "impact": finding["impact"],
            "confidence": finding["confidence"], "validation": finding["validation"],
        }
        if issue["affected_urls"]:
            validate_instance("technical-issue", issue)
            issues.append(issue)
    output["artifacts"]["technical_issues"] = issues
    output["artifacts"]["known_url_count"] = len(known_urls)
    return redact_mapping(output)
