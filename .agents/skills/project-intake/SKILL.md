---
name: project-intake
description: Collect and structure the business context, goals, constraints, available SEO evidence, data-access methods, and connector availability for an SEO engagement. Use at the start of a new SEO project, audit, strategy, content plan, competitor analysis, link-building campaign, recovery investigation, or performance review before routing the completed intake to seo-director.
---

# Project Intake

## Objective

Own business discovery, evidence collection, connector detection, and data-access intake for the engagement. Create a concise intake record that gives `seo-director` enough context to select the right specialist skills and sequence the work. Do not perform specialist SEO analysis, prioritize recommendations, or produce the execution plan.

## Intake workflow

1. Identify the website, preferred domain, business model, offerings, audiences, target markets, and primary conversions.
2. Confirm the business objective, requested deliverable, urgency, scope, constraints, stakeholders, and implementation capacity.
3. Determine which first-party, third-party, and public evidence is available.
4. Detect which connectors and task-relevant tools are available in the current environment before asking the user for exports.
5. Select the safest available acquisition method for each necessary source.
6. Record gaps, access limitations, date ranges, filters, and assumptions.
7. Produce the intake record and route it to `seo-director`.

Ask only for information that materially affects intake completeness or the downstream director decision. If the user supplies only a URL, collect what can be verified publicly, label inferences, and continue without blocking.

## Evidence and access

Support these sources and methods:

- Google Search Console
- Google Analytics 4
- Ahrefs API
- Ahrefs screenshots
- CSV or XLSX exports
- Public website and search research

Also record other relevant sources when available, including Bing Webmaster Tools, crawl exports, CRM data, ecommerce data, call tracking, rank tracking, backlink platforms, and implementation logs.

Classify evidence separately from acquisition method:

- **Evidence tier:** First-party, Third-party, or Public
- **Acquisition method:** Connector/API, Export, Screenshot, or Public research

Do not treat screenshots or third-party estimates as equivalent to complete first-party data. Record the property, target, country, timezone, date range, filters, dimensions, aggregation, export method/date, row limits, and known limitations where applicable. For GA4, also record organic-channel definition, key-event definitions, attribution settings, consent/modeling constraints, thresholding, sampling, and freshness when relevant and observable.

Read these skill-local references only when relevant:

- `data-sources.md` for source selection and fallback logic
- `integrations.md` for API, connector, secret-handling, and retention rules
- `data-access.md` for GSC, GA4, Ahrefs, and manual-export request packs
- `integration-catalog.md` for Phase 3 source contracts, required metadata, validation, cadence, storage, fallback, and consumer rules
- `authorization-manifest.md` when recording machine-readable, minimum-scope data authorization

Phase 3 Batch 1 defines provider-neutral contracts only. Do not claim that a listed API connector is implemented, connected, or authorized. Continue to use available browser, export, screenshot, and public-research paths under the existing evidence rules.

## Connector detection

Before requesting manual data:

1. Inspect the currently available connectors and tools.
2. Use a relevant configured connector when it provides authorized, read-only access suitable for the task.
3. Never claim that a connector is available until it is visible in the current environment.
4. If no suitable connector exists, request the minimum export or screenshot needed.
5. Fall back to public research when authenticated evidence is unavailable.

Connector availability does not imply authorization for unrelated properties or broader data access. Use only the sources and scope relevant to the engagement.

## Security rules

- Never request passwords, session cookies, recovery codes, multifactor codes, or account sharing.
- Never ask the user to paste API keys or tokens into chat, code, Markdown, reports, or Git.
- For Ahrefs API access, require a configured environment variable or cloud secret such as `AHREFS_API_KEY` and confirm only whether it is available.
- Ask users to sign in to authenticated platforms themselves.
- Prefer minimum-scope, read-only access and the smallest necessary dataset.
- Treat client exports and API responses as confidential.
- Store raw exports in `research/raw/` and processed derivatives in `research/processed/` only when file handling is requested.
- Never invent unavailable metrics.

## Required intake record

Produce the following structure:

```markdown
# SEO Project Intake

## Project identity
- Website:
- Preferred domain:
- Organization:
- Intake date:
- Requested deliverable:

## Business context
- Business model:
- Main offerings:
- Target audiences:
- Target markets/languages:
- Primary conversions:
- Commercial priorities:

## Objective and constraints
- Primary objective:
- Success criteria:
- Urgency/timeline:
- Stakeholders/owners:
- Implementation capacity:
- Known risks or constraints:

## Evidence inventory
| Source | Evidence tier | Acquisition method | Available | Scope/date range | Limitations |
|---|---|---|---|---|---|

## Connector and tool availability
| Connector/tool | Available | Authorized scope | Intended use |
|---|---|---|---|

## Verified facts, assumptions, and unknowns
- Verified:
- Inferred:
- Requires validation:

## Handoff to SEO Director
- Primary destination: seo-director
- Intake completeness:
- Blocking intake gaps:
- Non-blocking evidence gaps:
```

Use `Not provided`, `Unavailable`, or `Requires validation` instead of leaving ambiguity.

## Handoff

Pass the completed intake record to `seo-director`. Do not recommend or select specialist skills; that decision belongs to the director. If direct skill-to-skill invocation is unavailable, return the intake record to the calling workflow with an explicit instruction to continue with `seo-director`.

Do not route directly to specialist execution. If `seo-director` is unavailable, return the completed intake and identify the routing dependency without selecting a substitute workflow.

## Ownership boundary

This skill is the sole owner of:

- Business and market discovery
- Business goals, audiences, offerings, markets, conversions, and constraints
- Evidence inventory and collection requests
- Connector and tool availability detection
- API, export, screenshot, and public-research access selection
- Credential-safety and intake data-handling instructions

Pass these facts downstream through the intake record. Do not ask downstream skills to rediscover them unless the record is materially incomplete or stale.
