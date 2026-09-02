"""Provider-neutral data-quality result contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping, Protocol, Sequence


class QualityStatus(StrEnum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass(frozen=True, slots=True)
class QualityIssue:
    code: str
    status: QualityStatus
    message: str
    field: str | None = None
    record_reference: str | None = None


@dataclass(frozen=True, slots=True)
class QualityReport:
    source: str
    record_type: str
    issues: tuple[QualityIssue, ...]

    @property
    def status(self) -> QualityStatus:
        statuses = {issue.status for issue in self.issues}
        if QualityStatus.FAIL in statuses:
            return QualityStatus.FAIL
        if QualityStatus.WARN in statuses:
            return QualityStatus.WARN
        return QualityStatus.PASS

    @property
    def usable(self) -> bool:
        return self.status is not QualityStatus.FAIL


class DataQualityCheck(Protocol):
    code: str

    def evaluate(self, records: Sequence[Mapping[str, Any]]) -> QualityIssue | None: ...
