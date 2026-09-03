# Deterministic SEO CRO Procedure

Runtime: `src/seo_os/procedures/cro.py` (`seo-cro`, version `1.0.0`).

## Input contract

Accept approved GA4 organic landing-page, GSC page, generic UX observation, or CrUX field snapshots. Preserve GA4 sessions, GSC clicks, conversions, and field measurements as separate source-defined evidence.

## Rules

Select landing-page candidates from observed traffic/conversion evidence. Create hypotheses only from explicit CTA visibility, message match, form error, trust, mobile obstruction, or field-performance observations. State observation, causal hypothesis, proposed change, expected behavior, primary metric, guardrails, and measurement design separately. Do not claim causality from an observed conversion rate.

The default minimum for displaying a GA4 conversion rate is 100 sessions. The draft experiment template records MDE 10%, alpha 0.05, power 0.80, and 14 days; these are explicit planning defaults, not a computed sample size, and Measurement must validate or replace them before approval.

## Output and validation

Emit schema-valid `cro-hypothesis` artifacts and stable `CRO-*` findings. Hypotheses remain draft until Measurement defines sample-size/test parameters and the director approves execution. No site change or experiment launch occurs.
