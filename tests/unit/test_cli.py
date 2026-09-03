from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from seo_os.cli import _print_json, main
from seo_os.ingestion import deterministic_snapshot_id

from tests.connectors.helpers import FIXTURES, authorization


class CliTests(unittest.TestCase):
    def test_cli_output_applies_final_secret_redaction(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            _print_json({"metadata": {"access_token": "runtime-only-value"}})  # synthetic-secret-fixture
        self.assertNotIn("runtime-only-value", output.getvalue())
        self.assertEqual("[REDACTED]", json.loads(output.getvalue())["metadata"]["access_token"])

    def test_list_connectors(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = main(["connectors"])
        self.assertEqual(0, result)
        providers = {json.loads(line)["provider"] for line in output.getvalue().splitlines()}
        self.assertEqual({"gsc", "ga4", "ahrefs", "pagespeed-insights", "crux", "tabular"}, providers)

    def test_validate_authorization_and_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            auth_path = root / "authorization.json"
            auth_path.write_text(json.dumps(authorization(provider="gsc", resource="sc-domain:example.test", fields=("query",))), encoding="utf-8")
            base = {"schema_version": "1.0.0", "ingestion_id": "ingestion-fixture", "project_id": "PROJECT-FIXTURE", "source": "gsc", "dataset_type": "gsc-search-performance", "resource_id": "sc-domain:example.test", "retrieved_at": "2026-09-03T00:00:00Z", "period": None, "dimensions": [], "metrics": [], "limitations": [], "provenance": {}, "quality": {"status": "pass"}, "records": []}
            snapshot_path = root / "snapshot.json"
            snapshot_path.write_text(json.dumps({"snapshot_id": deterministic_snapshot_id(base), **base}), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(0, main(["validate-authorization", str(auth_path)]))
                self.assertEqual(0, main(["validate-snapshot", str(snapshot_path)]))

    def test_mock_connector_command_uses_fixture_transport(self) -> None:
        fields = "query,page,country,device,clicks,impressions,ctr,average_position"
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(output):
            result = main([
                "mock-connector",
                "--authorization", str(FIXTURES / "authorization-gsc.json"),
                "--data-root", directory,
                "--provider", "gsc",
                "--record-type", "gsc-search-performance",
                "--resource", "sc-domain:example.test",
                "--fields", fields,
                "--start-date", "2026-08-01",
                "--end-date", "2026-08-31",
                "--filters", '{"aggregation_type":"byPage"}',
                "--fixture", str(FIXTURES / "gsc-search-page.json"),
            ])
        self.assertEqual(0, result)
        self.assertEqual("complete", json.loads(output.getvalue())["status"])

    def test_ingest_export_command(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "raw" / "input.csv"
            source.parent.mkdir(parents=True)
            source.write_text("date,clicks\n2026-08-01,12\n", encoding="utf-8")
            auth_path = root / "authorization.json"
            auth_path.write_text(
                json.dumps(authorization(provider="tabular", resource="approved-export", fields=("date", "clicks"), methods=("export",), authentication_method="user-export", credential_reference=None)),
                encoding="utf-8",
            )
            with contextlib.redirect_stdout(io.StringIO()):
                result = main([
                    "ingest-export", "--authorization", str(auth_path),
                    "--data-root", str(root), "--record-type", "generic-tabular-evidence",
                    "--resource", "approved-export", "--fields", "date,clicks", "--file", "input.csv",
                ])
        self.assertEqual(0, result)


if __name__ == "__main__":
    unittest.main()
