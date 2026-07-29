# Project Instructions

This repository contains a modular SEO Agency Operating System with these skills:

- `.agents/skills/project-intake/SKILL.md` — collect business context, evidence availability, access methods, and constraints.
- `.agents/skills/seo-director/SKILL.md` — select and coordinate the required specialist workflow and produce the execution plan.
- `.agents/skills/seo-growth-blueprint/SKILL.md` — produce the complete initial SEO Growth Blueprint.

For a new or materially changed engagement, run `project-intake` first and route its structured output to `seo-director`. The director selects and briefs `seo-growth-blueprint` when this specialist execution is required, then consumes its findings to produce the prioritized execution plan.

`project-intake` exclusively owns business discovery, evidence collection, connector detection, data-access selection, export requests, and credential-safety intake. `seo-director` exclusively owns orchestration, routing, delegation, prioritization, sequencing, and execution planning. `seo-growth-blueprint` exclusively owns the selected specialist SEO analysis and specialist QA.

When file output is requested, save generated reports to `reports/`, unchanged source exports to `research/raw/`, and cleaned working artifacts to `research/processed/`. These locations are ignored by default for new generated files; commit a sanitized artifact only through an explicit review decision.
