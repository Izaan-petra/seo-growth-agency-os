from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from seo_os.connectors import AcquisitionRequest, ConnectorError, FixtureTransport, build_default_registry
from seo_os.secrets import MappingSecretResolver

from .helpers import authorization, context, fixture


class ConnectorContractTests(unittest.TestCase):
    def test_default_registry_contains_only_batch_2_read_only_connectors(self) -> None:
        registry = build_default_registry()
        self.assertEqual(
            ("ahrefs", "crux", "ga4", "gsc", "pagespeed-insights", "tabular"),
            registry.providers(),
        )
        for provider in registry.providers():
            self.assertTrue(registry.get(provider).capabilities.read_only)

    def test_unauthorized_field_is_rejected_before_transport(self) -> None:
        resource = "sc-domain:example.test"
        manifest = authorization(provider="gsc", resource=resource, fields=("query", "clicks"))
        transport = FixtureTransport([fixture("gsc-search-page.json")])
        connector = build_default_registry(
            transport=transport,
            secret_resolver=MappingSecretResolver({"FIXTURE_PROVIDER_ACCESS": "mock"}),
        ).get("gsc")
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ConnectorError) as caught:
                connector.collect(
                    context(Path(directory), manifest),
                    AcquisitionRequest(
                        "gsc", "gsc-search-performance", resource,
                        ("query", "page", "clicks"), "2026-08-01", "2026-08-31",
                    ),
                )
        self.assertEqual("field_not_authorized", caught.exception.category)
        self.assertEqual([], transport.requests)

    def test_missing_manifest_is_rejected_before_transport(self) -> None:
        transport = FixtureTransport([fixture("pagespeed.json")])
        connector = build_default_registry(transport=transport).get("pagespeed-insights")
        with tempfile.TemporaryDirectory() as directory:
            empty_context = context(Path(directory), authorization(provider="pagespeed-insights", resource="https://example.test/", fields=("performance_score",)))
            empty_context = empty_context.__class__(
                project_id=empty_context.project_id,
                authorization_id=empty_context.authorization_id,
                credential_reference=None,
                data_root=empty_context.data_root,
                requested_at=empty_context.requested_at,
            )
            with self.assertRaises(ConnectorError) as caught:
                connector.collect(
                    empty_context,
                    AcquisitionRequest("pagespeed-insights", "psi-lab-performance", "https://example.test/", ("performance_score",)),
                )
        self.assertEqual("authorization_missing", caught.exception.category)
        self.assertEqual([], transport.requests)

    def test_probe_separates_implementation_authorization_and_secret_availability(self) -> None:
        resource = "sc-domain:example.test"
        manifest = authorization(provider="gsc", resource=resource, fields=("query", "clicks"))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            unavailable = build_default_registry().get("gsc").probe(context(root, manifest))
            available = build_default_registry(
                secret_resolver=MappingSecretResolver({"FIXTURE_PROVIDER_ACCESS": "mock"})
            ).get("gsc").probe(context(root, manifest))
        self.assertTrue(unavailable.available)
        self.assertFalse(unavailable.authorized)
        self.assertTrue(available.authorized)


if __name__ == "__main__":
    unittest.main()
