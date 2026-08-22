# SEO Agency Operating System

## Structure

- `.agents/skills/project-intake/SKILL.md` — business discovery, evidence, connectors and data access
- `.agents/skills/project-intake/data-access.md` — authenticated-data and export request packs
- `.agents/skills/project-intake/data-sources.md` — evidence-source selection and fallback logic
- `.agents/skills/project-intake/integrations.md` — connector, API, secret and retention rules
- `.agents/skills/seo-director/SKILL.md` — orchestration, routing, delegation and execution planning
- `.agents/skills/seo-director/scoring.md` — director-owned prioritization framework
- `.agents/skills/seo-director/specialist-contract.md` — shared delegation and specialist-output contract
- `.agents/skills/seo-director/google-search-requirements.md` — official-source Google Search policy and measurement baseline
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
