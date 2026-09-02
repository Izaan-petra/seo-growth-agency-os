from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / ".agents" / "skills" / "seo-director" / "routing-matrix.md"
EXPECTED_ENGAGEMENTS = {
    "Full SEO Audit",
    "Technical Audit",
    "SEO Growth Strategy",
    "Keyword Research",
    "Content Strategy",
    "Competitor Analysis",
    "Link-Building Campaign",
    "GEO/AEO Audit",
    "Ecommerce SEO Audit",
    "SEO CRO Review",
    "SEO Performance Review",
    "Migration Review",
    "Recovery Investigation",
}
RESERVED = {"ecommerce-seo", "seo-implementation-qa"}


def table_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    in_matrix = False
    for line in text.splitlines():
        if line.startswith("| Engagement type |"):
            in_matrix = True
            continue
        if in_matrix and re.match(r"^\|[-|]+\|$", line.replace(" ", "")):
            continue
        if in_matrix and line.startswith("|"):
            rows.append([cell.strip() for cell in line.strip("|").split("|")])
        elif in_matrix and rows:
            break
    return rows


def skills_in(cell: str) -> set[str]:
    return {
        value.strip().removesuffix(" (reserved)")
        for value in cell.split(",")
        if value.strip() and value.strip() != "none"
    }


class RoutingMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = MATRIX.read_text(encoding="utf-8")
        cls.rows = table_rows(cls.text)
        cls.active = {
            path.parent.name
            for path in (ROOT / ".agents" / "skills").glob("*/SKILL.md")
        }

    def test_all_engagement_types_are_present_once(self) -> None:
        names = [row[0] for row in self.rows]
        self.assertEqual(EXPECTED_ENGAGEMENTS, set(names))
        self.assertEqual(len(names), len(set(names)))

    def test_referenced_skills_are_active_or_reserved(self) -> None:
        for row in self.rows:
            with self.subTest(engagement=row[0]):
                referenced = skills_in(row[1]) | skills_in(row[2])
                self.assertFalse(referenced - self.active - RESERVED)

    def test_reserved_skills_are_not_claimed_as_active(self) -> None:
        self.assertTrue(RESERVED.isdisjoint(self.active))
        for reserved in RESERVED:
            self.assertIn(f"`{reserved}`", self.text)
            self.assertIn(f"{reserved} (reserved)", self.text)

    def test_control_columns_are_populated(self) -> None:
        for row in self.rows:
            with self.subTest(engagement=row[0]):
                self.assertEqual(9, len(row))
                self.assertTrue(all(cell for cell in row))
                self.assertIn(row[7], {"Yes", "No"})


if __name__ == "__main__":
    unittest.main()
