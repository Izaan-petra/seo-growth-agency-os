---
name: seo-measurement
description: Design SEO measurement frameworks, KPI definitions, event requirements, reporting dimensions, monitoring, and validation plans. Use when seo-director delegates analytics readiness, SEO KPI design, tracking review, reporting requirements, experiment measurement, or performance-monitoring strategy.
---

# SEO Measurement

## Objective

Define how the engagement will establish baselines, measure implementation, monitor risk, and evaluate qualified organic outcomes.

Read `../seo-director/specialist-contract.md`. Use business conversions, reporting needs, available platforms, and attribution constraints recorded by `project-intake`. Do not request credentials or change analytics configurations without explicit authorization.

## Analyze

- Search Console, GA4, Bing Webmaster Tools, CRM/ecommerce, rank, crawl, backlink, and field-performance coverage
- Organic conversion and lead-quality definitions
- Branded/non-branded, market, device, landing-page, content-type, and funnel segmentation
- Event names, trigger conditions, parameters, deduplication, and validation needs
- Baselines, comparable periods, seasonality, annotations, and implementation logs
- Monitoring for crawl/indexation, manual actions, security issues, Core Web Vitals, migrations, rankings, links, and generative-AI visibility where supported
- Search Console property/search type, filters, dimensions, aggregation, timezone, date range, canonical-URL assignment, privacy omissions, row limits, and export method
- GA4 property timezone, organic-channel definition, traffic-source scope, event/key-event definitions, attribution model/lookback window, consent/modeling, thresholding, sampling, and freshness
- Metric-definition and attribution limitations, including why Search Console clicks are not GA4 sessions and why average position is not a universal rank

Do not combine metrics with different definitions as though they are identical. Record whether data is observed, modeled, sampled, thresholded, partial, or delayed. Google includes generative-AI feature data in overall Search Console totals; detect whether the limited-rollout dedicated reports are available for the property before requesting or promising them. Avoid targets or forecasts unsupported by a baseline and business constraints.

## Deliverable-specific output

Provide a measurement specification containing:

- KPI and guardrail definitions
- Formula, scope, source, owner dependency, and review cadence
- Required events/dimensions and validation procedure
- Baseline and target-setting requirements
- Dashboard/report views
- Monitoring and alert conditions
- Known attribution and data-quality limitations
- Report-availability and data-coverage notes

Use `MEASURE-##` IDs. Return the specification to `seo-director`.
