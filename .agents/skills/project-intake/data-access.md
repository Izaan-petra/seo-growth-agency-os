# Data Access and Manual Export Playbooks

## Operating modes

### Public mode
Use when no authenticated data is available. Continue with live-site and public research. Label performance conclusions as unvalidated.

### Assisted mode
The user has platform access but no API. Guide them to export only the required reports and upload the files. This is the default mode for shared Ahrefs accounts.

### First-party mode
Use supplied GSC, GA4, Bing Webmaster Tools, CRM or conversion exports. Record property, date range, filters, timezone and attribution limitations.

## Opening authenticated tools safely

When browser interaction is supported, say:

> Please open the platform in the browser and sign in yourself. Tell me when the correct property is selected. I will guide you to the reports and exports needed for this task.

Never ask for passwords, cookies, backup codes or account credentials. If Codex cannot see or control the authenticated browser, provide navigation steps and request exported files instead.

# Request Pack A — Initial SEO Audit

## Google Search Console
Request the last 16 months when available, plus a recent comparison period.

1. Performance > Search results
   - Search type: Web
   - Date: Last 16 months
   - Export: Queries, Pages, Countries, Devices, Search appearance
2. Performance comparison
   - Last 3 months versus previous period
   - Export Queries and Pages
3. Indexing > Pages
   - Export indexed and non-indexed reasons where available
4. Sitemaps
   - Export or screenshot submitted sitemap status
5. Experience/Core Web Vitals
   - Export or screenshot mobile and desktop issue groups
6. Enhancements
   - Export or screenshot relevant structured-data reports
7. Links
   - Export top linked pages, top linking sites and internal links

Minimum acceptable GSC pack: Queries + Pages for 16 months and the Indexing summary.

## Google Analytics 4
Request the same core comparison windows used in GSC.

1. Reports > Acquisition > Traffic acquisition
   - Filter Session default channel group = Organic Search
   - Export by month with Sessions, Engaged sessions, Engagement rate, Key events/Conversions and Total revenue when applicable
2. Reports > Engagement > Landing page
   - Filter Organic Search
   - Export Landing page, Sessions, Users, Engagement rate, Key events and Revenue
3. Reports > Demographics/Tech
   - Export Country and Device category for organic traffic
4. Key events
   - Provide the names and definitions of conversions used for SEO evaluation

Never combine GSC clicks and GA4 sessions as though they are the same metric.

# Request Pack B — Content and Keyword Planning

## GSC
- Queries and Pages, last 16 months
- Query/page exports for priority directories
- Recent 3 months versus previous 3 months
- Include clicks, impressions, CTR and average position

## Ahrefs
Site Explorer > Organic keywords:
- Target: domain or relevant subfolder
- Location: target country
- Mode: current plus historical comparison if available
- Export fields: keyword, country, position, previous position, volume, traffic estimate, URL, SERP features, keyword difficulty, CPC where available

Also request:
- Top pages
- Competing domains
- Content gap for 3–5 genuine organic competitors

Use Ahrefs volume and traffic as directional estimates. Validate priority opportunities against business relevance, SERP intent and GSC evidence.

# Request Pack C — Competitor Analysis

Ask the user to confirm 3–5 business competitors and allow the agent to identify organic competitors separately.

Ahrefs exports:
1. Competing domains
2. Organic competitors
3. Content gap
   - Competitors rank in top 10 or 20
   - Target does not rank, or ranks below the selected threshold
4. Top pages for each selected competitor
5. Best by links for each selected competitor
6. Referring domains for selected competitor pages, only when link analysis is part of the task

Required columns when available: keyword/page, position, volume, traffic estimate, referring domains, backlinks, URL, country and date.

# Request Pack D — Link Building Campaign

Do not request all exports automatically. Choose based on campaign stage.

## Baseline profile
Ahrefs Site Explorer for the target domain:
- Overview screenshot/export
- Referring domains: Dofollow, One link per domain, Live
- Backlinks: Live, Dofollow, One link per domain where suitable
- Anchors
- Best by links
- Linked domains
- Broken backlinks
- New and lost referring domains for the last 12 months

Preferred export columns:
- Referring page title and URL
- Referring domain
- Domain Rating or equivalent third-party metric
- Estimated organic traffic
- Target URL
- Anchor and surrounding text when available
- Dofollow/nofollow
- First seen and last check
- Language
- Platform/type

## Competitor link gap
For 3–5 true organic competitors:
- Link Intersect: domains linking to competitors but not the target
- Referring domains
- Best by links
- Broken backlinks
- Top linked pages

Recommended Link Intersect filters:
- Dofollow
- One link per domain
- Live
- Target country/language where useful

## Asset-led outreach
Request:
- Best by links for competitors
- Content Explorer results for the target topic
- Pages with meaningful referring-domain counts and recent traffic
- Broken or outdated resources that the client can genuinely replace

## Prospect qualification
Do not approve prospects on DR alone. Review:
- Topical and audience relevance
- Real editorial standards
- Organic visibility plausibility
- Recent publishing activity
- Outbound-link quality
- Placement context
- Geographic/language fit
- Evidence of sponsored-link farms or unnatural patterns
- Whether the link can send qualified referral traffic

## Campaign keyword inputs
For link building, request keyword data only when it helps choose target pages or assets. Ask for:
- Priority commercial keyword clusters
- Informational topics that support those pages
- Competitor keywords tied to linkable assets
- Search intent and target country
- Existing ranking URL and current GSC performance where available

The agent should not ask the user for a vague “keyword list.” It should provide exact seed topics, competitor domains and Ahrefs report settings.

# Request Pack E — SEO Performance Review

Request comparable periods and note seasonality.

- GSC Queries and Pages
- GA4 organic Landing pages and conversions
- Ahrefs Organic keywords, Top pages, New/lost backlinks and Referring domains
- Implementation log with dates
- Business events, migrations, promotions or tracking changes

# File handling and validation

For every upload:
- Confirm platform and property/domain
- Confirm export date and report date range
- Confirm country, search type and filters
- Check whether rows were truncated
- Check encoding and column names
- Keep raw files unchanged in `research/raw/` when possible
- Save cleaned working files in `research/processed/`
- Cite data source and limitations in the final report
