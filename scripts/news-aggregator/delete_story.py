"""Takedown CLI for Genetic Current stories.

Removes a single cluster: deletes the HTML and any downloaded images, drops it
from state.json, appends an audit row to takedowns.log. After running, re-run
renderer.py and commit. GitHub Pages republishes in ~60-90 seconds.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime, timezone

from utils import (
    SITE_NEWS_DIR,
    TAKEDOWNS_PATH,
    load_state,
    save_state,
    story_dir,
)

REASONS = ["publisher-request", "correction", "legal", "other"]


def find_cluster(state: dict, query: str) -> dict | None:
    for cluster in state.get("clusters", []):
        if cluster.get("slug") == query:
            return cluster
    for cluster in state.get("clusters", []):
        if query and query in (cluster.get("slug") or ""):
            return cluster
    for cluster in state.get("clusters", []):
        for source in cluster.get("sources", []):
            if source.get("url") == query or (query and query in source.get("url", "")):
                return cluster
    return None


def remove_story_dir(cluster: dict) -> bool:
    out_dir = story_dir(cluster)
    if out_dir.exists():
        shutil.rmtree(out_dir)
        return True
    return False


def remove_image_dir(cluster: dict) -> bool:
    try:
        year, month, _ = cluster["run_date"].split("-")
    except (KeyError, ValueError):
        return False
    image_dir = SITE_NEWS_DIR / "images" / year / month / cluster["slug"]
    if image_dir.exists():
        shutil.rmtree(image_dir)
        return True
    return False


def log_takedown(slug: str, reason: str, headline: str) -> None:
    TAKEDOWNS_PATH.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()
    line = f"{ts}\t{slug}\t{reason}\t{headline}\n"
    with TAKEDOWNS_PATH.open("a", encoding="utf-8") as fh:
        fh.write(line)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Take down a Genetic Current story")
    parser.add_argument("query", help="Slug, URL, or URL fragment of the story to take down")
    parser.add_argument("--reason", choices=REASONS, default="other", help="Reason category (logged to takedowns.log)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without changing files")
    args = parser.parse_args(argv)

    state = load_state()
    cluster = find_cluster(state, args.query)
    if not cluster:
        print(f"ERROR: No cluster matching '{args.query}'", file=sys.stderr)
        print("  Try the slug from the URL (e.g. crispr-base-editing-leukaemia-trial),", file=sys.stderr)
        print("  or paste the full story URL or source URL.", file=sys.stderr)
        return 2

    slug = cluster["slug"]
    headline = cluster.get("headline", "")
    print(f"Match: '{headline}'")
    print(f"  slug:   {slug}")
    print(f"  date:   {cluster.get('run_date')}")
    print(f"  reason: {args.reason}")

    if args.dry_run:
        print("\n[DRY RUN] No files changed.")
        return 0

    removed_html = remove_story_dir(cluster)
    removed_img = remove_image_dir(cluster)
    state["clusters"] = [c for c in state["clusters"] if c.get("slug") != slug]
    state.setdefault("takedowns", []).append({
        "slug": slug,
        "headline": headline,
        "date": datetime.now(timezone.utc).date().isoformat(),
        "reason": args.reason,
    })
    save_state(state)
    log_takedown(slug, args.reason, headline)

    print()
    print(f"  Removed HTML directory: {removed_html}")
    print(f"  Removed image directory: {removed_img}")
    print(f"  Audit row appended to {TAKEDOWNS_PATH.name}")
    print()
    print("Now re-render and commit:")
    print("  python scripts/news-aggregator/renderer.py")
    print(f'  git add news/ scripts/news-aggregator/state.json scripts/news-aggregator/takedowns.log')
    print(f'  git commit -m "[news-takedown] {slug} ({args.reason})"')
    print("  git push")
    return 0


if __name__ == "__main__":
    sys.exit(main())
