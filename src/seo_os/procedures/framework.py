"""Common deterministic procedure contracts and schema-valid finding output."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from seo_os.ingestion import validate_snapshot_payload
from seo_os.schemas import validate_instance
from seo_os.security import redact_mapping, scan_text

from .common import confidence_for, deduplicate_preserving_order, evidence_tier, stable_id


class ProcedureError(ValueError):
    """Fail-closed procedure error safe to surface to the director."""


@dataclass(frozen=True, slots=True)
class ProcedureSpec:
    procedure_id: str
    version: str
    workstream: str
    prefix: str
    minimum_any: tuple[str, ...]
    required_datasets: tuple[str, ...] = ()
    optional_datasets: tuple[str, ...] = ()
    output_schemas: tuple[str, ...] = ("specialist-finding",)


@dataclass(frozen=True, slots=True)
class FindingDraft:
    rule_id: str
    observed_fact: str
    classification: str
    recommendation: str
    dataset_ids: tuple[str, ...]
    affected_assets: tuple[str, ...] = ()
    inference: str | None = None
    requires_validation: tuple[str, ...] = ("Validate after approved implementation.",)
    finding_type: str = "issue"
    impact: str = "medium"
    effort: str = "medium"
    confidence: str | None = None
    dependencies: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PreparedInputs:
    spec: ProcedureSpec
    project_id: str
    brief_id: str
    datasets: tuple[Mapping[str, Any], ...]
    skipped: tuple[str, ...]
    limitations: tuple[str, ...]
    degraded: bool

    @property
    def input_dataset_ids(self) -> tuple[str, ...]:
        return tuple(str(item["snapshot_id"]) for item in self.datasets)

    @property
    def data_quality_status(self) -> str:
        statuses = {str(item.get("quality", {}).get("status", "warning")) for item in self.datasets}
        return "warning" if self.degraded or "warning" in statuses else "pass"

    def of_type(self, *dataset_types: str) -> tuple[Mapping[str, Any], ...]:
        allowed = set(dataset_types)
        return tuple(item for item in self.datasets if item["dataset_type"] in allowed)

    def evidence(self, dataset_ids: Sequence[str]) -> list[dict[str, Any]]:
        selected = [item for item in self.datasets if item["snapshot_id"] in set(dataset_ids)]
        return [
            {
                "reference": str(item["snapshot_id"]),
                "evidence_tier": evidence_tier(str(item["source"]), item.get("provenance", {})),
                "observed_at": str(item["retrieved_at"]),
                "limitations": list(item.get("limitations", [])),
            }
            for item in selected
        ]


def prepare_inputs(
    spec: ProcedureSpec,
    *,
    project_id: str,
    brief_id: str,
    datasets: Sequence[Mapping[str, Any]],
    approved_dataset_ids: Sequence[str],
) -> PreparedInputs:
    if not approved_dataset_ids:
        raise ProcedureError("Procedure execution requires explicit approved dataset IDs")
    approved = set(approved_dataset_ids)
    valid: list[Mapping[str, Any]] = []
    skipped: list[str] = []
    limitations: list[str] = []
    seen: set[str] = set()
    allowed_types = set(spec.minimum_any + spec.required_datasets + spec.optional_datasets)
    for dataset in datasets:
        snapshot_id = str(dataset.get("snapshot_id", ""))
        if not snapshot_id or snapshot_id in seen:
            raise ProcedureError("Every input must have one unique snapshot ID")
        seen.add(snapshot_id)
        if snapshot_id not in approved:
            raise ProcedureError(f"Dataset is not approved for this procedure: {snapshot_id}")
        validate_snapshot_payload(dataset)
        if scan_text(json.dumps(dataset, sort_keys=True, default=str), f"snapshot:{snapshot_id}"):
            raise ProcedureError(f"Dataset contains credential-like material and cannot be analyzed: {snapshot_id}")
        if dataset.get("project_id") != project_id:
            raise ProcedureError(f"Dataset belongs to another project: {snapshot_id}")
        if dataset.get("dataset_type") not in allowed_types:
            raise ProcedureError(f"Dataset type is outside procedure scope: {dataset.get('dataset_type')}")
        status = str(dataset.get("quality", {}).get("status", "warning"))
        if status == "blocking":
            skipped.append(snapshot_id)
            limitations.append(f"Blocked dataset excluded: {snapshot_id}")
            continue
        valid.append(dataset)
        limitations.extend(str(item) for item in dataset.get("limitations", []))

    present = {str(item["dataset_type"]) for item in valid}
    missing_required = set(spec.required_datasets) - present
    if missing_required:
        raise ProcedureError(f"Required datasets are unavailable or blocking: {', '.join(sorted(missing_required))}")
    if spec.minimum_any and not present.intersection(spec.minimum_any):
        raise ProcedureError("Minimum viable evidence is unavailable or blocking")
    missing_optional = set(spec.optional_datasets) - present
    degraded = bool(skipped or missing_optional or any(str(item.get("quality", {}).get("status")) == "warning" for item in valid))
    limitations.extend(f"Optional dataset unavailable: {item}" for item in sorted(missing_optional))
    return PreparedInputs(
        spec, project_id, brief_id, tuple(sorted(valid, key=lambda item: str(item["snapshot_id"]))),
        tuple(skipped), deduplicate_preserving_order(limitations), degraded,
    )


def build_output(
    prepared: PreparedInputs,
    drafts: Sequence[FindingDraft],
    *,
    artifacts: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    components: list[dict[str, Any]] = []
    for draft in sorted(drafts, key=lambda item: (item.rule_id, item.affected_assets, item.classification)):
        finding_id = stable_id(prepared.spec.prefix, prepared.project_id, prepared.spec.procedure_id, prepared.spec.version, draft.rule_id, draft.affected_assets, draft.classification)
        evidence = prepared.evidence(draft.dataset_ids)
        if not evidence:
            raise ProcedureError(f"Finding has no approved evidence: {draft.rule_id}")
        confidence = "low" if prepared.degraded else draft.confidence or confidence_for(
            direct=draft.inference is None,
            tiers=(item["evidence_tier"] for item in evidence),
            degraded=False,
        )
        finding = {
            "schema_version": "1.0.0",
            "finding_id": finding_id,
            "project_id": prepared.project_id,
            "brief_id": prepared.brief_id,
            "workstream": prepared.spec.workstream,
            "finding_type": draft.finding_type,
            "statement": draft.observed_fact,
            "evidence": evidence,
            "affected_assets": list(draft.affected_assets),
            "recommended_direction": draft.recommendation,
            "impact": draft.impact,
            "confidence": confidence,
            "effort": draft.effort,
            "dependencies": list(draft.dependencies),
            "validation": list(draft.requires_validation),
        }
        validate_instance("specialist-finding", finding)
        findings.append(finding)
        components.append(
            {
                "finding_id": finding_id,
                "observed_fact": draft.observed_fact,
                "deterministic_classification": draft.classification,
                "evidence_backed_inference": draft.inference,
                "recommendation": draft.recommendation,
                "requires_validation": list(draft.requires_validation),
            }
        )
    input_evidence = [
        {
            "snapshot_id": str(item["snapshot_id"]),
            "ingestion_id": str(item["ingestion_id"]),
            "manifest_reference": item.get("manifest_reference"),
            "source": str(item["source"]),
            "dataset_type": str(item["dataset_type"]),
            "resource_id": str(item["resource_id"]),
            "period": item.get("period"),
            "retrieved_at": str(item["retrieved_at"]),
            "provider_timestamp": item.get("provenance", {}).get("provider_timestamp"),
            "provenance": dict(item.get("provenance", {})),
            "quality": dict(item.get("quality", {})),
            "evidence_tier": evidence_tier(str(item["source"]), item.get("provenance", {})),
            "limitations": list(item.get("limitations", [])),
        }
        for item in prepared.datasets
    ]
    output = {
        "procedure_id": prepared.spec.procedure_id,
        "procedure_version": prepared.spec.version,
        "output_schemas": list(prepared.spec.output_schemas),
        "project_id": prepared.project_id,
        "brief_id": prepared.brief_id,
        "workstream": prepared.spec.workstream,
        "input_dataset_ids": list(prepared.input_dataset_ids),
        "input_evidence": input_evidence,
        "data_quality_status": prepared.data_quality_status,
        "degraded_mode": prepared.degraded,
        "skipped_dataset_ids": list(prepared.skipped),
        "limitations": list(prepared.limitations),
        "findings": findings,
        "finding_components": components,
        "artifacts": dict(artifacts or {}),
        "handoff": "seo-director",
    }
    return redact_mapping(output)
