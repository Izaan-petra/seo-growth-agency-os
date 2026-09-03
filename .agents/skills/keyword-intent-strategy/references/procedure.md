# Deterministic Keyword and Intent Procedure

Runtime: `src/seo_os/procedures/keyword.py` (`keyword-intent-strategy`, version `1.0.0`).

## Input contract

Accept approved GSC query/page, Ahrefs keyword/ranking, or generic query evidence. At least one usable query is required. Brand terms, market, language, clustering threshold, and CTR threshold are explicit configuration, never guessed.

## Rules

1. Normalize Unicode, case, punctuation, whitespace, and URL noise while retaining the original query.
2. Label brand as branded, non-branded, or ambiguous when no brand vocabulary is supplied.
3. Apply deterministic multi-label token rules for intent.
4. Cluster by configured lexical overlap or shared observed URL using stable union ordering.
5. Mark cannibalization possible for multiple URLs and confirmed only when each persists in at least two supplied periods.
6. Map clusters to exactly one of existing-page-fit, refresh-existing, consolidate, create-new, or unresolved.
7. Preserve first-party demand separately from directional third-party volume and never forecast traffic.

Defaults are lexical Jaccard overlap of 0.50 and an observed low-CTR review boundary of 0.03 for positions greater than 4 through 20. These are configurable planning rules, not search-engine thresholds. Confirmed cannibalization requires each competing URL in at least two supplied periods.

## Output and validation

Emit schema-valid `keyword-cluster` artifacts and stable `KEYWORD-*` findings. Content and technical specialists consume mappings or dependencies; `seo-director` resolves final action.
