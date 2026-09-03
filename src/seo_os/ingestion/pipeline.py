"""Immutable raw capture, manifest creation, quality gating, and snapshots."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping, Sequence

from seo_os.connectors.base import AcquisitionRequest, ConnectorContext, ConnectorResult
from seo_os.datasets import CanonicalDataset, DATASET_DEFINITIONS
from seo_os.schemas import repository_root
from seo_os.security.privacy import scan_text

from .manifest import IngestionManifest, write_ingestion_manifest
from .quality import QualityIssue, quality_report_as_dict, validate_records
from .snapshot import deterministic_snapshot_id, write_immutable_json


def persist_acquisition(
    *,
    context: ConnectorContext,
    request: AcquisitionRequest,
    acquisition_method: str,
    dataset: CanonicalDataset,
    raw_content: bytes,
    raw_media_type: str,
    rejected_records: Sequence[Mapping[str, Any]] = (),
    extra_quality_issues: Sequence[QualityIssue] = (),
    truncated: bool = False,
    partial_api_result: bool = False,
    screenshot_evidence: bool = False,
    missing_field_data: bool = False,
) -> ConnectorResult:
    root = _approved_root(context.data_root)
    retrieved_at = dataset.retrieved_at.astimezone(UTC)
    date_path = retrieved_at.date().isoformat()
    ingestion_id = _ingestion_id(context, request, acquisition_method, retrieved_at)
    extension = _media_extension(raw_media_type)
    raw_relative = Path("raw") / context.project_id / dataset.source / date_path / f"{ingestion_id}{extension}"
    raw_path = root / raw_relative

    if raw_media_type.startswith("text/") or raw_media_type.endswith("json"):
        try:
            raw_text = raw_content.decode("utf-8")
        except UnicodeDecodeError:
            raw_text = ""
        findings = scan_text(raw_text, raw_relative.as_posix()) if raw_text else ()
        if findings:
            raise ValueError("Raw provider payload contains credential-like material and was not stored")

    raw_checksum = _write_immutable_bytes(raw_path, raw_content)
    definition = DATASET_DEFINITIONS[dataset.dataset_type]
    expected_currency = str(dataset.provenance.get("expected_currency") or "") or None
    quality = validate_records(
        source=dataset.source,
        record_type=dataset.dataset_type,
        records=dataset.records,
        required_fields=definition.required_fields,
        duplicate_key_fields=definition.duplicate_key_fields,
        resource_id=dataset.resource_id,
        expected_currency=expected_currency,
        truncated=truncated,
        partial_api_result=partial_api_result,
        screenshot_evidence=screenshot_evidence,
        missing_field_data=missing_field_data,
        extra_issues=extra_quality_issues,
    )
    quality_payload = quality_report_as_dict(quality)
    status = "quarantined" if not quality.usable else "partial" if (rejected_records or truncated or partial_api_result or missing_field_data) else "complete"
    period = None
    if request.start_date and request.end_date:
        period = {"start_date": request.start_date, "end_date": request.end_date}
    manifest_payload = {
        "schema_version": "1.0.0",
        "ingestion_id": ingestion_id,
        "project_id": context.project_id,
        "authorization_id": context.authorization_id,
        "source": dataset.source,
        "record_type": dataset.dataset_type,
        "resource_id": request.resource_id,
        "acquisition_method": acquisition_method,
        "retrieved_at": retrieved_at.isoformat().replace("+00:00", "Z"),
        "period": period,
        "filters": _safe_manifest_filters(request.filters),
        "metadata": _safe_manifest_metadata(dataset.provenance),
        "fields": list(dict.fromkeys(request.fields)),
        "raw_artifact": {
            "relative_path": raw_relative.as_posix(),
            "media_type": raw_media_type,
            "checksum_sha256": raw_checksum,
            "size_bytes": len(raw_content),
        },
        "row_count": len(dataset.records),
        "status": status,
        "errors": [],
        "limitations": list(dataset.limitations),
    }
    manifest = IngestionManifest.from_mapping(manifest_payload)
    manifest_relative = Path("processed") / context.project_id / "manifests" / date_path / f"{ingestion_id}.json"
    write_ingestion_manifest(root / manifest_relative, manifest)

    snapshot_payload = None
    snapshot_descriptor = None
    if quality.usable:
        snapshot_base = {
            **dataset.as_dict(),
            "ingestion_id": ingestion_id,
            "project_id": context.project_id,
            "manifest_reference": manifest_relative.as_posix(),
            "quality": quality_payload,
        }
        snapshot_id = deterministic_snapshot_id(snapshot_base)
        snapshot_payload = {"snapshot_id": snapshot_id, **snapshot_base}
        snapshot_relative = Path("snapshots") / context.project_id / dataset.source / date_path / f"{snapshot_id}.json"
        snapshot_checksum = write_immutable_json(root / snapshot_relative, snapshot_payload)
        snapshot_descriptor = {
            "snapshot_id": snapshot_id,
            "project_id": context.project_id,
            "source": dataset.source,
            "record_type": dataset.dataset_type,
            "captured_at": retrieved_at.isoformat().replace("+00:00", "Z"),
            "schema_version": dataset.schema_version,
            "row_count": len(dataset.records),
            "checksum_sha256": snapshot_checksum,
            "relative_path": snapshot_relative.as_posix(),
            "ingestion_id": ingestion_id,
            "manifest_reference": manifest_relative.as_posix(),
            "provenance": dict(dataset.provenance),
        }

    metadata = {
        **dict(dataset.provenance),
        "raw_artifact": raw_relative.as_posix(),
        "ingestion_manifest": manifest_relative.as_posix(),
    }
    return ConnectorResult(
        source=dataset.source,
        acquisition_method=acquisition_method,
        retrieved_at=retrieved_at,
        records=dataset.records,
        limitations=dataset.limitations,
        metadata=metadata,
        status=status,
        ingestion_manifest=manifest.as_dict(),
        quality_report=quality_payload,
        snapshot=snapshot_descriptor,
        rejected_records=tuple(dict(item) for item in rejected_records),
    )


def persist_failure(
    *,
    context: ConnectorContext,
    request: AcquisitionRequest,
    source: str,
    acquisition_method: str,
    category: str,
    message: str,
    retryable: bool,
) -> ConnectorResult:
    now = datetime.now(UTC)
    safe_error = {"category": category, "message": message, "retryable": retryable}
    raw_content = (json.dumps({"status": "failed", "error": safe_error}, sort_keys=True) + "\n").encode("utf-8")
    root = _approved_root(context.data_root)
    ingestion_id = _ingestion_id(context, request, acquisition_method, now)
    relative = Path("raw") / context.project_id / source / now.date().isoformat() / f"{ingestion_id}.json"
    checksum = _write_immutable_bytes(root / relative, raw_content)
    period = {"start_date": request.start_date, "end_date": request.end_date} if request.start_date and request.end_date else None
    manifest_payload = {
        "schema_version": "1.0.0", "ingestion_id": ingestion_id,
        "project_id": context.project_id, "authorization_id": context.authorization_id,
        "source": source, "record_type": request.record_type,
        "resource_id": request.resource_id, "acquisition_method": acquisition_method,
        "retrieved_at": now.isoformat().replace("+00:00", "Z"), "period": period,
        "filters": _safe_manifest_filters(request.filters), "fields": list(dict.fromkeys(request.fields)),
        "raw_artifact": {"relative_path": relative.as_posix(), "media_type": "application/json", "checksum_sha256": checksum, "size_bytes": len(raw_content)},
        "row_count": 0, "status": "failed", "errors": [safe_error], "limitations": [],
    }
    manifest = IngestionManifest.from_mapping(manifest_payload)
    manifest_relative = Path("processed") / context.project_id / "manifests" / now.date().isoformat() / f"{ingestion_id}.json"
    write_ingestion_manifest(root / manifest_relative, manifest)
    return ConnectorResult(
        source=source, acquisition_method=acquisition_method, retrieved_at=now,
        records=(), status="failed", ingestion_manifest=manifest.as_dict(),
        metadata={"ingestion_manifest": manifest_relative.as_posix()}, errors=(safe_error,),
    )


def _approved_root(path: Path) -> Path:
    root = path.resolve()
    if ".git" in {part.lower() for part in root.parts}:
        raise ValueError("Data root cannot be inside Git metadata")
    repository = repository_root().resolve()
    try:
        root.relative_to(repository)
    except ValueError:
        pass
    else:
        approved = (repository / "research").resolve()
        if root != approved:
            raise ValueError("Repository-local data root must be the ignored research directory")
    root.mkdir(parents=True, exist_ok=True)
    return root


def _ingestion_id(context: ConnectorContext, request: AcquisitionRequest, method: str, at: datetime) -> str:
    identity = json.dumps(
        {"project": context.project_id, "authorization": context.authorization_id, "source": request.source,
         "record_type": request.record_type, "resource": request.resource_id, "method": method,
         "retrieved_at": at.isoformat()}, sort_keys=True, separators=(",", ":")
    )
    return f"ingestion-{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:20]}"


def _media_extension(media_type: str) -> str:
    return {"application/json": ".json", "text/csv": ".csv", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx"}.get(media_type, ".bin")


def _write_immutable_bytes(path: Path, content: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    checksum = hashlib.sha256(content).hexdigest()
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    except FileExistsError:
        if hashlib.sha256(path.read_bytes()).hexdigest() != checksum:
            raise FileExistsError(f"Immutable artifact already exists with different content: {path}")
        return checksum
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    return checksum


def _safe_manifest_filters(filters: Mapping[str, Any]) -> dict[str, Any]:
    excluded = {"path", "file", "fixture", "evidence_manifest", "visible_values"}
    return {key: value for key, value in filters.items() if key not in excluded and "secret" not in key.lower() and "token" not in key.lower() and "key" not in key.lower()}


def _safe_manifest_metadata(metadata: Mapping[str, Any]) -> dict[str, Any]:
    excluded_terms = ("secret", "token", "password", "authorization", "cookie", "credential")
    return {
        key: value
        for key, value in json.loads(json.dumps(metadata, default=str)).items()
        if not any(term in key.lower() for term in excluded_terms)
    }
