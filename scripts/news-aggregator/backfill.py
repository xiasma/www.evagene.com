"""One-time seed backfill for Genetic Current launch.

Two phases:
1. Deep RSS scan (default 30-day lookback) against the same Claude editor pipeline.
2. Claude web_search to find significant items that have aged out of RSS retention.
"""
from __future__ import annotations

import argparse
import sys
from datetime import timedelta

from aggregator import (
    call_editor,
    dedup_against_state,
    fetch_feeds,
    load_sources,
    merge_into_state,
    parse_editor_response,
    recent_clusters_summary,
)
from utils import SYSTEM_PROMPT_PATH, load_state, save_state, utc_now


def web_search_for_more(target: int, existing: int, start_date: str, model: str) -> dict | None:
    needed = max(0, target - existing)
    if needed <= 0:
        print("Target already met, skipping web search.")
        return None

    from anthropic import Anthropic

    system_text = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    user_text = (
        f"You are seeding Genetic Current with historical content. The pipeline already loaded "
        f"{existing} clusters from recent RSS; we need approximately {needed} more.\n\n"
        f"Use the web_search tool to find significant genetics and genomics news published from "
        f"{start_date} onwards, from the sources in your editor brief (NHGRI, CDC, NHS England, "
        f"Genomics England, PHG Foundation, Wellcome Sanger, Cancer Research UK, The Conversation, "
        f"PLOS Genetics, Nature Medical Genetics, EurekAlert, ScienceDaily, Stat News, "
        f"The Scientist, bioRxiv).\n\n"
        f"Find REAL stories with real URLs you can verify. Do not invent items. Apply all editorial "
        f"standards from your brief.\n\n"
        f"Today's date is {utc_now().date().isoformat()}. Set published_iso to the actual publication "
        f"date of each source. Quality over quantity — if you can find {needed} excellent stories, "
        f"great; if not, return what you can find.\n\n"
        f"Return the same JSON schema you would for a daily run."
    )

    client = Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=16000,
        system=[{
            "type": "text",
            "text": system_text,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": user_text}],
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 30}],
    )

    text_blocks = [block.text for block in response.content if block.type == "text"]
    if not text_blocks:
        return None
    final_text = text_blocks[-1]
    try:
        return parse_editor_response(final_text)
    except Exception as exc:
        print(f"WARN: Could not parse web-search response: {exc}", file=sys.stderr)
        print(final_text[:1000], file=sys.stderr)
        return None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Backfill seed articles for Genetic Current")
    parser.add_argument("--target", type=int, default=50, help="Minimum clusters to aim for")
    parser.add_argument("--start", default=None, help="Earliest date to search (YYYY-MM-DD); default 60 days ago")
    parser.add_argument("--lookback-hours", type=int, default=720, help="RSS lookback hours (default ~30 days)")
    parser.add_argument("--model", default="claude-sonnet-4-6")
    parser.add_argument("--skip-web-search", action="store_true", help="Skip phase 2 web search")
    args = parser.parse_args(argv)

    start_date = args.start or (utc_now() - timedelta(days=60)).date().isoformat()
    print(f"Backfill: target {args.target} clusters")
    print(f"  Phase 1 — RSS lookback {args.lookback_hours}h")
    print(f"  Phase 2 — web search from {start_date}")

    sources = load_sources()
    state = load_state()

    print(f"\n[Phase 1] Scanning {len(sources)} feeds…")
    items, failures = fetch_feeds(sources, args.lookback_hours)
    print(f"  Got {len(items)} items; {len(failures)} feeds failed")
    for fail in failures:
        print(f"    FAIL: {fail['source']}: {fail['error']}")
    items = dedup_against_state(items, state)
    print(f"  {len(items)} items after dedup")

    if items:
        recent = recent_clusters_summary(state)
        output = call_editor(items, recent, utc_now().date().isoformat(), args.model, dry_run=False)
        if output:
            merge_into_state(state, output)
            save_state(state)
            print(f"  Emitted {len(output.get('clusters', []))} clusters (skipped: {len(output.get('skipped', []))})")

    cluster_count = len(state.get("clusters", []))
    print(f"\nAfter phase 1: {cluster_count} clusters in state.")

    if args.skip_web_search:
        print("Skipping web search per --skip-web-search.")
    elif cluster_count < args.target:
        print(f"\n[Phase 2] Web search for additional items (target {args.target} − have {cluster_count})…")
        try:
            output = web_search_for_more(args.target, cluster_count, start_date, args.model)
            if output:
                merge_into_state(state, output)
                save_state(state)
                print(f"  Emitted {len(output.get('clusters', []))} clusters")
        except Exception as exc:
            print(f"  Phase 2 failed: {exc}")
            print("  Continuing with RSS-only seed.")
    else:
        print("Target met from RSS alone, skipping web search.")

    final = len(state.get("clusters", []))
    print(f"\nFinal cluster count: {final}.")
    if final < args.target:
        print(f"Note: target was {args.target}; we found {final}. Run again with --start <earlier-date> or "
              "raise the lookback if you want more.")
    print("\nNext: python scripts/news-aggregator/renderer.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
