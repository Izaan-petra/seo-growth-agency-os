# Project Instructions

This repository contains a modular SEO Agency Operating System with these skills:

- `.agents/skills/project-intake/SKILL.md` — collect business context, evidence availability, access methods, and constraints.
- `.agents/skills/seo-director/SKILL.md` — select and coordinate the required specialist workflow and produce the execution plan.
- `.agents/skills/seo-growth-blueprint/SKILL.md` — assemble and quality-check the complete initial SEO Growth Blueprint from selected specialist results.

The focused specialist layer contains:

- `technical-seo`
- `competitor-serp-analysis`
- `keyword-intent-strategy`
- `seo-content-strategy`
- `geo-aeo`
- `authority-link-building`
- `seo-cro`
- `seo-measurement`

Phase 3 Batch 1 adds machine-readable contracts and the provider-neutral Python foundation. Batch 2 registers read-only GSC, GA4, Ahrefs, PageSpeed Insights, CrUX, and generic CSV/XLSX adapters. Validate data objects against `schemas/`, use `.agents/skills/seo-director/routing-matrix.md` and `.agents/skills/seo-director/ownership-matrix.md` as the director control plane, and use `.agents/skills/project-intake/integration-catalog.md` plus `.agents/skills/project-intake/authorization-manifest.md` for source and authorization intake.

`ecommerce-seo` and `seo-implementation-qa` are reserved later-batch skill names. They are not executable until their skill directories and skill entrypoint files exist. Shopify, Merchant Center, Bing Webmaster Tools, Google Business Profile, Screaming Frog CLI, CRM, rank tracking, monitoring, scheduling, and write actions remain unimplemented.

For a new or materially changed engagement, run `project-intake` first and route its structured output to `seo-director`. The director selects and briefs the focused specialist skills required. When an integrated blueprint is requested, route their results through `seo-growth-blueprint`, then return the assembled report to the director for prioritization and execution planning.

`project-intake` exclusively owns business discovery, evidence collection, connector detection, data-access selection, export requests, and credential-safety intake. `seo-director` exclusively owns orchestration, routing, delegation, strategic synthesis, prioritization, sequencing, and execution planning. Focused specialist skills exclusively own their domain analysis. `seo-growth-blueprint` exclusively owns integrated report assembly and cross-domain QA.

When file output is requested, save generated reports to `reports/`, unchanged source exports to `research/raw/`, and cleaned working artifacts to `research/processed/`. These locations are ignored by default for new generated files; commit a sanitized artifact only through an explicit review decision.

Every connector must implement the read-only interface under `src/seo_os/connectors/`, execute only a Project Intake-approved authorization manifest, and return an ingestion manifest. An implemented connector is not proof that credentials, a property, or authorization are available for a particular engagement.

Run `scripts/validate-skills.ps1` as the stable repository validation entry point. CI must require Python contract tests; local Phase 1/2 validation may still run without Python and will state when the Phase 3 tests were skipped.
