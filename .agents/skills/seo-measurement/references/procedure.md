# Deterministic SEO Measurement Procedure

Runtime: `src/seo_os/procedures/measurement.py` (`seo-measurement`, version `1.0.0`).

## Input contract

Accept approved GSC, GA4 organic landing-page, Ahrefs keyword/backlink, or CrUX snapshots. A valid dataset period is required for a baseline. Preserve resource, retrieval time, provider timestamp, provenance, quality, provider limits, timezone, currency, attribution, and reporting-delay limitations.

## Rules

1. Aggregate provider metrics only within their own definitions.
2. Calculate GSC CTR as clicks/impressions and impression-weighted average position.
3. Calculate GA4 conversion rate as key events/sessions.
4. Compare only equal-duration supplied periods; mark unequal, incomplete, or absent comparisons.
5. Report zero denominators deterministically without fabricating growth percentages.
6. Treat third-party values as directional and add seasonality, freshness, attribution, privacy, sampling, and currency caveats.
7. Never normalize GSC clicks as GA4 sessions.

The default material-change review boundary is 20% absolute change. Comparisons require equal-duration windows and an explicit mode from previous-period, WoW, MoM, YoY, or pre/post; thresholds trigger investigation, never a causal conclusion or alert.

## Output and validation

Emit schema-valid `measurement-kpi` artifacts, stable `MEASURE-*` findings, source-separated baselines, comparisons, threshold definitions, and validation conditions. This batch performs no monitoring, scheduling, alerting, or analytics mutation. Return to `seo-director`.
