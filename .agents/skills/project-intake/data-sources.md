# SEO Data Source Manager

## Purpose

Select the safest and most useful data-collection method for each project. Do not assume that an API, authenticated browser session, export permission, or first-party access is available.

## Intake question

First inspect the connectors and tools visible in the current environment. Then, only when the relevant source availability or acquisition method remains unknown, ask one concise question such as:

> Which data sources are available for this project: Google Search Console, GA4, Bing Webmaster Tools, Ahrefs, Semrush, Screaming Frog, CRM or conversion data? For each paid platform, tell me whether you can use an API, export CSV/XLSX files, or provide screenshots.

Ask only for sources relevant to the current objective. Do not ask the user to repeat connector availability already visible in the environment.

## Access modes

### Mode 1 — API integration

Use when the user has an eligible paid account, API access, and permission to use the data for this project.

Rules:

- Never ask the user to paste an API key into chat, a Markdown file, source code, or a Git repository.
- Ask the user to store the key as an environment variable or Codex Cloud secret.
- Use a provider-specific variable name, such as `AHREFS_API_KEY`.
- Confirm only whether the secret is configured; never print or echo its value.
- Request the minimum API scopes and data needed for the task.
- Do not log authorization headers, tokens, cookies, or secret values.
- If API access fails, report the error without exposing the secret and switch to Manual Export or Screenshot mode.
- Treat third-party metrics as directional estimates.
- Respect account permissions, API quotas, rate limits, and provider terms.

Recommended agent response:

> API access can be used for this task. Please configure the provider key as an environment secret named `AHREFS_API_KEY` and tell me when it is available. Do not paste the key into this chat or commit it to the repository.

### Mode 2 — Manual export

Use when the user can access the platform but has no API key, uses a shared plan, or prefers manual control.

Rules:

- Tell the user exactly which report to open.
- Specify domain or URL mode, country, date range, filters, columns, and export format.
- Request only the minimum reports needed for the current stage.
- Prefer CSV or XLSX.
- Store unchanged exports in `research/raw/` when file handling is requested.
- Record report name, property/domain, export date, date range, and applied filters.

### Mode 3 — Screenshot-assisted

Use when API access and exports are unavailable.

Rules:

- Request one clearly labeled screenshot per report or view.
- Ask the user to include the report title, selected property/domain, date range, filters, and visible column headings.
- Request additional screenshots only when the current image does not contain enough evidence.
- Do not infer hidden rows, totals, filters, or historical values.
- Label screenshot-derived findings as limited or partial evidence.

### Mode 4 — Public-data fallback

Use when authenticated data is unavailable.

Rules:

- Continue with live-site and public research.
- Do not block the project.
- Clearly identify conclusions that require GSC, GA4, backlink, ranking, crawl, or conversion validation.
- Do not invent unavailable metrics.

## Provider priority

For first-party performance truth, prefer:

1. Google Search Console for Google organic search visibility and query/page performance.
2. GA4 or another analytics platform for on-site behavior and configured conversions.
3. CRM, ecommerce, call-tracking, or sales data for lead quality and revenue outcomes.
4. Crawl exports for technical inventory and diagnostics.
5. Ahrefs, Semrush, or similar platforms for directional keyword, competitor, backlink, and market estimates.
6. Screenshots when structured exports are impossible.
7. Public data when no authenticated source is available.

Do not merge metrics from different platforms as though they use identical definitions.

## Task-specific source selection

### Initial SEO audit

Prefer GSC, GA4, crawl data, sitemap/indexing evidence, and a limited Ahrefs or Semrush overview.

### Keyword and content plan

Prefer GSC queries/pages, third-party organic keyword reports, competitor content-gap reports, and confirmed business priorities.

### Competitor analysis

Prefer confirmed business competitors, third-party competing-domain/content-gap reports, SERP research, and competitor top-page exports.

### Link-building campaign

Prefer Ahrefs or equivalent referring domains, backlinks, anchors, best-by-links, broken backlinks, new/lost links, and Link Intersect exports.

### Performance review

Prefer comparable-period GSC, GA4, conversion/CRM data, implementation logs, and third-party visibility/backlink trends.

## Fallback order

When a preferred source cannot be used, follow this order:

`API -> CSV/XLSX export -> screenshot -> public-data assessment`

The agent should continue unless the missing source is essential to the user's requested deliverable. If it is essential, explain exactly what cannot be concluded and why.
