"""Snapshot metadata and storage interfaces."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import BinaryIO, Protocol


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


class SnapshotStore(Protocol):
    def put(self, descriptor: SnapshotDescriptor, content: BinaryIO) -> None: ...

    def open(self, snapshot_id: str) -> BinaryIO: ...

    def describe(self, snapshot_id: str) -> SnapshotDescriptor: ...
