"""Snapshot metadata and storage interfaces."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO, Mapping, Protocol


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True, slots=True)
class SnapshotDescriptor:
    snapshot_id: str
    project_id: str
    source: str
    record_type: str
    captured_at: datetime
    schema_version: str
    row_count: int
    checksum_sha256: str
    relative_path: str
    ingestion_id: str | None = None
    manifest_reference: str | None = None
    provenance: Mapping[str, Any] | None = None


class SnapshotStore(Protocol):
    def put(self, descriptor: SnapshotDescriptor, content: BinaryIO) -> None: ...

    def open(self, snapshot_id: str) -> BinaryIO: ...

    def describe(self, snapshot_id: str) -> SnapshotDescriptor: ...


def deterministic_snapshot_id(payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return f"snapshot-{hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:20]}"


def write_immutable_json(path: str | Path, payload: Mapping[str, Any]) -> str:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    content = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    checksum = hashlib.sha256(content).hexdigest()
    try:
        descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    except FileExistsError:
        if hashlib.sha256(destination.read_bytes()).hexdigest() != checksum:
            raise FileExistsError(f"Immutable artifact already exists with different content: {destination}")
        return checksum
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    return checksum


def validate_snapshot_payload(payload: Mapping[str, Any]) -> None:
    required = {
        "schema_version", "snapshot_id", "ingestion_id", "project_id", "source",
        "dataset_type", "resource_id", "retrieved_at", "limitations", "provenance",
        "quality", "records",
    }
    missing = sorted(required - set(payload))
    if missing:
        raise ValueError(f"Snapshot is missing required fields: {', '.join(missing)}")
    identity_payload = {key: value for key, value in payload.items() if key != "snapshot_id"}
    expected = deterministic_snapshot_id(identity_payload)
    if payload["snapshot_id"] != expected:
        raise ValueError("Snapshot identifier does not match canonical content")
