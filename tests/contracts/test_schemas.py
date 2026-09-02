from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from seo_os.schemas import SchemaValidationError, load_schema, validate_instance


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_NAMES = {
    "authorization-manifest",
    "ingestion-manifest",
    "project-intake",
    "specialist-brief",
    "specialist-finding",
    "keyword-cluster",
    "technical-issue",
    "content-action",
    "backlink-prospect",
    "cro-hypothesis",
    "measurement-kpi",
    "implementation-qa-result",
    "monitoring-event",
}


class SchemaContractTests(unittest.TestCase):
    def test_exact_required_schema_set_exists(self) -> None:
        actual = {
            path.name.removesuffix(".schema.json")
            for path in (ROOT / "schemas").glob("*.schema.json")
        }
        self.assertEqual(SCHEMA_NAMES, actual)

    def test_schemas_declare_json_schema_2020_12(self) -> None:
        for schema_name in sorted(SCHEMA_NAMES):
            with self.subTest(schema=schema_name):
                schema = load_schema(schema_name)
                self.assertEqual(
                    "https://json-schema.org/draft/2020-12/schema", schema["$schema"]
                )
                self.assertEqual("object", schema["type"])

    def test_all_schema_fixtures_validate(self) -> None:
        fixture_root = ROOT / "tests" / "fixtures" / "schemas"
        for schema_name in sorted(SCHEMA_NAMES):
            with self.subTest(schema=schema_name):
                fixture = json.loads(
                    (fixture_root / f"{schema_name}.json").read_text(encoding="utf-8")
                )
                validate_instance(schema_name, fixture)

    def test_unknown_authorization_property_is_rejected(self) -> None:
        fixture = json.loads(
            (ROOT / "tests" / "fixtures" / "schemas" / "authorization-manifest.json").read_text(encoding="utf-8")
        )
        invalid = copy.deepcopy(fixture)
        invalid["connectors"][0]["access_token"] = "not-allowed"
        with self.assertRaises(SchemaValidationError):
            validate_instance("authorization-manifest", invalid)


if __name__ == "__main__":
    unittest.main()
