from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from seo_os.connectors import AcquisitionRequest, FixtureTransport, HttpResponse, build_default_registry
from seo_os.secrets import MappingSecretResolver

from .helpers import authorization, context, fixture


class AhrefsTests(unittest.TestCase):
    def test_api_organic_keywords_are_estimate_labeled(self) -> None:
        resource = "example.test"
        fields = ("keyword", "url", "best_position", "volume", "keyword_country")
        manifest = authorization(provider="ahrefs", resource=resource, fields=fields)
        connector = build_default_registry(
            transport=FixtureTransport([fixture("ahrefs-organic-keywords.json")]),
            secret_resolver=MappingSecretResolver({"FIXTURE_PROVIDER_ACCESS": "mock"}),
        ).get("ahrefs")
        with tempfile.TemporaryDirectory() as directory:
            result = connector.collect(
                context(Path(directory), manifest),
                AcquisitionRequest("ahrefs", "ahrefs-organic-keywords", resource, fields, "2026-08-01", "2026-08-31", {"country": "us", "limit": 100}),
            )
        self.assertEqual("complete", result.status)
        self.assertEqual("garden sprayer", result.records[0]["keyword"])
        self.assertTrue(result.metadata["third_party_estimate"])
        self.assertIn("third-party estimates", " ".join(result.limitations))

    def test_api_backlink_family_uses_backlink_dataset(self) -> None:
        resource = "example.test"
        fields = ("url_from", "url_to", "root_name_source", "domain_rating_source", "first_seen")
        manifest = authorization(provider="ahrefs", resource=resource, fields=fields, record_types=("ahrefs-backlinks",))
        connector = build_default_registry(
            transport=FixtureTransport([fixture("ahrefs-backlinks.json")]),
            secret_resolver=MappingSecretResolver({"FIXTURE_PROVIDER_ACCESS": "mock"}),
        ).get("ahrefs")
        with tempfile.TemporaryDirectory() as directory:
            result = connector.collect(
                context(Path(directory), manifest),
                AcquisitionRequest("ahrefs", "ahrefs-backlinks", resource, fields, filters={"limit": 100}),
            )
        self.assertEqual("ahrefs-backlink-refdomain", result.ingestion_manifest["record_type"])
        self.assertEqual("publisher.test", result.records[0]["root_name_source"])

    def test_manual_export_reports_duplicate_rejections(self) -> None:
        resource = "example.test"
        fields = ("keyword", "url", "best_position")
        manifest = authorization(
            provider="ahrefs", resource=resource, fields=fields, methods=("export",),
            authentication_method="user-export", credential_reference=None,
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "raw" / "exports" / "keywords.csv"
            source.parent.mkdir(parents=True)
            source.write_text(
                "keyword,url,best_position\n"
                "garden sprayer,https://example.test/products/sprayer,4\n"
                "garden sprayer,https://example.test/products/sprayer,4\n",
                encoding="utf-8",
            )
            connector = build_default_registry().get("ahrefs")
            result = connector.collect(
                context(root, manifest),
                AcquisitionRequest(
                    "ahrefs", "ahrefs-organic-keywords", resource, fields,
                    filters={"acquisition_method": "export", "path": "exports/keywords.csv", "type_mapping": {"best_position": "integer"}, "duplicate_keys": ["keyword", "url"]},
                ),
            )
        self.assertEqual("partial", result.status)
        self.assertEqual(1, len(result.records))
        self.assertEqual("duplicate-row", result.rejected_records[0]["reasons"][0])

    def test_screenshot_mode_uses_only_explicit_visible_values(self) -> None:
        resource = "example.test"
        fields = ("keyword", "url", "best_position")
        manifest = authorization(
            provider="ahrefs", resource=resource, fields=fields, methods=("screenshot",),
            authentication_method="user-screenshot", credential_reference=None,
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image = root / "raw" / "screens" / "organic.png"
            image.parent.mkdir(parents=True)
            image.write_bytes(b"synthetic-image-placeholder")
            checksum = hashlib.sha256(image.read_bytes()).hexdigest()
            connector = build_default_registry().get("ahrefs")
            result = connector.collect(
                context(root, manifest),
                AcquisitionRequest(
                    "ahrefs", "ahrefs-organic-keywords", resource, fields,
                    filters={
                        "acquisition_method": "screenshot",
                        "evidence_manifest": {"relative_path": "screens/organic.png", "checksum_sha256": checksum, "captured_at": "2026-09-03T08:00:00Z", "report": "organic-keywords", "target": resource, "visible_fields": list(fields)},
                        "visible_values": [{"keyword": "garden sprayer", "url": "https://example.test/products/sprayer", "best_position": 4}],
                    },
                ),
            )
        self.assertEqual("complete", result.status)
        self.assertTrue(any(issue["code"] == "screenshot-limitation" for issue in result.quality_report["issues"]))

    def test_public_fallback_declares_no_ahrefs_values(self) -> None:
        resource = "example.test"
        fields = ("keyword",)
        manifest = authorization(
            provider="ahrefs", resource=resource, fields=fields, methods=("public-research",),
            authentication_method="none", credential_reference=None,
        )
        with tempfile.TemporaryDirectory() as directory:
            result = build_default_registry().get("ahrefs").collect(
                context(Path(directory), manifest),
                AcquisitionRequest("ahrefs", "ahrefs-organic-keywords", resource, fields, filters={"acquisition_method": "public-research"}),
            )
        self.assertEqual("partial", result.status)
        self.assertEqual((), result.records)
        self.assertIn("No Ahrefs values", " ".join(result.limitations))

    def test_rate_limit_returns_sanitized_retryable_error(self) -> None:
        resource = "example.test"
        fields = ("keyword", "url")
        manifest = authorization(provider="ahrefs", resource=resource, fields=fields)
        connector = build_default_registry(
            transport=FixtureTransport([HttpResponse(429, {"internal": "not retained"}, {"Retry-After": "30"})]),
            secret_resolver=MappingSecretResolver({"FIXTURE_PROVIDER_ACCESS": "mock"}),
        ).get("ahrefs")
        with tempfile.TemporaryDirectory() as directory:
            result = connector.collect(
                context(Path(directory), manifest),
                AcquisitionRequest("ahrefs", "ahrefs-organic-keywords", resource, fields, end_date="2026-08-31"),
            )
        self.assertEqual("failed", result.status)
        self.assertEqual("rate_or_quota_limit", result.errors[0]["category"])
        self.assertTrue(result.errors[0]["retryable"])


if __name__ == "__main__":
    unittest.main()
