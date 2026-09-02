# SEO Data Integration Catalog

Use this catalog during `project-intake` to identify the minimum evidence and safest acquisition method required by the current engagement. It defines contracts, not implemented API clients. Batch 1 provides no external provider connector.

The authorization record must conform to `../../../schemas/authorization-manifest.schema.json`. Every completed acquisition must produce an ingestion record conforming to `../../../schemas/ingestion-manifest.schema.json`.

## Availability states

- **Contract only:** the source and fallback are defined, but no repository connector exists yet.
- **Manual supported:** Project Intake can request and validate a user-provided export or screenshot using the existing playbooks.
- **Public supported:** public research may be used without authentication, subject to scope, terms, and evidence limitations.

Never describe a contract-only source as connected or executable. Detect the tools actually available in the current environment.

## Integration contracts

| Source | Batch 1 availability | Authentication | Supported acquisition paths | Minimum requested fields | Validation | Refresh guidance | Missing-data fallback | Storage | Consumers |
|---|---|---|---|---|---|---|---|---|---|
| Google Search Console | Manual supported; API contract only | OAuth 2.0 or authorized service account; read-only scope | Future API, CSV/XLSX export, screenshot | Property, search type, date, query/page, country, device, appearance, clicks, impressions, CTR, position, filters, aggregation | Property, date range, search type, aggregation, filters, row limits, anonymized-query limits, export method | Daily monitoring later; weekly/monthly analysis | Export, then screenshot, then public-only limitation | Raw export and ingestion manifest; normalized snapshot later | Technical, keyword, content, ecommerce later, measurement |
| Google Analytics 4 | Manual supported; API contract only | OAuth/ADC or service account with property access | Future Data API, CSV/XLSX export, screenshot | Property, timezone, date, landing path, organic definition, device/country, sessions, users, engagement, key events, revenue | Property/timezone, channel definition, event definitions, attribution, thresholding, sampling/modeling, freshness | Daily or weekly later | Export, screenshot, or measurement limitation | Confidential raw aggregate; normalized snapshot later | Measurement, CRO, content, ecommerce later |
| Ahrefs | Manual supported; API contract only | Environment/cloud secret for API v3; user signs in for exports | Future API, CSV/XLSX export, screenshot | Report, target/mode, country, date, keyword/rank/URL or link/referring-domain fields | Target, country, report, filters, fields, row count, limits, retrieval date | Weekly/monthly later | Export, screenshot, public research | Confidential raw export; normalized snapshot later | SERP, keyword, authority, content, GEO |
| PageSpeed Insights | Public supported; API contract only | None for limited use; environment secret for repeated API use | Future API, manual PSI result, crawl export | Requested/final URL, strategy, fetch time, Lighthouse version, lab metrics, audit IDs | URL, final URL, mobile/desktop strategy, timestamp, Lighthouse version | Before/after and sampled weekly later | Lighthouse/crawl output or manual public test | Raw JSON/result; summarized snapshot later | Technical, CRO, implementation QA later, measurement |
| Chrome UX Report | Public/manual supported; API contract only | Environment/cloud API key | Future API, GSC CWV export/screenshot | URL or origin, form factor, metric, histogram, p75, collection window | Page versus origin, device, data availability, rolling period | Weekly later | GSC CWV or unavailable | Raw JSON/export; time-series snapshot later | Technical, measurement, implementation QA later |
| Bing Webmaster Tools | Manual supported; API contract only | OAuth 2.0 read access preferred; API key fallback | Future API, export, screenshot | Verified site, date, query/page metrics, crawl/index evidence, filters | Site, period, scope, export completeness | Weekly later | Export or screenshot | Raw JSON/CSV; snapshot later | Measurement, keyword, technical |
| Google Business Profile | Manual/public supported; API contract only | OAuth 2.0; approved Google Cloud project | Future Performance API, UI export, screenshot, public profile | Account/location, date, metrics, monthly search terms, profile status | Authorized location, metric availability, period, API approval | Weekly/monthly later | UI screenshot/export or public profile | Raw export/screenshot; snapshot later | GEO/local work, measurement |
| Shopify/ecommerce platform | Manual/public supported; API contract only | Provider OAuth/custom app with minimum read scopes | Future GraphQL/API, product CSV, admin screenshot, public storefront | Product, variant, collection, handle, status, inventory, price/currency, content, SEO fields, publication state | Store, API version, scopes, pagination, markets/currency, product counts | Product/inventory daily later; content weekly | Product CSV, admin screenshot, public storefront | Confidential catalog export; snapshot later | Ecommerce later, content, technical, CRO |
| Google Merchant Center | Manual supported; API contract only | OAuth 2.0 and Merchant API authorization | Future API, feed export, UI screenshot | Offer ID, link, availability, price/currency, condition, feed label, language, countries, item issues | Account/data source, offer uniqueness, target country/language, issue severity | Daily later for availability/price | Feed export or UI screenshot | Confidential feed/export; snapshot later | Ecommerce later, technical, measurement |
| Screaming Frog/crawl exports | Manual supported; CLI contract only | Local licensed installation when applicable | Future CLI/MCP, CSV/XLSX/JSON export, saved crawl | URL, status, content type, indexability, canonical, directives, metadata, links, depth, rendering mode | Configuration hash, robots setting, rendering, seeds, scope, completion, exclusions | Per audit; weekly later | User-provided crawl export or public sample | Raw crawl export; normalized URL inventory later | Technical, content, ecommerce later, implementation QA later |
| CRM/ecommerce conversions | Manual aggregate export only | Provider OAuth/service account later; authorized export now | Future provider adapter, aggregate CSV/XLSX | Date, conversion type, landing attribution, aggregate leads/orders/revenue/status | Timezone, currency, deduplication, refunds, attribution, aggregation, PII absence | Weekly/monthly later | GA4 proxy or unavailable | Aggregate confidential data only | Measurement, CRO, ecommerce later |
| Rank tracking | Manual export only; provider API contract later | Provider environment/cloud secret or authorized export | Future provider adapter, CSV/XLSX | Engine, query, locale, device, date, rank, URL, SERP features, tags | Engine, locale/device, collection time, rank sentinel, top-N depth | Daily/weekly later | Repeatable SERP sample or GSC average position | Raw export; time-series snapshot later | Keyword, SERP, measurement |
| Manual CSV/XLSX | Manual supported | User-authorized upload | CSV/XLSX | Source-specific required fields plus property, period, export date and filters | Encoding, headers, source, property, dates, filters, truncation, unexpected PII | Per upload | Corrected or smaller export | Unchanged in `research/raw/` | Selected specialist |
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
