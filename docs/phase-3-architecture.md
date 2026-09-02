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

## Control and data flow

```text
Business objective
  -> project-intake
  -> authorization manifest + acquisition plan
  -> connector registry (empty in Batch 1)
  -> ingestion manifest
  -> schema validation
  -> normalization/data-quality/snapshot interfaces
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

`ConnectorRegistry` rejects duplicate provider names and any connector whose capabilities are not read-only. Batch 1 registers no providers.

### Ingestion

- `manifest.py` validates and atomically writes ingestion manifests.
- `normalization.py` defines canonical normalized-record and normalizer interfaces.
- `quality.py` defines pass, warning and failure outcomes. A failed report is unusable.
- `snapshot.py` defines snapshot metadata, storage behavior and SHA-256 calculation.

### Schemas

Schema documents are stored in `schemas/`. The Batch 1 validator supports the JSON Schema keywords used by these contracts without adding a network-installed dependency. The public validation interface can later delegate to a complete standards library without changing callers.

### Security

`src/seo_os/security/` supplies recursive redaction, safe logging, privacy findings and high-confidence secret detection. Repository validation also enforces ignored-artifact policy.

## Skill availability

The eight Phase 2 specialist skills remain active. `ecommerce-seo` and `seo-implementation-qa` are declared as reserved in the routing and ownership matrices so later batches can implement them without silently pretending they already execute.

## Compatibility

- Existing Markdown specialist outputs remain valid.
- Machine-readable objects are an additive contract in Batch 1.
- The existing specialist delegation contract remains authoritative.
- The blueprint remains optional assembly only.
- The director remains the only final routing, conflict-resolution and planning owner.
- Project Intake remains the only access-discovery and authorization owner.

## Later batches

Later approved batches may add provider connectors, specialist procedures, ecommerce, implementation QA and monitoring. Each must add contract fixtures and tests before being described as executable.
