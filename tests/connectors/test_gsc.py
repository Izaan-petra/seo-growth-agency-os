from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from seo_os.connectors import AcquisitionRequest, FixtureTransport, build_default_registry
from seo_os.secrets import MappingSecretResolver

from .helpers import authorization, context, fixture


class GoogleSearchConsoleTests(unittest.TestCase):
    def test_search_analytics_is_paginated_normalized_and_persisted(self) -> None:
        resource = "sc-domain:example.test"
        fields = ("query", "page", "country", "device", "clicks", "impressions", "ctr", "average_position")
        manifest = authorization(provider="gsc", resource=resource, fields=fields)
        transport = FixtureTransport([fixture("gsc-search-page.json")])
        connector = build_default_registry(
            transport=transport,
            secret_resolver=MappingSecretResolver({"FIXTURE_PROVIDER_ACCESS": "mock"}),
        ).get("gsc")
        with tempfile.TemporaryDirectory() as directory:
            result = connector.collect(
                context(Path(directory), manifest),
                AcquisitionRequest(
                    "gsc", "gsc-search-performance", resource, fields,
                    "2026-08-01", "2026-08-31", {"aggregation_type": "byPage"},
                ),
            )
            self.assertTrue((Path(directory) / result.metadata["raw_artifact"]).is_file())
            self.assertTrue((Path(directory) / result.snapshot["relative_path"]).is_file())
        self.assertEqual("complete", result.status)
        self.assertEqual(1, result.ingestion_manifest["row_count"])
        self.assertEqual("byPage", result.ingestion_manifest["metadata"]["aggregation_mode"])
        self.assertEqual(4.2, result.records[0]["average_position"])
        self.assertIn("top rows", " ".join(result.limitations))
        self.assertNotIn("Authorization", transport.requests[0]["json_body"])

    def test_offset_pagination_advances_until_an_empty_page(self) -> None:
        resource = "sc-domain:example.test"
        fields = ("query", "page", "country", "device", "clicks", "impressions", "ctr", "average_position")
        manifest = authorization(provider="gsc", resource=resource, fields=fields)
        transport = FixtureTransport([fixture("gsc-search-page.json"), {"rows": [], "responseAggregationType": "byPage"}])
        connector = build_default_registry(
            transport=transport,
            secret_resolver=MappingSecretResolver({"FIXTURE_PROVIDER_ACCESS": "mock"}),
        ).get("gsc")
        with tempfile.TemporaryDirectory() as directory:
            result = connector.collect(
                context(Path(directory), manifest),
                AcquisitionRequest("gsc", "gsc-search-performance", resource, fields, "2026-08-01", "2026-08-31", {"aggregation_type": "byPage", "row_limit": 1}),
            )
        self.assertEqual("complete", result.status)
        self.assertEqual([0, 1], [request["json_body"]["startRow"] for request in transport.requests])

    def test_page_grouping_cannot_use_property_aggregation(self) -> None:
        resource = "sc-domain:example.test"
        fields = ("page", "clicks")
        manifest = authorization(provider="gsc", resource=resource, fields=fields)
        connector = build_default_registry(
            transport=FixtureTransport([fixture("gsc-search-page.json")]),
            secret_resolver=MappingSecretResolver({"FIXTURE_PROVIDER_ACCESS": "mock"}),
        ).get("gsc")
        with tempfile.TemporaryDirectory() as directory:
            result = connector.collect(
                context(Path(directory), manifest),
                AcquisitionRequest("gsc", "gsc-search-performance", resource, fields, "2026-08-01", "2026-08-31", {"aggregation_type": "byProperty"}),
            )
        self.assertEqual("failed", result.status)
        self.assertEqual("unsupported_combination", result.errors[0]["category"])


if __name__ == "__main__":
    unittest.main()
