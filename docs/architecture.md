# SEO Agency Operating System Architecture

## Responsibility layers

| Layer | Owner | Responsibility |
|---|---|---|
| Intake | `project-intake` | Business discovery, evidence inventory, connector detection, data-access selection, export requests, and credential safety |
| Direction | `seo-director` | Workstream selection, delegation, dependencies, prioritization, sequencing, approval gates, and execution planning |
| Specialist execution | Focused specialist skills | Domain analysis and evidence-backed recommendations within a director brief |
| Blueprint synthesis | `seo-growth-blueprint` | Combine selected specialist results into a coherent Growth Blueprint and run cross-domain QA |
| Final planning | `seo-director` | Score, deduplicate, assign owners, phase work, and issue the execution plan |
| Execution contracts | `schemas/` and `src/seo_os/` | Validate authorization and ingestion, run approved read-only acquisition, normalize evidence, apply quality gates, and write immutable snapshots |

## End-to-end flow

```text
User objective
  -> project-intake
  -> seo-director brief and routing
  -> selected specialist skills
  -> seo-growth-blueprint synthesis when a full blueprint is requested
  -> seo-director prioritization and execution plan
  -> human approval before external or production changes
```

For a narrow engagement, the director may route directly to one or more specialists and omit blueprint synthesis unless an integrated report is requested.

## Specialist catalog

| Skill | Primary scope |
|---|---|
| `technical-seo` | Crawlability, indexability, rendering, architecture, structured data, internationalization, performance risks |
| `competitor-serp-analysis` | Organic competitors, SERP formats, intent patterns, competitive gaps and feasibility |
| `keyword-intent-strategy` | Query/topic clusters, intent, page mapping, cannibalization and targeting |
| `seo-content-strategy` | Existing-content actions, content gaps, page opportunities and briefs |
| `geo-aeo` | Entity clarity, answer readiness, citation-worthiness, trust and structured answers |
| `authority-link-building` | Backlink evidence, authority, digital PR, link earning, reclamation and outreach planning |
| `seo-cro` | Organic landing journeys, message match, trust, forms, CTAs and testable conversion improvements |
| `seo-measurement` | KPI definitions, events, reporting dimensions, monitoring and validation |

All specialists follow `.agents/skills/seo-director/specialist-contract.md`. Applicable Google-specific work also follows the maintained official-source baseline in `.agents/skills/seo-director/google-search-requirements.md`.

## Data flow and ownership

- Intake facts flow downstream; specialists must not independently recollect them.
- The director brief limits scope and approved evidence.
- Specialists return stable IDs, evidence, estimates, dependencies, and validation instructions.
- The blueprint preserves specialist provenance and does not invent missing workstreams.
- Only the director assigns final priority, owner, phase, and execution order.

## File policy

- Generated reports: `reports/`
- Unchanged source exports: `research/raw/`
- Cleaned working artifacts: `research/processed/`

New files in these directories are ignored by Git by default. Commit only sanitized artifacts after explicit review.

## Phase 3 execution layer

Phase 3 Batches 1 and 2 add contracts and a read-only evidence layer beneath the existing skill flow without changing Phase 1 or Phase 2 ownership:

```text
project-intake
  -> authorization manifest and evidence plan
  -> registered read-only connector selected from the approved source/mode
  -> immutable raw artifact and ingestion manifest
  -> canonical evidence, deterministic quality gate, and immutable snapshot
  -> seo-director routing matrix
  -> existing selected specialists
```

Batch 2 registers GSC, GA4, Ahrefs, PageSpeed Insights, CrUX, and generic tabular adapters. Every execution still requires an active Project Intake authorization grant for the exact provider, acquisition method, record type, resource, fields, and date range. Connector availability never grants access by itself.

Provider API responses are normalized into seven canonical dataset families. Specialists consume the resulting snapshot/evidence reference; they do not receive credentials or permission to recollect or expand scope. `ecommerce-seo` and `seo-implementation-qa` remain reserved names only, and there is no monitoring or external write runtime.

The stable validation entry point is `scripts/validate-skills.ps1`. It preserves the current Phase 1/2 checks, validates the new control plane and schemas, runs privacy checks, and runs Python tests when a Python interpreter is supplied or available.
