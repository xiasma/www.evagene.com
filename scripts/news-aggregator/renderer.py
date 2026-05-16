"""Render Genetic Current HTML pages from state.json."""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from image_pipeline import resolve_image
from utils import (
    AUDIENCES,
    AUDIENCE_LABELS,
    SITE_NEWS_DIR,
    absolute_url,
    load_state,
    parse_iso,
    story_dir,
    story_url_path,
    utc_now,
)

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
SOURCE_COUNT = 16

AUDIENCE_HEADINGS = {
    "researchers": "Genetics news for researchers",
    "gps": "Genetics news for GPs and primary care",
    "oncologists": "Genetics news for oncologists",
    "genetic-counsellors": "Genetics news for genetic counsellors",
    "educators": "Genetics news for educators",
    "students": "Genetics news for students",
    "genealogists": "Genetics news for genealogists",
    "patients": "Genetics news for patients and families",
}

AUDIENCE_INTROS = {
    "researchers": "Primary research, methods advances, and major preprints — surfaced from peer-reviewed and open-access sources. Updated daily.",
    "gps": "Developments relevant to general practice and primary care — service changes, family-history guidance, and what's shifting in how genetics meets the front line.",
    "oncologists": "Hereditary cancer, somatic genomics, and treatment-relevant findings. New BRCA / Lynch / TP53 evidence, novel targeted therapies, and clinical-trial readouts.",
    "genetic-counsellors": "Implementation, communication, ethics, and family-history practice. For counsellors and genetic nurses keeping up with the wider conversation.",
    "educators": "Teaching-friendly stories you can drop into a lecture, seminar, or course module. Suitable for undergraduate and postgraduate genetics teaching.",
    "students": "Accessible explanations of new research and developments in genetics, written so a learner can pick up the thread.",
    "genealogists": "Ancestry genetics, inheritance patterns, founder effects, consumer testing, and family-history-relevant research.",
    "patients": "Plain-language summaries for patients and families with an interest in genetics. Educational only — not medical advice.",
}


def trending_score(cluster: dict, now: datetime) -> float:
    scores = cluster.get("scores", {})
    newest_iso = scores.get("newest_iso") or cluster.get("run_iso") or cluster.get("run_date", "")
    newest = parse_iso(newest_iso) or now
    days_old = max(0, (now - newest).days)
    importance = scores.get("importance", 0)
    breadth = scores.get("audience_breadth", 0)
    novelty = scores.get("novelty", 0)
    publishers = {s.get("publisher") for s in cluster.get("sources", [])}
    diversity = len(publishers)

    return (
        importance * 1.5
        + breadth * 0.8
        + novelty * 1.0
        + diversity * 2.0
        - days_old * 0.5
    )


def make_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def split_paragraphs(text: str) -> list[str]:
    if not text:
        return []
    paragraphs = re.split(r"\n\s*\n", text.strip())
    return [p.strip() for p in paragraphs if p.strip()]


def format_month_label(month_key: str) -> str:
    try:
        return datetime.strptime(month_key, "%Y-%m").strftime("%B %Y")
    except ValueError:
        return month_key


def resolve_items(state: dict, skip_images: bool) -> list[dict[str, Any]]:
    clusters = state.get("clusters", [])
    takedown_slugs = {t["slug"] for t in state.get("takedowns", [])}
    clusters = [c for c in clusters if c.get("slug") and c.get("slug") not in takedown_slugs]

    out: list[dict] = []
    for cluster in clusters:
        if skip_images:
            image = {
                "src": "/news/images/placeholders/generic.webp",
                "alt": cluster.get("headline", ""),
                "caption": "Illustrative image — not from the source article.",
                "is_placeholder": True,
            }
        else:
            image = resolve_image(cluster)
        url_path = story_url_path(cluster)
        out.append({
            "cluster": cluster,
            "image": image,
            "url": url_path,
            "absolute_url": absolute_url(url_path),
        })
    return out


def render_trending(env, items, audience_counts, common):
    template = env.get_template("trending.html")
    ctx = {
        **common,
        "page_title": "Genetic Current — Trending genetics news",
        "page_description": "Trending genetics and genomics news, summarised daily from trusted public sources for researchers, clinicians, educators, students, and patients.",
        "canonical": "https://evagene.com/news/",
        "breadcrumb": [
            {"label": "Home", "url": "https://evagene.com/"},
            {"label": "Genetic Current", "url": "/news/"},
        ],
        "trending_clusters": items,
        "audience_counts": audience_counts,
        "source_count": SOURCE_COUNT,
    }
    html = template.render(**ctx)
    out = SITE_NEWS_DIR / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"  /news/  ({len(items)} stories)")


def render_audience(env, audience_key, all_items, common):
    items = [it for it in all_items if audience_key in it["cluster"].get("audiences", [])]
    label = AUDIENCE_LABELS[audience_key]
    ctx = {
        **common,
        "audience_key": audience_key,
        "audience_label": label,
        "audience_heading": AUDIENCE_HEADINGS.get(audience_key, f"Genetics news for {label.lower()}"),
        "audience_intro": AUDIENCE_INTROS.get(audience_key, ""),
        "page_title": f"Genetics news for {label.lower()} — Genetic Current",
        "page_description": f"Curated genetics and genomics news for {label.lower()}, summarised daily from trusted public sources.",
        "canonical": f"https://evagene.com/news/{audience_key}/",
        "breadcrumb": [
            {"label": "Home", "url": "https://evagene.com/"},
            {"label": "Genetic Current", "url": "/news/"},
            {"label": label, "url": f"/news/{audience_key}/"},
        ],
        "clusters": items,
    }
    html = env.get_template("audience_index.html").render(**ctx)
    out = SITE_NEWS_DIR / audience_key / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"  /news/{audience_key}/  ({len(items)} stories)")


def render_story(env, item, common):
    cluster = item["cluster"]
    image = item["image"]
    url_path = item["url"]
    canonical = absolute_url(url_path)
    og_image_src = image["src"]
    og_image_url = absolute_url(og_image_src) if og_image_src.startswith("/") else og_image_src
    ctx = {
        **common,
        "cluster": cluster,
        "image": image,
        "summary_paragraphs": split_paragraphs(cluster.get("summary", "")),
        "for_patients_paragraphs": split_paragraphs(cluster.get("for_patients", "") or ""),
        "page_title": cluster.get("headline", ""),
        "page_description": (cluster.get("standfirst") or "")[:160],
        "canonical": canonical,
        "og_title": cluster.get("headline", ""),
        "og_description": cluster.get("standfirst", ""),
        "og_image": og_image_url,
        "og_type": "article",
        "share_url": canonical,
        "share_title": cluster.get("headline", ""),
        "share_text": cluster.get("standfirst", ""),
        "breadcrumb": [
            {"label": "Home", "url": "https://evagene.com/"},
            {"label": "Genetic Current", "url": "/news/"},
            {"label": cluster.get("headline", "")[:60], "url": url_path},
        ],
    }
    html = env.get_template("story.html").render(**ctx)
    out_dir = story_dir(cluster)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(html, encoding="utf-8")


def render_archive(env, items, common):
    by_month: dict[str, list[dict]] = defaultdict(list)
    for it in items:
        run_date = it["cluster"].get("run_date", "")
        if not run_date:
            continue
        by_month[run_date[:7]].append(it)
    months_sorted = sorted(by_month.items(), reverse=True)
    months_formatted = [(format_month_label(m), its) for m, its in months_sorted]
    if items:
        sorted_by_date = sorted(items, key=lambda x: x["cluster"].get("run_date", ""))
        first_date = sorted_by_date[0]["cluster"].get("run_date", "—")
    else:
        first_date = "—"
    ctx = {
        **common,
        "page_title": "Genetic Current archive",
        "page_description": "Every Genetic Current story, organised by month.",
        "canonical": "https://evagene.com/news/archive/",
        "breadcrumb": [
            {"label": "Home", "url": "https://evagene.com/"},
            {"label": "Genetic Current", "url": "/news/"},
            {"label": "Archive", "url": "/news/archive/"},
        ],
        "months": months_formatted,
        "total": len(items),
        "first_date": first_date,
    }
    html = env.get_template("archive.html").render(**ctx)
    out = SITE_NEWS_DIR / "archive" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"  /news/archive/  ({len(items)} total)")


def render_all(state: dict, env: Environment, skip_images: bool = False) -> None:
    now = utc_now()
    items = resolve_items(state, skip_images)
    items.sort(key=lambda it: trending_score(it["cluster"], now), reverse=True)

    audiences_for_nav = [
        {"key": a, "label": AUDIENCE_LABELS[a], "url": f"/news/{a}/"}
        for a in AUDIENCES
    ]
    audience_counts: dict[str, int] = defaultdict(int)
    for it in items:
        for aud in it["cluster"].get("audiences", []):
            audience_counts[aud] += 1

    common_ctx = {
        "audiences": audiences_for_nav,
        "audiences_labels": AUDIENCE_LABELS,
        "now_iso": now.isoformat(),
        "now_human": now.strftime("%d %b %Y %H:%M UTC"),
    }

    render_trending(env, items, audience_counts, common_ctx)
    for aud in AUDIENCES:
        render_audience(env, aud, items, common_ctx)
    for item in items:
        render_story(env, item, common_ctx)
    render_archive(env, items, common_ctx)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Render Genetic Current HTML from state.json")
    parser.add_argument("--skip-images", action="store_true", help="Skip image download / use placeholders for all")
    args = parser.parse_args(argv)

    state = load_state()
    env = make_env()
    cluster_count = len(state.get("clusters", []))
    print(f"Rendering Genetic Current with {cluster_count} clusters…")
    render_all(state, env, skip_images=args.skip_images)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
