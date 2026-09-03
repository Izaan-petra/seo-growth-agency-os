from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from seo_os.connectors import AcquisitionRequest, FixtureTransport, HttpResponse, build_default_registry
from seo_os.security import scan_path
from seo_os.secrets import MappingSecretResolver

from tests.connectors.helpers import FIXTURES, authorization, context


class ConnectorSecurityTests(unittest.TestCase):
    def test_credential_like_request_is_rejected_before_transport_or_persistence(self) -> None:
        resource = "sc-domain:example.test"
        fields = ("query", "clicks")
        manifest = authorization(provider="gsc", resource=resource, fields=fields)
        transport = FixtureTransport([{"rows": []}])
        connector = build_default_registry(
            transport=transport,
            secret_resolver=MappingSecretResolver({"FIXTURE_PROVIDER_ACCESS": "mock"}),
        ).get("gsc")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(RuntimeError, "credential-like material"):
                connector.collect(
                    context(root, manifest),
                    AcquisitionRequest(
                        "gsc", "gsc-search-performance", resource, fields,
                        "2026-08-01", "2026-08-31",
                        {"access_token": "runtime-only-value"},  # synthetic-secret-fixture
                    ),
                )
            self.assertEqual([], list(root.rglob("*")))
        self.assertEqual([], transport.requests)

    def test_provider_error_body_and_credential_are_not_persisted(self) -> None:
        resource = "sc-domain:example.test"
        fields = ("query", "clicks")
        manifest = authorization(provider="gsc", resource=resource, fields=fields)
        resolver = MappingSecretResolver({"FIXTURE_PROVIDER_ACCESS": "runtime-only-value"})
        transport = FixtureTransport([HttpResponse(500, {"provider_internal": "private-response-detail"}, {})])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = build_default_registry(transport=transport, secret_resolver=resolver).get("gsc").collect(
                context(root, manifest),
                AcquisitionRequest("gsc", "gsc-search-performance", resource, fields, "2026-08-01", "2026-08-31"),
            )
            persisted = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in root.rglob("*") if path.is_file())
        self.assertEqual("failed", result.status)
        self.assertNotIn("private-response-detail", persisted)
        self.assertNotIn("runtime-only-value", persisted)
        self.assertEqual("provider_unavailable", result.errors[0]["category"])

    def test_all_connector_json_fixtures_pass_secret_scan(self) -> None:
        findings = [finding for path in FIXTURES.glob("*.json") for finding in scan_path(path)]
        self.assertEqual([], findings)

    def test_fixture_transport_does_not_retain_header_values(self) -> None:
        transport = FixtureTransport([{"ok": True}])
        transport.request("GET", "https://example.test", headers={"Authorization": "synthetic"})
        serialized = json.dumps(transport.requests)
        self.assertIn("Authorization", serialized)
        self.assertNotIn("synthetic", serialized)

    def test_sensitive_provider_payload_is_quarantined_without_retention(self) -> None:
        resource = "sc-domain:example.test"
        fields = ("query", "clicks")
        manifest = authorization(provider="gsc", resource=resource, fields=fields)
        provider_payload = {"rows": [], "debug": {"access_token": "sensitive-marker"}}  # synthetic-secret-fixture
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = build_default_registry(
                transport=FixtureTransport([provider_payload]),
                secret_resolver=MappingSecretResolver({"FIXTURE_PROVIDER_ACCESS": "mock"}),
            ).get("gsc").collect(
                context(root, manifest),
                AcquisitionRequest("gsc", "gsc-search-performance", resource, fields, "2026-08-01", "2026-08-31"),
            )
            persisted = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in root.rglob("*") if path.is_file())
        self.assertEqual("failed", result.status)
        self.assertEqual("privacy_quarantine", result.errors[0]["category"])
        self.assertNotIn("sensitive-marker", persisted)


if __name__ == "__main__":
    unittest.main()
