"""Provider-neutral data-quality result contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping, Protocol, Sequence


class QualityStatus(StrEnum):
    PASS = "pass"
    INFO = "info"
    WARN = "warning"
    WARNING = "warning"
    FAIL = "blocking"
    BLOCKING = "blocking"


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
        if QualityStatus.BLOCKING in statuses:
            return QualityStatus.FAIL
        if QualityStatus.WARNING in statuses:
            return QualityStatus.WARN
        return QualityStatus.PASS

    @property
    def usable(self) -> bool:
        return self.status is not QualityStatus.FAIL


class DataQualityCheck(Protocol):
    code: str

    def evaluate(self, records: Sequence[Mapping[str, Any]]) -> QualityIssue | None: ...


def validate_records(
    *,
    source: str,
    record_type: str,
    records: Sequence[Mapping[str, Any]],
    required_fields: Sequence[str] = (),
    duplicate_key_fields: Sequence[str] = (),
    resource_id: str | None = None,
    expected_currency: str | None = None,
    truncated: bool = False,
    partial_api_result: bool = False,
    screenshot_evidence: bool = False,
    missing_field_data: bool = False,
    extra_issues: Sequence[QualityIssue] = (),
) -> QualityReport:
    """Run deterministic cross-provider quality checks."""

    issues = list(extra_issues)
    seen: set[tuple[str, ...]] = set()
    for index, record in enumerate(records, start=1):
        reference = str(record.get("source_row") or index)
        for field_name in required_fields:
            if field_name not in record or record[field_name] in (None, ""):
                issues.append(
                    QualityIssue(
                        "missing-required-field",
                        QualityStatus.BLOCKING,
                        f"Required field is missing: {field_name}",
                        field_name,
                        reference,
                    )
                )
        if resource_id and record.get("resource_id") not in (None, resource_id):
            issues.append(
                QualityIssue(
                    "resource-mismatch",
                    QualityStatus.BLOCKING,
                    "Record resource does not match the authorized resource",
                    "resource_id",
                    reference,
                )
            )
        if expected_currency and record.get("currency") not in (None, "", expected_currency):
            issues.append(
                QualityIssue(
                    "unexpected-currency",
                    QualityStatus.BLOCKING,
                    "Revenue currency differs from the authorized currency",
                    "currency",
                    reference,
                )
            )
        _check_impossible_metrics(record, reference, issues)
        if duplicate_key_fields:
            key = tuple(str(record.get(field, "")) for field in duplicate_key_fields)
            if any(key) and key in seen:
                issues.append(
                    QualityIssue(
                        "duplicate-row",
                        QualityStatus.WARNING,
                        "Duplicate canonical key detected",
                        record_reference=reference,
                    )
                )
            seen.add(key)

    if truncated:
        issues.append(QualityIssue("truncated-export", QualityStatus.WARNING, "Source export was truncated"))
    if partial_api_result:
        issues.append(QualityIssue("partial-api-result", QualityStatus.WARNING, "Provider returned a partial or capped result"))
    if screenshot_evidence:
        issues.append(QualityIssue("screenshot-limitation", QualityStatus.WARNING, "Only values visibly recorded in screenshot evidence are usable"))
    if missing_field_data:
        issues.append(QualityIssue("missing-field-data", QualityStatus.WARNING, "Requested field data is unavailable for this resource"))
    if not records:
        issues.append(QualityIssue("empty-dataset", QualityStatus.WARNING, "No usable records were returned"))
    return QualityReport(source, record_type, tuple(_deduplicate_issues(issues)))


def quality_report_as_dict(report: QualityReport) -> dict[str, Any]:
    return {
        "source": report.source,
        "record_type": report.record_type,
        "status": report.status.value,
        "usable": report.usable,
        "issues": [
            {
                "code": issue.code,
                "severity": issue.status.value,
                "message": issue.message,
                "field": issue.field,
                "record_reference": issue.record_reference,
            }
            for issue in report.issues
        ],
    }


def _check_impossible_metrics(
    record: Mapping[str, Any], reference: str, issues: list[QualityIssue]
) -> None:
    nonnegative = {
        "clicks", "impressions", "average_position", "sessions", "totalUsers",
        "activeUsers", "engagedSessions", "keyEvents", "conversions", "totalRevenue",
        "purchaseRevenue", "position", "best_position", "volume", "traffic",
        "links_to_target", "performance_score", "numeric_value", "p75",
    }
    proportions = {"ctr", "engagementRate", "performance_score", "density", "score"}
    for field_name, value in _walk_values(record):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if field_name in nonnegative and value < 0:
            issues.append(QualityIssue("impossible-metric", QualityStatus.BLOCKING, "Metric cannot be negative", field_name, reference))
        if field_name in proportions and not 0 <= value <= 1:
            issues.append(QualityIssue("impossible-rate", QualityStatus.BLOCKING, "Rate must be between 0 and 1", field_name, reference))


def _walk_values(value: Any) -> list[tuple[str, Any]]:
    result: list[tuple[str, Any]] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            result.append((str(key), item))
            result.extend(_walk_values(item))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for item in value:
            result.extend(_walk_values(item))
    return result


def _deduplicate_issues(issues: Sequence[QualityIssue]) -> list[QualityIssue]:
    unique: list[QualityIssue] = []
    seen: set[tuple[Any, ...]] = set()
    for issue in issues:
        key = (issue.code, issue.status, issue.field, issue.record_reference, issue.message)
        if key not in seen:
            seen.add(key)
            unique.append(issue)
    return unique
