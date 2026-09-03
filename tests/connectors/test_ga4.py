from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from seo_os.connectors import AcquisitionRequest, FixtureTransport, build_default_registry
from seo_os.secrets import MappingSecretResolver

from .helpers import authorization, context, fixture


class GoogleAnalytics4Tests(unittest.TestCase):
    def test_pagination_continues_when_provider_omits_row_count(self) -> None:
        resource = "123456"
        fields = ("sessionDefaultChannelGroup", "sessions")
        manifest = authorization(provider="ga4", resource=resource, fields=fields)
        first_page = fixture("ga4-report.json")
        first_page.pop("rowCount", None)
        first_page["dimensionHeaders"] = [{"name": "sessionDefaultChannelGroup"}]
        first_page["metricHeaders"] = [{"name": "sessions", "type": "TYPE_INTEGER"}]
        first_page["rows"] = [{"dimensionValues": [{"value": "Organic Search"}], "metricValues": [{"value": "20"}]}]
        second_page = {
            "dimensionHeaders": [{"name": "sessionDefaultChannelGroup"}],
            "metricHeaders": [{"name": "sessions", "type": "TYPE_INTEGER"}],
            "rows": [],
        }
        transport = FixtureTransport([
            fixture("ga4-metadata.json"), fixture("ga4-compatibility.json"), first_page, second_page,
        ])
        connector = build_default_registry(
            transport=transport,
            secret_resolver=MappingSecretResolver({"FIXTURE_PROVIDER_ACCESS": "mock"}),
        ).get("ga4")
        with tempfile.TemporaryDirectory() as directory:
            result = connector.collect(
                context(Path(directory), manifest),
                AcquisitionRequest(
                    "ga4", "ga4-organic-landing-performance", resource, fields,
                    "2026-08-01", "2026-08-31", {"row_limit": 1},
                ),
            )
        self.assertEqual("complete", result.status)
        self.assertEqual(1, len(result.records))
        self.assertEqual(["0", "1"], [item["json_body"]["offset"] for item in transport.requests[2:]])

    def test_metadata_validates_fields_and_report_is_normalized(self) -> None:
        resource = "123456"
        fields = (
            "landingPagePlusQueryString", "sessionSource", "sessionMedium",
            "sessionDefaultChannelGroup", "country", "deviceCategory",
            "sessions", "totalUsers", "engagementRate", "keyEvents",
        )
        manifest = authorization(provider="ga4", resource=resource, fields=fields)
        transport = FixtureTransport([fixture("ga4-metadata.json"), fixture("ga4-compatibility.json"), fixture("ga4-report.json")])
        connector = build_default_registry(
            transport=transport,
            secret_resolver=MappingSecretResolver({"FIXTURE_PROVIDER_ACCESS": "mock"}),
        ).get("ga4")
        with tempfile.TemporaryDirectory() as directory:
            result = connector.collect(
                context(Path(directory), manifest),
                AcquisitionRequest("ga4", "ga4-organic-landing-performance", resource, fields, "2026-08-01", "2026-08-31"),
            )
        self.assertEqual("complete", result.status)
        self.assertEqual(20, result.records[0]["sessions"])
        self.assertEqual("America/New_York", result.metadata["timezone"])
        self.assertEqual("America/New_York", result.ingestion_manifest["metadata"]["timezone"])
        self.assertIn("sessions", result.metadata["metric_definition_metadata"])
        self.assertIn("different definitions", " ".join(result.limitations))
        self.assertEqual(3, len(transport.requests))

    def test_revenue_requires_expected_currency(self) -> None:
        resource = "123456"
        fields = ("sessionDefaultChannelGroup", "totalRevenue")
        manifest = authorization(provider="ga4", resource=resource, fields=fields)
        connector = build_default_registry(
            transport=FixtureTransport([fixture("ga4-metadata.json"), {"dimensionCompatibilities": [{"dimensionMetadata": {"apiName": "sessionDefaultChannelGroup"}, "compatibility": "COMPATIBLE"}], "metricCompatibilities": [{"metricMetadata": {"apiName": "totalRevenue"}, "compatibility": "COMPATIBLE"}]}]),
            secret_resolver=MappingSecretResolver({"FIXTURE_PROVIDER_ACCESS": "mock"}),
        ).get("ga4")
        with tempfile.TemporaryDirectory() as directory:
            result = connector.collect(
                context(Path(directory), manifest),
                AcquisitionRequest("ga4", "ga4-organic-landing-performance", resource, fields, "2026-08-01", "2026-08-31"),
            )
        self.assertEqual("failed", result.status)
        self.assertEqual("currency_required", result.errors[0]["category"])

    def test_incompatible_dimension_metric_pair_is_rejected(self) -> None:
        resource = "123456"
        fields = ("sessionDefaultChannelGroup", "sessions")
        manifest = authorization(provider="ga4", resource=resource, fields=fields)
        incompatible = {
            "dimensionCompatibilities": [{"dimensionMetadata": {"apiName": "sessionDefaultChannelGroup"}, "compatibility": "COMPATIBLE"}],
            "metricCompatibilities": [{"metricMetadata": {"apiName": "sessions"}, "compatibility": "INCOMPATIBLE"}],
        }
        connector = build_default_registry(
            transport=FixtureTransport([fixture("ga4-metadata.json"), incompatible]),
            secret_resolver=MappingSecretResolver({"FIXTURE_PROVIDER_ACCESS": "mock"}),
        ).get("ga4")
        with tempfile.TemporaryDirectory() as directory:
            result = connector.collect(
                context(Path(directory), manifest),
                AcquisitionRequest("ga4", "ga4-organic-landing-performance", resource, fields, "2026-08-01", "2026-08-31"),
            )
        self.assertEqual("failed", result.status)
        self.assertEqual("unsupported_combination", result.errors[0]["category"])


if __name__ == "__main__":
    unittest.main()
