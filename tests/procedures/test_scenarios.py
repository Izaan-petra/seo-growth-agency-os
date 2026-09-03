from __future__ import annotations

import unittest

from seo_os.procedures import (
    run_authority_procedure,
    run_content_procedure,
    run_cro_procedure,
    run_geo_procedure,
    run_keyword_procedure,
    run_measurement_procedure,
    run_serp_procedure,
    run_technical_procedure,
)
from seo_os.schemas import validate_instance

from tests.procedures.helpers import scenario_snapshots


def select(items, *types):
    return [item for item in items if item["dataset_type"] in types]


def run(function, items, **config):
    return function(
        project_id="PROJECT-FIXTURE", brief_id="BRIEF-FIXTURE", datasets=items,
        approved_dataset_ids=[item["snapshot_id"] for item in items], config=config,
    )


class DeterministicScenarioTests(unittest.TestCase):
    def test_scenario_a_first_party_workstreams(self) -> None:
        data = scenario_snapshots("scenario-a-ecommerce-first-party.json")
        technical = run(run_technical_procedure, select(data, "generic-tabular-evidence", "crux-field-performance", "psi-lab-performance", "gsc-search-performance"))
        self.assertTrue(any(item["classification"] == "poor" for item in technical["artifacts"]["core_web_vitals"]))
        self.assertEqual("lab", technical["artifacts"]["psi_lab_diagnostics"][0]["evidence_class"])
        self.assertTrue(any(item["rule_id"] == "internal-links" for item in technical["artifacts"]["technical_issues"]))
        self.assertTrue(any(item["rule_id"] == "redirect-chain" for item in technical["artifacts"]["technical_issues"]))
        self.assertTrue(any(item["rule_id"] == "sitemap" and "noindex-in-sitemap" in item["affected_urls"][0] for item in technical["artifacts"]["technical_issues"]))

        keyword = run(run_keyword_procedure, select(data, "gsc-search-performance"), brand_terms=["shop brand"], market="US", language="en")
        for item in keyword["artifacts"]["keyword_clusters"]:
            validate_instance("keyword-cluster", item)
        brand_states = {query["brand_classification"] for item in keyword["artifacts"]["keyword_clusters"] for query in item["queries"]}
        self.assertIn("branded", brand_states)
        self.assertIn("non-branded", brand_states)

        content = run(run_content_procedure, select(data, "generic-tabular-evidence", "gsc-search-performance", "ga4-organic-landing-performance"), as_of_date="2026-09-03")
        actions = {item["action"] for item in content["artifacts"]["content_actions"]}
        self.assertIn("redirect", actions)
        self.assertIn("requires-review", actions)
        seasonal = next(item for item in content["artifacts"]["content_actions"] if item["url"] == "https://shop.example/seasonal")
        self.assertEqual("retain", seasonal["action"])
        for item in content["artifacts"]["content_actions"]:
            validate_instance("content-action", item)

        geo = run(run_geo_procedure, select(data, "generic-tabular-evidence"))
        self.assertIn("not an AI-engine visibility metric", geo["artifacts"]["page_readiness"][0]["score_definition"])
        cro = run(run_cro_procedure, select(data, "generic-tabular-evidence", "gsc-search-performance", "ga4-organic-landing-performance", "crux-field-performance"))
        self.assertGreater(len(cro["artifacts"]["cro_hypotheses"]), 0)
        self.assertIn("remain separate", cro["artifacts"]["metric_boundary"])
        for item in cro["artifacts"]["cro_hypotheses"]:
            validate_instance("cro-hypothesis", item)

        measurement = run(run_measurement_procedure, select(data, "gsc-search-performance", "ga4-organic-landing-performance", "ahrefs-keyword-ranking", "ahrefs-backlink-refdomain", "crux-field-performance"))
        sources = {item["source"] for item in measurement["artifacts"]["measurement_kpis"]}
        self.assertIn("gsc-search-performance", sources)
        self.assertIn("ga4-organic-landing-performance", sources)
        self.assertIn("Never normalize", measurement["artifacts"]["source_boundaries"]["rule"])
        self.assertTrue(all("resource_id" in item and "retrieved_at" in item and "quality" in item and "provenance" in item for item in measurement["input_evidence"]))
        for item in measurement["artifacts"]["measurement_kpis"]:
            validate_instance("measurement-kpi", item)

    def test_scenario_b_public_serp_degrades_without_inventing_metrics(self) -> None:
        data = scenario_snapshots("scenario-b-service-public-limited.json")
        result = run(run_serp_procedure, data, minimum_results_per_query=2, competitor_recurrence_queries=2)
        self.assertEqual(1, result["artifacts"]["invalid_row_count"])
        self.assertEqual(2, result["artifacts"]["domain_frequency"]["competitor.example"])
        self.assertTrue(any(component["deterministic_classification"] == "limited-sample" for component in result["finding_components"]))
        self.assertFalse(any("traffic" in item["statement"].casefold() for item in result["findings"]))

    def test_scenario_c_exports_dedupe_and_risk_triage(self) -> None:
        data = scenario_snapshots("scenario-c-ahrefs-export-ecommerce.json")
        keyword = run(run_keyword_procedure, select(data, "ahrefs-keyword-ranking"), brand_terms=["shop"], market="US", language="en")
        self.assertTrue(keyword["degraded_mode"])
        self.assertTrue(any(item["target_mapping"]["cannibalization"] in {"possible", "confirmed"} for item in keyword["artifacts"]["keyword_clusters"]))
        authority = run(run_authority_procedure, select(data, "ahrefs-backlink-refdomain"), target_domain="shop.example")
        self.assertEqual(1, authority["artifacts"]["duplicate_record_count"])
        self.assertEqual(1, authority["artifacts"]["invalid_row_count"])
        self.assertTrue(any("suspected-link-network" in item["risk_flags"] for item in authority["artifacts"]["backlink_prospects"]))
        self.assertTrue(all(item["approval_status"] == "not-reviewed" for item in authority["artifacts"]["backlink_prospects"]))
        for item in authority["artifacts"]["backlink_prospects"]:
            validate_instance("backlink-prospect", item)

    def test_repeated_execution_is_identical(self) -> None:
        data = scenario_snapshots("scenario-b-service-public-limited.json")
        first = run(run_serp_procedure, data)
        second = run(run_serp_procedure, data)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
