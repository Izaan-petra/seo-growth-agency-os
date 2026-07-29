---
name: seo-growth-blueprint
description: Execute an evidence-based SEO Growth Blueprint covering technical SEO, architecture, competitors and SERPs, keywords and intent, content, GEO/AEO, authority, CRO, measurement, and QA. Use after project-intake supplies business and evidence context and seo-director selects this specialist workflow, or when the user explicitly requests this known deliverable with a current intake already available.
---

# SEO Growth Blueprint

## Objective

Execute the specialist SEO analysis selected by `seo-director` and return evidence-backed findings and recommendations. Consume the business context, goals, audiences, markets, conversions, constraints, evidence inventory, and access decisions from `project-intake`.

Do not repeat business discovery or data-access intake. Do not orchestrate other skills, score final priorities, sequence implementation, assign the final roadmap, or produce the engagement execution plan.

If no current intake record exists, route to `../project-intake/SKILL.md` before substantial work. If no director brief exists, return specialist findings for `../seo-director/SKILL.md` to prioritize and convert into the execution plan.

## Specialist scope

Execute only the workstreams selected in the director brief:

- Technical SEO and site architecture
- Competitor and SERP analysis
- Keyword and search-intent strategy
- Existing-content assessment and new-page opportunities
- GEO, AEO, entity, and AI-search readiness
- Authority, trust, E-E-A-T, digital PR, and ethical link acquisition
- CRO and UX observations connected to organic journeys
- Measurement recommendations
- Specialist QA and report assembly

Use business facts supplied by the intake to judge relevance and business value. Flag missing or stale inputs for the director instead of rediscovering the business from scratch.

## Inputs

Require or explicitly mark unavailable:

- Completed `project-intake` record
- Director-selected workstreams and acceptance criteria
- Target website, markets, languages, and scope
- Permitted evidence sources and their limitations
- Requested specialist output

Proceed in public-evidence mode when the intake confirms authenticated data is unavailable. Do not block a URL-only assessment after intake has classified the evidence gap.

## References

Read only the files needed for the selected workstreams:

- `prompts.md` for specialist execution workflows
- `checklists.md` for specialist coverage and QA
- `templates.md` for the blueprint report structure
- `examples.md` for recommendation and confidence-label quality

Data-source selection, connector detection, export requests, and secret handling belong to `project-intake`. Prioritization and execution planning belong to `seo-director`.

## Execution workflow

1. Read the intake record and director brief.
2. Validate the target URL and preferred host as technical evidence, without repeating business intake.
3. Execute only the selected specialist workstreams from `prompts.md`.
4. Cite website-specific evidence and exact URLs where possible.
5. Separate verified findings, suspected risks, inferences, assumptions, and validation needs.
6. Produce actionable specialist recommendations with impact and confidence evidence.
7. Run specialist QA using `checklists.md`.
8. Assemble the selected specialist sections using `templates.md`; leave director-owned planning sections for `seo-director`.
9. Return the specialist output to `seo-director` for prioritization, sequencing, ownership, and execution planning.

## Evidence rules

Never invent:

- Search volumes
- Rankings
- Organic traffic
- Backlinks
- Conversion rates
- Revenue
- Indexed-page counts
- Competitor performance
- Traffic forecasts
- AI citations

Use exact figures only when supported by an intake-approved source. Otherwise use qualitative labels such as High, Medium, Low, Short-term, Medium-term, Long-term, and Requires validation.

Do not guarantee rankings, traffic, leads, or revenue.

## Specialist recommendation standard

For each material recommendation, provide:

- Finding or recommendation
- Affected URL or page type
- Classification
- Evidence
- Why it matters
- Exact implementation direction
- Expected strategic outcome
- Business relevance based on intake
- Estimated impact
- Confidence
- Estimated effort
- Dependencies or validation needs
- Suggested validation method and success measure

Impact, confidence, and effort are specialist estimates for director review, not final prioritization. Do not assign the final priority, owner, phase, or roadmap position.

## New-page standard

For every justified page proposal, provide:

- Proposed title and URL
- Page type
- Target audience from intake
- Search intent
- Primary and supporting topics/entities
- Required sections and questions
- Unique value or evidence required
- Internal links in and out
- CTA
- Structured-data opportunity
- Business relevance
- Dependencies and validation needs

Do not place the page into a final execution phase; return it to the director for prioritization.

## Scope notice

Adapt the report scope to the evidence recorded by intake. For public-only work, include:

> This SEO Growth Blueprint uses publicly accessible information, observable website data, live search research, and the business context recorded during project intake. Internal analytics, Search Console data, conversion information, historical rankings, and confirmed business priorities were unavailable unless explicitly listed in the intake. Findings are specialist assessments that `seo-director` should prioritize and sequence using first-party business and performance data where available.

## Output

Return:

- Specialist findings and supporting evidence
- Actionable recommendations
- Confidence and validation labels
- Unresolved evidence gaps
- Dependencies and risks for director review

When requested, save the assembled specialist report in `reports/` using:

`domain-seo-growth-blueprint-YYYY-MM-DD.md`

Do not modify the live website. Return the completed specialist output to `seo-director`.

## Ownership boundary

This skill is the sole owner of SEO specialist execution and specialist QA for the Growth Blueprint. It is not the owner of intake, orchestration, final prioritization, or execution planning.
