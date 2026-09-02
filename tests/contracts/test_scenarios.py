from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPECTED = {
    "ecommerce-first-party": {"gsc", "ga4", "ahrefs"},
    "service-public-only": {"public-web"},
    "ecommerce-export-mode": {"ahrefs-export", "ahrefs-screenshot"},
}


class ScenarioFixtureTests(unittest.TestCase):
    def test_required_scenarios_are_structured_and_synthetic(self) -> None:
        root = ROOT / "tests" / "fixtures" / "scenarios"
        self.assertEqual(EXPECTED, {path.name: EXPECTED[path.name] for path in root.iterdir() if path.is_dir()})
        for scenario, expected_sources in EXPECTED.items():
            with self.subTest(scenario=scenario):
                payload = json.loads((root / scenario / "scenario.json").read_text(encoding="utf-8"))
                self.assertTrue(payload["synthetic"])
                self.assertEqual(expected_sources, set(payload["available_sources"]))
                self.assertTrue(payload["expected_assertions"])


if __name__ == "__main__":
    unittest.main()
