from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from seo_os.connectors import AcquisitionRequest, FixtureTransport, HttpResponse, build_default_registry
from seo_os.secrets import MappingSecretResolver

from .helpers import authorization, context, fixture


class PerformanceConnectorTests(unittest.TestCase):
    def test_pagespeed_persists_lab_only_evidence(self) -> None:
        resource = "https://example.test/products/sprayer"
        fields = ("performance_score", "largest-contentful-paint", "cumulative-layout-shift")
        manifest = authorization(
            provider="pagespeed-insights", resource=resource, fields=fields,
            authentication_method="none", credential_reference=None,
        )
        connector = build_default_registry(transport=FixtureTransport([fixture("pagespeed.json")])).get("pagespeed-insights")
        with tempfile.TemporaryDirectory() as directory:
            result = connector.collect(
                context(Path(directory), manifest),
                AcquisitionRequest("pagespeed-insights", "psi-lab-performance", resource, fields, filters={"strategy": "mobile"}),
            )
        self.assertEqual("complete", result.status)
        self.assertEqual("2026-09-03T09:00:00+00:00", result.retrieved_at.isoformat())
        self.assertEqual("2026-09-03T08:00:00Z", result.metadata["provider_timestamp"])
        self.assertEqual("2026-09-03T08:00:00Z", result.metadata["fetch_timestamp"])
        self.assertEqual("lab", result.metadata["evidence_class"])
        self.assertEqual(0.81, result.records[0]["performance_score"])
        self.assertNotIn("loadingExperience", result.records[0])
        self.assertIn("not field Core Web Vitals", " ".join(result.limitations))

    def test_crux_preserves_p75_histograms_and_collection_period(self) -> None:
        resource = "https://example.test/products/sprayer"
        fields = ("largest_contentful_paint", "interaction_to_next_paint")
        manifest = authorization(provider="crux", resource=resource, fields=fields)
        connector = build_default_registry(
            transport=FixtureTransport([fixture("crux.json")]),
            secret_resolver=MappingSecretResolver({"FIXTURE_PROVIDER_ACCESS": "mock"}),
        ).get("crux")
        with tempfile.TemporaryDirectory() as directory:
            result = connector.collect(
                context(Path(directory), manifest),
                AcquisitionRequest("crux", "crux-field-performance", resource, fields, filters={"lookup": "url", "form_factor": "phone"}),
            )
        self.assertEqual("complete", result.status)
        self.assertEqual("field", result.metadata["evidence_class"])
        self.assertEqual(2400, result.records[0]["metrics"]["largest_contentful_paint"]["p75"])
        self.assertEqual(3, len(result.records[0]["metrics"]["largest_contentful_paint"]["histogram"]))

    def test_crux_missing_data_is_a_partial_dataset_not_a_raw_error(self) -> None:
        resource = "https://example.test/sparse"
        fields = ("largest_contentful_paint",)
        manifest = authorization(provider="crux", resource=resource, fields=fields)
        connector = build_default_registry(
            transport=FixtureTransport([HttpResponse(404, {"provider_detail": "not retained"}, {})]),
            secret_resolver=MappingSecretResolver({"FIXTURE_PROVIDER_ACCESS": "mock"}),
        ).get("crux")
        with tempfile.TemporaryDirectory() as directory:
            result = connector.collect(
                context(Path(directory), manifest),
                AcquisitionRequest("crux", "crux-field-performance", resource, fields),
            )
        self.assertEqual("partial", result.status)
        self.assertEqual((), result.records)
        self.assertTrue(any(issue["code"] == "missing-field-data" for issue in result.quality_report["issues"]))


if __name__ == "__main__":
    unittest.main()
