# SEO Specialist Delegation Contract

Use this contract for every workstream delegated by `seo-director` and every result returned by a specialist skill.

Phase 3 machine-readable briefs and findings validate against `../../../schemas/specialist-brief.schema.json` and `../../../schemas/specialist-finding.schema.json`. Batch 3 specialists also follow the procedure reference inside their own skill directory and emit validated domain artifacts when compatible approved snapshots are available. Preserve the existing Markdown result for human review.

## Deterministic procedure envelope

Every executable specialist procedure receives the project ID, director brief ID, immutable snapshots, and an explicit allowlist of approved snapshot IDs. It must:

- validate snapshot identity, project ownership, supported dataset type, and non-blocking data quality before analysis;
- preserve snapshot IDs as evidence references and preserve retrieval dates, provider timestamps, evidence tier, quality warnings, provider limitations, resource and period through the referenced snapshot;
- fail closed when minimum viable evidence is absent, malformed, unapproved, cross-project, or outside scope;
- skip a blocking optional input only when another allowed source satisfies minimum evidence, disclose the skip, and mark the result degraded;
- use versioned procedure identifiers and stable content-derived IDs;
- keep observed facts, deterministic classifications, evidence-backed inferences, recommendations, and post-change validation separate;
- validate every generic finding and every typed artifact against `schemas/` before returning the result to `seo-director`.

The procedures never collect additional evidence, broaden authorization, invent missing metrics, assign final priority, or perform an external change.

## Director brief

Provide:

- Engagement objective and requested deliverable
- Completed `project-intake` record or the relevant intake sections
- Specialist scope and explicit exclusions
- Target URLs, markets, languages, devices, and date range where applicable
- Approved evidence sources and their limitations
- Dependencies and blocking decisions
- Expected output and acceptance criteria

Do not delegate business discovery, connector detection, data-access intake, final prioritization, ownership assignment, or execution planning to a specialist.

## Evidence rules

- Read `google-search-requirements.md` and apply the sections relevant to the delegated work. Recheck an official source when the brief depends on a change-sensitive Google feature or policy.
- Use only intake-approved sources.
- Keep verified facts, source-backed estimates, inferences, and unknowns distinct.
- Cite exact URLs, reports, filters, and dates where available.
- Distinguish documented Google requirements and spam policies from recommendations, eligibility conditions, reporting limitations, and hypotheses. Do not present third-party conventions as confirmed Google ranking factors.
- Never invent traffic, rankings, search volume, backlinks, conversions, revenue, indexation, forecasts, or AI citations.
- Treat third-party metrics as directional unless the intake establishes otherwise.
- Report missing evidence instead of silently replacing it with assumptions.

## Specialist output

Return:

```markdown
# Specialist Workstream Result

## Scope executed
- Skill:
- Objective:
- Included:
- Excluded:

## Evidence used
| Source | Scope/date | Evidence tier | Limitations |
|---|---|---|---|

## Findings and recommendations
| ID | Finding or opportunity | Evidence | Affected URL/type | Recommended direction | Impact | Confidence | Effort | Dependencies | Validation |
|---|---|---|---|---|---|---|---|---|---|

## Deliverable-specific outputs

## Evidence gaps and conflicts

## Handoff notes for SEO Director
```

Use stable workstream-prefixed IDs such as `TECH-*`, `SERP-*`, or `CONTENT-*` so the director and blueprint can preserve provenance. Runtime IDs are deterministic hashes rendered under the same prefix; human-authored Markdown may retain sequential `##` suffixes.

Impact, confidence, and effort are specialist estimates. Do not assign final priority, owner, implementation phase, budget, or roadmap position.

## Completion standard

- Stay within the delegated scope.
- Support material claims with evidence.
- Make recommendations specific enough to implement.
- Identify dependencies, risks, and validation methods.
- Reject guarantees and tactics that violate applicable search-engine policies.
- Record the official source and verification date for material Google-specific claims.
- Return the result to `seo-director`; do not initiate external changes.
