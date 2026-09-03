# Deterministic SEO Content Procedure

Runtime: `src/seo_os/procedures/content.py` (`seo-content-strategy`, version `1.0.0`).

## Input contract

Accept approved page inventory, GSC page performance, and GA4 organic landing-page snapshots. Keyword clusters may be passed only as director-approved procedure configuration. Record invalid URLs and invalid dates rather than silently discarding them.

## Rules

Classify each page as retain, refresh, consolidate, redirect, remove-noindex-candidate, or requires-review using explicit status, indexability, duplicate/cannibalization, comparable decline, seasonality, age, conversion, and business-role fields. Add create-new only for an approved unmapped cluster. A decline rule requires a comparable prior value and does not fire when explicitly seasonal. Removal and consolidation remain review candidates, never automatic actions.

Defaults are a 20% comparable-period decline and 730 days since an observed update. Both are configurable and neither overrides a seasonal flag or missing/invalid evidence.

## Output and validation

Emit schema-valid `content-action` artifacts, structured briefs for refresh/create work, stable `CONTENT-*` findings, internal-link dependencies, and post-change QA. Validate intent and SERP format before execution; return to `seo-director`.
