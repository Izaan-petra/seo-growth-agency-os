# SEO Director Routing Matrix

This is the deterministic control plane for common engagement types. Select the smallest sufficient bundle. Apply `specialist-contract.md` to every active specialist.

## Skill availability

Active deterministic specialists in Phase 3 Batch 3:

- `technical-seo`
- `competitor-serp-analysis`
- `keyword-intent-strategy`
- `seo-content-strategy`
- `geo-aeo`
- `authority-link-building`
- `seo-cro`
- `seo-measurement`
- `seo-growth-blueprint` for assembly only

Reserved names, not executable in Batch 3:

- `ecommerce-seo`
- `seo-implementation-qa`

Do not route to a reserved skill until its `SKILL.md` exists and repository validation recognizes it. Until then, use the active specialists for work inside their existing scope and label uncovered ecommerce or implementation-QA needs as later-batch dependencies.

## Matrix

| Engagement type | Required specialists | Optional specialists | Dependencies | Required evidence | Minimum viable evidence | Expected output | Blueprint required | Implementation QA required |
|---|---|---|---|---|---|---|---|---|
| Full SEO Audit | technical-seo, competitor-serp-analysis, keyword-intent-strategy, seo-content-strategy, seo-measurement | geo-aeo, authority-link-building, seo-cro, ecommerce-seo (reserved) | competitor-serp-analysis before final keyword map; keyword map before content briefs; measurement before final plan | Completed intake, crawl, GSC and GA4 preferred | Public site, robots, sitemaps and representative SERPs | Integrated audit and director execution plan | Yes | No |
| Technical Audit | technical-seo, seo-measurement | ecommerce-seo (reserved) | URL inventory before issue classification | Crawl, GSC, PSI/CrUX preferred | Live HTTP, robots and sitemap checks | Technical workstream result | No | No |
| SEO Growth Strategy | technical-seo, competitor-serp-analysis, keyword-intent-strategy, seo-content-strategy, seo-measurement | geo-aeo, authority-link-building, seo-cro, ecommerce-seo (reserved) | SERP before keyword; keyword before content; measurement before planning | First-party performance and crawl preferred | Public site and SERP evidence | Integrated growth strategy and execution plan | Yes | No |
| Keyword Research | competitor-serp-analysis, keyword-intent-strategy | seo-content-strategy, seo-measurement, ecommerce-seo (reserved) | Representative SERP sampling before final clustering | GSC and third-party keyword evidence preferred | Public SERPs and site inventory | Keyword clusters and page map | No | No |
| Content Strategy | competitor-serp-analysis, keyword-intent-strategy, seo-content-strategy | technical-seo, geo-aeo, seo-cro, seo-measurement, ecommerce-seo (reserved) | Keyword map before briefs; technical constraints before remove/redirect actions | Content inventory and performance evidence preferred | Public content inventory and SERPs | Content actions and briefs | No | No |
| Competitor Analysis | competitor-serp-analysis | keyword-intent-strategy, authority-link-building, geo-aeo | Query sample before overlap conclusions | Confirmed business competitors and third-party evidence preferred | Representative public SERPs | Competitor and SERP result | No | No |
| Link-Building Campaign | authority-link-building, competitor-serp-analysis | keyword-intent-strategy, seo-content-strategy, geo-aeo, seo-measurement | Target-page and asset mapping before prospect preparation | Backlink/link-gap exports preferred | Public mentions and competitor evidence | Human-approval-ready authority plan | No | No |
| GEO/AEO Audit | geo-aeo, technical-seo, seo-content-strategy | authority-link-building, seo-measurement | Technical eligibility before answer-readiness conclusions | Site, schema and corroboration evidence | Public site and external sources | GEO/AEO workstream result | No | No |
| Ecommerce SEO Audit | technical-seo, seo-content-strategy, seo-measurement | keyword-intent-strategy, competitor-serp-analysis, seo-cro, geo-aeo, authority-link-building, ecommerce-seo (reserved) | Catalog/feed evidence before ecommerce conclusions | Catalog, crawl, GSC/GA4 and feed evidence preferred | Public catalog and storefront; reserved skill dependency disclosed | Partial active-specialist audit until ecommerce-seo exists | Yes | No |
| SEO CRO Review | seo-cro, seo-measurement | keyword-intent-strategy, seo-content-strategy, technical-seo, ecommerce-seo (reserved) | Tracking validation before impact claims | GA4 landing and conversion evidence preferred | Public landing-page heuristic evidence | CRO hypothesis backlog | No | No |
| SEO Performance Review | seo-measurement | technical-seo, keyword-intent-strategy, seo-content-strategy, authority-link-building, ecommerce-seo (reserved) | Comparable baseline before causal diagnosis | GSC, GA4 and implementation annotations preferred | One suitable first-party performance source | Performance review and evidence gaps | No | No |
| Migration Review | technical-seo, seo-measurement | keyword-intent-strategy, seo-content-strategy, ecommerce-seo (reserved), seo-implementation-qa (reserved) | Before snapshot and URL mapping before launch; reserved QA after launch | Source/destination inventory and redirect map | Source and destination URL inventories | Migration plan; post-launch QA remains reserved | No | Yes, when reserved skill exists |
| Recovery Investigation | technical-seo, seo-measurement | competitor-serp-analysis, keyword-intent-strategy, seo-content-strategy, ecommerce-seo (reserved), seo-implementation-qa (reserved) | Timeline and baseline before causal diagnosis | GSC/GA4, implementation history and crawl preferred | Verifiable change timeline plus one suitable evidence source | Recovery diagnosis and execution plan | Yes | Yes after changes, when reserved skill exists |

## Validation rules

- Every required or optional active specialist must exist under `.agents/skills/`.
- Reserved names must be explicitly declared above and must not be described as executable.
- `seo-growth-blueprint` is never a domain specialist; invoke it only where Blueprint required is `Yes`.
- An unavailable preferred source lowers confidence. It blocks the bundle only when the minimum viable evidence cannot support the requested conclusion.
- Implementation QA is a post-change gate and must not be simulated by the director or blueprint while its reserved skill is unavailable.
- When compatible Phase 3 snapshots exist, include their explicit approved IDs in each specialist brief and require the specialist's versioned procedure output.
- A procedure failure, skipped blocking input, degraded-mode result, or schema-validation failure returns to the director as an evidence/decision gate; it never authorizes another collection method.
