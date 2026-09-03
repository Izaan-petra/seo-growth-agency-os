# Deterministic Competitor and SERP Procedure

Runtime: `src/seo_os/procedures/serp.py` (`competitor-serp-analysis`, version `1.0.0`).

## Input contract

Require an approved generic SERP snapshot. Every usable result row must contain query, locale, language, device, location, timestamp, search engine, position, URL, result type, and a SERP-feature list. Reject unusable samples and report invalid rows.

## Rules

1. Preserve the complete sample configuration and timestamp.
2. Group by normalized query; never merge unlike locale/device/location samples silently.
3. Calculate result-type, feature, domain-frequency, and query-overlap counts directly from the sample.
4. Call a domain recurring only when it reaches the configured query-count threshold.
5. Distinguish declared business competitors from organic-only recurring domains.
6. Mark undersampled or mixed-intent query groups and lower confidence. Do not estimate market share or traffic.

Defaults are 3 observed results per query and recurrence across 2 distinct queries. Both are brief-level configuration; the result records the actual values.

## Output and validation

Emit stable `SERP-*` specialist findings plus the inspectable SERP snapshot, frequencies, overlap map, invalid-row count, and thresholds. Re-sample like-for-like before later-cycle decisions. Return to `seo-director`.
