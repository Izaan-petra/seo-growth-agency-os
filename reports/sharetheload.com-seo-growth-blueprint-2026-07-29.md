# SEO Growth Blueprint — Initial Public-Data Assessment

**Website:** https://sharetheload.com/  
**Prepared on:** 2026-07-29  
**Assessment type:** URL-only public-data assessment  
**Preferred domain observed:** `https://sharetheload.com/`

## 1. Executive summary

Sharetheload has a technically sound small-site foundation and a clear two-sided proposition: senders can match parcels with verified travelers, while travelers can earn from spare luggage space. The public site has dedicated sender and traveler pages, five relevant guides, valid self-referencing canonicals, one H1 per inspected page, indexable robots directives, structured data, social metadata, a permissive `robots.txt`, and a sitemap containing 16 URLs. HTTP and `www` variants redirect to the HTTPS non-`www` host.

The main constraint is not basic crawlability. It is the gap between a high-trust, cross-border service and the depth of public evidence needed to make users, search engines, and answer engines confident. Safety claims are prominent, but the site lacks a standalone, indexable trust-and-safety hub; its present footer link targets a homepage anchor. It also needs clearer disclosure of the current operating legal entity, jurisdiction, address, payment/escrow provider and coverage, verification provider/process, insurance or liability position, customs responsibilities, dispute path, and country-specific restrictions. This is particularly important because official passenger guidance varies by market: for example, UK government guidance warns passengers not to carry goods for someone else and separately requires declarations for commercial goods in baggage. The service therefore needs jurisdiction-specific, professionally reviewed guidance rather than broad global assurances.

The strongest growth opportunity is a trust-led information architecture built around two commercial hubs—sending and earning—supported by safety, pricing, route, comparison, customs, prohibited-item, and proof content. This can improve qualified discovery without chasing raw informational traffic. Route pages should be created only for corridors where the marketplace has real supply, demand, operational support, and compliant guidance.

**Biggest opportunity:** become the clearest, most transparent source for responsible peer-to-peer parcel delivery, then build corridor pages around verified marketplace liquidity.  
**Biggest risk:** entity, safety, customs, liability, and service-availability details are not yet explicit enough for a trust-sensitive international logistics marketplace.  
**Top three actions:**

1. Publish a comprehensive `/trust-and-safety/` hub and supporting prohibited-items, customs, verification, payment protection, claims, and handoff pages after legal/operations review.
2. Reconcile and disclose the current operating entity and service terms consistently across the site, schema, Google Play, privacy policy, terms, contact page, and external profiles.
3. Install/validate first-party measurement, define app-download and activation events, then improve sender/traveler landing pages and internal linking against real conversion data.

**Recommended strategic direction:** win trust and category understanding first; expand into high-intent route and use-case demand only where first-party marketplace data confirms that Sharetheload can fulfill the promise.

## 2. Scope, methodology and limitations

This SEO Growth Blueprint has been prepared using publicly accessible information, observable website data, live search research and inferred business context. Internal analytics, Google Search Console data, conversion information, historical ranking data and confirmed business priorities were not available. The recommendations represent an initial strategic assessment and should be validated and refined using first-party business and performance data before major implementation or forecasting.

Public research included the live homepage and all 16 URLs declared in the XML sitemap; HTTP/HTTPS and `www` redirect behavior; `robots.txt`; titles, descriptions, canonicals, robots directives, headings, social metadata and structured data in downloaded HTML; the public [Google Play listing](https://play.google.com/store/apps/details?id=com.teamsharetheload); public search-result patterns; selected direct competitors; and official customs/baggage guidance. No login, app workflow, payment, account verification, live delivery, analytics, backlink database, rank tracker, full browser-rendered crawl, lab performance test, or Core Web Vitals dataset was available.

No traffic, rankings, search volume, backlink totals, conversions, revenue, indexed-page counts, forecasts, or AI citations are claimed in this report. “Demand” and “competition” are qualitative judgments based on intent and observed public results, not keyword-tool measurements.

## 3. Analysis confidence

| Area | Conclusion | Confidence status | Notes |
|---|---|---|---|
| Preferred host and crawl controls | HTTPS non-`www` is preferred; HTTP and `www` redirect to it; robots allows crawling; sitemap is present | **Verified** | Direct header and file checks on 2026-07-29 |
| On-page implementation | Inspected sitemap pages have unique titles/descriptions, self-canonicals, index/follow, one H1 and JSON-LD | **Verified** | Based on downloaded server HTML for all 16 sitemap URLs |
| Business model | Two-sided marketplace matching parcel senders with travelers who have spare luggage capacity | **Verified** | Stated across homepage, sender/traveler pages and app listing |
| Primary conversion | Android app install followed by parcel/trip posting | **High-confidence inference** | Dominant CTA points to Google Play; funnel behavior was not tested |
| Geographic focus | Global/cross-border ambition, with an Australian operating footprint visible in Google Play | **High-confidence inference** | Site says worldwide routes; Google Play names an Australian company/address |
| Current legal/operator identity | Must be reconciled and confirmed | **Requires first-party validation** | Public properties refer to Sharetheload International, an Australian entity, and legal provisions involving Hong Kong/Panama |
| Organic visibility and rankings | Unknown | **Requires first-party validation** | Search Console/rank data unavailable |
| Backlink strength | Unknown | **Requires first-party validation** | No backlink platform data supplied |
| Conversion and marketplace liquidity | Unknown | **Requires first-party validation** | No route supply, match rate, activation or transaction data supplied |
| Core Web Vitals | Unknown | **Could not verify** | No reliable field dataset or completed lab test was available |
| App quality/retention | Unknown | **Requires first-party validation** | Public Google Play listing was reviewed; private performance was not |

## 4. Business and website understanding

### Verified findings

- Sharetheload describes itself as a peer-to-peer parcel-delivery marketplace connecting senders with verified travelers already taking a suitable route.
- The sender flow includes parcel posting, route matching, external parcel verification, escrow-supported payment where available, live tracking and delivery confirmation.
- The traveler flow includes identity/profile checks, adding an existing trip, reviewing requests, public handoff, delivery confirmation and payment release.
- The public site repeatedly warns against unidentified or prohibited items and tells users to check airline, customs and local rules.
- The website offers a route/parcel quote interface, but says final pricing and availability are confirmed in the app.
- The public site links only to Google Play. The [Google Play listing](https://play.google.com/store/apps/details?id=com.teamsharetheload) was live when reviewed, identified `SHARETHELOAD INTERNATIONAL PTY LTD` as the developer, and showed that the app shares/collects several data categories. App-install and usage performance are not inferred from this listing.
- The site contains commercial pages for [senders](https://sharetheload.com/send-parcels) and [travelers](https://sharetheload.com/earn-while-traveling), an [About page](https://sharetheload.com/about-us), a [founder message](https://sharetheload.com/founders-message), a contact page, legal policies and five articles.

### Inferences and assumptions

- **High-confidence inference:** the primary business conversion is an app install followed by registration, identity verification, and a first parcel or trip post.
- **High-confidence inference:** the marketplace needs both sender demand and traveler supply on the same corridors; generic site traffic without route liquidity is unlikely to create business value.
- **Medium-confidence inference:** international/air routes are the initial emphasis because the copy repeatedly discusses flights, luggage, customs and routes such as London–Dubai, Sydney–Jakarta and New York–London.
- **Medium-confidence inference:** Australia may now be the primary operating base because Google Play names an Australian private company and address, while the public site presents global coverage.
- **Requires first-party validation:** priority countries/corridors, actual service availability, transaction model, fee structure, payment coverage, insurance/claims handling, customer segments, unit economics and revenue priorities.

### Likely audiences and conversion goals

| Audience | Need | Likely primary conversion | Secondary conversion |
|---|---|---|---|
| International parcel sender | Affordable, trackable delivery on a suitable route | Install app and post parcel | Check route, contact support |
| Frequent traveler | Monetize unused baggage allowance without changing trip | Install app and add journey | Read safety/earning guidance |
| Diaspora families/students | Move gifts, documents or personal items between recurring corridors | Find route and post parcel | Subscribe or contact support |
| Small cross-border seller | Move legitimate merchandise or samples | **Assumption; legal/operational fit must be confirmed** | Review customs guidance |
| Partners | Verification, payment, travel, community or logistics integration | Partnership inquiry | Founder/contact engagement |

Highest-value public page types are sender, traveler, trust/safety, route, pricing/fees, comparison, app-download and proof pages. Blog traffic is valuable only when it assists those journeys.

## 5. Current-state scorecard

These 0–100 scores are directional assessments, not precise measurements.

| Area | Score | Evidence and interpretation |
|---|---:|---|
| Technical SEO | 76 | Strong host redirects, robots, sitemap, canonicals, metadata, headings and schema; CWV, rendered crawl and error coverage remain unverified |
| Site architecture | 58 | Clear sender/traveler hubs and blog, but trust, pricing, routes, customs and core policies are shallow or anchored to the homepage |
| On-page SEO | 72 | Unique, descriptive metadata and aligned H1s; several pages can better address decision-stage questions and differentiated evidence |
| Content quality | 57 | Five coherent guides, but limited breadth, proof, jurisdictional depth and original evidence |
| Topical authority | 43 | Good category starting point; too few supporting clusters for a global logistics/safety topic |
| E-E-A-T and trust | 38 | Founder, contact email and policies exist; operating entity, credentials, providers, liability, claims and verifiable proof need clarity |
| GEO/AEO readiness | 55 | Direct explanatory copy and schema exist; entity facts, cited evidence, expert review and answer-ready safety resources are weak |
| Off-page authority | 30 | Some public company/social/app references were found, but quality and backlink strength were not measured |
| UX and conversion | 60 | Clear dual-value proposition and CTAs; indicative quote does not return a public answer and key objections remain unresolved |
| Measurement readiness | 25 | No public evidence can confirm analytics, app attribution, conversion definitions or reporting |

## 6. Critical findings

| ID | Finding | URL/page type | Evidence | Impact | Recommended fix | Priority |
|---|---|---|---|---|---|---|
| F1 | Trust-and-safety information is not a standalone indexable hub | Homepage/footer | “Trust & Safety” links to `/#safety`; cross-border obligations are dispersed | Weakens trust, answer coverage and internal-link focus | Build a reviewed `/trust-and-safety/` hub with supporting policies | Critical |
| F2 | Current operating entity and jurisdiction are not explicit and consistent enough | About, contact, schema, legal pages, app store | Google Play names an Australian company/address; terms reference Hong Kong and Panama; website schema lacks a visible complete legal identity | Creates user, compliance and entity-understanding ambiguity | Confirm operator, then align legal name, number, address, jurisdiction and support details everywhere | Critical |
| F3 | Broad “global coverage” positioning lacks route availability and country-specific qualification | Homepage and service pages | Site claims worldwide routes but provides illustrative corridors and app-only confirmation | Risks mismatched expectations and thin generic targeting | Publish availability rules and only build route pages for validated corridors | High |
| F4 | Safety content needs authoritative, jurisdiction-specific substantiation | Sender/traveler/blog pages | The site advises checking customs but gives no country guidance or citations; official rules can be restrictive | Safety is both a conversion barrier and a material compliance issue | Commission legally reviewed customs/airline guides with official citations and clear disclaimers | Critical |
| F5 | Limited public proof of product operation | Commercial pages | No visible case studies, delivery stories, aggregate service evidence, named verification/payment partners or claims process | Users and answer engines lack corroboration | Add verifiable process/provider details and consented case studies without inflated claims | High |
| F6 | Measurement and app-funnel performance cannot be assessed | Website/app | Analytics and conversion data unavailable | Prioritization and ROI cannot be refined | Implement/validate event taxonomy and app attribution | High |
| F7 | Commercial architecture is too small for category and route discovery | Sitewide | Only two core service pages and five articles in sitemap | Limits qualified landing-page coverage | Add pricing, safety, route, comparison and use-case layers based on evidence | High |
| F8 | Homepage HTML is much larger than other pages and CWV is unknown | Homepage | Observed HTML response was about 154 KB versus roughly 9–84 KB for other inspected pages | Possible performance/maintenance risk, not a proven CWV failure | Profile templates and assets; test CWV before changing | Medium |

## 7. Technical SEO roadmap

| ID | Issue/status | Evidence | Affected URL/type | Exact fix | Owner | Effort | Priority | Validation |
|---|---|---|---|---|---|---|---|---|
| T1 | Preferred-host behavior is correct | HTTP and HTTPS `www` returned 301 to HTTPS non-`www`; canonical homepage returned 200 | Domain | Maintain; add redirect regression test | Developer | Low | Maintenance | Crawl all host/protocol variants quarterly |
| T2 | Robots and sitemap are healthy | `robots.txt` allows `/` and references sitemap; sitemap lists 16 canonical HTTPS URLs | Sitewide | Maintain automated sitemap generation and truthful `lastmod` | Developer/SEO | Low | Maintenance | Compare sitemap to crawl and CMS releases |
| T3 | Core metadata baseline is strong | All 16 inspected sitemap pages had a title, meta description, self-canonical, index/follow, one H1, OG/Twitter metadata and JSON-LD | Sitewide | Preserve template rules; add automated uniqueness/length checks | Developer/SEO | Low | High | CI crawl and Search Console inspection |
| T4 | No hreflang implementation | Zero hreflang annotations observed | Sitewide | Do not add until genuine localized equivalents exist; if launched, use reciprocal language/region annotations plus `x-default` | SEO/Developer | Medium | Validation required | International targeting audit |
| T5 | Schema needs richer, reconciled entity graph | Organization/WebSite/MobileApplication on home; page-appropriate WebPage, Service, CollectionPage and BlogPosting observed | Sitewide | Use one stable Organization `@id`; add confirmed legal identity, address, support contact, app store URL and verified profiles; add BreadcrumbList to nested pages | Developer/Legal/SEO | Medium | High | Schema validator plus manual content parity check |
| T6 | Standalone safety architecture missing | Footer uses `/#safety` | Sitewide | Create `/trust-and-safety/`; update nav/footer/contextual links; include in sitemap | Content/Legal/Developer | Medium | Critical | Crawl, indexability and user testing |
| T7 | Performance evidence incomplete | Homepage server HTML about 154 KB; CWV not verified | Homepage/templates | Run PageSpeed/Lighthouse and inspect CrUX/Search Console CWV; compress/minify only against measured bottlenecks; audit hero images, fonts and JS | Developer | Medium | Medium | Mobile lab tests and 28-day field data |
| T8 | JavaScript and form outcomes require functional QA | Quote and newsletter forms observed; app and account paths not crawled | Forms/app links | Test no-JS content, validation, success/error states, spam protection and analytics events | Developer/QA | Medium | High | Cross-device test and event debugger |
| T9 | Broken-link/orphan coverage incomplete | Sitemap pages and obvious nav links were inspected, but no full rendered crawl was completed | Sitewide | Run a rendered crawler including assets, JS-generated links and response codes | SEO/Developer | Low | High | Zero broken internal links on priority templates |
| T10 | Old `.html` URL appears in public search | Search surfaced `/about-us.html`, while sitemap/canonical uses `/about-us` | Legacy URLs | Inventory `.html` variants and 301 each to the canonical extensionless URL; remove internal references | Developer | Low | High | Header checks and Search Console indexing report |

Technical caveats: pagination, facets, hreflang, mixed content, mobile usability, JavaScript rendering and Core Web Vitals were either not applicable to the small observed site or could not be fully verified. No claim of a technical failure is made without evidence.

## 8. Architecture and internal linking

### Current structure

The current architecture is shallow: homepage → sender/traveler pages, about/founder/contact, blog index → five posts, and legal pages. This is crawlable and easy to understand, but it does not yet reflect the decision journey of a cross-border marketplace.

### Recommended hierarchy

```text
Home
├── Send Parcels
│   ├── How It Works for Senders
│   ├── Pricing and Fees
│   ├── Routes (only validated corridors)
│   ├── What You Can Send
│   └── Compare Delivery Options
├── Earn While Traveling
│   ├── How It Works for Travelers
│   ├── Earnings and Payouts
│   ├── Traveler Responsibilities
│   └── Available Routes
├── Trust & Safety
│   ├── Verification
│   ├── Payment Protection
│   ├── Safe Handoffs and Tracking
│   ├── Prohibited and Restricted Items
│   ├── Customs and Airline Rules
│   └── Loss, Damage, Disputes and Support
├── Guides
│   ├── Sender guides
│   ├── Traveler guides
│   ├── Route/country guides
│   └── Comparisons
├── Customer Stories / Delivery Evidence
└── Company
    ├── About
    ├── Founder and leadership
    ├── Partners
    ├── Contact
    └── Legal
```

Priority internal links:

- Link every sender/traveler page and relevant article to the trust hub, pricing, prohibited items, customs responsibilities and app CTA.
- Link each route page to both sender and traveler hubs, the relevant country guidance, pricing explanation and safety hub.
- Add breadcrumb navigation and `BreadcrumbList` schema to all nested guides.
- Add “next best action” modules to articles rather than relying only on generic footer links.
- Use descriptive anchors such as “peer-to-peer parcel safety checks” and “traveler customs responsibilities,” avoiding repetitive exact-match stuffing.

## 9. Competitor and SERP analysis

Observed search results for category queries heavily favor product homepages that explain both sender and carrier workflows, show matching/payment mechanics, answer safety objections and offer an immediate app/waitlist action. They also surface broad informational definitions and community discussions about trust and legal risk. This means Sharetheload competes in both product and education SERPs.

| Competitor/type | Why it competes | Observed strengths | Observed weakness/unknown | Opportunity for Sharetheload |
|---|---|---|---|---|
| [SpareLuggage](https://www.spareluggage.com/) | Direct international spare-luggage marketplace | Specific booking journey, capacity/date/rating details, two-mode account | Service maturity and authority not assessed | Outperform with verified safety/legal depth and route proof |
| [PackIt](https://www.itspackit.com/) | Direct sender–traveler app | Clear negotiation mechanics and explicit statement that it is not a shipping company | Trust evidence not assessed | Explain responsibility, escrow, tracking and claims more concretely |
| [Air-Dash](https://www.airdashapp.com/) | International traveler delivery | Clear sender/traveler steps and app availability | Evidence/coverage not assessed | Build stronger entity transparency and cited guidance |
| [Berkat](https://www.berkat.io/) | Crowdshipping through personal networks | Distinct “trusted circles” model, six languages, secured payments | Different matching model | Differentiate verified open marketplace plus route coverage |
| [CarryOn](https://carryonapp.com/) | P2P cross-border shopper/traveler app | Strong category framing and sustainability angle | Claims require independent validation | Avoid unsupported superlatives; win through proof and responsible guidance |
| [Kolivo](https://www.kolivo.net/) | Sender/traveler delivery | Simple benefit-led UX, verification/payment language, testimonials | Testimonial verification unknown | Publish consented, verifiable delivery evidence and richer FAQ |
| [Routag](https://routag.com/) | Crowd delivery platform | Concrete sender/courier flows, wallet and tracking | Broader local/fleet positioning | Own international traveler-safety specialization |
| [ZendZap](https://www.zendzap.com/) | Traveler package marketplace | Route examples, reviews/pricing framing, delivery-code flow | Public claims need validation | Provide transparent pricing methodology without unverified promises |
| Traditional courier/comparison pages | Alternative solution for same sender need | Familiarity, schedules, established policies | Often higher cost/less personal | Publish fair “when P2P is/is not appropriate” comparisons |
| Government/airline guidance | Competes for safety/customs answers | Authoritative and jurisdiction-specific | Not product-oriented | Cite these sources and translate requirements into workflows |

**SERP feasibility:** broad terms such as “international parcel delivery” are likely highly competitive. Category terms like “peer-to-peer parcel delivery” are more relevant but still crowded with product pages. The most feasible business-led path is corridor + use case + safety intent, gated by actual route liquidity and expert-reviewed guidance. This is a qualitative assessment; rankings and volumes are unknown.

## 10. Keyword and topic strategy

| Cluster | Intent | Stage | Existing/new page | Page type | Business value | Relative demand | Relative competition | Conversion potential | Differentiation angle | Priority |
|---|---|---|---|---|---|---|---|---|---|---|
| Peer-to-peer parcel delivery | Informational/commercial | Awareness–consideration | Existing homepage + guide | Category hub | High | Medium | Medium | Medium | Verification, escrow, tracking and responsibilities | High |
| Send parcel with traveler | Transactional | Decision | Existing `/send-parcels` | Commercial | High | Medium | Medium | High | Transparent route matching and safety | Critical |
| Earn money while traveling | Commercial | Consideration–decision | Existing `/earn-while-traveling` | Supply acquisition | High | Medium | High | High | Existing trips only; responsible acceptance | Critical |
| Parcel delivery pricing/fees | Commercial | Decision | New | Pricing explainer | High | Medium | Medium | High | Explain variables, fees and payment release without fake quotes | Critical |
| Traveler verification and safety | Commercial/informational | Consideration | New | Trust hub | High | Medium | Medium | High | Provider/process proof and limits | Critical |
| What can I carry/send | Informational/transactional | Consideration | New | Policy hub | High | Medium | Medium | High | Searchable item rules plus jurisdiction caveats | Critical |
| Customs and baggage rules | Informational | Consideration | New | Expert-reviewed guide hub | High | High | High | Medium | Official citations, country-level updates | High |
| Route-specific delivery | Transactional/localized | Decision | New only after validation | Route landing page | High | Route-dependent | Medium–High | High | Live availability and corridor-specific proof | High/validation required |
| P2P vs courier | Comparison | Consideration | New | Comparison guide | Medium–High | Medium | Medium | Medium–High | Honest fit/no-fit criteria | High |
| Documents/gifts/electronics | Use-case | Consideration | New after policy validation | Use-case guide | Medium–High | Medium | Medium | Medium–High | Exact restrictions, packaging and declaration steps | Medium–High |
| Lost/damaged parcel and disputes | Support/commercial | Consideration | New | Claims/support page | High | Low–Medium | Low–Medium | High | Clear responsibility and escalation path | High |
| Brand + reviews/safety/legit | Branded/reputation | Decision | New proof/FAQ | Trust/reputation | High | Unknown | Low–Medium | High | Verifiable legal/entity and customer evidence | Critical |

## 11. Existing content improvements

| URL | Problem | Evidence | Recommended change | Business value | Priority |
|---|---|---|---|---|---|
| `/` | Carries too many roles and claims; trust details remain high-level | Long homepage, broad “global coverage,” anchor-only safety | Keep concise category framing; link to dedicated trust, pricing, routes and proof pages; qualify coverage | High | High |
| `/send-parcels` | Good process but decision objections remain unresolved | No fees, claims, provider or detailed customs explanation | Add eligibility, exact next steps, fees model, delivery fit/no-fit, claims summary, proof and contextual links | High | Critical |
| `/earn-while-traveling` | Responsible language exists but legal burden is still generic | Tells traveler to check rules without country-specific workflow | Add traveler responsibility checklist, inspection evidence, declarations, payout/fee explanation and route eligibility | High | Critical |
| `/about-us` | Mission-led but thin on corporate facts and leadership credentials | About 336 approximate visible words; no complete visible operator profile | Add current legal entity, registration, operating location, leadership bios, governance and verified partner disclosures | High | Critical |
| `/founders-message` | Human story helps, but claims such as “movement” lack evidence | Founder identified as Tarek Mohamed; no linked profile/evidence | Add dated bio, relevant experience, current role, LinkedIn and substantiated milestones | Medium–High | High |
| `/contact-us` | Minimal public support detail | Contact copy and email/form, limited escalation/service hours | Publish service hours, response expectations, company address, urgent safety/dispute route and partnership path | High | High |
| `/blogs` | Small undifferentiated archive | Five posts, no clear topic taxonomy beyond labels | Build sender, traveler, safety/customs, route and comparison collections; add editorial policy | Medium | Medium |
| `/blogs/how-to-prepare-a-parcel-for-peer-to-peer-delivery` | Says a “sealed” parcel builds confidence, while other pages say travelers should not carry sealed items | Contradictory wording across public content | Clarify tamper-evident packaging after traveler inspection; define documented inspection/sealing workflow | High | Critical |
| Safety/advantage guides | Good direct answers but limited external authority | No official citations or named reviewer | Add jurisdiction-scoped citations, expert review, updated dates and responsibility tables | High | High |
| Legal pages | Long and difficult to navigate; operator alignment requires review | Terms are approximately 11,800 visible words and reference multiple jurisdictions | Add summary/navigation, effective date/version history and lawyer-reviewed operator consistency; do not simplify away legal meaning | High | Critical |

Content consolidation: keep the “What Is” and “Advantages” articles separate only if Search Console shows distinct intent. Otherwise consider one definitive category guide plus a focused “P2P vs courier” comparison to reduce overlap. Do not redirect until query/page data validates cannibalization.

## 12. New content roadmap

| Proposed title | Recommended URL | Page type | Intent | Unique value required | CTA | Priority |
|---|---|---|---|---|---|---|
| Trust & Safety at Sharetheload | `/trust-and-safety/` | Trust hub | Commercial/informational | Verified controls, limits, responsibilities and escalation map | Review safety, then install app | Critical |
| Sharetheload Pricing, Fees and Payouts | `/pricing-and-fees/` | Commercial | Decision | Transparent fee variables and examples labeled illustrative | Check route in app | Critical |
| Prohibited and Restricted Items | `/prohibited-and-restricted-items/` | Policy/support | Transactional | Searchable rules, reason, route caveats, update owner | Check an item/contact support | Critical |
| Customs and Airline Rules for Traveler Delivery | `/customs-and-airline-rules/` | Expert guide hub | Informational/commercial | Official sources, jurisdiction matrix and professional review | Check route eligibility | Critical |
| Peer-to-Peer Delivery vs Traditional Couriers | `/peer-to-peer-vs-courier-delivery/` | Comparison | Commercial | Honest suitability matrix, no unsupported cost/speed claims | Compare route options | High |
| How Verification Works | `/trust-and-safety/verification/` | Trust detail | Commercial | Named provider or precisely described process and limitations | Complete verification | High |
| Lost, Damaged or Delayed Parcels | `/trust-and-safety/claims-and-disputes/` | Support/trust | Support/commercial | Clear liability, evidence, timing and escalation | Start support request | High |
| Routes | `/routes/` | Directory | Transactional | Only active, supportable routes; freshness and availability | Find a route | High after validation |
| Customer Delivery Stories | `/customer-stories/` | Proof hub | Branded/commercial | Consented, verifiable journeys and outcomes | Post parcel/add trip | High |

### Full brief A — Trust & Safety at Sharetheload

- **Target audience:** senders, travelers, recipients, partners and evaluators.
- **Search intent:** understand whether and how the platform manages identity, parcels, payment, tracking, handoffs and disputes.
- **Primary topic:** Sharetheload safety and platform safeguards.
- **Supporting topics/entities:** identity verification, parcel inspection, escrow/payment protection, GPS, prohibited items, customs, airline rules, ratings, privacy, claims, law enforcement and support.
- **Required sections:** what the platform does; what it cannot guarantee; sender/traveler responsibilities; step-by-step inspection and handoff; payment availability; tracking/privacy; prohibited items; jurisdiction rules; incident response; linked policies; last reviewed date.
- **Questions to answer:** Who verifies users? What documents are checked? Is every payment held? Who is liable? Is delivery insured? What happens after loss/damage? Can a traveler open/inspect the parcel? Which routes are unavailable?
- **Unique evidence required:** confirmed provider/process details, internal policy excerpts, support SLAs, versioned controls, and legally approved language.
- **Internal links in:** homepage, sender, traveler, quote, all guides, footer. **Out:** verification, pricing, prohibited items, customs, claims, privacy and terms.
- **CTA:** “Review the safety checklist, then continue in the app.”
- **Structured-data opportunity:** WebPage + FAQPage only for visible, non-duplicative FAQs; Organization references via stable `@id`.
- **Business value:** reduces the central conversion objection and strengthens entity/answer clarity.
- **Priority/time horizon:** Critical / first 30 days.

### Full brief B — Pricing, Fees and Payouts

- **Target audience:** senders comparing options and travelers evaluating earnings.
- **Search intent:** commercial/transactional.
- **Primary topic:** how Sharetheload prices deliveries and pays travelers.
- **Supporting topics/entities:** route, size, weight, urgency, traveler quote, platform fee, currency, escrow availability, refunds, payout timing and taxes.
- **Required sections:** pricing components; sender charges; traveler earnings; platform fees; currency/payment coverage; illustrative scenarios explicitly marked non-binding; refund/cancellation; payout timing; taxes; route CTA.
- **Questions:** Who sets the price? What does Sharetheload charge? When is money held/released? Are there minimums? What changes the quote? What happens after cancellation?
- **Unique evidence required:** finance/product-approved fee schedule and actual regional availability.
- **Internal links in:** homepage quote, sender/traveler pages, route pages, comparison content. **Out:** terms, payment protection, refunds/claims and app.
- **CTA:** “Enter your actual route and parcel details in the app.”
- **Structured-data opportunity:** Service; avoid AggregateOffer/price markup unless public prices are real and eligible.
- **Business value:** resolves high-intent friction and prevents misleading price expectations.
- **Priority/time horizon:** Critical / first 30–60 days.

### Full brief C — Prohibited and Restricted Items

- **Target audience:** senders and travelers before posting/accepting.
- **Search intent:** informational with immediate transactional consequence.
- **Primary topic:** what cannot be sent through Sharetheload.
- **Supporting topics/entities:** dangerous goods, weapons, drugs, counterfeit goods, perishables, liquids, batteries, medicine, valuables, documents, customs and airline restrictions.
- **Required sections:** absolute platform prohibitions; items requiring route-specific checks; sender disclosure; traveler inspection; packaging after inspection; declaration responsibility; reporting; policy enforcement; jurisdiction disclaimer.
- **Questions:** Can I send electronics, batteries, medicine, food, documents or cash? Can a parcel be sealed? Who checks contents? What if the description is false?
- **Unique evidence required:** operations/legal-approved rules, version history and links to official authorities such as [IATA passenger baggage rules](https://www.iata.org/en/programs/ops-infra/baggage/passenger-baggage-rules/).
- **Internal links in:** every posting/acceptance guide and app pre-handoff help. **Out:** trust, customs, packaging, claims and support.
- **CTA:** “Check your item before posting; ask support if uncertain.”
- **Structured-data opportunity:** WebPage + FAQPage where eligible.
- **Business value:** prevents unsafe demand, reduces support risk and builds trust.
- **Priority/time horizon:** Critical / first 30 days.

### Full brief D — Customs and Airline Rules

- **Target audience:** international senders and travelers.
- **Search intent:** research and risk validation.
- **Primary topic:** responsibilities when carrying someone else’s goods across borders.
- **Supporting topics/entities:** customs declarations, commercial goods in baggage, personal allowances, duties/taxes, airline baggage, dangerous goods, origin/destination/transit rules.
- **Required sections:** strong global disclaimer; decision tree by parcel purpose; origin/destination/transit checks; declaration documents; duties/taxes; airline approval; examples; links to country guides; review date and reviewer.
- **Questions:** Must goods be declared? Who pays duty? Do personal allowances apply? Can a traveler carry goods for someone else? Which official source controls?
- **Unique evidence required:** qualified legal/customs review and direct official citations. UK guidance, for example, says commercial goods carried in baggage must be declared and separately warns travelers never to carry anything into the UK for someone else ([HMRC commercial-goods guidance](https://www.gov.uk/guidance/bringing-commercial-goods-into-great-britainin-your-baggage), [UK customs information](https://www.gov.uk/government/publications/travelling-to-the-uk/travelling-to-the-uk)). The page must not generalize UK rules to other jurisdictions.
- **Internal links in:** sender, traveler, route, item and safety pages. **Out:** official authorities, terms, support and prohibited items.
- **CTA:** “Confirm route eligibility before accepting a delivery.”
- **Structured-data opportunity:** Article/WebPage with named qualified reviewer; no claim that schema confers authority.
- **Business value:** addresses the highest-risk objection and filters unsuitable transactions.
- **Priority/time horizon:** Critical / start within 30 days; expand over 6–12 months.

### Route-page gate

Before publishing any `/routes/{origin}-to-{destination}/` page, require: active sender and traveler evidence; confirmed legal/operational support; current customs guidance; a real availability mechanism; unique corridor content; support ownership; and a review/update SLA. Do not mass-generate city pairs or imply inventory that does not exist.

## 13. GEO, AEO and AI-search plan

1. **Entity clarity:** publish a single canonical statement of current legal/operator identity, headquarters, registration, service regions, founder/leadership and support contacts. Mirror it in Organization schema and verified profiles.
2. **Direct answers:** begin each core page with a 40–70-word plain-language answer, followed by who it is for, conditions and limitations.
3. **Responsibility tables:** use visible sender/platform/traveler/recipient responsibility matrices. These are easier to quote accurately than broad marketing prose.
4. **Cited safety content:** cite primary government, customs, airline and IATA sources, with jurisdiction and review dates. Separate platform policy from law.
5. **Named expertise:** add author/reviewer bios for legal, customs, safety and privacy content. Organization-only authorship is insufficient for high-risk guidance.
6. **Original evidence:** publish anonymized, consented delivery case studies; route/process research; support learnings; and methodology. Never fabricate usage or success claims.
7. **Schema:** maintain the stable Organization entity; link the Android app; add breadcrumbs; use FAQ schema only where visible content qualifies; ensure schema matches page text.
8. **External corroboration:** align Google Play, LinkedIn and other public profiles with the current entity and product description. Pursue legitimate coverage from travel, diaspora, logistics and safety publications.
9. **Answer monitoring:** manually test representative questions in major search/AI products and record citations/accuracy, but do not claim “AI visibility” from schema alone.

## 14. E-E-A-T and authority plan

### Trust gaps

- Confirm and expose the current operating legal entity, registration number, registered/business address and governing service entity.
- Explain the relationship, if any, among the public brand, Australian developer company, prior Hong Kong references and Panama intellectual-property language.
- Name payment/escrow and verification partners only when contracts and regional availability support the claim.
- Publish insurance/liability and loss/damage treatment in plain language with links to binding terms.
- Resolve the content contradiction between “keep the parcel sealed” and “never carry sealed or unidentified items” by documenting an inspection-then-seal process.
- Reconcile support emails shown on the website and Google Play, and decide which is authoritative.

### Authority roadmap

- Publish expert-reviewed country/corridor guides with direct government sources.
- Create a transparent annual “Peer-to-Peer Delivery Safety and Operations Report” using only validated aggregate data and a disclosed methodology.
- Develop university/international-student, diaspora-organization, travel-community and responsible-logistics partnerships.
- Offer founder/product experts for commentary on crowdshipping, customs literacy and unused-capacity logistics—without overstating environmental benefits.
- Seek relevant product directories and app listings; keep name, address, description and links consistent.
- Build case studies around specific journeys, documented challenges and safeguards, not vague testimonials.
- Monitor unlinked brand mentions and request attribution where editorially appropriate.
- Reject paid-link schemes, PBNs, fake reviews, mass guest posts and manipulative exchanges.

## 15. CRO and UX observations

| URL/page type | Friction | Why it matters | Recommendation | Validation |
|---|---|---|---|---|
| Homepage | One page serves two audiences and multiple stages | Sender and traveler intent can compete | Persistently segment “Send” and “Earn” paths; tailor proof and CTA labels | Path click-through and activated-user rate |
| Quote module | It requests route/parcel inputs but does not show a guaranteed public quote | Users may expect an estimate or availability result | State before submission exactly what output they will receive; pass entered data into app/deep link if possible | Completion, app-open and abandonment events |
| App CTA | Android-only public link observed | iOS users may reach a dead end | Explicitly label platform availability; add iOS only if live; provide waitlist/support alternative | CTA by device and store completion |
| Sender page | Fees, route supply and claims remain unclear | High-intent objections delay install | Add concise pricing, availability, safety and claims summaries above the final CTA | Scroll depth, CTA rate and parcel-post activation |
| Traveler page | Earnings language lacks fee/payout examples and legal decision support | Can attract poorly qualified supply | Add payout mechanics, responsibility checklist and route-demand qualification | Verified-trip activation and request acceptance quality |
| Trust claims | “Verified,” “escrow” and “global” are broad | Users need evidence and limitations | Link each claim to a detailed, current explainer | Trust-page engagement and assisted activation |
| Contact/support | Escalation and response expectations are not prominent | Logistics incidents are time-sensitive | Publish support categories, hours/SLA and emergency/safety flow | Resolution time and repeat contacts |
| Blog | Generic article CTA | Weak intent continuity | Use sender/traveler/route-specific CTAs and related-answer modules | Assisted conversions by article |

## 16. Prioritized opportunity backlog

Formula: `(Business Value + SEO Impact + Traffic Potential + Conversion Potential + Strategic Fit + Confidence + Urgency) − (Effort + Competition)`. Scores are comparative, not predictive.

| ID | Recommendation | Classification | BV | SEO | Traffic | Conv. | Fit | Conf. | Urgency | Effort | Comp. | Score | Priority | Time horizon |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| P1 | Reconcile operating entity and legal/trust disclosures | Critical fix | 5 | 5 | 3 | 5 | 5 | 4 | 5 | 3 | 2 | 27 | Critical | 0–30 days |
| P2 | Launch reviewed Trust & Safety hub | Strategic project | 5 | 5 | 4 | 5 | 5 | 5 | 5 | 3 | 3 | 28 | Critical | 0–30 days |
| P3 | Resolve sealed-parcel content contradiction | Quick win | 5 | 3 | 2 | 4 | 5 | 5 | 5 | 1 | 1 | 27 | Critical | Immediate |
| P4 | Publish prohibited/restricted-items policy | Critical fix | 5 | 4 | 4 | 5 | 5 | 5 | 5 | 3 | 2 | 28 | Critical | 0–30 days |
| P5 | Validate analytics and app-funnel events | Validation required | 5 | 3 | 2 | 5 | 5 | 3 | 5 | 3 | 1 | 24 | High | 0–30 days |
| P6 | Publish pricing/fees/payout explainer | Growth opportunity | 5 | 4 | 4 | 5 | 5 | 4 | 4 | 3 | 3 | 25 | High | 30–60 days |
| P7 | Add entity facts and expert profiles to site/schema | Growth opportunity | 5 | 4 | 3 | 4 | 5 | 4 | 4 | 2 | 2 | 25 | High | 30–60 days |
| P8 | Redirect legacy `.html` URL variants | Quick win | 3 | 4 | 2 | 2 | 4 | 4 | 4 | 1 | 1 | 20 | Medium | 0–30 days |
| P9 | Build customs/airline guidance program | Strategic project | 5 | 5 | 5 | 4 | 5 | 4 | 4 | 5 | 4 | 23 | High | 30–180 days |
| P10 | Improve sender/traveler commercial pages | Growth opportunity | 5 | 4 | 4 | 5 | 5 | 4 | 4 | 3 | 3 | 25 | High | 30–60 days |
| P11 | Create verified case-study/proof hub | Strategic project | 5 | 4 | 3 | 5 | 5 | 3 | 3 | 4 | 3 | 21 | High | 60–90 days |
| P12 | Launch only validated corridor pages | Strategic project | 5 | 5 | 5 | 5 | 5 | 2 | 3 | 5 | 5 | 20 | Medium | 60–365 days |
| P13 | Add breadcrumb UI/schema to nested content | Quick win | 3 | 3 | 2 | 2 | 4 | 5 | 3 | 2 | 2 | 18 | Medium | 30–60 days |
| P14 | Establish digital PR/partner program | Strategic project | 4 | 4 | 4 | 3 | 4 | 3 | 2 | 4 | 4 | 16 | Medium | 90–365 days |
| P15 | Measure and optimize CWV | Validation required | 4 | 4 | 3 | 3 | 4 | 2 | 3 | 3 | 2 | 18 | Medium | 0–60 days |

**Highest-priority action:** reconcile the legal/operator identity and convert it into a complete trust layer.  
**Strongest quick win:** correct the sealed-versus-inspected parcel contradiction across the site.  
**Most important strategic project:** standalone trust/safety plus jurisdiction-specific customs guidance.  
**Highest-risk unresolved issue:** whether service operations and marketing claims are fully aligned with each route’s customs, baggage and legal requirements.  
**Most important validation-required item:** marketplace liquidity and conversion performance by corridor.

Top five immediate actions are P1–P5. Top ten 90-day priorities are P1–P11 excluding P12 and including P13. Defer mass route generation, multilingual expansion and broad informational publishing until product-market, route and conversion evidence supports them.

## 17. First 30 days

1. Confirm legal entity, service jurisdictions, physical/contact information, payment/verification providers, insurance/liability, support SLAs and route eligibility with legal and operations owners.
2. Correct conflicting parcel-sealing language immediately; align the website, app and support scripts.
3. Publish the trust-and-safety and prohibited-items hubs, or at minimum approved interim pages with clear limitations.
4. Validate GA4, Search Console and Bing Webmaster Tools; define app-store/deep-link attribution and funnel events.
5. Crawl all canonical and legacy URLs, redirect `.html` variants, test forms and record a technical baseline.
6. Add explicit Android availability, current entity facts and support paths to high-intent pages.

## 18. Days 31–60

1. Publish pricing/fees/payout and claims/disputes explainers.
2. Expand sender/traveler pages with objections, responsibilities, eligibility, proof and contextual links.
3. Add breadcrumb navigation/schema and topic-based guide navigation.
4. Commission qualified review for the customs/airline hub and the first priority-country guides.
5. Run mobile lab testing and collect field CWV data; address only measured bottlenecks.
6. Align Google Play, LinkedIn, schema and all legal/support identity fields.

## 19. Days 61–90

1. Publish the first legally reviewed country/corridor guidance for routes validated by product data.
2. Launch consented delivery stories with documented safeguards and outcomes.
3. Test route-to-app deep links and segmented sender/traveler messaging.
4. Refresh/merge overlapping category articles only after Search Console query evidence.
5. Begin targeted partnerships and expert outreach in priority corridors.
6. Review performance by activated parcels/trips—not pageviews alone—and re-score the backlog.

## 20. Six-to-twelve-month direction

- Build a route directory from verified marketplace liquidity, not programmatic permutations.
- Expand country-specific customs and item guidance with accountable expert review and update schedules.
- Develop original data assets on route availability, safe handoffs and marketplace behavior using privacy-safe aggregate data.
- Add localized content only for markets with operational support, native review and demand; implement hreflang at that point.
- Build reputable travel, diaspora, university, commerce and logistics partnerships.
- Integrate web-to-app attribution, lifecycle content and retention reporting so SEO is optimized for completed safe deliveries.
- Review brand search, external mentions and answer-engine accuracy quarterly; correct misinformation at the source.

## 21. KPI and measurement framework

| KPI | Why it matters | Data source | Baseline needed | Review frequency |
|---|---|---|---|---|
| Valid indexed canonical pages | Confirms discoverability | Search Console/Bing | Yes | Monthly |
| Non-branded clicks by intent cluster | Measures qualified discovery | Search Console | Yes | Monthly |
| Route-page impressions and qualified app opens | Tests corridor fit | Search Console + deep-link analytics | Yes | Monthly |
| Organic app-store/deep-link clicks | Connects web discovery to product | GA4/app attribution | Yes | Weekly/monthly |
| Registration and verification completion | Measures activation quality | Product analytics | Yes | Weekly |
| First parcel posted / first trip added | Core marketplace activation | Product analytics | Yes | Weekly |
| Match and successful-delivery rate by route | Measures liquidity and outcome | Marketplace data | Yes | Weekly/monthly |
| Organic assisted safe completions | Business outcome without revenue invention | GA4/product/CRM | Yes | Monthly |
| Safety/support contacts by topic | Finds content and process gaps | Help desk | Yes | Monthly |
| Claims/disputes and resolution time | Trust and operational health | Operations/help desk | Yes | Monthly |
| Core Web Vitals pass rate | User/technical quality | Search Console/CrUX | Yes | Monthly |
| Branded vs non-branded visibility | Separates awareness from category growth | Search Console/rank tracker | Yes | Monthly |
| Referring-domain quality and earned mentions | Authority growth | Backlink/PR monitoring | Yes | Quarterly |
| Accurate AI/search citations on tracked questions | GEO/AEO visibility and accuracy | Manual monitoring with saved evidence | Yes | Monthly |

Every KPI needs a documented definition, owner, consent/privacy review, and segmentation by sender/traveler, country/corridor, device and acquisition source where legally appropriate.

## 22. Next-phase validation requirements

The next phase should use:

- Google Search Console and Bing Webmaster Tools performance/index reports.
- GA4 and consent configuration, including form and app-click events.
- App analytics, store-console acquisition data and deep-link attribution.
- Current keyword rankings from a transparent tracking set.
- Backlink data and earned-media inventory.
- Conversion, match, successful-delivery, claim and lead-quality data.
- Historical organic and app-acquisition performance.
- Confirmed target markets, priority corridors and customer segments.
- Revenue priorities, fee model and unit economics (kept internal where appropriate).
- Development, legal, support and content capacity.
- Sales/support interview themes and common objections.
- Current legal entity records, licenses/registrations, provider agreements, insurance/liability and jurisdiction review.
- Provider/coverage details for identity verification, payments/escrow, tracking and dispute handling.
- A full rendered crawl, log-file review, mobile usability test and Core Web Vitals field data.

## 23. Evidence register and review status

### Primary/first-party public sources

- [Sharetheload homepage](https://sharetheload.com/)
- [Sender page](https://sharetheload.com/send-parcels)
- [Traveler page](https://sharetheload.com/earn-while-traveling)
- [About](https://sharetheload.com/about-us), [founder message](https://sharetheload.com/founders-message), [blog](https://sharetheload.com/blogs), [privacy policy](https://sharetheload.com/privacy-policy), and [terms](https://sharetheload.com/terms-and-conditions)
- [robots.txt](https://sharetheload.com/robots.txt) and [XML sitemap](https://sharetheload.com/sitemap.xml)
- [Sharetheload on Google Play](https://play.google.com/store/apps/details?id=com.teamsharetheload)
- [Australian Business Register: SHARETHELOAD INTERNATIONAL PTY LTD](https://abr.business.gov.au/ABN/View?id=52686144552)

### External market and official guidance reviewed

- Direct/product alternatives: [SpareLuggage](https://www.spareluggage.com/), [PackIt](https://www.itspackit.com/), [Air-Dash](https://www.airdashapp.com/), [Berkat](https://www.berkat.io/), [CarryOn](https://carryonapp.com/), [Kolivo](https://www.kolivo.net/), [Routag](https://routag.com/) and [ZendZap](https://www.zendzap.com/).
- [IATA passenger baggage rules](https://www.iata.org/en/programs/ops-infra/baggage/passenger-baggage-rules/).
- [HMRC: bringing commercial goods into Great Britain in baggage](https://www.gov.uk/guidance/bringing-commercial-goods-into-great-britainin-your-baggage).
- [UK customs information for travelers](https://www.gov.uk/government/publications/travelling-to-the-uk/travelling-to-the-uk).

External competitor statements were treated as observations of positioning and page format, not independently verified performance claims.

## 24. Final QA statement

Senior QA review completed against the project checklist:

- Website and exact priority URLs inspected: **Yes**.
- Preferred host, robots, sitemap, canonicals, metadata and structured data reviewed: **Yes**.
- Business competitors separated from general alternatives/official sources: **Yes**.
- Facts, inferences, assumptions and validation needs separated: **Yes**.
- Invented traffic, rankings, volumes, backlinks, conversions, revenue, forecasts or AI citations: **None included**.
- Search intent, SERP format, competition and business value considered: **Yes, qualitatively**.
- Technical, content, GEO/AEO, authority, CRO and measurement included: **Yes**.
- High-priority recommendations include evidence, implementation direction, impact, owner/dependencies, validation, metrics and timing: **Yes**, across findings, roadmaps, briefs, scoring and KPI sections.
- Manipulative authority tactics and guarantees rejected: **Yes**.

Major limitations remain the absence of first-party performance data, app/account access, a complete rendered crawl, backlink/rank datasets, Core Web Vitals evidence and confirmed legal/operational inputs. All high-risk legal, customs, safety, liability and insurance content must be reviewed by qualified professionals before publication.
