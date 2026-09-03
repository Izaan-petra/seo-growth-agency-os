# Deterministic GEO/AEO Procedure

Runtime: `src/seo_os/procedures/geo.py` (`geo-aeo`, version `1.0.0`).

## Input contract

Require approved page-level generic evidence containing a valid URL and explicit observable readiness fields. Missing checks are `not-observed`, never failures or passes.

## Rules

Check entity clarity, organization consistency, attributable authorship/review, source quality, original evidence, direct answers, question coverage, structured-data/content alignment, external corroboration, and technical snippet eligibility. The transparent internal percentage is passed observable checks divided by observable checks. It is not a score from Google or an AI engine.

There is no pass threshold for the overall percentage. Each observable Boolean check stands on its own; unobserved fields remain unknown.

## Output and validation

Emit stable `GEO-*` findings and page-readiness artifacts that keep entity, content/evidence, structured-data, and corroboration dependencies explicit. Never claim AI Overview presence, answer-engine citation, ranking, or traffic from readiness. Return to `seo-director`.
