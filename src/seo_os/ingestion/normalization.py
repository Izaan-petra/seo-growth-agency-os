"""Interfaces for source-to-canonical normalization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Protocol


class NormalizationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class NormalizedRecord:
    record_type: str
    source_record_id: str
    values: Mapping[str, Any]
    evidence_reference: str


class Normalizer(Protocol):
    record_type: str

    def normalize(
        self, records: Iterable[Mapping[str, Any]]
    ) -> Iterable[NormalizedRecord]: ...
