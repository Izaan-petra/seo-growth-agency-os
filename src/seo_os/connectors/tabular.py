"""Authorized CSV/XLSX ingestion with row-level rejection and quarantine metadata."""

from __future__ import annotations

import csv
import io
import re
import zipfile
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence
from xml.etree import ElementTree as ET

from seo_os.authorization import AuthorizationGrant
from seo_os.ingestion.quality import QualityIssue, QualityStatus

from .base import AcquisitionRequest, ConnectorCapabilities, ConnectorContext, ConnectorError
from .managed import ManagedReadOnlyConnector, ProviderBatch


XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
PRIVACY_HEADER = re.compile(
    r"(?i)^(?:e-?mail|phone|mobile|first_?name|last_?name|full_?name|address|street|postal|zip|customer_?id|ip_?address|cookie|session_?id|notes?)$"
)
CREDENTIAL_HEADER = re.compile(
    r"(?i)^(?:password|passwd|api_?key|access_?token|refresh_?token|client_?secret|authorization|cookie|session_?token)$"
)


@dataclass(frozen=True, slots=True)
class ParsedTabular:
    records: tuple[Mapping[str, Any], ...]
    rejected: tuple[Mapping[str, Any], ...]
    raw_content: bytes
    media_type: str
    headers: tuple[str, ...]
    sheet: str | None
    encoding: str | None
    total_rows: int
    truncated: bool


class TabularConnector(ManagedReadOnlyConnector):
    default_acquisition_method = "export"

    @property
    def capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            provider="tabular", acquisition_methods=("export",),
            authentication_methods=("user-export",),
            supported_record_types=("generic-tabular-evidence",),
        )

    def authorization_fields(self, request: AcquisitionRequest) -> tuple[str, ...]:
        mapping = request.filters.get("field_mapping", {})
        return tuple(str(value) for value in mapping.values()) if isinstance(mapping, Mapping) else ()

    def collect_authorized(
        self, context: ConnectorContext, request: AcquisitionRequest, grant: AuthorizationGrant
    ) -> ProviderBatch:
        parsed = parse_authorized_tabular(context, request)
        issues = ()
        if parsed.rejected:
            issues = (
                QualityIssue(
                    "rejected-rows", QualityStatus.WARNING,
                    f"{len(parsed.rejected)} malformed, duplicate, or privacy-sensitive rows were quarantined",
                ),
            )
        records = tuple(
            {"values": dict(record["values"]), "source_row": record["source_row"], "resource_id": request.resource_id}
            for record in parsed.records
        )
        limitations = []
        if parsed.rejected:
            limitations.append("Rejected rows are reported by row number and reason and were not silently discarded.")
        if parsed.truncated:
            limitations.append("The configured row limit truncated this export.")
        return ProviderBatch(
            dataset_type="generic-tabular-evidence", records=records,
            raw_payload=parsed.raw_content, raw_media_type=parsed.media_type,
            dimensions=tuple(parsed.headers), limitations=tuple(limitations),
            metadata={"source_name": request.filters.get("source_name", "user-provided export"), "sheet": parsed.sheet, "encoding": parsed.encoding, "headers": list(parsed.headers), "total_source_rows": parsed.total_rows, "valid_rows": len(records), "rejected_rows": len(parsed.rejected), "truncated": parsed.truncated},
            rejected_records=parsed.rejected, extra_quality_issues=issues,
            truncated=parsed.truncated,
        )


def parse_authorized_tabular(context: ConnectorContext, request: AcquisitionRequest) -> ParsedTabular:
    relative_path = request.filters.get("path")
    if not isinstance(relative_path, str) or not relative_path:
        raise ConnectorError("missing_export", "Tabular ingestion requires a relative path under the raw data root")
    raw_root = (context.data_root / "raw").resolve()
    candidate = (raw_root / relative_path).resolve()
    try:
        candidate.relative_to(raw_root)
    except ValueError:
        raise ConnectorError("unsafe_path", "Export path must remain under the raw data root") from None
    if not candidate.is_file():
        raise ConnectorError("missing_export", "Authorized export file does not exist")
    maximum_size = _positive_int(request.filters.get("max_file_bytes", 50 * 1024 * 1024), "max_file_bytes")
    if candidate.stat().st_size > maximum_size:
        raise ConnectorError("export_too_large", "Export exceeds the approved file-size limit")
    suffix = candidate.suffix.lower()
    if suffix not in {".csv", ".xlsx"}:
        raise ConnectorError("unsupported_export", "Only CSV and XLSX exports are supported")
    raw = candidate.read_bytes()
    if suffix == ".csv":
        encoding = _detect_encoding(raw)
        table = list(csv.reader(io.StringIO(raw.decode(encoding, errors="strict"))))
        sheet = None
        media_type = "text/csv"
    else:
        sheet_name = request.filters.get("sheet")
        if sheet_name is not None and not isinstance(sheet_name, str):
            raise ConnectorError("invalid_sheet", "XLSX sheet must be a string")
        table, sheet = _read_xlsx(raw, sheet_name)
        encoding = None
        media_type = XLSX_MEDIA_TYPE
    return _normalize_table(raw, media_type, encoding, sheet, table, request)


def _normalize_table(
    raw: bytes,
    media_type: str,
    encoding: str | None,
    sheet: str | None,
    table: Sequence[Sequence[Any]],
    request: AcquisitionRequest,
) -> ParsedTabular:
    if not table:
        raise ConnectorError("malformed_export", "Export contains no rows")
    headers = tuple(str(value).strip() for value in table[0])
    if not headers or any(not header for header in headers) or len(headers) != len(set(headers)):
        raise ConnectorError("invalid_headers", "Headers must be non-empty and unique")
    mapping = request.filters.get("field_mapping", {})
    if not isinstance(mapping, Mapping) or any(key not in headers for key in mapping):
        raise ConnectorError("invalid_mapping", "Field mapping must reference existing source headers")
    mapped_headers = tuple(str(mapping.get(header, header)).strip() for header in headers)
    if any(not header for header in mapped_headers) or len(mapped_headers) != len(set(mapped_headers)):
        raise ConnectorError("invalid_mapping", "Mapped field names must be non-empty and unique")
    required = request.filters.get("required_fields", request.fields)
    if not isinstance(required, (list, tuple)) or not set(map(str, required)).issubset(set(mapped_headers)):
        raise ConnectorError("missing_required_field", "Required export fields are missing after mapping")
    selected_fields = tuple(request.fields)
    type_mapping = request.filters.get("type_mapping", {})
    if not isinstance(type_mapping, Mapping):
        raise ConnectorError("invalid_mapping", "type_mapping must be an object")
    unknown_types = set(type_mapping.values()) - {"string", "integer", "number", "boolean", "date"}
    if unknown_types or not set(type_mapping).issubset(set(selected_fields)):
        raise ConnectorError("invalid_mapping", "Type mapping contains unsupported types or fields")
    date_format = request.filters.get("date_format")
    duplicate_keys = request.filters.get("duplicate_keys", list(selected_fields))
    if not isinstance(duplicate_keys, (list, tuple)) or not set(map(str, duplicate_keys)).issubset(set(mapped_headers)):
        raise ConnectorError("invalid_mapping", "Duplicate keys must reference mapped fields")
    row_limit = _positive_int(request.filters.get("row_limit", 100000), "row_limit")
    sensitive_fields = {mapped_headers[index] for index, header in enumerate(headers) if PRIVACY_HEADER.fullmatch(header) or PRIVACY_HEADER.fullmatch(mapped_headers[index])}
    credential_fields = {mapped_headers[index] for index, header in enumerate(headers) if CREDENTIAL_HEADER.fullmatch(header) or CREDENTIAL_HEADER.fullmatch(mapped_headers[index])}

    valid: list[Mapping[str, Any]] = []
    rejected: list[Mapping[str, Any]] = []
    seen: set[tuple[str, ...]] = set()
    source_rows = [row for row in table[1:] if any(value not in (None, "") for value in row)]
    truncated = len(source_rows) > row_limit
    for row_number, row in enumerate(source_rows[:row_limit], start=2):
        reasons: list[str] = []
        if len(row) != len(headers):
            reasons.append("column-count-mismatch")
        padded = list(row[: len(headers)]) + [None] * max(0, len(headers) - len(row))
        source_values = dict(zip(mapped_headers, padded))
        if any(source_values.get(field) not in (None, "") for field in credential_fields):
            raise ConnectorError("privacy_quarantine", "Export contains a credential-like field and was not ingested")
        if any(source_values.get(field) not in (None, "") for field in sensitive_fields):
            reasons.append("privacy-sensitive-field")
        normalized: dict[str, Any] = {}
        for field_name in selected_fields:
            value = source_values.get(field_name)
            try:
                normalized[field_name] = _normalize_value(value, str(type_mapping.get(field_name, "string")), date_format)
            except ValueError:
                reasons.append(f"invalid-type:{field_name}")
        for field_name in map(str, required):
            if normalized.get(field_name) in (None, ""):
                reasons.append(f"missing-required:{field_name}")
        key = tuple(str(normalized.get(str(field), "")) for field in duplicate_keys)
        if key in seen:
            reasons.append("duplicate-row")
        if reasons:
            rejected.append({"source_row": row_number, "reasons": sorted(set(reasons)), "fields": sorted({reason.split(":", 1)[1] for reason in reasons if ":" in reason})})
            continue
        seen.add(key)
        valid.append({"source_row": row_number, "values": normalized})
    return ParsedTabular(tuple(valid), tuple(rejected), raw, media_type, mapped_headers, sheet, encoding, len(source_rows), truncated)


def _detect_encoding(raw: bytes) -> str:
    if raw.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return "utf-16"
    for encoding in ("utf-8", "cp1252"):
        try:
            raw.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            continue
    raise ConnectorError("invalid_encoding", "CSV encoding could not be detected")


def _normalize_value(value: Any, target_type: str, date_format: Any) -> Any:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date().isoformat() if target_type == "date" else value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = str(value).strip()
    if target_type == "string":
        return text
    if target_type == "integer":
        if re.fullmatch(r"[-+]?[0-9]+", text) is None:
            raise ValueError
        return int(text)
    if target_type == "number":
        return float(text.replace(",", ""))
    if target_type == "boolean":
        normalized = text.lower()
        if normalized in {"true", "yes", "1"}:
            return True
        if normalized in {"false", "no", "0"}:
            return False
        raise ValueError
    if target_type == "date":
        if date_format:
            return datetime.strptime(text, str(date_format)).date().isoformat()
        return date.fromisoformat(text).isoformat()
    raise ValueError


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool):
        raise ConnectorError("invalid_limit", f"{name} must be a positive integer")
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ConnectorError("invalid_limit", f"{name} must be a positive integer") from None
    if parsed < 1:
        raise ConnectorError("invalid_limit", f"{name} must be a positive integer")
    return parsed


def _read_xlsx(raw: bytes, requested_sheet: str | None) -> tuple[list[list[Any]], str]:
    try:
        archive = zipfile.ZipFile(io.BytesIO(raw))
    except zipfile.BadZipFile:
        raise ConnectorError("malformed_export", "XLSX file is not a valid ZIP package") from None
    with archive:
        total_uncompressed = sum(item.file_size for item in archive.infolist())
        if total_uncompressed > 200 * 1024 * 1024:
            raise ConnectorError("export_too_large", "XLSX expanded content exceeds the safety limit")
        try:
            workbook = ET.fromstring(archive.read("xl/workbook.xml"))
            relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        except (KeyError, ET.ParseError):
            raise ConnectorError("malformed_export", "XLSX workbook metadata is invalid") from None
        ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main", "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
        rel_ns = {"p": "http://schemas.openxmlformats.org/package/2006/relationships"}
        targets = {item.attrib["Id"]: item.attrib["Target"] for item in relationships.findall("p:Relationship", rel_ns)}
        sheets = []
        for item in workbook.findall("m:sheets/m:sheet", ns):
            relation_id = item.attrib.get(f"{{{ns['r']}}}id")
            if relation_id in targets:
                target = PurePosixPath(targets[relation_id])
                sheet_path = str(target if str(target).startswith("xl/") else PurePosixPath("xl") / target)
                sheets.append((item.attrib.get("name", ""), sheet_path))
        if not sheets:
            raise ConnectorError("malformed_export", "XLSX contains no readable worksheets")
        selected = next((item for item in sheets if item[0] == requested_sheet), None) if requested_sheet else sheets[0]
        if selected is None:
            raise ConnectorError("invalid_sheet", "Requested XLSX sheet does not exist")
        shared_strings = _xlsx_shared_strings(archive)
        date_styles = _xlsx_date_styles(archive)
        date_1904 = workbook.find("m:workbookPr", ns) is not None and workbook.find("m:workbookPr", ns).attrib.get("date1904") in {"1", "true"}
        try:
            worksheet = ET.fromstring(archive.read(selected[1]))
        except (KeyError, ET.ParseError):
            raise ConnectorError("malformed_export", "Selected XLSX worksheet is invalid") from None
        rows: list[list[Any]] = []
        for row in worksheet.findall("m:sheetData/m:row", ns):
            values: dict[int, Any] = {}
            for cell in row.findall("m:c", ns):
                reference = cell.attrib.get("r", "A1")
                column = _column_index(reference)
                values[column] = _xlsx_cell_value(cell, ns, shared_strings, date_styles, date_1904)
            if values:
                rows.append([values.get(index) for index in range(max(values) + 1)])
        return rows, selected[0]


def _xlsx_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    try:
        root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    except ET.ParseError:
        raise ConnectorError("malformed_export", "XLSX shared strings are invalid") from None
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    return ["".join(node.text or "" for node in item.findall(".//m:t", ns)) for item in root.findall("m:si", ns)]


def _xlsx_date_styles(archive: zipfile.ZipFile) -> set[int]:
    try:
        root = ET.fromstring(archive.read("xl/styles.xml"))
    except KeyError:
        return set()
    except ET.ParseError:
        raise ConnectorError("malformed_export", "XLSX styles are invalid") from None
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    custom = {int(item.attrib["numFmtId"]): item.attrib.get("formatCode", "") for item in root.findall("m:numFmts/m:numFmt", ns)}
    builtin_dates = set(range(14, 23)) | set(range(45, 48))
    result: set[int] = set()
    for index, style in enumerate(root.findall("m:cellXfs/m:xf", ns)):
        number_format = int(style.attrib.get("numFmtId", "0"))
        if number_format in builtin_dates or re.search(r"[ymdhis]", custom.get(number_format, ""), re.IGNORECASE):
            result.add(index)
    return result


def _xlsx_cell_value(cell: ET.Element, ns: Mapping[str, str], shared: Sequence[str], date_styles: set[int], date_1904: bool) -> Any:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        return "".join(node.text or "" for node in cell.findall(".//m:t", ns))
    value_node = cell.find("m:v", ns)
    if value_node is None or value_node.text is None:
        return None
    value = value_node.text
    if cell_type == "s":
        try:
            return shared[int(value)]
        except (ValueError, IndexError):
            raise ConnectorError("malformed_export", "XLSX shared-string reference is invalid") from None
    if cell_type == "b":
        return value == "1"
    if cell_type in {"str", "e"}:
        return value
    try:
        number = float(value)
    except ValueError:
        return value
    style = int(cell.attrib.get("s", "0"))
    if style in date_styles:
        epoch = datetime(1904, 1, 1, tzinfo=UTC) if date_1904 else datetime(1899, 12, 30, tzinfo=UTC)
        return epoch + timedelta(days=number)
    return int(number) if number.is_integer() else number


def _column_index(reference: str) -> int:
    match = re.match(r"([A-Z]+)", reference.upper())
    if not match:
        raise ConnectorError("malformed_export", "XLSX cell reference is invalid")
    result = 0
    for character in match.group(1):
        result = result * 26 + ord(character) - ord("A") + 1
    return result - 1
