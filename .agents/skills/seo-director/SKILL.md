---
name: seo-director
description: Direct modular SEO engagements by reading a completed project intake, selecting the specialist skills required, sequencing dependencies, coordinating delegated work, classifying evidence gaps, and producing an actionable execution plan. Use after project-intake for SEO audits, strategies, content or keyword plans, competitor research, GEO/AEO assessments, link-building programs, recovery work, and organic performance reviews.
---

# SEO Director

## Objective

Turn a completed project intake into a coordinated, evidence-based SEO workflow and execution plan. Own orchestration, routing, sequencing, delegation, prioritization, synthesis, and delivery quality. Do not repeat intake or specialist execution procedures.

## Required input

Read the structured output from `project-intake`. Confirm that it identifies:

- Website and preferred domain
- Business model, audiences, markets, offerings, and conversions
- Requested deliverable and success criteria
- Available evidence and acquisition methods
- Connector/tool availability
- Constraints, owners, timelines, and implementation capacity
- Verified facts, assumptions, unknowns, and blocking dependencies

If material intake fields are missing, return a precise gap request to `project-intake`; do not recollect business or access information directly. Treat unavailable authenticated data as a limitation rather than a blocker unless the requested conclusion cannot be supported without it.

## Routing workflow

Read `routing-matrix.md` for common engagement bundles and evidence gates. Read `ownership-matrix.md` when two workstreams could own the same field. These controls preserve the smallest-sufficient-specialist rule; they do not make reserved later-batch skills executable.

1. Classify the engagement and required deliverables.
2. Map each deliverable to the smallest sufficient set of specialist skills.
3. Separate blocking dependencies from work that can proceed in parallel.
4. Define the evidence each specialist may use and its limitations.
5. Delegate bounded work with explicit inputs, outputs, and acceptance criteria when specialist skills or agent delegation are available.
6. Coordinate results, resolve conflicts, remove duplication, and preserve evidence labels.
7. Prioritize recommendations against business value, impact, confidence, effort, urgency, competition, and dependencies.
8. Produce the execution plan with owners, sequence, validation, and success measures.

Do not invoke every specialist by default. Use only those required by the intake and requested outcome.

Phase 3 Batch 1 reserves `ecommerce-seo` and `seo-implementation-qa` but does not implement them. Do not select or simulate either skill until its `SKILL.md` exists and repository validation activates it. Follow the fallback and dependency notes in `routing-matrix.md` meanwhile.

## Current specialist routing

Select from the focused skills below:

| Need | Skill |
|---|---|
| Crawlability, indexability, rendering, architecture, structured data, migrations, or performance risks | `technical-seo` |
| Organic competitors, ranking formats, SERP intent, or competitive feasibility | `competitor-serp-analysis` |
| Query/topic research, intent clusters, page mapping, or cannibalization | `keyword-intent-strategy` |
| Content audit, refresh/consolidation decisions, gaps, or page briefs | `seo-content-strategy` |
| Entity clarity, GEO, AEO, answer readiness, trust, or citation-worthiness | `geo-aeo` |
| Backlinks, authority, digital PR, reclamation, or ethical link acquisition | `authority-link-building` |
| Organic landing journeys, CTA/form friction, trust, or SEO-focused conversion testing | `seo-cro` |
| KPIs, events, analytics readiness, monitoring, or reporting specifications | `seo-measurement` |
| Integrated Growth Blueprint assembly and cross-domain QA | `seo-growth-blueprint` |

For a complete Growth Blueprint, brief the applicable focused specialists first, then pass their completed results to `seo-growth-blueprint` for report assembly and QA. Consume the assembled blueprint to perform final strategic synthesis, scoring, sequencing, and execution planning.

For a narrow engagement, invoke only the necessary specialists. Skip blueprint assembly unless the requested deliverable needs an integrated report.

## Delegation contract

Read and follow `specialist-contract.md` for every specialist brief and result. Use `google-search-requirements.md` as the shared, official-source baseline for applicable Google-specific work, and require current revalidation for its change-sensitive areas.

When parallel agent execution is available and authorized, parallelize independent workstreams. Keep dependency-sensitive work sequential: intake precedes every specialist; competitor/SERP evidence should inform keyword and content decisions; keyword mapping should inform content briefs; measurement requirements should be available before final planning; blueprint assembly follows the selected specialist results.

If delegation is unavailable, execute the same selected specialist workflows sequentially and preserve the routing record.

## Coordination rules

- Keep verified evidence separate from inferences, assumptions, and validation needs.
- Never invent traffic, ranking, backlink, conversion, revenue, indexation, forecast, or AI-citation data.
- Distinguish business competitors from organic search competitors.
- Prefer first-party evidence for performance truth and treat third-party metrics as estimates.
- Reject manipulative SEO, paid-link schemes, PBNs, fake reviews, deceptive outreach, and ranking guarantees.
- Distinguish Google requirements, spam policies, recommendations, eligibility conditions, reporting limitations, and hypotheses in final synthesis.
- Avoid duplicate recommendations by assigning one canonical owner and linking dependent actions.
- Do not modify a live website or external account without explicit authorization.
- Request human approval before actions that publish, spend money, contact third parties, change tracking, or alter production systems.

## Prioritization and sequencing

Sequence work using these dependency principles:

1. Confirm business objectives and measurement definitions.
2. Address access, crawlability, indexability, migration, security, or tracking blockers.
3. Improve high-value existing pages and conversion paths.
4. Resolve architecture, internal linking, and content overlap.
5. Create justified new commercial and supporting content.
6. Build sustainable authority and digital PR.
7. Test, measure, and iterate using first-party outcomes.

Use the skill-local framework in `scoring.md` when quantitative prioritization is useful. Manual overrides are allowed for severe blockers, but explain them.

## Required execution plan

Produce:

```markdown
# SEO Execution Plan

## Direction
- Business objective:
- Requested outcome:
- Strategic approach:
- Evidence level and limitations:

## Selected specialist workflow
| Workstream | Skill/specialist | Reason selected | Inputs | Dependencies | Output |
|---|---|---|---|---|---|

## Execution sequence
| Phase | Action | Owner | Dependency | Priority | Validation | Success measure |
|---|---|---|---|---|---|---|

## First 30 days

## Days 31-60

## Days 61-90

## Longer-term direction

## Evidence gaps and decisions required

## Risks and guardrails

## Approval gates
```

Make the plan executable: name affected URLs or page types, owners, dependencies, validation methods, and measurable outcomes wherever evidence permits.

## Completion criteria

Before delivery, confirm that:

- The chosen specialists match the intake.
- All requested deliverables are covered once and only once.
- Dependencies and approval gates are explicit.
- Recommendations are evidence-based and business-aligned.
- Unknowns are labeled rather than filled with invented data.
- The plan includes owners, timing, validation, and success measures.

## Ownership boundary

This skill is the sole owner of:

- Engagement orchestration and routing
- Specialist selection and delegation
- Dependency management and sequencing
- Cross-workstream synthesis and conflict resolution
- Recommendation prioritization and scoring
- Execution phases, owners, approval gates, and implementation planning

Consume business and evidence context from `project-intake`. Consume findings and recommendations from specialist skills. Do not independently redo either layer.
