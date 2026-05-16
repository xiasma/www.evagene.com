"""Image handling for Genetic Current stories.

For sources whose images are reusable (public domain, OGL, CC BY, press-release
with editorial permission), download, optimise to WebP, and rehost. For
everything else (all-rights-reserved, CC BY-ND text where images aren't covered,
mixed), substitute a category-illustration placeholder from the library.
"""
from __future__ import annotations

import io
from typing import Optional

import requests
from PIL import Image

from utils import REUSABLE_LICENCES, SITE_NEWS_DIR

USER_AGENT = "EvagaeneNewsBot/1.0 (+https://evagene.com)"
DOWNLOAD_TIMEOUT = 10
MIN_BYTES = 2000
MAX_WIDTH_HERO = 1200
WEBP_QUALITY = 82

# Tag → placeholder category. First match wins.
PLACEHOLDER_TAG_MAP: list[tuple[str, list[str]]] = [
    ("crispr", ["crispr", "gene-editing", "base-editing", "prime-editing", "cas9", "casgevy", "exa-cel"]),
    ("oncology", ["cancer", "oncology", "tumour", "tumor", "leukaemia", "leukemia", "lymphoma", "carcinoma", "brca", "lynch", "hereditary-cancer"]),
    ("rare-disease", ["rare-disease", "ultra-rare", "orphan-disease", "rare-genetic"]),
    ("public-health", ["public-health", "screening", "newborn-screening", "epidemiology", "horizon-scan", "population-screening"]),
    ("paediatric", ["paediatric", "pediatric", "neonatal", "child", "infant"]),
    ("pharmacogenomics", ["pharmacogenomics", "pharmacogenetics", "drug-response", "cpic", "precision-prescribing"]),
    ("ancestry", ["ancestry", "genealogy", "23andme", "haplogroup", "consumer-genetics"]),
    ("inheritance", ["mendelian", "autosomal-dominant", "autosomal-recessive", "x-linked", "mitochondrial", "imprinting", "uniparental-disomy"]),
    ("polygenic", ["polygenic", "complex-trait", "gwas", "prs", "polygenic-risk", "multifactorial"]),
    ("methods", ["sequencing", "whole-genome", "whole-exome", "long-read", "single-cell", "ngs", "wgs", "wes"]),
    ("ethics", ["ethics", "policy", "regulation", "elsi", "gdpr", "consent", "data-protection"]),
]

LICENCE_CAPTION = {
    "public_domain": "Image: {publisher} — public-domain release.",
    "ogl": "Image: {publisher} — UK Open Government Licence.",
    "cc_by": "Image: {publisher} — used under CC BY.",
    "press_release": "Image: {publisher} — used with editorial permission of the press release.",
}


def pick_placeholder_category(tags: list[str]) -> str:
    tagset = {t.lower() for t in tags}
    for category, keywords in PLACEHOLDER_TAG_MAP:
        if tagset & set(keywords):
            return category
    return "generic"


def _fetch_bytes(url: str) -> Optional[bytes]:
    try:
        response = requests.get(
            url,
            timeout=DOWNLOAD_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
            stream=False,
        )
    except Exception:
        return None
    if response.status_code != 200:
        return None
    content = response.content
    if len(content) < MIN_BYTES:
        return None
    return content


def _optimise(raw: bytes, max_width: int) -> Optional[bytes]:
    try:
        img = Image.open(io.BytesIO(raw))
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="WEBP", quality=WEBP_QUALITY, method=6)
        return buf.getvalue()
    except Exception:
        return None


def resolve_image(cluster: dict) -> dict:
    """
    Decide image for a cluster. Side effect: writes the file to disk if downloaded.
    Returns: {src, alt, caption, is_placeholder}
    """
    sources = cluster.get("sources", [])
    primary = next((s for s in sources if s.get("is_primary")), None) or (sources[0] if sources else None)

    if primary:
        licence = primary.get("image_licence_class", "all_rights")
        image_url = primary.get("image_url")
        if image_url and licence in REUSABLE_LICENCES:
            raw = _fetch_bytes(image_url)
            if raw:
                optimised = _optimise(raw, MAX_WIDTH_HERO)
                if optimised:
                    year, month, _ = cluster["run_date"].split("-")
                    out_dir = SITE_NEWS_DIR / "images" / year / month / cluster["slug"]
                    out_dir.mkdir(parents=True, exist_ok=True)
                    (out_dir / "hero.webp").write_bytes(optimised)
                    caption_tpl = LICENCE_CAPTION.get(licence, "Image: {publisher}.")
                    return {
                        "src": f"/news/images/{year}/{month}/{cluster['slug']}/hero.webp",
                        "alt": primary.get("image_alt") or cluster.get("headline", ""),
                        "caption": caption_tpl.format(publisher=primary.get("publisher", "source")),
                        "is_placeholder": False,
                    }

    category = pick_placeholder_category(cluster.get("tags", []))
    return {
        "src": f"/news/images/placeholders/{category}.webp",
        "alt": f"Illustration for {category.replace('-', ' ')} story",
        "caption": "Illustrative image — not from the source article.",
        "is_placeholder": True,
    }
