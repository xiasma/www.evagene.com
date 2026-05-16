# Genetic Current — news aggregator

Daily genetics news pipeline that publishes to `/news/` on evagene.com.

## What it does

1. Pulls ~16 RSS / Atom feeds (see `sources.yml`).
2. Dedups against the last 14 days of state, drops items already published.
3. Sends a batch to Claude (Sonnet 4.6) with `system_prompt.md` as the editor brief.
4. Claude clusters, scores, tags, summarises, and produces strict JSON.
5. Downloads images from sources with reusable licences (public domain, OGL, press-release-with-permission, CC BY); substitutes a category placeholder for everything else.
6. Renders HTML: trending front page, eight audience indices, per-story permalinks, monthly archive.
7. Updates `sitemap.xml` and `llms.txt` with the new entries.
8. Pagefind builds a full-text search index over the rendered HTML.
9. Workflow commits with a `[news]` subject prefix and pushes; GitHub Pages redeploys.

## Files

| File | What |
|---|---|
| `sources.yml` | Feed roster + per-source licence stance + priority |
| `system_prompt.md` | Editor brief for Claude — the editorial voice |
| `aggregator.py` | Daily run: RSS → dedup → Claude → state |
| `renderer.py` | Render HTML from state into `/news/` |
| `image_pipeline.py` | Download or substitute placeholder per story |
| `delete_story.py` | Takedown CLI (single story by slug or URL) |
| `backfill.py` | One-time seed of ~50 articles for launch |
| `state.json` | Cluster history + seen-URLs + takedowns audit |
| `takedowns.log` | Append-only audit trail (public; minimal fields) |
| `templates/` | Jinja2 templates for every news surface |

## Run locally (dry, no API)

```
pip install -r scripts/news-aggregator/requirements.txt
python scripts/news-aggregator/aggregator.py --dry-run
```

## Run live

Set `ANTHROPIC_API_KEY` in the environment, then:

```
python scripts/news-aggregator/aggregator.py
python scripts/news-aggregator/renderer.py
```

The GitHub Actions workflow `.github/workflows/news-aggregator.yml` runs both steps daily at 07:00 UTC and commits the result.

## Backfill (one-time)

```
python scripts/news-aggregator/backfill.py --target 50 --start 2026-04-01
```

Costs ~$5–15 in API spend; runs once. Reports how many real stories it found if the target isn't reachable.

## Takedown

```
python scripts/news-aggregator/delete_story.py <slug-or-url> --reason publisher-request
```

Removes the story HTML, drops the cluster from `state.json`, regenerates affected indices and the Pagefind index, appends to `takedowns.log`, commits with a `[news-takedown]` prefix.

## Editing the system prompt

The system prompt is the editorial voice of every entry. Edit `system_prompt.md` directly; the next run picks up the change. It is sent verbatim to Claude with prompt caching, so changes incur a one-time cache-miss cost on the run after the edit.

## Editing sources

Edit `sources.yml`. The first run after a change will ping each feed and log failures.
