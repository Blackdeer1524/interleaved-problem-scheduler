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
- `GET/POST /api/solved` — reads/writes `progress.json` in simple format `{ topicId: [indices] }`.

**`build.py`** — reads `progress.json` (in the rich export format) and inlines topics + progress data into `dist.html` as `window.__TOPICS__` and `window.__PROGRESS__` globals, producing a fully static file for offline use.

**`problems/`** — tree of `.md` files. Each file is one topic; numbered list items are problems. A bare URL on its own line becomes a link-type problem; everything else is rendered as markdown+LaTeX.

```
problems/
  ydsa/
    algorithms/        # flat topic files (bfs.md, bin_search.md, …)
    mathematics/       # nested lecture folders → topic files
  yandex/             # LeetCode problems for Yandex interviews
    arrays_prefix_sum/ junior/ middle/
    binary_search/     junior/ middle/ senior/
    design/            junior/ middle/ senior/
    dynamic_programming/ junior/ middle/
    graph_bfs_dfs/     middle/ senior/
    hash_map_set/      junior/ middle/ senior/
    intervals/         junior/ middle/
    linked_list/       junior/ middle/ senior/
    math_probability/  middle/
    sliding_window/    junior/ middle/ senior/
    stack_queue/       junior/ middle/ senior/
    strings/           junior/ middle/ senior/
    trees/             junior/ middle/ senior/
    two_pointers/      junior/ middle/ senior/
```

Each problem file contains a single `1. <url>` line. The `topicId` used in localStorage / API is the file path relative to `problems/` without the `.md` extension (e.g. `yandex/trees/senior/01 Binary Tree Maximum Path Sum`).

**`CMakeLists.txt` / `tmp/`** — C++ scratch pad for problem solutions; unrelated to the web app.

## Two operating modes

The app detects its mode via `window.__TOPICS__`:
- **Server mode** (`make start`): topics loaded from `/api/problems`; solved data synced to `progress.json` via `/api/solved` (simple `{ topicId: [indices] }` format); localStorage is a fallback.
- **Static mode** (`dist.html`): topics and progress seeded from `window.__TOPICS__` / `window.__PROGRESS__`; all persistence is localStorage only.

## `progress.json` formats

Two distinct formats exist — do not confuse them:

| Context | Format |
|---|---|
| Server's `/api/solved` (on disk, server mode) | `{ topicId: [indices] }` |
| `exportProgress()` / `importProgress()` / `build.py` input | `{ topicId: { "idx": { status: "solved"\|"failed"\|"buried", difficulty?: "hard"\|"good"\|"easy" } } }` |

To build a `dist.html` with progress, export `progress.json` from the UI first, then run `make build`.

## State in `index.html`

All persistence in static/server-fallback mode is `localStorage`. Keys:
- `algo_shad_solved` — `{ topicId: [indices] }`
- `algo_shad_failed` — same shape
- `algo_shad_buried` — same shape (buried = removed from rotation permanently)
- `algo_shad_difficulties` — `{ topicId: { "idx": "hard"|"good"|"easy" } }`
- `algo_shad_answers` — `{ topicId: { "idx": { text, images: [base64…] } } }`
- `algo_shad_time_stats` — per-problem timing/attempt counters
- `algo_shad_sidebar_width` — sidebar width in px (integer string)
- `algo_shad_timer`, `algo_shad_topics`, `algo_shad_collapsed` — UI prefs

## Problem scheduling

`buildRound()` picks one unsolved problem per active topic, shuffles them into a deck. `firstUnsolved(topic)` skips any problem present in solved, failed, or buried sets. `advance()` walks the deck and calls `buildRound()` when exhausted.

## Key functions

| Function | Purpose |
|---|---|
| `markSolved(difficulty)` | Hard/Good/Easy — adds to solved+difficulties, removes from rotation |
| `failProblem()` | Adds to failed set, removes from rotation |
| `buryProblem()` | Adds to buried set, removes from rotation |
| `delayProblem()` | Skips without tracking — problem stays in rotation |
| `newSession()` | Resets deck and calls `advance()` to start fresh |
| `recordTime(outcome)` | Logs wall-clock time per problem into timeStats |
| `exportProgress()` | Downloads `progress.json` with all states in rich format |
| `importProgress()` | Reads a `progress.json` (rich format) and merges into live state |
| `renderSolvedView()` / `renderFailedView()` / `renderBuriedView()` | Tab content renderers |
| `renderStatsView()` / `exportStatsCSV()` | Aggregate and per-problem stats |
| `switchView(v)` | Switches between `train`, `solved`, `failed`, `buried`, `stats` tabs |
