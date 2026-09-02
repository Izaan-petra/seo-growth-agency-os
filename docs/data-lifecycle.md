# SEO OS Data Lifecycle

## Principles

- Collect the minimum data needed for the approved purpose.
- Keep raw evidence unchanged.
- Separate raw, processed, snapshot, cache, report and log lifecycles.
- Store no credential values in repository artifacts.
- Default client and generated data to ignored locations.
- Preserve provenance and checksums for every transformed dataset.

## Storage classes

| Class | Location | Purpose | Git policy | Default retention recommendation |
|---|---|---|---|---|
| Raw | `research/raw/` | Unchanged API response, export or screenshot | Ignored except `.gitkeep` | 30 days after acceptance unless contract requires otherwise |
| Processed | `research/processed/` | Cleaned, redacted or normalized working data | Ignored except `.gitkeep` | 90 days |
| Snapshot | `research/snapshots/` | Dated normalized state for comparison | Ignored except `.gitkeep` | Up to 13 months when seasonality requires it |
| Cache | `research/cache/` | Re-creatable provider or computation cache | Ignored except `.gitkeep` | 7 days |
| Client control | `clients/` | Local client-specific manifests and policy | Ignored except `.gitkeep` | Engagement plus approved closeout period |
| Reports | `reports/` | Human-readable generated deliverables | Ignored by default | Client contract |
| Logs | `logs/` | Redacted execution diagnostics | Ignored except `.gitkeep` | 30 days |
| Synthetic fixtures | `tests/fixtures/` | Non-client deterministic tests | Tracked | Repository lifetime |

The durations are policy defaults, not automatic deletion authority. Apply a client-specific legal or contractual retention rule when one exists.

## Lifecycle stages

1. Project Intake records purpose, authorized source, resources, fields, dates, acquisition method and retention rule.
2. Collection stores the raw artifact without modification.
3. An ingestion manifest records checksum, size, fields, filters, dates, row count, limitations and error status.
4. Validation quarantines malformed, over-scoped or privacy-risk data.
5. Normalization creates source-independent records while preserving evidence references.
6. Data-quality checks mark the dataset pass, warn or fail.
7. Snapshot storage captures approved comparable state.
8. Specialists consume processed/snapshot evidence, not credentials.
9. Reports cite evidence and limitations without embedding unnecessary raw data.
10. Closeout follows the approved retention and deletion decision.

## PII controls

- CRM, order and ecommerce conversion data must be aggregate by default.
- Exclude names, emails, phones, postal addresses, free-text notes and customer IDs unless explicitly essential and authorized.
- Quarantine an export when an unexpected sensitive column appears.
- Pseudonymize record identifiers before processed storage when record-level analysis is approved.
- A redaction report may record removed field names and counts, never removed values.

## Integrity

Use SHA-256 for raw and snapshot artifacts. Do not overwrite a raw file under an existing ingestion ID. A changed export creates a new ingestion and snapshot record.
