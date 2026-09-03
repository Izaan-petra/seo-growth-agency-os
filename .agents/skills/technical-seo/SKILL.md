---
name: technical-seo
description: Analyze technical SEO, crawlability, indexability, rendering, site architecture, internal linking, structured data, internationalization, and performance risks. Use when seo-director delegates a technical audit, migration review, crawl/indexation investigation, or technical workstream.
---

# Technical SEO

## Objective

Find technical conditions that prevent search engines and users from reliably accessing, understanding, rendering, consolidating, and navigating important pages.

Read `../seo-director/specialist-contract.md` and follow the director brief. Consume business and evidence context from `project-intake`; do not run a separate intake or assign final priorities.

When executing against Phase 3 snapshots, read `references/procedure.md` and use its deterministic runtime contract. Do not substitute an ad hoc analysis when compatible approved datasets are available.

## Analyze

- Minimum Google eligibility: Googlebot access, an HTTP `200` response, and indexable content; state that eligibility does not guarantee indexing
- HTTP status codes, redirect chains, loops, and broken links
- `robots.txt`, XML sitemaps, meta robots, and `X-Robots-Tag`, including whether Google can crawl URLs that must expose `noindex`
- Canonicals, duplicate URLs, parameters, pagination, facets, and crawl traps; reject `robots.txt`, removals, and `noindex` as canonicalization substitutes
- Real `404`/`410` handling, soft 404s, and redirect-to-replacement logic
- Architecture, crawl depth, orphan risk, breadcrumbs, and internal linking
- Server-rendered versus browser-rendered content, rendered links/metadata/directives, and JavaScript dependencies or conflicts
- Mobile-first parity for important content, metadata, structured data, images, and directives
- Lazy loading and infinite scroll that remain discoverable without user interaction
- Mobile usability and observable performance/Core Web Vitals evidence; separate field data from lab diagnostics and treat page experience holistically
- HTTPS, mixed content, host and protocol consistency
- Hreflang and international URL implementation when applicable
- Structured data validity, current feature eligibility, and alignment with visible content; do not imply rich-result guarantees
- Title, snippet-preview, image, and video discoverability controls when relevant to the delegated scope
- Crawl-budget analysis only when site scale, update frequency, or indexing evidence justifies it
- Migration-specific redirects, parity, and monitoring when delegated

Do not claim field performance, indexed-page totals, rendered behavior, or Google-selected canonicals without supporting evidence. Distinguish direct checks, crawl data, field data, lab observations, Search Console evidence, and unverified risks.

## Deliverable-specific output

In addition to the shared contract, provide:

- Technical coverage and crawl limitations
- Template-level patterns rather than isolated examples where supported
- Exact affected URLs or reproducible URL types
- Implementation direction suitable for engineering
- Validation steps using recrawl, inspection, logs, field data, or monitoring
- Dependencies on platform, templates, analytics, content, or releases

Use `TECH-##` IDs. Return findings to `seo-director`.
