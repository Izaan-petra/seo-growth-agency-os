# Deterministic Technical SEO Procedure

Runtime: `src/seo_os/procedures/technical.py` (`technical-seo`, version `1.0.0`).

## Input contract

Accept only Project Intake-approved immutable snapshots whose IDs are explicitly listed in the director brief. Supported inputs are generic crawl/page evidence, CrUX field performance, PSI lab performance, and GSC search performance. A usable input from at least one supported dataset is required. Blocking datasets are skipped and disclosed; malformed, unapproved, cross-project, or out-of-scope snapshots fail closed.

## Rules

1. Canonicalize URL identity without altering the evidence snapshot.
2. Classify HTTP errors, redirect chains/loops, robots/noindex, sitemap contradictions, canonical mismatch, soft-404 evidence, orphan status, crawl depth, and crawl-trap patterns from explicit fields only.
3. Analyze URL/template patterns and retain exact affected URLs.
4. Classify CrUX p75 field metrics independently from PSI lab diagnostics. Good/needs-improvement/poor boundaries are LCP 2,500/4,000 ms, INP 200/500 ms, and CLS 0.1/0.25.
5. Never infer Google-selected canonicals, index totals, rendering, or field performance from unsupported evidence.

Default excessive-depth threshold is greater than 4 clicks and is configurable. Core Web Vitals thresholds are fixed to the maintained Google baseline; other classifications require explicit source fields rather than a hidden score.

## Output and validation

Emit schema-valid `technical-issue` artifacts and `specialist-finding` records with stable `TECH-*` IDs, evidence snapshot references, observed time, classification, recommendation, confidence, and recrawl/inspection validation. Return to `seo-director`; perform no remediation.
