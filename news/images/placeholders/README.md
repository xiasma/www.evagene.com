# Placeholder hero illustrations

For stories whose source images aren't legally rehostable (all-rights-reserved, CC BY-ND text where images aren't covered, mixed-licence sources), the renderer substitutes a category illustration from this directory.

## Categories

| Slug | Used for stories tagged |
|---|---|
| `crispr` | crispr, gene-editing, base-editing, prime-editing, cas9 |
| `oncology` | cancer, oncology, brca, lynch, hereditary-cancer |
| `rare-disease` | rare-disease, ultra-rare, orphan-disease |
| `public-health` | public-health, screening, newborn-screening, epidemiology |
| `paediatric` | paediatric, pediatric, neonatal |
| `pharmacogenomics` | pharmacogenomics, drug-response, cpic |
| `ancestry` | ancestry, genealogy, 23andme, haplogroup |
| `inheritance` | mendelian, autosomal-dominant, x-linked, mitochondrial, imprinting |
| `polygenic` | polygenic, complex-trait, gwas, prs |
| `methods` | sequencing, whole-genome, long-read, single-cell |
| `ethics` | ethics, policy, regulation, elsi, gdpr |
| `generic` | fallback when nothing matches |

## Initial set

The workflow runs `bootstrap_placeholders.py` automatically if this directory is empty. That generates a minimal gradient-and-label set so the renderer has something to substitute. They're functional but not beautiful.

## Upgrading to proper imagery

Replace any `<slug>.webp` here with a real image. Keep:
- Same filename and `.webp` format.
- ~1200 × 675 (16:9). The renderer will display them at multiple sizes.
- Quality ~82 for a good size / fidelity trade-off.

Suitable sources for replacements:
- **Unsplash** — free for editorial use, CC0-style licence, attribution appreciated.
- **NHGRI image gallery** — public domain (US gov).
- **CDC Public Health Image Library** — public domain (US gov).
- **Commissioned editorial illustration** — strongest option visually, has a cost.
- **AI-generated under a permissive licence** — fine if you label them as such in image_pipeline.py captions.

For each replacement, update the caption in `image_pipeline.py` if attribution is required.
