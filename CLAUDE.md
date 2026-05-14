# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**mkdocs-macros-utils** is a [zensical](https://zensical.org/) macros module that provides reusable Jinja2 macros for link cards, GitHub Gist code blocks, and X/Twitter embeds. It is loaded via `zensical.extensions.macros` (the built-in macros extension in zensical v0.0.40+). The module automatically copies its own CSS/JS static assets into the docs directory on first use.

## Development Setup

This project uses [uv](https://docs.astral.sh/uv/) for Python dependency management and Node.js/npm for JavaScript testing.

```sh
uv sync                 # Install Python dependencies (creates .venv)
npm install             # Install JavaScript test dependencies
```

## Commands

### Python Tests

```sh
# Run all tests with coverage
uv run task testcoverageverbose

# Run a single test file
uv run pytest tests/python/mkdocs_macros_utils/test_link_card.py -s -vv

# Run tests matching a marker
uv run pytest -m link_card -s -vv

# CI variants
uv run task testcixml    # XML report (for CI)
uv run task testciterm   # Terminal report (for CI)
```

Coverage requirement: **90% minimum** enforced on PRs.

### JavaScript Tests

```sh
npm test                # Run Jest tests once
npm run test:watch      # Watch mode
npm run test:coverage   # With coverage
```

### Docs (local preview)

```sh
uv run zensical serve
uv run zensical build
```

### Linting & Type Checking

Pre-commit runs ruff, mypy, and several other checks. To run manually:

```sh
uv run ruff check .             # Lint
uv run ruff format .            # Format
uv run mypy mkdocs_macros_utils/
pre-commit run --all-files      # Run all hooks
```

mypy is configured with `disallow_untyped_defs = true` — all functions must be fully annotated.

## Architecture

### Module Lifecycle (`mkdocs_macros_utils/__init__.py`)

The module exports `define_env(env: MacroEnv)` called by zensical's macros extension:
- Reads `mkdocs.yml` (via `_load_config()`) to get `docs_dir`, `site_url`, and `extra` settings
- Copies CSS/JS static assets into `docs/` via `copy_static_files()` (skips if already up-to-date)
- Registers the three macros by calling each sub-module's `define_env`

Use `MACROS_UTILS_DOCS_DIR` env var to override the default `docs/` target directory.

### Macro Modules

| Module | Macro | What it does |
|---|---|---|
| `link_card.py` | `link_card(url, ...)` | Fetches SVG icons (from GitHub Gists), renders an HTML link card with image/SVG, domain, and description. Uses `env.variables["_site_url"]` for base URL. |
| `gist_codeblock.py` | `gist_codeblock(gist_url, ...)` | Fetches raw Gist content via GitHub API, auto-detects language via filename extension and Pygments, returns a fenced Markdown code block |
| `x_twitter_card.py` | `x_twitter_card(url)` | Normalizes x.com/twitter.com URLs and renders a Twitter embed widget with dark mode support |
| `debug_logger.py` | (internal) | Per-feature debug logging controlled by `extra.debug.{link_card,gist_codeblock,x_twitter_card}` in `mkdocs.yml`. Read via `env.variables["extra"]` set by `define_env`. |

### Tests (`tests/python/`)

Tests mirror the source layout under `tests/python/mkdocs_macros_utils/`. Shared fixtures live in `tests/python/conftest.py`, including:
- `MockMacroEnv` — simulates the zensical `MacroEnv` object (has `variables`, `macros`, `filters`, `macro()`, `filter()`)
- `mock_requests_get()` helper — patches `requests.get` for HTTP calls
- `processor` fixture — pre-built `GistProcessor` instance

`test__init__.py` monkeypatches `_get_docs_dir` and `_load_extra_config` to avoid filesystem/config dependencies in tests.

Custom pytest markers: `gist`, `link_card`, `debug`.

CI matrix: Ubuntu/Windows/macOS × Python 3.10–3.13, timezone Asia/Tokyo.
