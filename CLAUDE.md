# CLAUDE.md — Evagene marketing site

This file is loaded into every conversation. Keep it tight; update when the workflow changes.

---

## What this repo is

Static HTML marketing site for **Evagene** — an academic, research, and educational pedigree modelling platform (see *Regulatory positioning* section below). Deployed to `evagene.com` (GitHub Pages via the `CNAME` file). ~125 pages. No build step; Tailwind via CDN.

Authoritative product docs live in a sibling repo at `../evagene/docs/` — particularly:
- `docs/guides/risk_models.md` — every risk calculator, parameters, examples, citations
- `docs/guides/diseases_catalogue.md` and `docs/guides/diseases/*.md` — disease data
- `docs/architecture.md` — module-level overview

**Always verify feature claims against `../evagene` before writing them into marketing copy.**

---

## Regulatory positioning — not a medical device

**This is the single most important rule in this file. Read it before writing any copy.**

Evagene is positioned as an **academic, research, and educational pedigree modelling platform**. It is **not** a medical device, not clinical decision support software, and not a diagnostic or screening tool. Every page — body copy, meta tags, OG/Twitter cards, JSON-LD, alt text, competitor comparisons, `llms.txt`, `llms-full.txt`, release notes — must be consistent with that positioning.

**Why this matters.** MHRA (UK MDR 2002 as amended) and EU MDCG (MDR 2017/745, Rule 11) assess *intended purpose* holistically across a manufacturer's entire body of promotional material, not just the formal intended-use statement. A footer disclaimer does not cure clinical positioning spread across 125 pages; MDCG 2019-11 is explicit on this. Clinical-positioning copy risks classification as Class IIa medical device software, with enforcement consequences including forced takedown, fines, and director liability under UK MDR s.55. The fix is repositioning, not disclaiming.

**The existing site contains legacy clinical-positioning copy.** Treat it as in-flight repositioning work, not a template to emulate. When copying structure from an existing page (meta tags, JSON-LD, cookie banner, footer), rewrite the body copy to the canonical positioning below.

### Canonical intended-use statement

Use this wording; paraphrases must not weaken the substance:

> Evagene is an academic, research, and educational pedigree modelling platform. It supports structured family-history documentation, teaching, and exploratory use of published risk models. Evagene is not intended to diagnose, prevent, monitor, predict, treat, or manage disease; determine eligibility for screening, testing, referral, or treatment; or replace professional clinical judgement. Outputs are illustrative and for educational / research purposes only.

A short-form version should appear on every page (above or within the footer). The long-form belongs on the homepage, every risk-model page, every disease page, and in the T&Cs.

### Forbidden phrases and their replacements

| Never write | Use instead |
|---|---|
| clinical-grade | research- and education-grade / teaching-grade |
| precision medicine | research and education |
| AI-powered clinical interpretation | AI-assisted draft summaries for educational / research review |
| clinical decision support | research and teaching tool |
| screening recommendation(s) | discussion prompts and literature-linked considerations |
| clinically actionable | illustrative threshold from published literature; not a recommendation |
| identify patients who warrant referral / warrants referral | illustrate how published referral criteria may be represented |
| patient-facing risk report(s) | plain-language educational summaries, not medical advice |
| no medical degree required | for learners, students, and researchers |
| warrants testing / warrants screening | example threshold described in published guideline X |
| recommend (issued by the platform) | illustrate / describe / document |
| consider IHC/MSI / consider EUS/MRI screening (as platform output) | published guideline X notes that [action] may be considered; this software does not make that recommendation |

Grep for each of these before shipping any page or release.

### Off-limits framings

Never position Evagene as:

- Diagnosing, preventing, monitoring, predicting, treating, or managing disease.
- Determining eligibility for screening, testing, referral, or treatment.
- Replacing, augmenting, or supporting professional clinical judgement in a care pathway.
- Generating outputs for direct delivery to individual patients as medical information.
- Integrating with EHR / EMR / FHIR / HL7 for patient-care workflows. Static file export that a clinician can *choose* to consume off-platform (e.g. the CanRisk file bridge) is fine; "clinical workflow integration" framing is not.
- Automating triage, screening logic, or any "flag patients who…" behaviour.

### Risk-model labelling

The existing Tyrer-Cuzick and BOADICEA caveats are preserved and extended to **every** mention of any of the 20 risk models (Claus 1994, Couch 1997, Frank 2002, Evans 2004, Vasen 1999, Umar 2004, Gail 1989, Tyrer/Duffy/Cuzick 2004, BayesMendel BRCAPRO / MMRpro / PancPRO, family-history scoring):

- Frame outputs as **illustrative / for research / for teaching**, not as clinical outputs.
- Where a clinical-grade computation exists off-platform (BOADICEA at canrisk.org, Tyrer-Cuzick against the official IBIS binary), route there explicitly and emphasise the architectural separation. The CanRisk file-export bridge is *positive evidence* of non-clinical intent — emphasise it, do not minimise it.
- Never attach risk-model outputs to named individuals in marketing copy, screenshots, worked examples, or demo videos. Use fictional families, pedigree IDs, or anonymised identifiers.

### JSON-LD and schema.org

Never use `MedicalWebPage`, `MedicalCondition`, `MedicalEntity`, `MedicalAudience`, `MedicalTest`, `MedicalProcedure`, `Drug`, `Physician`, or any `schema.org/Medical*` type — these are machine-readable clinical-intent signals. Use `Article`, `TechArticle`, `CollectionPage`, `ScholarlyArticle`, `EducationalOccupationalProgram`, `LearningResource`, or `Course` instead. For disease references in structured data, use `Thing` or `DefinedTerm`, not `MedicalCondition`.

### Competitor and comparison pages

Comparison-matrix rows must not implicitly claim clinical parity with device-positioned competitors. If a competitor markets FDA-cleared clinical decision support or CE-/UKCA-marked diagnostic workflow and we tick the same row, we inherit the classification. Where the competitor claims a clinical capability that Evagene does not replicate, say so plainly — e.g. "Competitor X markets clinical-workflow integration; Evagene is positioned as a research and education tool" — rather than ticking the row.

### Patient-facing pages

Any page addressed to patients or families (`for-patients.html`, `for-families.html`, genealogy / consumer pages) must frame outputs as educational summaries, not medical information. Do not include worked examples that look like clinical reports. Do not suggest actions a patient should take based on the output. Patient-facing individualised risk output is the single highest-risk feature surface — treat with extreme care, and prefer fictional / anonymised examples.

### When in doubt

Escalate to the user. It is always cheaper to ask than to ship a clinical-positioning sentence that later needs purging from 40 pages, `llms-full.txt`, the sitemap, and cached search snippets.

---

## Tone, style, and brand rules

- **"Evagene"** — capitalised as one word, never "EvAgene" or "EvaGene". Correct everywhere including meta descriptions.
- **Factual, specialist-facing (clinicians, researchers, educators, students), not hyperbolic.** No unqualified superlatives ("the best", "revolutionary"). Specific, verifiable claims only.
- **Never claim** regulatory clearance, device registration, CE marking, UKCA marking, FDA clearance, or equivalence to any registered or cleared medical-device software. See *Regulatory positioning* section.
- **Never position** Evagene as replacing, augmenting, or supporting professional clinical judgement. See *Regulatory positioning* section.
- **No emojis** in copy or code unless the user explicitly asks.
- **Exclusions** — these two caveats must appear wherever the feature is mentioned:
  - **Tyrer-Cuzick** is an *IBIS-style approximation* of the published Tyrer / Duffy / Cuzick 2004 algorithm. Not the official IBIS Breast Cancer Risk Evaluator binary (whose full coefficients are not public). Label every mention.
  - **BOADICEA is not bundled.** Licensed by the University of Cambridge. Evagene exports a `##CanRisk 2.0` pedigree file that the clinician uploads at canrisk.org. Say this every time BOADICEA is mentioned.

---

## Rounded-numbers rule

Any `[number]+` claim must be a round number. "19+" reads as 20 — use `20` or `20+` instead. Round hundreds (200+, 220+) and round fives at the tens place (50+, 55+) are acceptable. Awkward numbers (19+, 23+, 14+) are not.

Canonical counts (keep consistent across every page, llms.txt, llms-full.txt, sitemap-related metadata):

| Claim | Current value | Source |
|---|---|---|
| Risk models + CanRisk bridge | **20** (exact) + CanRisk bridge | 7 single-gene-adjacent + 1 polygenic engine + 3 BayesMendel + 9 family-history scoring |
| Disease catalogue | **230+** | `ls ../evagene/docs/guides/diseases/*.md \| wc -l` currently returns 233 |
| Complex / polygenic / oligogenic conditions | **20+** | Subset with empirical recurrence tables (22 confirmed + major depression = 23) |
| Help-catalogue guides | **1,900+** | 1,924 individual guides across 6 catalogues (diseases 233, clinical tests 713, treatments 729, markers / genes 150, allergies 53, traits 46); external refs LOINC, NCBI Gene, OMIM, ClinVar, RxNorm, BNF, DrugBank. Browse at `https://evagene.net/help/#browse` |
| Disease guides (subset of above) | **230+** | 233 `.md` files in `../evagene/docs/guides/diseases/` |
| Role-specific workflow guides | **8** | One per persona |
| Allergies | **50+** · Traits: **50+** | Catalogues in app |
| Research-paper citations | **4** · Institutions: **10+** | `research-citations.html` |

Update this table when any count changes materially.

---

## Required elements on every new page

Copy from an existing recent page (`research-citations.html`, `for-reproductive-medicine.html`, or any `release-*.html`) rather than authoring from scratch. Required:

1. **`<title>`**, **`<meta name="description">`**, **`<meta name="keywords">`** — specific, keyword-rich, under 160 chars for description.
2. **Open Graph** tags (`og:title`, `og:description`, `og:type`, `og:url`, `og:image`, `og:site_name`, `og:locale=en_GB`).
3. **Twitter Card** tags (`twitter:card=summary_large_image`, title, description, image).
4. **`<link rel="canonical">`** pointing at the clean URL (no `.html` in the canonical).
5. **Favicon** reference.
6. **Tailwind CDN + config** — match existing brand colour palette and Inter font.
7. **JSON-LD** — at minimum an `Article`/`CollectionPage`/`TechArticle` and a `BreadcrumbList`. FAQ pages also need `FAQPage`. **Never use `Medical*` schema types** — see *Regulatory positioning* section.
8. **Cookie consent banner + opt-in analytics loader** — identical pattern across the site. Google Analytics, Microsoft Clarity, and EngageBay fire only after consent. Copy the `cookie-banner` div and the IIFE at the bottom of `for-reproductive-medicine.html` verbatim.
9. **Footer** with the standard four columns (logo, Product, Learn More / Inheritance, Legal).
10. **Breadcrumb `<nav>`** under the fixed top nav.
11. **Alpha CTA section** before the footer.

No page should ship without (8), (9), (10).

---

## When you ship a new page, update these six places

1. **`sitemap.xml`** — add a `<url>` entry with appropriate `lastmod`, `changefreq`, `priority` (0.6–0.9 depending on importance).
2. **`llms.txt`** — add to the relevant section (Topic Guides, Persona Pages, Inheritance-Model Landing Pages, Release Notes, etc.).
3. **`llms-full.txt`** — only if the page introduces a new capability that belongs in the full LLM index.
4. **Cross-links** — at minimum from one existing pillar page (hereditary-cancer-risk-assessment, mendelian-inheritance-calculator, or the decision matrix on for-clinical-geneticists).
5. **Footer links on related pages** — if the page is in a group (e.g. the four inheritance landing pages link to each other via their footers).
6. **`changelog.html`** — add an entry if the page represents a user-facing release.

---

## robots.txt

Located at `/robots.txt`. Allows all search engines and AI crawlers by design. When a major AI crawler appears, add it to the allowlist (current: GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-SearchTool, anthropic-ai, PerplexityBot, GoogleOther, Google-Extended, Applebot-Extended, cohere-ai, Meta-ExternalAgent, Amazonbot, CCBot, Ai2Bot, and many others).

The only `Disallow:` is `/terms`. Do not add more without a clear reason.

Sitemap reference at the bottom must point at `https://evagene.com/sitemap.xml`.

---

## sitemap.xml

Organised by section with HTML-style comments as dividers. Keep sections in order:
- Homepage
- Pillar landing pages (priority 0.9)
- Compare and Alternatives hubs (0.8)
- Direct competitor vs-Evagene pages (0.7–0.8)
- Specialised comparison pages
- Germline mosaicism + flagship clinical pages
- Cross-competitor pages
- Alternatives-to pages
- Cancer risk calculators
- Mendelian / inheritance calculator hubs
- Pedigree drawing / notation / tutorial
- Platform / integration
- Genealogy / consumer
- Specialised clinical
- Best-of roundups
- Persona pages
- Country-specific
- Authority & trust (research-citations, changelog)
- Risk-engine expansion releases
- Inheritance-model landing pages
- Legal
- LLMs metadata

`lastmod` dates should be honest (the date the page actually changed). Bulk-updating all `lastmod` to today is a red flag to crawlers and a waste.

---

## llms.txt and llms-full.txt

- **`llms.txt`** — concise index for LLM consumption. One-liner per section entry. Update when a new page, persona, or capability ships.
- **`llms-full.txt`** — complete prose description of the product. Update when a major capability changes (e.g. a new risk model family). Keep the headings stable so diffs are reviewable.

Both files are referenced from `sitemap.xml`.

When adding a new model or feature:
- Add a bullet to the "Core Features" section of `llms.txt`.
- Rewrite the relevant paragraph in `llms-full.txt` — don't append; integrate.
- If the capability has its own landing page, cross-link from the right section in `llms.txt`.

---

## Competitor / comparison pages

Honest comparative advertising is protected in the UK under **Trade Marks Act 1994 s.10(6)** and the **Business Protection from Misleading Marketing Regulations 2008**. Misleading claims are not. Stay on the legal side.

### Ground rules

1. **Every claim about a competitor must be sourced from their public product pages or documentation.** Don't invent pricing, customer counts, or feature claims. If a claim is second-hand, mark it so.
2. **Date the comparison.** State "as of [Month Year]" on every page. The competitor's current pages supersede our article.
3. **Where the competitor is stronger, say so.** Readers (and judges) punish asymmetric hit pieces. This also builds trust with evaluators who have already seen the competitor.
4. **Feature matrices must be symmetric.** Same rows, same cell types. If a row has a tick for one product and a dash for the other, that is a real finding — don't hide rows that go the wrong way.
5. **"—" (dash) means "not publicly documented", not "absent".** Enterprise products often keep capabilities behind sales. State this near every matrix.
6. **Include a plain-English short version ("Short version." paragraph)** before the matrix. Decision-makers read that and skip the grid.

### Review cadence

- **Quarterly**: spot-check each `*-vs-evagene.html` page against the competitor's current public site. Update the "as of [Month Year]" date and any changed claims.
- **Whenever Evagene ships a feature that affects a comparison row**: update every vs-X page that mentions that row. Check `canrisk-vs-evagene.html`, `famgenix-vs-evagene.html`, `phenotips-vs-evagene.html`, `progeny-vs-evagene.html`, `trakgene-vs-evagene.html` as a minimum set.
- **Whenever a competitor announces a new feature that affects us** (e.g. Phenotips ships AI interpretation): update the matrix, update the FAQ answers, update the "Short version."

### Files to audit in this sweep

Direct clinical competitors: `phenotips-vs-evagene.html`, `progeny-vs-evagene.html`, `trakgene-vs-evagene.html`, `famgenix-vs-evagene.html`, `canrisk-vs-evagene.html`, `pedigreetool-vs-evagene.html`, `quickped-vs-evagene.html`, `genopro-vs-evagene.html`, `progeny-cloud-vs-evagene.html`, `f-tree-vs-evagene.html`, `conceptviz-vs-evagene.html`, `genodraw-vs-evagene.html`, `perseus-vs-evagene.html`.

Generic diagram tools: `smartdraw-pedigree-vs-evagene.html`, `creately-pedigree-vs-evagene.html`, `visual-paradigm-pedigree-vs-evagene.html`, `edraw-pedigree-vs-evagene.html`, `cloudairy-vs-evagene.html`.

Cross-competitor: `phenotips-vs-progeny.html`, `trakgene-vs-phenotips.html`, `famgenix-vs-phenotips.html`, `famgenix-vs-progeny.html`, `boadicea-vs-brcapro.html`.

"Alternatives-to" pages: `alternatives-to-*.html` (8 pages). These should name three or four genuine competitors *including Evagene*, not redirect all traffic to Evagene.

---

## When Evagene ships a new feature / release

Per-release checklist:

1. **Write a release page** — `release-YYYY-MM-DD-short-slug.html`. Cite canonical papers where applicable. Explicit boundaries section ("What Evagene does not claim").
2. **Add to `changelog.html`** — most-recent entry first.
3. **Update the homepage** — `index.html` risk-analysis section, features cards, meta descriptions, OG/Twitter cards, JSON-LD `featureList`, and any stale FAQ answers.
4. **Update `llms.txt`** — Core Features bullets + Release Notes section.
5. **Update `llms-full.txt`** — rewrite (don't append) the relevant section.
6. **Update `sitemap.xml`** — register the release page + any new landing pages.
7. **Update the pillar pages** — `hereditary-cancer-risk-assessment.html`, `mendelian-inheritance-calculator.html` — if the feature touches their scope.
8. **Update the decision matrix** at `for-clinical-geneticists.html#decision-matrix` — if the feature is a new risk model or indication.
9. **Sweep persona pages** — add a "What's new · [Month Year]" callout before the FAQ on the relevant `for-*.html` pages. Keep each callout 3 bullets max with outbound links.
10. **Sweep competitor pages** — per the review cadence above.
11. **Update canonical counts** in the table at the top of this file if any changed.

---

## Cookie consent + analytics — strict opt-in

The banner pattern is identical across every page. Never inline Google Analytics / Clarity / EngageBay into `<head>` — the existing IIFE at the bottom of each page ensures nothing fires until the user clicks Accept. If you edit a page and remove this IIFE you will be tracking users without consent. Don't.

Consent state is stored in `localStorage` under the key `evagene-cookie-consent` with value `'accepted'` or `'rejected'`. `loadAnalytics()` is called only when state is `'accepted'`.

---

## Content voice — quick reminders

- **Specialists read the first paragraph; decision-makers read the first sentence.** Lead with the concrete technical or research point, not a marketing hook.
- **Name the models**, cite the papers. Claus 1994, Couch 1997, Frank 2002, Evans 2004, Vasen 1999, Umar 2004, Gail 1989, Tyrer/Duffy/Cuzick 2004, NICE CG164/NG101, Carter 1961, Falconer 1965. These names carry weight; don't paraphrase.
- **Use "BayesMendel"** for BRCAPRO/MMRpro/PancPRO — the statistical heritage is part of the claim.
- **British English** throughout (counselling, paediatrics, favour, behaviour, organisation). Exception: direct quotes from sources that use American English.
- **Proper caveats inline**, not in a footnote. Tyrer-Cuzick approximation label belongs next to the model name, not at the bottom of the page.

---

## Don't

- Don't bulk-update `lastmod` dates without a real change.
- Don't add new `Disallow:` rules to `robots.txt` without a specific reason.
- Don't use emojis.
- Don't claim regulatory clearance, device registration, CE/UKCA marking, or FDA clearance.
- Don't write "clinical-grade", "precision medicine", "clinical decision support", "AI-powered clinical interpretation", "clinically actionable", "screening recommendation", "warrants referral", "patient-facing risk report", or any similar clinical-intent framing — see *Regulatory positioning* section for replacements.
- Don't tick competitor-matrix rows that imply clinical parity with device-positioned competitors.
- Don't use `MedicalWebPage`, `MedicalCondition`, `MedicalEntity`, `MedicalAudience`, `MedicalTest`, `MedicalProcedure`, `Drug`, `Physician`, or any `schema.org/Medical*` type in JSON-LD.
- Don't frame EHR / FHIR / HL7 / EMR as clinical-workflow integration. The CanRisk off-platform file-export pattern is the template.
- Don't attach risk-model outputs to named individuals in screenshots, worked examples, or demo videos.
- Don't invent numbers for competitors.
- Don't use awkward "X+" figures — round or exact only.
- Don't commit unless the user has explicitly asked.
- Don't force-push, amend published commits, or skip commit hooks.
- Don't delete the cookie-banner IIFE from any page.
