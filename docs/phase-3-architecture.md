# Phase 3 Architecture

## Objective

Phase 3 moves the SEO Agency Operating System from descriptive specialist knowledge toward repeatable collection, processing, analysis, validation, and monitoring. It is implemented in controlled batches so the existing Phase 1 and Phase 2 workflow remains usable after every change.

## Batch 1 scope

Batch 1 establishes foundation and contracts only:

- JSON Schema 2020-12 contracts for intake, authorization, ingestion, director briefs, findings and future validation/monitoring records
- deterministic director routing and field-level ownership matrices
- Project Intake integration and authorization controls
- a provider-neutral, read-only Python package
- schema, routing, ownership, runtime and security tests
- privacy, secret, pre-commit and CI controls

Batch 1 does not implement:

- GSC, GA4, Ahrefs, Shopify, Merchant Center or any external API client
- recurring monitoring execution
- `ecommerce-seo`
- `seo-implementation-qa`
- deterministic specialist procedures
- external writes, publishing, outreach or production deployment

## Batch 2 scope

Batch 2 implements the first read-only acquisition layer:

| Connector ID | Implemented modes | Canonical output |
|---|---|---|
| `gsc` | Search Analytics API with filters, aggregation and offset pagination | `gsc-search-performance` |
| `ga4` | Data API metadata, compatibility preflight and paginated `runReport` | `ga4-organic-landing-performance` |
| `ahrefs` | Selected Site Explorer API reports, CSV/XLSX, screenshot evidence and public fallback | `ahrefs-keyword-ranking`, `ahrefs-backlink-refdomain` |
| `pagespeed-insights` | PageSpeed Insights v5 performance category | `psi-lab-performance` |
| `crux` | CrUX URL/origin current-record API | `crux-field-performance` |
| `tabular` | Generic authorized CSV/XLSX | `generic-tabular-evidence` |

Batch 2 does not implement OAuth login/token refresh, service-account file handling, Shopify, Merchant Center, Bing Webmaster Tools, Google Business Profile, Screaming Frog CLI, CRM/rank-tracker adapters, monitoring, scheduled jobs, specialist procedures, new skills, outreach, or external writes.

## Control and data flow

```text
Business objective
  -> project-intake
  -> authorization manifest + acquisition plan
  -> registered connector + exact authorization scope gate
  -> provider or user-supplied read-only evidence
  -> immutable raw artifact + ingestion manifest
  -> canonical normalization + deterministic quality gate
  -> immutable dated snapshot
  -> seo-director routing matrix
  -> active Phase 2 specialists
  -> optional seo-growth-blueprint assembly
  -> seo-director prioritization and execution plan
```

## Runtime packages

### Connectors

`src/seo_os/connectors/base.py` defines the only allowed provider contract. A connector must:

- report read-only capabilities
- probe availability without exposing secrets
- collect only fields and resources present in the acquisition request
- return redacted, categorized errors
- never broaden authorization or mutate an external system

`ConnectorRegistry` rejects duplicate provider names and any connector whose capabilities are not read-only. `build_default_registry()` registers only the six Batch 2 connectors. Provider-specific code uses a shared managed connector base so authorization is enforced before secret resolution or transport access.

The default HTTPS transport never includes provider bodies, credential values or request URLs in exceptions. Tests and the mock CLI use queued synthetic responses and record only header/query names.

## Canonical dataset definitions

Every snapshot has a typed envelope containing `schema_version`, `dataset_type`, `source`, `resource_id`, retrieval timestamp, period, dimension names, metric names, limitations, provenance and records. `src/seo_os/datasets.py` is the executable definition.

| Dataset | Row definition |
|---|---|
| `gsc-search-performance` | Requested date/query/page/country/device/search-appearance dimensions plus clicks, impressions, CTR and average position |
| `ga4-organic-landing-performance` | Requested landing, acquisition, country and device dimensions plus sessions, users, engagement, key events/conversions and explicitly authorized revenue/currency |
| `ahrefs-keyword-ranking` | Keyword or top-page evidence with ranking URL, market/date dimensions and selected rank, volume, difficulty or traffic estimates |
| `ahrefs-backlink-refdomain` | Backlink/referring-domain evidence with source/target identities and selected authority/link metrics |
| `psi-lab-performance` | Requested/final URL, strategy, fetch time, Lighthouse version, score, selected lab audit metrics and audit identifiers |
| `crux-field-performance` | URL/origin scope, form factor, collection period and per-metric p75, histogram and fraction evidence |
| `generic-tabular-evidence` | Source row number and only the authorized, mapped and type-normalized values |

Provider-specific fields remain named so evidence is not silently conflated. In particular, GA4 sessions are never normalized into GSC clicks, and PSI lab metrics never enter the CrUX field dataset.

### Ingestion

- `manifest.py` validates and atomically writes ingestion manifests.
- `normalization.py` retains the source-to-canonical interface; Batch 2 canonical envelopes and definitions live in `datasets.py`.
- `quality.py` deterministically classifies issues as information, warning or blocking. Blocking reports are unusable.
- `snapshot.py` creates content-derived IDs, create-only JSON artifacts, SHA-256 checksums and identity validation.
- `pipeline.py` owns immutable raw capture, ingestion manifests, quality gates and dated snapshots for all connectors.

### Schemas

Schema documents are stored in `schemas/`. The Batch 1 validator supports the JSON Schema keywords used by these contracts without adding a network-installed dependency. The public validation interface can later delegate to a complete standards library without changing callers.

The authorization schema now permits `allowed_record_types` as an additive operation allowlist. Existing Batch 1 manifests still validate, but a Batch 2 connector will not execute an entry without an explicit allowed record type. Ingestion manifests may include provider-safe metadata such as property, aggregation, timezone, selected fields, row counts and limitations.

### Security

`src/seo_os/security/` supplies recursive redaction, safe logging, privacy findings and high-confidence secret detection. Repository validation also enforces ignored-artifact policy.

Environment-variable names or `secret://` references are stored in authorization manifests; values are resolved only at request time. The built-in environment resolver does not resolve managed-secret URIs, which require a host-injected resolver. Google connectors consume host-minted read-only access tokens and never store refresh tokens or service-account contents.

## Provider semantics and sources

Official behavior was verified on 2026-09-03:

- [Search Analytics query](https://developers.google.com/webmaster-tools/v1/searchanalytics/query) documents the 25,000-row request cap, offset pagination, Pacific Time dates, aggregation behavior and top-row limitation.
- [GA4 Data API](https://developers.google.com/analytics/devguides/reporting/data/v1) documents metadata, compatibility and reporting methods; [reporting expectations](https://developers.google.com/analytics/devguides/reporting/data/v1/reporting-data-expectations) explains thresholding, sampling and high-cardinality effects.
- [Ahrefs API v3](https://docs.ahrefs.com/en/api/docs/introduction) documents paid units, rate limits and Site Explorer reports.
- [PageSpeed Insights v5](https://developers.google.com/speed/docs/insights/v5/get-started) documents Lighthouse lab results and recommends CrUX APIs for field evidence.
- [CrUX API](https://developer.chrome.com/docs/crux/api) documents URL/origin lookup, form factors, collection periods, histograms and p75 values.

## Skill availability

The eight Phase 2 specialist skills remain active. `ecommerce-seo` and `seo-implementation-qa` are declared as reserved in the routing and ownership matrices so later batches can implement them without silently pretending they already execute.

## Compatibility

- Existing Markdown specialist outputs remain valid.
- Machine-readable objects are an additive contract in Batch 1.
- Batch 2 normalized snapshots are additive evidence references; Markdown specialist outputs remain valid.
- The existing specialist delegation contract remains authoritative.
- The blueprint remains optional assembly only.
- The director remains the only final routing, conflict-resolution and planning owner.
- Project Intake remains the only access-discovery and authorization owner.

## Later batches

Later approved batches may add the explicitly excluded providers, deterministic specialist procedures, ecommerce, implementation QA and monitoring. Each must add contract fixtures and tests before being described as executable. Batch 2 performs no comparisons or scheduling.
