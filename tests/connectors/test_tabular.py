from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from seo_os.connectors import AcquisitionRequest, build_default_registry

from .helpers import authorization, context


class TabularIngestionTests(unittest.TestCase):
    def test_csv_normalizes_types_and_quarantines_bad_or_private_rows(self) -> None:
        resource = "synthetic-export"
        fields = ("date", "clicks")
        manifest = authorization(
            provider="tabular", resource=resource, fields=fields, methods=("export",),
            authentication_method="user-export", credential_reference=None,
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "raw" / "uploads" / "search.csv"
            source.parent.mkdir(parents=True)
            source.write_text(
                "Report Date,Clicks,email\n"
                "2026-08-01,12,\n"
                "not-a-date,8,\n"
                "2026-08-02,4,person@example.test\n",
                encoding="utf-8",
            )
            result = build_default_registry().get("tabular").collect(
                context(root, manifest),
                AcquisitionRequest(
                    "tabular", "generic-tabular-evidence", resource, fields,
                    filters={"path": "uploads/search.csv", "field_mapping": {"Report Date": "date", "Clicks": "clicks"}, "required_fields": list(fields), "type_mapping": {"date": "date", "clicks": "integer"}},
                ),
            )
            snapshot_path = root / result.snapshot["relative_path"]
            self.assertTrue(snapshot_path.is_file())
        self.assertEqual("partial", result.status)
        self.assertEqual(1, len(result.records))
        self.assertEqual(12, result.records[0]["values"]["clicks"])
        self.assertEqual(2, len(result.rejected_records))
        self.assertTrue(any("privacy-sensitive-field" in row["reasons"] for row in result.rejected_records))
        self.assertNotIn("person@example.test", str(result.rejected_records))

    def test_xlsx_sheet_selection_and_numeric_normalization(self) -> None:
        resource = "synthetic-workbook"
        fields = ("keyword", "position")
        manifest = authorization(
            provider="tabular", resource=resource, fields=fields, methods=("export",),
            authentication_method="user-export", credential_reference=None,
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "raw" / "uploads" / "rankings.xlsx"
            source.parent.mkdir(parents=True)
            _write_minimal_xlsx(source)
            result = build_default_registry().get("tabular").collect(
                context(root, manifest),
                AcquisitionRequest(
                    "tabular", "generic-tabular-evidence", resource, fields,
                    filters={"path": "uploads/rankings.xlsx", "sheet": "Rankings", "required_fields": list(fields), "type_mapping": {"position": "integer"}},
                ),
            )
        self.assertEqual("complete", result.status)
        self.assertEqual("Rankings", result.metadata["sheet"])
        self.assertEqual(3, result.records[0]["values"]["position"])

    def test_export_path_cannot_escape_raw_root(self) -> None:
        resource = "synthetic-export"
        fields = ("keyword",)
        manifest = authorization(
            provider="tabular", resource=resource, fields=fields, methods=("export",),
            authentication_method="user-export", credential_reference=None,
        )
        with tempfile.TemporaryDirectory() as directory:
            result = build_default_registry().get("tabular").collect(
                context(Path(directory), manifest),
                AcquisitionRequest("tabular", "generic-tabular-evidence", resource, fields, filters={"path": "../../outside.csv"}),
            )
        self.assertEqual("failed", result.status)
        self.assertEqual("unsafe_path", result.errors[0]["category"])


def _write_minimal_xlsx(path: Path) -> None:
    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>"""
    root_rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""
    workbook = """<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets><sheet name="Rankings" sheetId="1" r:id="rId1"/></sheets>
</workbook>"""
    workbook_rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>"""
    worksheet = """<?xml version="1.0" encoding="UTF-8"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>
  <row r="1"><c r="A1" t="inlineStr"><is><t>keyword</t></is></c><c r="B1" t="inlineStr"><is><t>position</t></is></c></row>
  <row r="2"><c r="A2" t="inlineStr"><is><t>garden sprayer</t></is></c><c r="B2"><v>3</v></c></row>
</sheetData></worksheet>"""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", root_rels)
        archive.writestr("xl/workbook.xml", workbook)
        archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        archive.writestr("xl/worksheets/sheet1.xml", worksheet)


if __name__ == "__main__":
    unittest.main()
