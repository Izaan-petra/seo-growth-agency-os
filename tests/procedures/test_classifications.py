from __future__ import annotations

import unittest

from seo_os.procedures.content import run_content_procedure
from seo_os.procedures.framework import ProcedureError, ProcedureSpec, prepare_inputs
from seo_os.procedures.keyword import classify_brand, classify_intent
from seo_os.procedures.measurement import run_measurement_procedure
from seo_os.procedures.technical import classify_url

from tests.procedures.helpers import snapshot


class ClassificationTests(unittest.TestCase):
    def test_technical_url_classification_combinations(self) -> None:
        classes = classify_url({"values": {"url": "https://example.test/a", "status_code": 200, "meta_robots": "noindex", "inlinks": 0, "duplicate": True}})
        self.assertEqual(("noindex", "duplicate-risk", "orphan-risk"), classes)
        self.assertEqual(("blocked",), classify_url({"values": {"url": "https://example.test/b", "status_code": 200, "robots_allowed": False}}))

    def test_keyword_brand_boundaries_and_multilabel_intent(self) -> None:
        self.assertEqual("ambiguous", classify_brand("brand product", []))
        self.assertEqual("non-branded", classify_brand("educational category", ["cat"]))
        self.assertEqual("branded", classify_brand("Acme login", ["Acme"]))
        self.assertEqual({"branded", "navigational"}, set(classify_intent("Acme login", branded=True)))

    def test_content_decay_requires_comparable_nonseasonal_evidence(self) -> None:
        item = snapshot("generic-tabular-evidence", [
            {"values": {"url": "https://example.test/seasonal", "status_code": 200, "indexable": True, "current_clicks": 10, "comparable_clicks": 100, "seasonal": True, "last_updated": "2026-01-01"}, "source_row": 1},
            {"values": {"url": "https://example.test/decline", "status_code": 200, "indexable": True, "current_clicks": 10, "comparable_clicks": 100, "seasonal": False, "last_updated": "2026-01-01"}, "source_row": 2},
        ])
        result = run_content_procedure(project_id="PROJECT-FIXTURE", brief_id="BRIEF-X", datasets=[item], approved_dataset_ids=[item["snapshot_id"]], config={"as_of_date": "2026-09-03"})
        actions = {row["url"]: row["action"] for row in result["artifacts"]["content_actions"]}
        self.assertEqual("retain", actions["https://example.test/seasonal"])
        self.assertEqual("refresh", actions["https://example.test/decline"])

    def test_measurement_zero_denominator_and_unequal_period(self) -> None:
        current = snapshot("gsc-search-performance", [{"date": "2026-08-01", "query": "zero", "page": "https://example.test", "clicks": 0, "impressions": 0}], period={"start_date": "2026-08-01", "end_date": "2026-08-31"}, name="current")
        previous = snapshot("gsc-search-performance", [{"date": "2026-07-01", "query": "zero", "page": "https://example.test", "clicks": 0, "impressions": 0}], period={"start_date": "2026-07-01", "end_date": "2026-07-15"}, name="previous")
        result = run_measurement_procedure(project_id="PROJECT-FIXTURE", brief_id="BRIEF-X", datasets=[current, previous], approved_dataset_ids=[current["snapshot_id"], previous["snapshot_id"]])
        ctr = next(item for item in result["artifacts"]["measurement_kpis"] if item["name"].endswith(": ctr"))
        self.assertEqual(0, ctr["baseline"]["value"])
        self.assertTrue(any(item.get("reason") == "Unequal period lengths" for item in result["artifacts"]["comparisons"]))

    def test_blocking_optional_dataset_is_disclosed_and_degraded(self) -> None:
        spec = ProcedureSpec("test", "1.0.0", "technical-seo", "TECH", ("generic-tabular-evidence",), optional_datasets=("psi-lab-performance",))
        usable = snapshot("generic-tabular-evidence", [{"values": {"url": "https://example.test"}, "source_row": 1}], name="usable")
        blocked = snapshot("psi-lab-performance", [], quality="blocking", name="blocked")
        prepared = prepare_inputs(spec, project_id="PROJECT-FIXTURE", brief_id="BRIEF-X", datasets=[usable, blocked], approved_dataset_ids=[usable["snapshot_id"], blocked["snapshot_id"]])
        self.assertTrue(prepared.degraded)
        self.assertEqual((blocked["snapshot_id"],), prepared.skipped)

    def test_unsupported_comparison_mode_fails_closed(self) -> None:
        first = snapshot("gsc-search-performance", [{"clicks": 1, "impressions": 10}], period={"start_date": "2026-07-01", "end_date": "2026-07-31"}, name="first")
        second = snapshot("gsc-search-performance", [{"clicks": 2, "impressions": 10}], period={"start_date": "2026-08-01", "end_date": "2026-08-31"}, name="second")
        with self.assertRaises(ProcedureError):
            run_measurement_procedure(project_id="PROJECT-FIXTURE", brief_id="BRIEF-X", datasets=[first, second], approved_dataset_ids=[first["snapshot_id"], second["snapshot_id"]], config={"comparison_mode": "magic"})


if __name__ == "__main__":
    unittest.main()
