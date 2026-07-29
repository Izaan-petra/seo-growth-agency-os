# SEO Growth Blueprint Codex Project

## Structure

- `.agents/skills/seo-growth-blueprint/SKILL.md` — main orchestrator
- `prompts.md` — specialist workflows
- `checklists.md` — audit coverage and QA
- `scoring.md` — prioritization
- `templates.md` — final report format
- `examples.md` — quality examples
- `reports/` — generated client reports
- `research/` — optional research notes and exports

## Test prompt

Use the `seo-growth-blueprint` skill for:

`https://example.com`

Create the complete initial SEO Growth Blueprint using public information. Clearly separate verified findings from assumptions. Do not invent performance data. Save the report in the `reports` directory using the domain and current date.

## Normal use

For a new client, provide only:

`Use the SEO Growth Blueprint skill for https://clientwebsite.com`

## Important

The URL-only report is an initial strategic assessment. Refine it later with Search Console, GA4, ranking, backlink, conversion and business-priority data.


## Data-assisted workflows

The skill now supports three modes: Public, Assisted, and First-party. It can guide users through Google Search Console, GA4, Bing Webmaster Tools, and manual Ahrefs exports without requiring an Ahrefs API key. See `.agents/skills/seo-growth-blueprint/data-access.md`.

For authenticated platforms, the user should sign in themselves. Codex must not request passwords or session credentials. When direct browser access is unavailable, upload CSV/XLSX exports.

## Codex cloud

Commit the complete project to a GitHub repository, including the hidden `.agents` directory and root `AGENTS.md`. Connect that repository to Codex cloud and create an environment for it. The repository-local skill will then travel with the project.


## API, export and screenshot modes

The skill supports four data-access paths:

1. API integration using an environment variable or Codex Cloud secret such as `AHREFS_API_KEY`.
2. Manual CSV/XLSX exports for shared or non-API accounts.
3. Clearly labeled screenshots when exports are unavailable.
4. Public-data fallback when no authenticated source is available.

Never paste API keys into prompts or commit them to the repository. See `.agents/skills/seo-growth-blueprint/data-sources.md` and `integrations.md`.
