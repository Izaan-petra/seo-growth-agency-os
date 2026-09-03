from __future__ import annotations

import copy
import unittest

from seo_os.procedures.common import canonicalize_url, classify_cwv, normalize_query, stable_id
from seo_os.procedures import PROCEDURES, get_procedure
from seo_os.procedures.framework import ProcedureError, ProcedureSpec, prepare_inputs
from seo_os.procedures.ownership import assert_owner
from seo_os.security import REDACTED, redact_mapping

from tests.procedures.helpers import snapshot


class ProcedureFrameworkTests(unittest.TestCase):
    def test_exact_batch_3_procedure_registry(self) -> None:
        self.assertEqual({"authority-link-building", "competitor-serp-analysis", "geo-aeo", "keyword-intent-strategy", "seo-content-strategy", "seo-cro", "seo-measurement", "technical-seo"}, set(PROCEDURES))
        self.assertIs(PROCEDURES["technical-seo"], get_procedure("technical-seo"))
        with self.assertRaises(KeyError):
            get_procedure("ecommerce-seo")

    def test_common_normalization_and_ids_are_deterministic(self) -> None:
        self.assertEqual("best sprayer", normalize_query("  BEST—Sprayer!! "))
        self.assertEqual("https://example.test/a?a=1", canonicalize_url("HTTPS://EXAMPLE.TEST//a/?utm_source=x&a=1#part"))
        self.assertEqual(stable_id("TECH", "a"), stable_id("TECH", "a"))

    def test_cwv_threshold_boundaries(self) -> None:
        self.assertEqual("good", classify_cwv("largest_contentful_paint", 2500))
        self.assertEqual("needs-improvement", classify_cwv("interaction_to_next_paint", 500))
        self.assertEqual("poor", classify_cwv("cumulative_layout_shift", 0.251))

    def test_exact_approval_project_and_quality_fail_closed(self) -> None:
        spec = ProcedureSpec("test", "1.0.0", "technical-seo", "TECH", ("generic-tabular-evidence",))
        item = snapshot("generic-tabular-evidence", [{"values": {"url": "https://example.test"}, "source_row": 1}])
        with self.assertRaises(ProcedureError):
            prepare_inputs(spec, project_id="PROJECT-FIXTURE", brief_id="BRIEF-1", datasets=[item], approved_dataset_ids=[])
        with self.assertRaises(ProcedureError):
            prepare_inputs(spec, project_id="OTHER-PROJECT", brief_id="BRIEF-1", datasets=[item], approved_dataset_ids=[item["snapshot_id"]])
        blocked = snapshot("generic-tabular-evidence", [], quality="blocking", name="blocked")
        with self.assertRaises(ProcedureError):
            prepare_inputs(spec, project_id="PROJECT-FIXTURE", brief_id="BRIEF-1", datasets=[blocked], approved_dataset_ids=[blocked["snapshot_id"]])
        malformed = copy.deepcopy(item)
        malformed["records"].append({"tampered": True})
        with self.assertRaises(ValueError):
            prepare_inputs(spec, project_id="PROJECT-FIXTURE", brief_id="BRIEF-1", datasets=[malformed], approved_dataset_ids=[item["snapshot_id"]])

    def test_programmatic_ownership_rejects_wrong_owner(self) -> None:
        assert_owner("cannibalization", "keyword-intent-strategy")
        with self.assertRaises(ValueError):
            assert_owner("cannibalization", "seo-content-strategy")

    def test_credential_like_material_is_rejected(self) -> None:
        spec = ProcedureSpec("test", "1.0.0", "technical-seo", "TECH", ("generic-tabular-evidence",))
        sensitive_record = {"values": {"api_" + "key": "synthetic" + "value123456"}, "source_row": 1}
        item = snapshot("generic-tabular-evidence", [sensitive_record], name="sensitive")
        with self.assertRaises(ProcedureError):
            prepare_inputs(spec, project_id="PROJECT-FIXTURE", brief_id="BRIEF-1", datasets=[item], approved_dataset_ids=[item["snapshot_id"]])

    def test_output_redaction_preserves_ga4_session_metrics(self) -> None:
        result = redact_mapping({"sessions": 42, "sessionSource": "google", "session_" + "id": "sensitive-value"})
        self.assertEqual(42, result["sessions"])
        self.assertEqual("google", result["sessionSource"])
        self.assertEqual(REDACTED, result["session_id"])


if __name__ == "__main__":
    unittest.main()
