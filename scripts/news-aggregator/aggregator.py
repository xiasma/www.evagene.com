"""Daily news aggregator for Genetic Current.

Pulls RSS / Atom feeds, dedups, sends to Claude for clustering and editorial
summarisation, persists state. Run via GitHub Actions cron or locally.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import feedparser
import yaml

from utils import (
    REUSABLE_LICENCES,
    SOURCES_PATH,
    SYSTEM_PROMPT_PATH,
    load_state,
    parse_iso,
    save_state,
    utc_now,
)


def load_sources() -> list[dict[str, Any]]:
    with SOURCES_PATH.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)["sources"]


def _parse_entry_date(entry: Any) -> datetime | None:
    for field in ("published_parsed", "updated_parsed"):
        value = getattr(entry, field, None) or entry.get(field) if hasattr(entry, "get") else None
        if value:
            try:
                return datetime(*value[:6], tzinfo=timezone.utc)
            except (TypeError, ValueError):
                continue
    return None


def _extract_image_url(entry: Any) -> str | None:
    for key in ("media_content", "media_thumbnail"):
        items = entry.get(key) if hasattr(entry, "get") else getattr(entry, key, None)
        if items:
            url = items[0].get("url") if isinstance(items, list) else None
            if url:
                return url
    enclosures = entry.get("enclosures") if hasattr(entry, "get") else getattr(entry, "enclosures", None)
    if enclosures:
        for enc in enclosures:
            if enc.get("type", "").startswith("image/"):
                return enc.get("href") or enc.get("url")
    content = entry.get("content")
    if content:
        text = content[0].value if hasattr(content[0], "value") else content[0].get("value", "")
        match = re.search(r'<img[^>]+src="([^"]+)"', text or "")
        if match:
            return match.group(1)
    return None


def _extract_lede(entry: Any) -> str:
    summary = entry.get("summary", "") if hasattr(entry, "get") else getattr(entry, "summary", "")
    text = re.sub(r"<[^>]+>", " ", summary or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text[:600]


def _extract_tags(entry: Any) -> list[str]:
    tags = entry.get("tags") if hasattr(entry, "get") else getattr(entry, "tags", None)
    if not tags:
        return []
    out = []
    for tag in tags:
        term = tag.get("term") if isinstance(tag, dict) else getattr(tag, "term", None)
        if term:
            out.append(term)
    return out[:8]


def fetch_feeds(sources: list[dict], lookback_hours: int = 48) -> tuple[list[dict], list[dict]]:
    cutoff = utc_now() - timedelta(hours=lookback_hours)
    items: list[dict] = []
    failures: list[dict] = []

    for source in sources:
        url = source["feed_url"]
        try:
            feed = feedparser.parse(url)
            if feed.bozo and not feed.entries:
                failures.append({"source": source["name"], "error": str(feed.bozo_exception)})
                continue
            for entry in feed.entries:
                published = _parse_entry_date(entry)
                if published and published < cutoff:
                    continue
                link = entry.get("link") if hasattr(entry, "get") else getattr(entry, "link", None)
                title = entry.get("title", "").strip() if hasattr(entry, "get") else getattr(entry, "title", "").strip()
                if not link or not title:
                    continue
                items.append({
                    "url": link,
                    "title": title,
                    "lede_text": _extract_lede(entry),
                    "publisher": source["publisher"],
                    "source_name": source["name"],
                    "source_priority": source["priority"],
                    "published_iso": published.isoformat() if published else "",
                    "image_url": _extract_image_url(entry),
                    "image_licence_class": source["image_licence"],
                    "feed_tags": _extract_tags(entry),
                    "is_preprint": source.get("preprint", False),
                })
        except Exception as exc:
            failures.append({"source": source["name"], "error": str(exc)})

    return items, failures


def dedup_against_state(items: list[dict], state: dict, ttl_days: int = 14) -> list[dict]:
    cutoff = (utc_now() - timedelta(days=ttl_days)).isoformat()
    seen = {url: ts for url, ts in state.get("seen_urls", {}).items() if ts > cutoff}
    state["seen_urls"] = seen
    return [item for item in items if item["url"] not in seen]


def recent_clusters_summary(state: dict, days: int = 14) -> list[dict]:
    cutoff = (utc_now() - timedelta(days=days)).date().isoformat()
    return [
        {
            "run_date": c.get("run_date", ""),
            "headline": c.get("headline", ""),
            "tags": c.get("tags", []),
        }
        for c in state.get("clusters", [])
        if c.get("run_date", "") >= cutoff
    ]


def format_user_prompt(items: list[dict], recent: list[dict], run_date: str) -> str:
    lines = [
        f"Today is {run_date} ({utc_now().isoformat(timespec='seconds')}).",
        "",
        f"Here are the {len(items)} items collected from feeds in the past 48 hours.",
        "Items already published as Genetic Current clusters in the past 14 days",
        "are listed at the bottom — use them to detect repeats and to score 'novelty'.",
        "",
        "== NEW ITEMS ==",
        "",
    ]
    for idx, item in enumerate(items, 1):
        lines.append(f"[{idx}] {item['publisher']} — {item['published_iso']}")
        lines.append(f"    URL:   {item['url']}")
        lines.append(f"    Title: {item['title']}")
        if item["lede_text"]:
            lines.append(f"    Lede:  {item['lede_text']}")
        lines.append(f"    Image: {item['image_url'] or 'none'} ({item['image_licence_class']})")
        if item["feed_tags"]:
            lines.append(f"    Feed tags: {', '.join(item['feed_tags'])}")
        if item.get("is_preprint"):
            lines.append("    Preprint: yes")
        lines.append("")
    lines.append("== RECENT PUBLISHED CLUSTERS (last 14 days) ==")
    lines.append("")
    if recent:
        for prev in recent:
            tags = ", ".join(prev.get("tags", []))
            lines.append(f"- {prev['run_date']} — {prev['headline']} (tags: {tags})")
    else:
        lines.append("(none)")
    lines.append("")
    lines.append("Please process per your editor brief and return the JSON schema.")
    return "\n".join(lines)


def parse_editor_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```\s*$", "", text)
    return json.loads(text)


def call_editor(
    items: list[dict],
    recent: list[dict],
    run_date: str,
    model: str,
    dry_run: bool,
    max_tokens: int = 16000,
    max_clusters_hint: int | None = None,
) -> dict | None:
    system_text = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    user_text = format_user_prompt(items, recent, run_date)
    if max_clusters_hint:
        user_text += (
            f"\n\nIMPORTANT — output budget: for this run, emit at most {max_clusters_hint} "
            f"clusters. Pick the most newsworthy and highest-importance items. Put everything "
            f"else in `skipped` with reason `low-priority-for-this-batch` (no need to list them "
            f"all individually — a summary count is fine)."
        )

    if dry_run:
        print(f"[DRY RUN] Would call {model} with {len(items)} items, {len(system_text)} chars of system prompt, {len(user_text)} chars of user prompt.")
        return None

    from anthropic import Anthropic

    client = Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=[{
            "type": "text",
            "text": system_text,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": user_text}],
    )

    text = "".join(block.text for block in response.content if block.type == "text")
    stop_reason = getattr(response, "stop_reason", "")
    if stop_reason == "max_tokens":
        print(f"WARN: editor response was truncated at max_tokens={max_tokens}. Increase max_tokens or lower max_clusters_hint.", file=sys.stderr)
    try:
        return parse_editor_response(text)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Could not parse editor response as JSON: {exc}", file=sys.stderr)
        print(f"  stop_reason: {stop_reason}", file=sys.stderr)
        print(f"  output length: {len(text)} chars", file=sys.stderr)
        print("--- Response (first 2KB) ---", file=sys.stderr)
        print(text[:2000], file=sys.stderr)
        print("--- Response (last 2KB) ---", file=sys.stderr)
        print(text[-2000:], file=sys.stderr)
        raise


def merge_into_state(state: dict, output: dict) -> None:
    now_iso = utc_now().isoformat()
    for cluster in output.get("clusters", []):
        for source in cluster.get("sources", []):
            state["seen_urls"][source["url"]] = now_iso
    for skipped in output.get("skipped", []):
        url = skipped.get("url")
        if url:
            state["seen_urls"][url] = now_iso

    # Replace clusters with same slug (re-run safety); append new ones.
    existing_by_slug = {c["slug"]: i for i, c in enumerate(state["clusters"]) if c.get("slug")}
    for cluster in output.get("clusters", []):
        cluster.setdefault("run_date", output.get("run_date"))
        cluster.setdefault("run_iso", output.get("run_iso"))
        slug = cluster.get("slug")
        if slug in existing_by_slug:
            state["clusters"][existing_by_slug[slug]] = cluster
        else:
            state["clusters"].append(cluster)

    state["last_run"] = now_iso


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Genetic Current daily aggregator")
    parser.add_argument("--dry-run", action="store_true", help="Skip the Claude API call")
    parser.add_argument("--lookback-hours", type=int, default=48)
    parser.add_argument("--model", default="claude-sonnet-4-6")
    parser.add_argument("--output", default=None, help="Optional path to write the run JSON")
    args = parser.parse_args(argv)

    sources = load_sources()
    state = load_state()

    print(f"Fetching {len(sources)} feeds, lookback {args.lookback_hours}h…")
    items, failures = fetch_feeds(sources, args.lookback_hours)
    print(f"  Got {len(items)} items; {len(failures)} feeds failed")
    for fail in failures:
        print(f"  FEED FAIL: {fail['source']}: {fail['error']}")

    items = dedup_against_state(items, state)
    print(f"  {len(items)} items after dedup against last 14 days of state")

    if not items:
        print("Nothing new to process.")
        save_state(state)
        return 0

    recent = recent_clusters_summary(state)
    run_date = utc_now().date().isoformat()

    output = call_editor(items, recent, run_date, args.model, args.dry_run)
    if output is None:
        return 0

    print(f"Editor returned {len(output.get('clusters', []))} clusters, {len(output.get('skipped', []))} skipped")
    merge_into_state(state, output)
    save_state(state)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            json.dump(output, fh, indent=2, ensure_ascii=False)
        print(f"Wrote run output to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
