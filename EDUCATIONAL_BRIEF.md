# Educational landing-page brief (read this first)

You are writing educational landing pages for **evagene.com**, a static HTML marketing site for Evagene — an academic, research, and educational pedigree modelling platform. The pages you are writing are educational content that will sit alongside the existing 130+ pages.

## Critical regulatory positioning rules

**Evagene is positioned as an academic, research, and educational pedigree modelling platform. It is NOT a medical device, NOT clinical decision support, NOT a diagnostic or screening tool.** Every sentence you write must be consistent with that positioning.

The site is subject to MHRA (UK MDR 2002 as amended) and EU MDCG (MDR 2017/745, Rule 11) which assess intended purpose holistically across a manufacturer's promotional material. Clinical-positioning copy risks classification as Class IIa medical device software.

### Forbidden phrases and replacements

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
| warrants testing / warrants screening | example threshold described in published guideline X |
| recommend (issued by the platform) | illustrate / describe / document |
| consider IHC/MSI / consider EUS/MRI screening (as platform output) | published guideline X notes that [action] may be considered; this software does not make that recommendation |

### Off-limits framings

Never position Evagene as:
- Diagnosing, preventing, monitoring, predicting, treating, or managing disease.
- Determining eligibility for screening, testing, referral, or treatment.
- Replacing, augmenting, or supporting professional clinical judgement in a care pathway.
- Generating outputs for direct delivery to individual patients as medical information.
- Integrating with EHR / EMR / FHIR / HL7 for patient-care workflows. Static file export that a clinician can choose to consume off-platform (e.g. the CanRisk file bridge) is fine; "clinical workflow integration" framing is not.
- Automating triage, screening logic, or any "flag patients who…" behaviour.

These constraints apply EVERYWHERE — body copy, FAQ answers, JSON-LD descriptions, OG/Twitter tags, alt text. A footer disclaimer does NOT cure clinical-positioning copy elsewhere.

### Risk-model labelling rules

For any of the 20 risk models (Claus 1994, Couch 1997, Frank 2002, Evans 2004, Vasen 1999, Umar 2004, Gail 1989, Tyrer/Duffy/Cuzick 2004, BayesMendel BRCAPRO / MMRpro / PancPRO, family-history scoring):
- Frame outputs as illustrative / for research / for teaching, not as clinical outputs.
- **Tyrer-Cuzick** in Evagene is an IBIS-style approximation of the published Tyrer / Duffy / Cuzick 2004 algorithm. Not the official IBIS Breast Cancer Risk Evaluator binary.
- **BOADICEA** is licensed by the University of Cambridge and is NOT bundled in Evagene. Evagene exports a `##CanRisk 2.0` pedigree file that the user uploads at canrisk.org. Say this every time BOADICEA is mentioned.
- Never attach risk-model outputs to named individuals in marketing copy, screenshots, worked examples, or demo videos. Use fictional families, pedigree IDs, or anonymised identifiers.

## JSON-LD schema rules

Never use any `schema.org/Medical*` type — `MedicalWebPage`, `MedicalCondition`, `MedicalEntity`, `MedicalAudience`, `MedicalTest`, `MedicalProcedure`, `Drug`, `Physician`. These are machine-readable clinical-intent signals.

Use instead: `Article`, `TechArticle`, `ScholarlyArticle`, `LearningResource`, `Course`, `EducationalOccupationalProgram`, `CollectionPage`. For diseases / conditions referenced in structured data, use `Thing` or `DefinedTerm` rather than `MedicalCondition`.

## Tone, style, and brand

- **"Evagene"** — capitalised as one word, never "EvAgene" or "EvaGene".
- **Specialist-facing** (clinicians, researchers, educators, students), factual, not hyperbolic. No unqualified superlatives.
- **British English** throughout (counselling, paediatrics, favour, behaviour, organisation, haemoglobin). Exception: direct quotes from sources that use American English.
- **No emojis** in copy or code.
- **Cite specific papers and authors.** When you reference a model, give author and year (e.g., "Bennett et al. 1995"). When you reference a database, link to the canonical URL (e.g., omim.org/entry/603956).
- **Round numbers only** for "X+" claims. "20+", "200+", "1,900+" are fine. "19+", "23+", "14+" are not.

## Required SEO infrastructure on every page

Use D:\dev\wwwevagenecom\pedigree-chart.html as the structural template. Every page MUST include:

1. `<title>` (under 70 chars), `<meta name="description">` (under 160 chars), `<meta name="keywords">` — all keyword-rich.
2. Open Graph tags (`og:title`, `og:description`, `og:type=article`, `og:url`, `og:image=https://evagene.com/og-image.png`, `og:site_name=Evagene`, `og:locale=en_GB`).
3. Twitter Card tags (`twitter:card=summary_large_image`, title, description, image).
4. `<link rel="canonical">` pointing at `https://evagene.com/[slug]` (no `.html` in canonical).
5. Favicon reference.
6. Tailwind CDN + brand colour config (copy from template).
7. JSON-LD: at minimum `Article` and `BreadcrumbList`. Add `FAQPage` if you include a FAQ section. Use `LearningResource` instead of or in addition to `Article` where it fits.
8. Cookie consent banner + opt-in analytics IIFE (copy verbatim from template — bottom of `<body>`).
9. Footer with the four-column structure (logo + tagline, Product, Learn More, copyright + legal links).
10. Breadcrumb `<nav>` under the fixed top nav.
11. Alpha CTA section before the footer.

## Citation requirements

Every page must cite **at least 5 authoritative sources** with stable public URLs. Preferred sources:
- Peer-reviewed papers (cite by author surname et al., year, journal; link to PubMed via PMID where possible)
- NCBI databases: PubMed, Gene, OMIM, ClinVar, dbSNP, gnomAD
- GeneReviews (NIH/NCBI Bookshelf)
- Annual Reviews (especially Annual Review of Genetics, Annual Review of Genomics and Human Genetics, Annual Review of Biochemistry)
- Nature, NEJM, Cell, Science, PNAS, Genome Research, Genome Biology, JAMA
- WHO, NIH, NHGRI, ENCODE, GTEx, UK Biobank
- Standards bodies: HGNC (genenames.org), HPO (hpo.jax.org), GA4GH, ISCN, NSGC

Inline link citations using `<a href="..." rel="noopener">...</a>`. Use the canonical stable URL where possible (PubMed `https://pubmed.ncbi.nlm.nih.gov/PMID/`, OMIM `https://omim.org/entry/NUMBER`, DOI `https://doi.org/...`).

## Voice and depth

- Each page should be **1000–1500 words**, written for a specialist or student reader.
- Lead with the concrete technical or research point, not a marketing hook.
- Name the canonical models / mechanisms / authors. Don't paraphrase a foundational figure name out.
- Proper caveats inline, not in a footnote.
- Cross-link to relevant existing Evagene pages where the link is genuinely useful (don't force it). Existing pages worth knowing about: `pedigree-drawing-tool.html`, `pedigree-chart.html`, `clinical-pedigree-drawing.html`, `mendelian-inheritance-calculator.html`, `hereditary-cancer-risk-assessment.html`, `complex-disease-pedigree-software.html`, `lynch-syndrome-risk-calculator.html`, `germline-mosaicism-calculator.html`, the disease pages (`achondroplasia-pedigree.html` etc.), `phenopackets-pedigree.html`, `iscn-pedigree-symbols.html`, `nsgc-pedigree-notation.html`, `karyogram-viewer.html`.

## Output

Write each page as a separate HTML file at `D:\dev\wwwevagenecom\[slug].html` using the slugs your task specifies. Do not write Markdown.

When done, list the files created and any sources you cited.
