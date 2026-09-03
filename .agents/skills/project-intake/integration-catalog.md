# SEO Data Integration Catalog

Use this catalog during `project-intake` to identify the minimum evidence and safest acquisition method required by the current engagement. Batch 2 implements only the sources explicitly marked **Implemented** below. Implementation does not imply environment availability, authentication, property access, or engagement authorization.

The authorization record must conform to `../../../schemas/authorization-manifest.schema.json`. Every completed acquisition must produce an ingestion record conforming to `../../../schemas/ingestion-manifest.schema.json`.

## Availability states

- **Contract only:** the source and fallback are defined, but no repository connector exists yet.
- **Implemented:** a tested read-only repository adapter exists; an active authorization manifest and any required host-managed secret are still mandatory.
- **Manual supported:** Project Intake can request and validate a user-provided export or screenshot using the existing playbooks.
- **Public supported:** public research may be used without authentication, subject to scope, terms, and evidence limitations.

Never describe a contract-only source as connected or executable. Detect the tools actually available in the current environment.

## Integration contracts

| Source | Current availability | Authentication | Supported acquisition paths | Minimum requested fields | Validation | Refresh guidance | Missing-data fallback | Storage | Consumers |
|---|---|---|---|---|---|---|---|---|---|
| Google Search Console | **Implemented:** Search Analytics API; manual fallback supported | Host-supplied read-only OAuth access-token reference | API, CSV/XLSX export through generic adapter, screenshot | Property, record type, search type, date, query/page, country, device, appearance, clicks, impressions, CTR, position, filters, aggregation | Exact property/operation/field/date authorization, API combinations, 25,000-row pages, cap and partial-data labeling | Manual runs only; scheduling is later | Export, then screenshot, then public-only limitation | Immutable raw API JSON; ingestion manifest; normalized snapshot | Technical, keyword, content, measurement |
| Google Analytics 4 | **Implemented:** Data API metadata, compatibility and runReport; manual fallback supported | Host-supplied read-only OAuth access-token reference | API, CSV/XLSX export through generic adapter, screenshot | Property, record type, timezone, date, landing path, organic definition, device/country, sessions, users, engagement, key events, authorized revenue/currency | Metadata and compatibility preflight, exact authorization, timezone/channel/attribution, thresholding, sampling, cardinality and currency checks | Manual runs only; scheduling is later | Export, screenshot, or measurement limitation | Immutable raw aggregate JSON; ingestion manifest; normalized snapshot | Measurement, CRO, content |
| Ahrefs | **Implemented:** selected API v3 Site Explorer reports, CSV/XLSX, screenshot, public fallback | `AHREFS_API_KEY` or another host-managed secret reference; user signs in for exports | API, CSV/XLSX export, screenshot, public research | Allowed record type, target/mode, country, date, approved select fields, limits | Exact target/operation/fields, safe select identifiers, report requirements, row caps, screenshot checksum, third-party-estimate label | Manual runs only; scheduling is later | Export, screenshot, public research | Immutable raw JSON/export/evidence manifest; ingestion manifest; normalized snapshot | SERP, keyword, authority, content, GEO |
| PageSpeed Insights | **Implemented:** v5 API lab evidence | None for limited use; `PAGESPEED_API_KEY` reference for repeated use | API | Requested/final URL, mobile/desktop strategy, fetch time, Lighthouse version, approved lab audits | Exact URL/operation/fields, strategy, required Lighthouse metadata | Manual runs only; monitoring is later | Manual public PSI test | Immutable raw JSON; ingestion manifest; lab snapshot | Technical, CRO, measurement |
| Chrome UX Report | **Implemented:** current-record API | `CRUX_API_KEY` or another host-managed secret reference | API | URL or origin, form factor, approved metrics, histogram, p75, collection window | Exact resource/operation/fields, lookup type, form factor, missing-data handling | Manual runs only; monitoring is later | GSC CWV evidence or declared unavailable | Immutable raw JSON; ingestion manifest; field snapshot | Technical, measurement |
| Bing Webmaster Tools | Manual supported; API contract only | OAuth 2.0 read access preferred; API key fallback | Future API, export, screenshot | Verified site, date, query/page metrics, crawl/index evidence, filters | Site, period, scope, export completeness | Weekly later | Export or screenshot | Raw JSON/CSV; snapshot later | Measurement, keyword, technical |
| Google Business Profile | Manual/public supported; API contract only | OAuth 2.0; approved Google Cloud project | Future Performance API, UI export, screenshot, public profile | Account/location, date, metrics, monthly search terms, profile status | Authorized location, metric availability, period, API approval | Weekly/monthly later | UI screenshot/export or public profile | Raw export/screenshot; snapshot later | GEO/local work, measurement |
| Shopify/ecommerce platform | Manual/public supported; API contract only | Provider OAuth/custom app with minimum read scopes | Future GraphQL/API, product CSV, admin screenshot, public storefront | Product, variant, collection, handle, status, inventory, price/currency, content, SEO fields, publication state | Store, API version, scopes, pagination, markets/currency, product counts | Product/inventory daily later; content weekly | Product CSV, admin screenshot, public storefront | Confidential catalog export; snapshot later | Ecommerce later, content, technical, CRO |
| Google Merchant Center | Manual supported; API contract only | OAuth 2.0 and Merchant API authorization | Future API, feed export, UI screenshot | Offer ID, link, availability, price/currency, condition, feed label, language, countries, item issues | Account/data source, offer uniqueness, target country/language, issue severity | Daily later for availability/price | Feed export or UI screenshot | Confidential feed/export; snapshot later | Ecommerce later, technical, measurement |
| Screaming Frog/crawl exports | Manual supported; CLI contract only | Local licensed installation when applicable | Future CLI/MCP, CSV/XLSX/JSON export, saved crawl | URL, status, content type, indexability, canonical, directives, metadata, links, depth, rendering mode | Configuration hash, robots setting, rendering, seeds, scope, completion, exclusions | Per audit; weekly later | User-provided crawl export or public sample | Raw crawl export; normalized URL inventory later | Technical, content, ecommerce later, implementation QA later |
| CRM/ecommerce conversions | Manual aggregate export only | Provider OAuth/service account later; authorized export now | Future provider adapter, aggregate CSV/XLSX | Date, conversion type, landing attribution, aggregate leads/orders/revenue/status | Timezone, currency, deduplication, refunds, attribution, aggregation, PII absence | Weekly/monthly later | GA4 proxy or unavailable | Aggregate confidential data only | Measurement, CRO, ecommerce later |
| Rank tracking | Manual export only; provider API contract later | Provider environment/cloud secret or authorized export | Future provider adapter, CSV/XLSX | Engine, query, locale, device, date, rank, URL, SERP features, tags | Engine, locale/device, collection time, rank sentinel, top-N depth | Daily/weekly later | Repeatable SERP sample or GSC average position | Raw export; time-series snapshot later | Keyword, SERP, measurement |
| Manual CSV/XLSX | **Implemented:** reusable generic adapter | User-authorized upload | CSV/XLSX | Source-specific required fields, mapping, types, duplicate keys, sheet/date rules | Encoding, sheets, headers, types, dates, duplicates, truncation, unexpected PII; invalid rows are reported and quarantined | Per upload | Corrected or smaller export | Unchanged source plus ingestion manifest and normalized snapshot | Selected specialist |
| Screenshot evidence | Manual supported | User signs in; no credentials shared | PNG/JPEG plus evidence manifest | Source, property, report/view, date range, filters, visible fields, capture time | Visible context and labels, completeness, image checksum; never infer hidden values | Ad hoc | Better screenshot or public fallback | Image in `research/raw/`; derived notes in `research/processed/` | Selected specialist with limited confidence |
| Public web research | Public supported | None | Browser/HTTP/search research | URL/query, locale/device, retrieved time, observed facts, limitations | Source, timestamp, scope, terms, evidence reproducibility | Task-specific | Mark unavailable | Snapshot only when retention is needed | All specialists as fallback |

## Error categories

Record only non-sensitive categories:

- connector unavailable
- authorization missing or expired
- resource not authorized
- rate or quota limit
- provider outage
- unsupported report or field
- malformed or truncated export
- privacy quarantine
- data too sparse
- validation failure

Do not log authorization headers, credential values, cookies, session identifiers, customer records, or unredacted provider responses.

## Minimum-data rule

Request only fields needed by the director-selected engagement. A catalog row is not permission to collect every listed field. Order-, CRM-, customer-, and revenue-related evidence requires explicit purpose and must default to aggregated, non-PII data.
