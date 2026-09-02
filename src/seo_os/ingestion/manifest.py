"""Validated ingestion-manifest loading and atomic writing."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from seo_os.schemas import validate_instance


@dataclass(frozen=True, slots=True)
class IngestionManifest:
    payload: Mapping[str, Any]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "IngestionManifest":
        copied = json.loads(json.dumps(payload))
        validate_instance("ingestion-manifest", copied)
        return cls(payload=copied)

    def as_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.payload))


def load_ingestion_manifest(path: str | Path) -> IngestionManifest:
    manifest_path = Path(path)
    with manifest_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Ingestion manifest must be a JSON object")
    return IngestionManifest.from_mapping(payload)


def write_ingestion_manifest(path: str | Path, manifest: IngestionManifest) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(manifest.as_dict(), indent=2, sort_keys=True) + "\n"
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, destination)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise
