# Google Search Requirements Baseline

Last verified against official Google documentation: 2026-08-22.

Use this baseline for Google-specific recommendations. Apply only the sections relevant to the director brief. Treat it as a maintained policy reference, not a ranking formula or a guarantee of crawling, indexing, rich results, traffic, or inclusion in generative features.

## How to state Google guidance

- Distinguish a documented technical requirement or spam policy from a recommendation, eligibility condition, reporting limitation, or observed hypothesis.
- Cite the applicable official Google page and record the verification date for material Google-specific claims.
- Do not describe third-party correlation studies, quality-rater guidance, or industry conventions as confirmed ranking factors.
- Recheck the official source when the work concerns a recently changed feature, report, structured-data type, or policy.

## Foundational eligibility and controls

- Googlebot must not be blocked, the page must return HTTP `200`, and the page must contain indexable content to meet Google's minimum technical requirements. Eligibility does not guarantee indexing.
- Use `robots.txt` to manage crawling, not to prevent indexing. Google must be allowed to crawl a URL to observe a `noindex` meta rule or `X-Robots-Tag`.
- Use one coherent canonicalization method, keep canonical signals consistent, link internally to preferred URLs, and do not use `robots.txt`, the URL removal tool, or `noindex` as canonicalization substitutes.
- Treat XML sitemaps as discovery hints, not indexing guarantees. Use accurate canonical URLs and meaningful `lastmod` values.
- Return real `404` or `410` responses for removed pages with no replacement; avoid soft-404 behavior. Use permanent redirects for genuine moves and avoid chains.
- Apply crawl-budget analysis mainly to very large or rapidly changing sites, or when Search Console shows substantial discovered-but-not-indexed inventory. Most sites need sound indexing controls and sitemaps rather than a crawl-budget project.

Official sources:

- [Technical requirements](https://developers.google.com/search/docs/essentials/technical)
- [Block indexing with noindex](https://developers.google.com/search/docs/crawling-indexing/block-indexing)
- [Canonicalization](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)
- [Build and submit a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [Crawl-budget management](https://developers.google.com/crawling/docs/crawl-budget)
- [Crawling and indexing troubleshooting](https://developers.google.com/search/docs/crawling-indexing/troubleshoot-crawling-errors)

## Rendering, mobile parity, and media discovery

- Validate important content, links, titles, meta descriptions, canonicals, robots directives, and structured data in rendered output. Prefer server-side rendering or prerendering when it materially improves reliability; JavaScript-generated canonical signals must not conflict with initial HTML.
- Do not place `noindex` in initial HTML when a script is expected to remove it, because Google may skip rendering after seeing `noindex`.
- Maintain important content, metadata, structured data, images, and directives on the mobile version used for mobile-first indexing.
- Lazy-loaded content must be discoverable without click, scroll, or other user interaction. Infinite-scroll implementations need persistent, uniquely addressable paginated URLs with crawlable sequential links.
- Use standard crawlable image and video embeds. Give important media stable accessible URLs, useful surrounding context, descriptive text, and—where applicable—image/video sitemaps and structured data that matches visible content.

Official sources:

- [JavaScript SEO basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)
- [Mobile-first indexing best practices](https://developers.google.com/search/docs/crawling-indexing/mobile/mobile-sites-mobile-first-indexing)
- [Lazy-loading content](https://developers.google.com/search/docs/crawling-indexing/javascript/lazy-loading)
- [Google Images best practices](https://developers.google.com/search/docs/appearance/google-images)
- [Video SEO best practices](https://developers.google.com/search/docs/appearance/video)

## People-first content and spam prevention

- Require original value, substantial and complete treatment, clear site purpose, demonstrable first-hand expertise where relevant, and a satisfying reader outcome.
- Do not prescribe a Google word-count target, create pages merely for keyword coverage, fake freshness by changing dates, or summarize other sources without adding meaningful value.
- Disallow keyword stuffing, cloaking, doorway pages, hidden text or links, scraped content, misleading functionality, machine-generated traffic, hacked content, and abusive redirects.
- Treat scaled content created primarily to manipulate rankings as spam regardless of whether it is produced by generative AI, people, scraping, translation, or other automation.
- Check expired-domain abuse and site-reputation abuse when ownership history or third-party publishing makes them relevant.

Official sources:

- [Creating helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
- [Google Search spam policies](https://developers.google.com/search/docs/essentials/spam-policies)
- [SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)

## Search appearance, structured data, and AI features

- Treat title elements and meta descriptions as inputs Google may rewrite, not fixed display promises. Keep titles descriptive, concise, distinct, and aligned with the page's language and visible main title.
- Use `nosnippet`, `data-nosnippet`, or `max-snippet` only when the business accepts their visibility tradeoffs.
- Use a currently supported structured-data type only when it fits visible page content and its feature-specific guidelines. Google recommends JSON-LD, also supports Microdata and RDFa, and does not guarantee rich results.
- Validate markup with the Rich Results Test and URL Inspection where access permits. Never add misleading, hidden, fabricated, or stale structured data.
- Google documents no special schema, AI text file, or optimization requirement for AI Overviews or AI Mode. Supporting pages must be indexed and eligible to show a snippet; important content should be available as text, internally discoverable, and supported by useful media where appropriate. Inclusion is never guaranteed.
- Keep Merchant Center and Business Profile information current when those products apply. Use Googlebot and Search preview controls to govern Search participation or displayed excerpts; do not treat Google-Extended, which controls some other Google systems, as the Search AI-feature control.

Official sources:

- [Title links](https://developers.google.com/search/docs/appearance/title-link)
- [Snippets and preview controls](https://developers.google.com/search/docs/appearance/snippet)
- [Structured data general guidelines](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)
- [AI features and your website](https://developers.google.com/search/docs/appearance/ai-features)

## Internationalization and page experience

- Use reciprocal, self-referencing `hreflang` annotations with valid language and optional region codes. Keep the canonical in the same language and use `x-default` when an unmatched-language selector or fallback is useful.
- Treat Core Web Vitals as field metrics: good thresholds are LCP at or below 2.5 seconds, INP below 200 milliseconds, and CLS below 0.1 at the 75th percentile. Page experience is holistic; no single signal or score guarantees ranking.

Official sources:

- [Localized versions and hreflang](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [Core Web Vitals](https://developers.google.com/search/docs/appearance/core-web-vitals)

## Authority and outbound-link compliance

- Reject buying or selling links for ranking credit, excessive reciprocal linking, automated link creation, low-quality directory or bookmark links, forum-comment spam, and optimized anchor links distributed through paid articles, press releases, widgets, or templates.
- Qualify advertisements, affiliate links, sponsorships, and other compensated placements with `rel="sponsored"`; `nofollow` remains acceptable for paid links, while `sponsored` is preferred. Mark user-generated links with `rel="ugc"` where appropriate. These attributes are hints, not guaranteed crawl blocks.
- Do not treat third-party authority scores as Google metrics or as proof that a placement is safe or valuable.

Official sources:

- [Qualify outbound links](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links)
- [Google Search spam policies: link spam](https://developers.google.com/search/docs/essentials/spam-policies#link-spam)

## Measurement and diagnosis

- Keep Search Console clicks separate from GA4 sessions. Search Console generally credits performance to Google's selected canonical URL, while GA4 reports the tagged landing URL users reach.
- Record Search Console property, search type, filters, dimensions, aggregation, timezone, date range, and export method. Query tables omit anonymized queries and may be truncated; chart totals can therefore exceed visible or exported query rows. UI exports commonly contain up to 1,000 representative rows, while the Search Analytics API and bulk export have different coverage and limits.
- Treat average position as a Search Console calculation, not a stable rank for every user. Account for result type, device, location, personalization, aggregation, and SERP composition.
- For GA4, record property timezone, organic-channel definition, event/key-event definitions, traffic-source scope, attribution model and lookback window, consent/modeling effects, thresholding, sampling, and data freshness. Attributed key-event credit can change after initial reporting.
- Google includes generative-AI feature data in overall Search Console performance totals. Dedicated generative-AI reports began limited rollout in 2026; detect property availability before promising or requesting them.
- Diagnose changes across technical errors, security issues, manual actions, spam-policy issues, algorithm updates, migrations, seasonality, demand changes, tracking changes, and business events before assigning a cause.

Official sources:

- [Using Search Console and Google Analytics data together](https://developers.google.com/search/docs/monitor-debug/google-analytics-search-console)
- [Search Console dimensions and data groupings](https://support.google.com/webmasters/answer/17011259)
- [Search Console metrics](https://support.google.com/webmasters/answer/7042828)
- [Search Console API export limits](https://support.google.com/webmasters/answer/12919192)
- [Direct Search Console export limits](https://support.google.com/webmasters/answer/12919797)
- [GA4 traffic-source scopes](https://support.google.com/analytics/answer/11080067)
- [GA4 key events and conversions](https://support.google.com/analytics/answer/13965727)
- [GA4 data freshness](https://support.google.com/analytics/answer/11198161)
- [GA4 data thresholds](https://support.google.com/analytics/answer/9383630)
- [GA4 modeled key events](https://support.google.com/analytics/answer/10710245)
- [Generative-AI performance reports](https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports)
- [Debugging Search traffic drops](https://developers.google.com/search/docs/monitor-debug/debugging-search-traffic-drops)

## Change-sensitive areas

Recheck official documentation before delivery when recommendations depend on:

- Structured-data feature availability or rich-result eligibility
- Search Console generative-AI reporting availability
- Spam-policy wording or enforcement categories
- Search appearance controls or result formats
- Analytics dimensions, attribution, privacy controls, quotas, or exports
- A migration, international configuration, or JavaScript framework behavior not directly verified on the target site
