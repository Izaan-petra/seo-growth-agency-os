# SEO Agency Operating System

## Structure

- `.agents/skills/project-intake/SKILL.md` — business discovery, evidence, connectors and data access
- `.agents/skills/project-intake/data-access.md` — authenticated-data and export request packs
- `.agents/skills/project-intake/data-sources.md` — evidence-source selection and fallback logic
- `.agents/skills/project-intake/integrations.md` — connector, API, secret and retention rules
- `.agents/skills/project-intake/integration-catalog.md` — Phase 3 source contracts, validation and fallback matrix
- `.agents/skills/project-intake/authorization-manifest.md` — minimum-scope authorization control
- `.agents/skills/seo-director/SKILL.md` — orchestration, routing, delegation and execution planning
- `.agents/skills/seo-director/scoring.md` — director-owned prioritization framework
- `.agents/skills/seo-director/specialist-contract.md` — shared delegation and specialist-output contract
- `.agents/skills/seo-director/google-search-requirements.md` — official-source Google Search policy and measurement baseline
- `.agents/skills/seo-director/routing-matrix.md` — deterministic engagement bundles and evidence gates
- `.agents/skills/seo-director/ownership-matrix.md` — field-level primary and contributing ownership
- `.agents/skills/technical-seo/SKILL.md` — technical SEO and architecture
- `.agents/skills/competitor-serp-analysis/SKILL.md` — competitors and SERP patterns
- `.agents/skills/keyword-intent-strategy/SKILL.md` — keyword, intent and page mapping
- `.agents/skills/seo-content-strategy/SKILL.md` — content audits, opportunities and briefs
- `.agents/skills/geo-aeo/SKILL.md` — entity, answer and generative-search readiness
- `.agents/skills/authority-link-building/SKILL.md` — authority, digital PR and ethical link acquisition
- `.agents/skills/seo-cro/SKILL.md` — organic landing journeys and conversion friction
- `.agents/skills/seo-measurement/SKILL.md` — KPI, tracking and monitoring specifications
- `.agents/skills/seo-growth-blueprint/SKILL.md` — integrated report assembly and cross-domain QA
- `.agents/skills/seo-growth-blueprint/checklists.md` — audit coverage and QA
- `.agents/skills/seo-growth-blueprint/templates.md` — final report format
- `.agents/skills/seo-growth-blueprint/examples.md` — quality examples
- `docs/architecture.md` — responsibility boundaries and routing model
- `scripts/validate-skills.ps1` — deterministic skill and reference validation
- `scripts/check-privacy.ps1` — staged, tracked, or workspace privacy and secret validation
- `schemas/` — versioned JSON Schema 2020-12 contracts
- `src/seo_os/` — authorization, read-only connectors, normalization, quality, snapshots, security, and CLI
- `src/seo_os/procedures/` — versioned deterministic procedures for the eight active SEO specialists
- `tests/` — schema, routing, ownership, mocked connector, runtime and security fixtures/tests
- `docs/phase-3-architecture.md` — Phase 3 batching and execution-layer design
- `docs/data-lifecycle.md` — raw, processed, snapshot, cache, report and log lifecycle
- `docs/security-and-privacy.md` — credential, privacy, CI and logging controls
- `reports/` — generated reports, ignored by default unless explicitly reviewed for commit
- `research/raw/` — unchanged source exports, ignored by default
- `research/processed/` — cleaned working artifacts, ignored by default

## Test prompt

Use the `seo-growth-blueprint` skill for:

`https://example.com`

Run Project Intake in public-research mode, route the intake through SEO Director, execute the selected focused specialist skills, assemble their results with SEO Growth Blueprint, and return the report to SEO Director for prioritization and execution planning. Clearly separate verified findings from assumptions. Do not invent performance data. Save the report in `reports/` using the domain and current date.

## Normal use

For a new client, start with project intake and SEO Director routing:

`Run Project Intake for https://clientwebsite.com, route it to SEO Director, execute the selected specialist skills, assemble a blueprint when needed, and create the appropriate SEO execution plan.`

For a known blueprint deliverable with a current intake and completed specialist results, use:

`Use the SEO Growth Blueprint skill for https://clientwebsite.com`

## Important

The URL-only report is an initial strategic assessment. Refine it later with Search Console, GA4, ranking, backlink, conversion and business-priority data.


## Data-assisted workflows

Project Intake supports Public, Assisted, and First-party evidence modes. It can guide users through Google Search Console, GA4, Bing Webmaster Tools, and manual Ahrefs exports without requiring an Ahrefs API key. See `.agents/skills/project-intake/data-access.md`.

Google-specific specialist work follows `.agents/skills/seo-director/google-search-requirements.md`, which records the official-source baseline and the areas that must be rechecked because Google changes them over time.

For authenticated platforms, the user should sign in themselves. Codex must not request passwords or session credentials. When direct browser access is unavailable, upload CSV/XLSX exports.

## Codex cloud

Commit the complete project to a GitHub repository, including the hidden `.agents` directory and root `AGENTS.md`. Connect that repository to Codex cloud and create an environment for it. The repository-local skill will then travel with the project.


## API, export and screenshot modes

Project Intake supports four data-access paths:

1. API integration using an environment variable or Codex Cloud secret such as `AHREFS_API_KEY`.
2. Manual CSV/XLSX exports for shared or non-API accounts.
3. Clearly labeled screenshots when exports are unavailable.
4. Public-data fallback when no authenticated source is available.

Never paste API keys into prompts or commit them to the repository. See `.agents/skills/project-intake/data-sources.md` and `.agents/skills/project-intake/integrations.md`.

## Phase 3 Batch 2 status

Batch 1 established contracts and the provider-neutral runtime. Batch 2 registers six read-only adapters:

- `gsc`: Search Analytics API
- `ga4`: Data API metadata, compatibility, and `runReport`
- `ahrefs`: selected Site Explorer API reports plus export, screenshot, and public-fallback modes
- `pagespeed-insights`: Lighthouse lab evidence from PageSpeed Insights v5
- `crux`: URL/origin field evidence from the CrUX current-record API
- `tabular`: authorized CSV/XLSX exports with explicit rejected-row reporting

These adapters do not run OAuth flows or store long-lived credentials. The host must supply an approved environment-variable or managed-secret reference in an active authorization manifest. For Google APIs, supply a short-lived read-only bearer access token through the configured reference. Do not store OAuth refresh tokens or service-account JSON in this repository.

Shopify, Merchant Center, Bing Webmaster Tools, Google Business Profile, Screaming Frog CLI, CRM adapters, rank trackers, scheduling, monitoring, production writes, `ecommerce-seo`, and `seo-implementation-qa` remain unimplemented.

### Safe local commands

Install the package in editable mode in an isolated environment, or set `PYTHONPATH` to `src`, then run:

```powershell
python -m pip install -e .
python -m seo_os connectors
python -m seo_os validate-authorization clients/example/authorization.json
python -m seo_os ingest-export --authorization clients/example/authorization.json --data-root research --record-type generic-tabular-evidence --resource approved-export --fields date,clicks --file uploads/search.csv
python -m seo_os validate-snapshot research/snapshots/PROJECT/source/YYYY-MM-DD/snapshot-id.json
python -m seo_os mock-connector --authorization tests/fixtures/connectors/authorization-gsc.json --data-root research --provider gsc --record-type gsc-search-performance --resource sc-domain:example.test --fields query,page,country,device,clicks,impressions,ctr,average_position --start-date 2026-08-01 --end-date 2026-08-31 --filters '{"aggregation_type":"byPage"}' --fixture tests/fixtures/connectors/gsc-search-page.json
```

The export path is relative to `DATA_ROOT/raw`. Real authorization manifests belong in ignored `clients/`; real exports and provider responses belong under ignored `research/`. The mock command is for synthetic fixtures only.

### Environment references

Recommended variable names are `GSC_ACCESS_TOKEN`, `GA4_ACCESS_TOKEN`, `AHREFS_API_KEY`, `PAGESPEED_API_KEY`, and `CRUX_API_KEY`. The manifest stores only the name, never its value. PageSpeed can run without a key for limited use when an authorization entry explicitly uses authentication method `none`.

### Provider limitations

- GSC Search Analytics returns top rows rather than a guaranteed complete underlying table; query privacy and Pacific Time can affect reconciliation.
- GA4 sessions are not GSC clicks. Channel configuration, attribution, thresholding, high cardinality, sampling, modeling, consent, and freshness can affect results.
- Ahrefs metrics are third-party estimates and API usage can consume paid units. Batch 2 limits API mode to organic keywords, top pages, backlinks, and referring domains.
- PageSpeed values are Lighthouse lab diagnostics. CrUX values are aggregated field evidence; they remain separate datasets.
- CrUX may have no URL/origin record for low-traffic resources.
- CSV/XLSX invalid, duplicate, truncated, or privacy-sensitive rows are reported; they are never silently discarded.

Run the stable validation entry point with Python 3.11 or newer:

```powershell
./scripts/validate-skills.ps1 -PythonPath python -RequirePython
```

If Python is not on `PATH`, pass its executable path. The command validates Phase 1/2 skills, Phase 3 contracts, connector registration, mocked provider behavior, privacy rules, routing, ownership, fixtures, ingestion, quality, snapshots, CLI, and security controls. No CI test requires live credentials.

## Phase 3 Batch 3 status

Batch 3 adds dataset-driven procedures for all eight active specialists: technical SEO, competitor/SERP analysis, keyword and intent strategy, content strategy, GEO/AEO, authority/link building, SEO CRO, and SEO measurement. Each skill links to a detailed procedure reference; runtime code lives under `src/seo_os/procedures/`.

Procedures accept only explicitly approved immutable snapshot IDs, validate scope and quality, preserve provenance, generate stable IDs, validate typed artifacts against `schemas/`, and return results to SEO Director. Blocking or insufficient evidence fails closed; missing optional evidence produces a disclosed degraded result. No procedure collects additional data or performs production changes.

Batch 3 does not add connectors, ecommerce execution, implementation QA, monitoring, scheduling, alerting, outreach, publishing, or any other external write action.
