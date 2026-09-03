"""Deterministic GEO/AEO readiness checks without unsupported visibility claims."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from .common import as_bool, canonicalize_url, values
from .framework import FindingDraft, ProcedureError, ProcedureSpec, build_output, prepare_inputs


SPEC = ProcedureSpec(
    "geo-aeo", "1.0.0", "geo-aeo", "GEO",
    minimum_any=("generic-tabular-evidence",), required_datasets=("generic-tabular-evidence",),
    output_schemas=("specialist-finding",),
)

CHECKS = {
    "entity_clarity": "Clarify the primary entity and its relationship to the organization.",
    "organization_consistency": "Reconcile organization identity, naming, and corroborating references.",
    "author_present": "Provide attributable authorship where readers benefit from accountable expertise.",
    "reviewer_present": "Add an appropriate expert review process where subject risk warrants it.",
    "sources_present": "Cite relevant, inspectable primary or authoritative sources.",
    "original_evidence": "Add first-hand evidence, methods, examples, or original analysis.",
    "direct_answer": "Provide a concise answer that is supported by the surrounding page evidence.",
    "definition_complete": "Add a precise, supportable definition for the principal concept where relevant.",
    "explanation_complete": "Explain material qualifications, mechanisms, and limitations needed for a complete answer.",
    "question_coverage": "Cover material follow-up questions without padding or unsupported claims.",
    "structured_data_aligned": "Align structured data with visible content and actual entity relationships.",
    "external_corroboration": "Pursue legitimate third-party corroboration; do not fabricate mentions.",
    "citation_worthy": "Strengthen inspectable sourcing, originality, specificity, and accountable expertise.",
    "snippet_eligible": "Correct blocking technical conditions before treating the page as answer-ready.",
}


def run_geo_procedure(
    *, project_id: str, brief_id: str, datasets: Sequence[Mapping[str, Any]],
    approved_dataset_ids: Sequence[str], config: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    prepared = prepare_inputs(SPEC, project_id=project_id, brief_id=brief_id, datasets=datasets, approved_dataset_ids=approved_dataset_ids)
    pages: list[dict[str, Any]] = []
    drafts: list[FindingDraft] = []
    invalid_rows = 0
    for dataset in prepared.datasets:
        dataset_id = str(dataset["snapshot_id"])
        for record in dataset.get("records", []):
            row = values(record)
            raw_url = row.get("url", row.get("page"))
            if not isinstance(raw_url, str) or not raw_url.startswith("http"):
                invalid_rows += 1
                continue
            url = canonicalize_url(raw_url)
            results: dict[str, str] = {}
            passed = observed = 0
            for check, recommendation in CHECKS.items():
                result = as_bool(row.get(check))
                if result is None:
                    results[check] = "not-observed"
                    continue
                observed += 1
                if result:
                    passed += 1
                    results[check] = "pass"
                else:
                    results[check] = "fail"
                    drafts.append(FindingDraft(
                        check, f"{url} failed the observed {check.replace('_', ' ')} check.", f"{check}-gap", recommendation,
                        (dataset_id,), (url,), finding_type="issue", impact="medium", effort="medium",
                        requires_validation=("Re-inspect visible page content and rendered structured data after an approved change.",),
                        dependencies=("seo-content-strategy",) if check not in {"snippet_eligible", "structured_data_aligned"} else ("technical-seo",),
                    ))
            score = round(100 * passed / observed, 1) if observed else None
            pages.append({
                "url": url, "checks": results, "observed_check_count": observed,
                "passed_check_count": passed, "internal_readiness_percentage": score,
                "score_definition": "Passed observable checks divided by observable checks; not an AI-engine visibility metric.",
                "dataset_id": dataset_id,
                "external_citation_evidence": row.get("external_citation_evidence", "not-observed"),
                "search_visibility_evidence": row.get("search_visibility_evidence", "not-observed"),
                "ai_visibility_evidence": row.get("ai_visibility_evidence", "not-observed"),
                "model_specific_state": "unknown unless explicitly observed in an approved, time-stamped source",
            })
            if observed == 0:
                drafts.append(FindingDraft(
                    "insufficient-observation", f"No GEO/AEO readiness fields were observable for {url}.", "requires-validation",
                    "Collect rendered page, visible content, authorship, source, entity, and structured-data evidence before classification.",
                    (dataset_id,), (url,), finding_type="validation-required", impact="low", effort="low", confidence="low",
                    requires_validation=("Acquire an approved page-level evidence record with explicit check values.",),
                ))
    if not pages:
        raise ProcedureError("No valid page-level GEO/AEO evidence rows are available")
    return build_output(prepared, drafts, artifacts={
        "page_readiness": sorted(pages, key=lambda item: item["url"]), "invalid_row_count": invalid_rows,
        "claim_boundary": "Outputs assess observable readiness only; they do not claim AI Overview, answer-engine, citation, or traffic visibility.",
    })
