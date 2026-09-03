from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from seo_os.connectors import AcquisitionRequest, FixtureTransport, build_default_registry
from seo_os.ingestion import QualityStatus, deterministic_snapshot_id, validate_records, validate_snapshot_payload

from tests.connectors.helpers import authorization, context, fixture


class QualityAndSnapshotTests(unittest.TestCase):
    def test_impossible_metrics_resource_and_currency_are_blocking(self) -> None:
        report = validate_records(
            source="ga4", record_type="ga4-organic-landing-performance",
            records=({"sessions": -1, "engagementRate": 1.2, "resource_id": "other", "currency": "EUR"},),
            resource_id="123", expected_currency="USD",
        )
        self.assertEqual(QualityStatus.FAIL, report.status)
        self.assertFalse(report.usable)
        self.assertEqual(
            {"impossible-metric", "impossible-rate", "resource-mismatch", "unexpected-currency"},
            {issue.code for issue in report.issues},
        )

    def test_duplicate_partial_and_missing_data_are_classified(self) -> None:
        report = validate_records(
            source="fixture", record_type="fixture",
            records=({"key": "same"}, {"key": "same"}), duplicate_key_fields=("key",),
            truncated=True, partial_api_result=True, screenshot_evidence=True, missing_field_data=True,
        )
        self.assertEqual(QualityStatus.WARN, report.status)
        self.assertEqual(
            {"duplicate-row", "truncated-export", "partial-api-result", "screenshot-limitation", "missing-field-data"},
            {issue.code for issue in report.issues},
        )

    def test_snapshot_identifier_is_deterministic_and_validated(self) -> None:
        base = {"schema_version": "1.0.0", "ingestion_id": "ingestion-demo", "project_id": "PROJECT-FIXTURE", "source": "fixture", "dataset_type": "generic-tabular-evidence", "resource_id": "resource", "retrieved_at": "2026-09-03T00:00:00Z", "period": None, "dimensions": [], "metrics": [], "limitations": [], "provenance": {}, "quality": {"status": "pass"}, "records": []}
        snapshot = {"snapshot_id": deterministic_snapshot_id(base), **base}
        validate_snapshot_payload(snapshot)
        changed = copy.deepcopy(snapshot)
        changed["records"] = [{"value": 1}]
        with self.assertRaises(ValueError):
            validate_snapshot_payload(changed)

    def test_connector_snapshot_file_validates(self) -> None:
        resource = "https://example.test/products/sprayer"
        fields = ("performance_score", "largest-contentful-paint")
        manifest = authorization(provider="pagespeed-insights", resource=resource, fields=fields, authentication_method="none", credential_reference=None)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = build_default_registry(transport=FixtureTransport([fixture("pagespeed.json")])).get("pagespeed-insights").collect(
                context(root, manifest), AcquisitionRequest("pagespeed-insights", "psi-lab-performance", resource, fields)
            )
            import json
            payload = json.loads((root / result.snapshot["relative_path"]).read_text(encoding="utf-8"))
            validate_snapshot_payload(payload)


if __name__ == "__main__":
    unittest.main()
