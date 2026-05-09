# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
make start   # run dev server at http://localhost:8080
make build   # generate dist.html (standalone, no server needed)
```

## Architecture

This is a single-file algorithm problem practice app. All HTML, CSS, and JS live in **`index.html`** — no build step, no modules, no framework.

**`server.py`** — minimal HTTP server. Serves `index.html`, exposes two API endpoints:
- `GET /api/problems` — scans `problems/**/*.md`, parses numbered lists into problem objects, returns JSON.
- `GET/POST /api/solved` — reads/writes `progress.json` (solved indices only, format `{ topicId: [indices] }`).

**`build.py`** — inlines topics and solved data from `progress.json` into `dist.html` as `window.__TOPICS__` and `window.__SOLVED__` globals, producing a fully static file for offline use.

**`problems/`** — tree of `.md` files. Each file is one topic; numbered list items are problems. A bare URL on its own line becomes a link-type problem; everything else is rendered as markdown+LaTeX.

## State in `index.html`

All persistence is `localStorage`. Keys:
- `algo_shad_solved` — `{ topicId: [indices] }`
- `algo_shad_failed` — same shape
- `algo_shad_buried` — same shape (buried = removed from rotation permanently)
- `algo_shad_difficulties` — `{ topicId: { "idx": "hard"|"good"|"easy" } }`
- `algo_shad_answers` — `{ topicId: { "idx": { text, images: [base64…] } } }`
- `algo_shad_time_stats` — per-problem timing/attempt counters
- `algo_shad_timer`, `algo_shad_topics`, `algo_shad_collapsed` — UI prefs

In server mode, `/api/solved` is authoritative for solved data; localStorage is the fallback.

## Problem scheduling

`buildRound()` picks one unsolved problem per active topic, shuffles them into a deck. `firstUnsolved(topic)` skips any problem present in solved, failed, or buried sets. `advance()` walks the deck and calls `buildRound()` when exhausted.

## Key functions

| Function | Purpose |
|---|---|
| `markSolved(difficulty)` | Hard/Good/Easy — adds to solved+difficulties, removes from rotation |
| `failProblem()` | Adds to failed set, removes from rotation |
| `buryProblem()` | Adds to buried set, removes from rotation |
| `delayProblem()` | Skips without tracking — problem stays in rotation |
| `recordTime(outcome)` | Logs wall-clock time per problem into timeStats |
| `exportProgress()` | Downloads `progress.json` with all states: solved/failed/buried |
| `renderSolvedView()` / `renderFailedView()` / `renderBuriedView()` | Tab content renderers |
| `renderStatsView()` / `exportStatsCSV()` | Aggregate and per-problem stats |
| `switchView(v)` | Switches between `train`, `solved`, `failed`, `buried`, `stats` tabs |
