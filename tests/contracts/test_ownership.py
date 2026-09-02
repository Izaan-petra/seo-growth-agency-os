from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / ".agents" / "skills" / "seo-director" / "ownership-matrix.md"
REQUIRED_FIELDS = {
    "Internal-link graph and crawl depth",
    "Cannibalization determination",
    "General structured-data validity",
    "Ecommerce product structured data",
    "Author, reviewer and trust signals",
    "External corroboration",
    "Performance and Core Web Vitals",
    "Mobile interaction and conversion UX",
    "CTA, proof and form recommendations",
    "Connector, property and date metadata",
    "KPI definitions and GSC/GA4 normalization",
    "Keyword-to-page mapping",
    "Recommendation implementation validation",
}


def table_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    started = False
    for line in text.splitlines():
        if line.startswith("| Field |"):
            started = True
            continue
        if started and re.match(r"^\|[-|]+\|$", line.replace(" ", "")):
            continue
        if started and line.startswith("|"):
            rows.append([cell.strip() for cell in line.strip("|").split("|")])
        elif started and rows:
            break
    return rows


class OwnershipMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = table_rows(MATRIX.read_text(encoding="utf-8"))

    def test_required_overlap_fields_have_an_owner(self) -> None:
        fields = {row[0] for row in self.rows}
        self.assertTrue(REQUIRED_FIELDS.issubset(fields))

    def test_each_field_has_one_primary_owner(self) -> None:
        fields = [row[0] for row in self.rows]
        self.assertEqual(len(fields), len(set(fields)))
        for row in self.rows:
            with self.subTest(field=row[0]):
                self.assertEqual(5, len(row))
                self.assertTrue(row[1])
                self.assertNotIn(",", row[1])

    def test_director_is_final_decision_owner(self) -> None:
        for row in self.rows:
            with self.subTest(field=row[0]):
                self.assertEqual("seo-director", row[3])


if __name__ == "__main__":
    unittest.main()
