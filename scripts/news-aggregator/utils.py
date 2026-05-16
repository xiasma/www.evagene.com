"""Shared utilities for the Genetic Current news aggregator."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent.parent
SITE_NEWS_DIR = REPO_ROOT / "news"
STATE_PATH = ROOT / "state.json"
SOURCES_PATH = ROOT / "sources.yml"
SYSTEM_PROMPT_PATH = ROOT / "system_prompt.md"
TAKEDOWNS_PATH = ROOT / "takedowns.log"

AUDIENCES = [
    "researchers",
    "gps",
    "oncologists",
    "genetic-counsellors",
    "educators",
    "students",
    "genealogists",
    "patients",
]

AUDIENCE_LABELS = {
    "researchers": "Researchers",
    "gps": "GPs",
    "oncologists": "Oncologists",
    "genetic-counsellors": "Genetic Counsellors",
    "educators": "Educators",
    "students": "Students",
    "genealogists": "Genealogists",
    "patients": "Patients & Families",
}

REUSABLE_LICENCES = {"public_domain", "ogl", "cc_by", "press_release"}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_today_iso() -> str:
    return utc_now().date().isoformat()


def parse_iso(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def empty_state() -> dict[str, Any]:
    return {
        "clusters": [],
        "seen_urls": {},
        "last_run": None,
        "takedowns": [],
    }


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return empty_state()
    with STATE_PATH.open(encoding="utf-8") as fh:
        state = json.load(fh)
    base = empty_state()
    base.update(state)
    return base


def save_state(state: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with STATE_PATH.open("w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, sort_keys=True, ensure_ascii=False)
        fh.write("\n")


def slugify(text: str, max_len: int = 60) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower(), flags=re.ASCII)
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text[:max_len].rstrip("-") or "story"


def story_dir(cluster: dict[str, Any]) -> Path:
    date = cluster.get("run_date") or utc_today_iso()
    year, month, day = date.split("-")
    return SITE_NEWS_DIR / year / month / day / cluster["slug"]


def story_url_path(cluster: dict[str, Any]) -> str:
    date = cluster.get("run_date") or utc_today_iso()
    year, month, day = date.split("-")
    return f"/news/{year}/{month}/{day}/{cluster['slug']}/"


def absolute_url(path: str) -> str:
    path = path if path.startswith("/") else f"/{path}"
    return f"https://evagene.com{path}"
