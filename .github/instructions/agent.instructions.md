---
description: "Instructions for AI coding agents working in this repository"
applyTo: "**"
---

# copilot instructions for this repo

Purpose: help AI coding agents become productive quickly in the watchcat workspace by
documenting the big-picture architecture, key files, run/test workflows, and repository
patterns that are discoverable from source.

- Repository shape
  - Two Python packages at the workspace root: `watchcat/` and `phdkit/` (see top-level
    `pyproject.toml` which declares them as workspace members).
  - This repository is a monorepo / workspace: the top-level `pyproject.toml` lists
    `watchcat` and `phdkit` as members under `tool.uv.workspace.members`. Treat the
    root as the workspace root when running tests or working across packages (for
    example, running `pytest` from the workspace root will discover tests in both
    packages).
  - `watchcat` is an LLM-driven pipeline that pulls content (currently email), builds
    prompts, and calls a GenAI model to summarize/analyze/evaluate content.
  - `phdkit` is a small utility library used by `watchcat` (config helpers, logging,
    small algorithms like IntervalTree).

- Big-picture architecture (what to read first)
  - Entrypoint & config: `src/watchcat/__init__.py` — contains the `App` class, default
    paths (uses `xdg_base_dirs`) and the Click `main()` wrapper. Read this to understand
    how configs and env files are loaded and where default DB/config files live.
  - Workflow orchestration: `src/watchcat/workflow/__init__.py` — the pipeline that
    pulls posts, orchestrates them into prompts, calls GenAI, and stores results.
  - Pullers/sources: `src/watchcat/puller/` — implement `Source`/`Mailbox`/`Mail`/`Arxiv`
    here. New sources should implement the `Source` interface and return `Post` objects
    with a `to_prompt()` method used by the workflow.
  - Persistence: `src/watchcat/datastore/__init__.py` — a small `Database` class backed
    by SQLite with a documented `SCHEMA` (tables: `topics`, `summaries`, `analyses`,
    `evaluations`). Use this to persist outputs or extend with additional tables.

- Runtime & quick commands
  - Python requirement: repo uses Python >= 3.12 (see `watchcat/pyproject.toml`).
  - Run everything via `uv`: This workspace uses `uv` as the runner. Always run Python commands
    (apps, scripts, tests) via `uv run ...` so the workspace sources and entry points are
    correctly discovered and the development environment matches CI. Examples:
    - Run the CLI (preferred): `uv run watchcat` (this uses the `watchcat` script defined in `pyproject.toml`).
    - Run tests: `uv run pytest` (execute from the workspace root so tests in both packages are discovered).
    - If you need to run a module-level command, run the command defined in `pyproject.toml` as `uv run <command>` rather than `python -m <module>`; running `python -m` directly may lead to import errors in this workspace.
    - Run a single test file: `uv run pytest -- tests/test_workflow_mock.py` (or point to any specific test path).
  - Config and env files: defaults use XDG paths, but the CLI accepts `--config`/`--env`
    to point to a TOML config and env file. Example (when using uv): `uv run watchcat -- --config ./default.config.toml --env ./default.env.toml`.

- Notable code patterns and project-specific conventions
  - Configs: `phdkit.configlib.configurable` and `@setting` are used to define app
    settings (see `App` in `src/watchcat/__init__.py`). Read that file when changing
    runtime configuration behavior.
  - Prompt templates & LLM calls: `src/watchcat/prompt/` (prompt templates and
    `fill_out_prompt`) + `workflow` call `google.genai.Client().models.generate_content`.
    The pipeline tolerantly extracts text using `_extract_text_from_response` in the
    workflow; follow that helper when adapting model response handling.
  - Persistence: `Database.SCHEMA` is the authoritative source for columns and table
    names. Rows use ISO-8601 timestamps. Many `store_*` helper methods already exist.
  - `TODO` placeholders: Several workflow storage functions are TDD/dev placeholders
    (e.g. `_store_posts_in_database`, `_store_summaries_in_database` print `TODO`). Be
    aware these are intentionally incomplete when running end-to-end.

- How to add a new data source or pipeline step (practical example)
  - Implement a `Source` subclass under `src/watchcat/puller/` and ensure it yields
    `Post` objects. `Post.to_prompt()` must return a text fragment the workflow can
    insert into a combined prompt (see `_join_posts_in_one`).
  - Update `src/watchcat/__init__.py` (App.run) to construct the new source and add
    it to the `Workflow([...])` constructor when you want it pulled.

- Integration points & third-party deps to be mindful of
  - Google GenAI: `google.genai` is used directly in `workflow`. Credentials and
    client setup are not centralized; tests commonly run with fallbacks/placeholder
    responses—do not rely on live API in unit tests.
  - Google APIs and storage: `google-api-python-client`, `google-auth-*`, and
    `google-cloud-storage` appear in `pyproject.toml`.
  - Persistent store: SQLite is used for simple storage; default DB path is XDG data
    dir unless overridden by config.

- Useful files to inspect when working here
  - `src/watchcat/__init__.py` — config, CLI, and App wiring
  - `src/watchcat/workflow/__init__.py` — orchestration and LLM interaction
  - `src/watchcat/datastore/__init__.py` — SQLite schema and helpers
  - `src/watchcat/puller/*` — source implementations (Mailbox, Mail, Arxiv)
  - `src/watchcat/prompt/*` — prompt templates and `fill_out_prompt`
  - `watchcat/default.config.toml`, `watchcat/default.env.toml` — reference configs

- When editing code, watch for these gotchas
  - Config loading uses `TomlReader` and XDG defaults; running locally without
    providing `--config`/`--env` may load different files on different machines.
  - Workflow currently assumes Chinese-language prompts (`fill_out_prompt(..., language="Chinese")`) in several places: check `language` values before changing defaults.
  - LLM responses are parsed liberally; prefer using `.parse()` methods on model
    classes (if present) to obtain structured JSON results.

- Why use `uv` (brief)
  - `uv` is used to ensure the workspace packages are installed/available on the
    PYTHONPATH and that `pyproject.toml` entry points are resolved the same way CI
    expects. Running `python -m <module>` directly in a workspace can cause
    import errors because the local package layout may not be on sys.path the same
    way `uv` configures it. Using `uv run` avoids these transient import issues and
    makes local runs reproducible.

If anything here is unclear or you'd like more examples (for instance, a short
example PR that implements a new `Source` and stores results in the DB), tell me
which area to expand and I will iterate.
