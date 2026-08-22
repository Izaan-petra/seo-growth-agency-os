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

For a new or materially changed engagement, run `project-intake` first and route its structured output to `seo-director`. The director selects and briefs the focused specialist skills required. When an integrated blueprint is requested, route their results through `seo-growth-blueprint`, then return the assembled report to the director for prioritization and execution planning.

`project-intake` exclusively owns business discovery, evidence collection, connector detection, data-access selection, export requests, and credential-safety intake. `seo-director` exclusively owns orchestration, routing, delegation, strategic synthesis, prioritization, sequencing, and execution planning. Focused specialist skills exclusively own their domain analysis. `seo-growth-blueprint` exclusively owns integrated report assembly and cross-domain QA.

When file output is requested, save generated reports to `reports/`, unchanged source exports to `research/raw/`, and cleaned working artifacts to `research/processed/`. These locations are ignored by default for new generated files; commit a sanitized artifact only through an explicit review decision.
