"""Deterministic organic landing-page CRO observations and test hypotheses."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping, Sequence

from seo_os.schemas import validate_instance

from .common import as_bool, as_number, canonicalize_url, stable_id, values
from .framework import FindingDraft, ProcedureError, ProcedureSpec, build_output, prepare_inputs


SPEC = ProcedureSpec(
    "seo-cro", "1.0.0", "seo-cro", "CRO",
    minimum_any=("ga4-organic-landing-performance", "gsc-search-performance", "generic-tabular-evidence", "crux-field-performance"),
    optional_datasets=("ga4-organic-landing-performance", "gsc-search-performance", "generic-tabular-evidence", "crux-field-performance"),
    output_schemas=("specialist-finding", "cro-hypothesis"),
)

FRICTION_RULES = {
    "cta_visible": (False, "primary-cta-not-visible", "Make the primary next step clear and visible."),
    "message_match": (False, "organic-message-mismatch", "Align the landing-page promise with observed organic query intent."),
    "value_proposition_clear": (False, "weak-value-proposition", "Clarify the differentiated value proposition with supportable proof."),
    "form_error": (True, "form-error", "Repair and validate the form flow."),
    "form_friction": (True, "form-friction", "Reduce only the observed unnecessary form friction while preserving required qualification."),
    "trust_signals_present": (False, "trust-gap", "Add accurate, substantiated trust evidence near the decision point."),
    "pricing_or_risk_unclear": (True, "pricing-risk-uncertainty", "Clarify substantiated pricing, delivery, return, or risk information relevant to the decision."),
    "mobile_obstruction": (True, "mobile-obstruction", "Remove the observed mobile interaction obstruction."),
    "navigation_dead_end": (True, "navigation-dead-end", "Provide a relevant next step without creating manipulative navigation."),
    "accessibility_issue": (True, "accessibility-observation", "Validate and remediate the observed accessibility barrier."),
}


def run_cro_procedure(
    *, project_id: str, brief_id: str, datasets: Sequence[Mapping[str, Any]],
    approved_dataset_ids: Sequence[str], config: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    settings = dict(config or {})
    prepared = prepare_inputs(SPEC, project_id=project_id, brief_id=brief_id, datasets=datasets, approved_dataset_ids=approved_dataset_ids)
    pages: dict[str, dict[str, Any]] = defaultdict(lambda: {"sessions": 0.0, "clicks": 0.0, "conversions": 0.0, "ids": set(), "observations": []})
    invalid_rows = 0
    for dataset in prepared.datasets:
        dataset_id = str(dataset["snapshot_id"])
        for record in dataset.get("records", []):
            row = values(record)
            raw_url = row.get("landingPage", row.get("page", row.get("url", row.get("resource"))))
            if not isinstance(raw_url, str) or not raw_url:
                invalid_rows += 1
                continue
            url = canonicalize_url(raw_url) if raw_url.startswith("http") else raw_url
            page = pages[url]
            page["ids"].add(dataset_id)
            page["sessions"] += as_number(row.get("sessions")) or 0
            page["clicks"] += as_number(row.get("clicks")) or 0
            page["conversions"] += as_number(row.get("keyEvents", row.get("conversions"))) or 0
            for field, (trigger, classification, recommendation) in FRICTION_RULES.items():
                observed = as_bool(row.get(field))
                if observed is trigger:
                    page["observations"].append((classification, recommendation, dataset_id))
            if row.get("field_classification") in {"poor", "needs-improvement"}:
                page["observations"].append(("field-performance-friction", "Resolve confirmed field-performance constraints before interpreting the test.", dataset_id))
    if not pages:
        raise ProcedureError("No valid organic landing-page evidence rows are available")

    minimum_sessions = float(settings.get("minimum_sessions_for_rate", 100))
    hypotheses: list[dict[str, Any]] = []
    drafts: list[FindingDraft] = []
    candidates: list[dict[str, Any]] = []
    for url, page in sorted(pages.items()):
        rate = page["conversions"] / page["sessions"] if page["sessions"] >= minimum_sessions else None
        candidates.append({"url": url, "sessions": page["sessions"], "gsc_clicks": page["clicks"], "conversions": page["conversions"], "ga4_conversion_rate": rate, "business_relevance": settings.get("business_relevance", {}).get(url, "requires-validation"), "landing_page_role": settings.get("landing_page_roles", {}).get(url, "requires-validation"), "evidence_quality": prepared.data_quality_status, "evidence_references": sorted(page["ids"])})
        for classification, recommendation, evidence_id in sorted(set(page["observations"])):
            hypothesis_text = f"If the observed {classification} is resolved for organic visitors, the primary metric may improve; causality is unproven until tested."
            hypothesis = {
                "schema_version": "1.0.0", "hypothesis_id": stable_id("CRO", project_id, url, classification), "project_id": project_id,
                "affected_pages": [url], "segment": str(settings.get("segment", "organic landing-page sessions")),
                "observation": f"The approved evidence explicitly records {classification} on {url}.", "evidence_references": [evidence_id],
                "hypothesis": hypothesis_text, "proposed_change": recommendation,
                "expected_behavior": "More eligible organic visitors complete the intended next step without worsening guardrail metrics.",
                "primary_metric": str(settings.get("primary_metric", "GA4 key events per organic session")),
                "guardrails": list(settings.get("guardrails", ["Organic sessions", "Revenue per organic session", "Field performance"])),
                "measurement_requirements": {
                    "method": str(settings.get("experiment_method", "controlled-experiment")),
                    "minimum_detectable_effect": float(settings.get("minimum_detectable_effect", 0.10)),
                    "alpha": float(settings.get("alpha", 0.05)),
                    "power": float(settings.get("power", 0.80)),
                    "minimum_duration_days": int(settings.get("minimum_duration_days", 14)),
                },
                "status": "draft",
            }
            validate_instance("cro-hypothesis", hypothesis)
            hypotheses.append(hypothesis)
            drafts.append(FindingDraft(
                "cro-friction", hypothesis["observation"], classification, recommendation, (evidence_id,), (url,),
                inference=hypothesis_text, finding_type="opportunity", impact="medium", effort="medium",
                requires_validation=("Define sample-size parameters with measurement ownership, obtain approval, run a controlled test where feasible, and evaluate guardrails.",),
                dependencies=("seo-measurement",),
            ))
    return build_output(prepared, drafts, artifacts={
        "landing_page_candidates": candidates, "cro_hypotheses": hypotheses, "invalid_row_count": invalid_rows,
        "experiment_boundary": "Default planning parameters are explicit and configurable; Measurement must validate sample size, duration, interference, and metric instrumentation before launch.",
        "metric_boundary": "GSC clicks and GA4 sessions remain separate fields; neither is substituted for the other.",
    })
