from __future__ import annotations

import copy
import unittest
from datetime import UTC, datetime

from seo_os.authorization import AuthorizationError, AuthorizationManifest

from tests.connectors.helpers import authorization


class AuthorizationTests(unittest.TestCase):
    def test_active_manifest_authorizes_exact_resource_fields_method_and_dates(self) -> None:
        payload = authorization(provider="gsc", resource="sc-domain:example.test", fields=("query", "clicks"))
        grant = AuthorizationManifest.from_mapping(payload).authorize(
            project_id="PROJECT-FIXTURE", authorization_id="AUTHZ-FIXTURE-200",
            provider="gsc", acquisition_method="api", resource_id="sc-domain:example.test",
            record_type="gsc-search-performance",
            fields=("query", "clicks"), start_date="2026-08-01", end_date="2026-08-31",
            at=datetime(2026, 9, 3, tzinfo=UTC),
        )
        self.assertEqual("read-only", payload["connectors"][0]["access_mode"])
        self.assertEqual("FIXTURE_PROVIDER_ACCESS", grant.credential_reference)

    def test_resource_method_date_and_status_scope_fail_closed(self) -> None:
        baseline = authorization(provider="gsc", resource="sc-domain:example.test", fields=("query", "clicks"))
        cases = [
            {"resource_id": "sc-domain:other.test"},
            {"acquisition_method": "export"},
            {"start_date": "2025-12-31"},
        ]
        defaults = {
            "project_id": "PROJECT-FIXTURE", "authorization_id": "AUTHZ-FIXTURE-200",
            "provider": "gsc", "acquisition_method": "api", "resource_id": "sc-domain:example.test",
            "record_type": "gsc-search-performance",
            "fields": ("query",), "start_date": "2026-08-01", "end_date": "2026-08-31",
            "at": datetime(2026, 9, 3, tzinfo=UTC),
        }
        for changes in cases:
            with self.subTest(changes=changes), self.assertRaises(AuthorizationError):
                AuthorizationManifest.from_mapping(baseline).authorize(**{**defaults, **changes})
        inactive = copy.deepcopy(baseline)
        inactive["status"] = "revoked"
        with self.assertRaises(AuthorizationError):
            AuthorizationManifest.from_mapping(inactive).authorize(**defaults)

    def test_secret_value_cannot_be_added_to_manifest(self) -> None:
        payload = authorization(provider="ahrefs", resource="example.test", fields=("keyword",))
        payload["connectors"][0]["api_key"] = "not-permitted"
        with self.assertRaises(ValueError):
            AuthorizationManifest.from_mapping(payload)

    def test_missing_operation_allowlist_cannot_execute(self) -> None:
        payload = authorization(provider="gsc", resource="sc-domain:example.test", fields=("query",))
        payload["connectors"][0].pop("allowed_record_types")
        with self.assertRaises(AuthorizationError) as caught:
            AuthorizationManifest.from_mapping(payload).authorize(
                project_id="PROJECT-FIXTURE", authorization_id="AUTHZ-FIXTURE-200",
                provider="gsc", acquisition_method="api", record_type="gsc-search-performance",
                resource_id="sc-domain:example.test", fields=("query",),
                at=datetime(2026, 9, 3, tzinfo=UTC),
            )
        self.assertEqual("operation_not_authorized", caught.exception.code)


if __name__ == "__main__":
    unittest.main()
