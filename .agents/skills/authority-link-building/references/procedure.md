# Deterministic Authority and Link Procedure

Runtime: `src/seo_os/procedures/authority.py` (`authority-link-building`, version `1.0.0`).

## Input contract

Accept approved Ahrefs backlink/referring-domain or generic backlink evidence. A valid source URL and target URL are required. Canonicalize and deduplicate exact source-target-anchor records while retaining all source snapshot references.

## Rules

Classify reclamation, unlinked mention, broken-link replacement, competitor gap, partner/association, resource-page, expert-contribution, digital-PR, linkable-asset, or other opportunities from explicit fields. Score relevance, audience, editorial quality, real-site plausibility, organic-visibility evidence, geographic and placement relevance on a transparent 1–5 rubric. Flag sitewide patterns, abnormal outbound-link counts, suspected networks/farms, irrelevant directories, paid/sponsored patterns, exact-match manipulation, automated spam, and safety risks. Third-party authority metrics are supporting evidence, not proof of quality.

Defaults flag 20 target URLs from one source domain as sitewide, more than 100 outbound links as abnormal, and a sponsored ratio above 0.50. An unflagged mean qualification of at least 4.0 is qualified; high-risk network, farm, malware, or automated-spam evidence is rejected. All thresholds are configurable and require human review.

## Output and validation

Emit schema-valid `backlink-prospect` artifacts and stable `AUTH-*` findings. Every prospect remains `not-reviewed`; human validation and approval are mandatory. Do not enrich contacts, send outreach, buy links, disavow, or alter any external system.
