"""One-shot: inject a 'Genetic Current' link into the top nav across existing HTML pages.

Two patterns covered:
  Phase 1: research-citations-style nav (logo and waitlist as direct siblings).
           News + waitlist get wrapped in a flex sub-div.
  Phase 2: any other nav with a desktop waitlist link (matches `href="#waitlist"`
           or `href="https://evagene.com/#waitlist"` carrying `hidden sm:inline-flex`).
           News link inserted as the previous sibling of the waitlist link.

Idempotent — skips files that already contain a /news/ link with `News</span>`.
Only touches *.html in the repo root.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

PHASE1_PATTERN = re.compile(
    r'(<a href="https://evagene\.com"[^>]*class="flex items-center gap-2\.5">.*?</a>)'
    r'(\s+)'
    r'(<a href="https://evagene\.com/#waitlist"[^>]*>Join Alpha Waiting List</a>)',
    re.DOTALL,
)

PHASE2_PATTERN = re.compile(
    r'(<a [^>]*href="[^"]*#waitlist"[^>]*hidden sm:inline-flex[^>]*>)',
    re.IGNORECASE,
)

NEWS_LINK = (
    '<a href="/news/" class="hidden sm:inline-flex items-center gap-1.5 text-sm font-medium '
    'text-gray-700 dark:text-gray-300 hover:text-brand-600 dark:hover:text-brand-300 mr-3" '
    'title="Genetic Current news">'
    '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">'
    '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" '
    'd="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/>'
    '</svg>'
    '<span>News</span>'
    '</a>'
)

NEWS_LINK_NO_MARGIN = NEWS_LINK.replace(" mr-3", "")


def phase1_replace(match: re.Match) -> str:
    logo_a, whitespace, waitlist_a = match.group(1), match.group(2), match.group(3)
    return f'{logo_a}{whitespace}<div class="flex items-center gap-4">{NEWS_LINK_NO_MARGIN}{waitlist_a}</div>'


def phase2_replace(match: re.Match) -> str:
    return f'{NEWS_LINK}{match.group(1)}'


def process(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if 'href="/news/"' in text and "News</span>" in text:
        return "skipped"
    new_text, n = PHASE1_PATTERN.subn(phase1_replace, text, count=1)
    if n > 0:
        path.write_text(new_text, encoding="utf-8")
        return "phase1"
    new_text, n = PHASE2_PATTERN.subn(phase2_replace, text, count=1)
    if n > 0:
        path.write_text(new_text, encoding="utf-8")
        return "phase2"
    return "no-match"


def main() -> None:
    counts = {"phase1": 0, "phase2": 0, "skipped": 0, "no-match": []}
    for path in sorted(REPO_ROOT.glob("*.html")):
        result = process(path)
        if result == "no-match":
            counts["no-match"].append(path.name)
        else:
            counts[result] += 1
    print(f"Phase 1 (wrapped sub-div): {counts['phase1']} pages")
    print(f"Phase 2 (sibling insert):  {counts['phase2']} pages")
    print(f"Already updated:           {counts['skipped']} pages")
    print(f"Total updated:             {counts['phase1'] + counts['phase2']} pages")
    if counts["no-match"]:
        print(f"\n{len(counts['no-match'])} pages still did not match:")
        for name in counts["no-match"][:20]:
            print(f"  - {name}")
        if len(counts["no-match"]) > 20:
            print(f"  ... and {len(counts['no-match']) - 20} more")


if __name__ == "__main__":
    main()
