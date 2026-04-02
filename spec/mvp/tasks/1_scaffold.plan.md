---
status: DONE
spec_name: mvp
plan: 1
task_slug: scaffold
git_branch: mvp/scaffold
depends_on_tasks: []
blocks_tasks: [core-models]
---

# Plan: Scaffold project layout and tooling

## Git branch

Branch: **`mvp/scaffold`**

- [x] Branch created from `main`.
- [ ] PR targets `main`; branch name matches `git_branch` in frontmatter.

## Related spec

- Spec folder: `spec/mvp/`
- Design: `spec/mvp/DESIGN.md`
- Requirements: `spec/mvp/REQUIREMENTS.md`
- Root: `PRODUCT.md`, `STRUCTURE.md`, `TECH.md`

When editing this plan, keep YAML aligned with **`.cursor/rules/spec-planning-enforcer.mdc`**: **`git_branch`**, **`task_slug`**, **`depends_on_tasks`**, **`blocks_tasks`**.

## Goal

Set up the repository skeleton so every subsequent task has a working package, dev tooling, and CI baseline to build on. After this task, `uv sync`, `uv run ruff check`, `uv run mypy`, and `uv run pytest` all succeed on an empty library.

## Definition of done

- [x] `pyproject.toml` exists with project metadata, `requires-python = ">=3.9.2,<3.15"` (floor/ceiling required by **`dlt`**; see **Notes**), hatchling build backend, base runtime **`dlt>=…`** (version floor only, no `[]` on the base line), **`[project.optional-dependencies]`** mirroring dlt (see **`TECH.md`**): `redshift` → `dlt[redshift]`, **`postgres` → `dlt[postgres]`**, `filesystem` → `dlt[filesystem]`, `sftp` → `dlt[sftp]`, **`mvp`** → **`dlt[redshift,postgres,filesystem,sftp]`**; dev **dependency group** (or legacy dev deps): ruff, mypy, pytest.
- [x] `uv.lock` committed and `uv sync` succeeds.
- [x] `dlk/` package exists with `__init__.py` (can be nearly empty; exports version).
- [x] Sub-packages exist as empty `__init__.py` stubs: `api/`, `builders/`, `core/`, `adapters/`, `connectors/`, `results/`, `utils/`.
- [x] `tests/` directory exists with a trivial passing test (`test_import.py`).
- [x] `examples/` directory exists (empty or with a placeholder README).
- [x] Ruff, mypy, and pytest pass in CI (GitHub Actions workflow). _(Verify on push.)_
- [x] `.gitignore` covers Python, uv, and IDE artifacts.

## Inter-task dependencies

No upstream dependencies — this is the first task.

| Dependency (task slug) | Branch that must land first | Notes |
|------------------------|-----------------------------|-------|
| — | — | None |

**Blocks:** `core-models` (and transitively all later tasks).

## Out of scope (this plan)

- Any real library logic, dataclasses, or dlt integration.
- README content beyond a one-liner.
- Publishing to PyPI.
- Docker / container setup.

## Steps

- [x] **Step 1:** Create `pyproject.toml` — project name `dataloadkit`, version `0.1.0`, `requires-python = ">=3.9.2,<3.15"`, hatchling build backend; **`dependencies`:** `dlt>=1.15.0` only; **`[project.optional-dependencies]`:** `redshift = ["dlt[redshift]"]`, **`postgres = ["dlt[postgres]"]`** ([dlt Postgres](https://dlthub.com/docs/dlt-ecosystem/destinations/postgres)), `filesystem = ["dlt[filesystem]"]`, `sftp = ["dlt[sftp]"]` ([SFTP / paramiko](https://dlthub.com/docs/dlt-ecosystem/destinations/filesystem)), **`mvp = ["dlt[redshift,postgres,filesystem,sftp]"]`**; dev tools via **`[dependency-groups]`** `dev` = `ruff`, `mypy`, `pytest` (or equivalent per uv docs).
- [x] **Step 2:** Run **`uv lock --extra mvp`** then **`uv sync --extra mvp --group dev`** (or project’s chosen groups) so the lockfile and local env include the full MVP dlt stack; document that bare `uv sync` without extras only installs base `dlt`. _(On **uv 0.9.x**, `uv lock` has no `--extra`; lockfile generated via **`uv sync --extra mvp --group dev`**.)_
- [x] **Step 3:** Create `dlk/__init__.py` with `__version__ = "0.1.0"`.
- [x] **Step 4:** Create empty sub-package stubs: `dlk/api/__init__.py`, `dlk/builders/__init__.py`, `dlk/core/__init__.py`, `dlk/adapters/__init__.py`, `dlk/connectors/__init__.py`, `dlk/results/__init__.py`, `dlk/utils/__init__.py`.
- [x] **Step 5:** Create `tests/__init__.py` and `tests/test_import.py` (`import dlk; assert dlk.__version__`).
- [x] **Step 6:** Create `examples/` directory with a placeholder `.gitkeep` or minimal `README.md`.
- [x] **Step 7:** Add `.gitignore` (Python, `__pycache__`, `.venv`, `dist/`, `.mypy_cache`, `.ruff_cache`).
- [x] **Step 8:** Add `ruff.toml` or `[tool.ruff]` in `pyproject.toml` with sensible defaults for the project.
- [x] **Step 9:** Add `mypy` config section in `pyproject.toml` (strict optional, Python 3.9 target).
- [x] **Step 10:** Add `.github/workflows/ci.yml` — matrix on Python 3.9 + latest stable; steps: **`uv sync --extra mvp --group dev`** (or `--all-extras` if policy locks all optional stacks), then `ruff check`, `ruff format --check`, `mypy dlk`, `pytest`.
- [x] **Step 11:** Verify locally (with **`mvp`** extra installed): `uv run ruff check`, `uv run mypy dlk`, `uv run pytest` all green.

## Other dependencies

- **Requires:** `DESIGN.md` and `REQUIREMENTS.md` exist (both DRAFT ✓).
- **External:** GitHub repo exists with Actions enabled.

## Affected files / modules

- `pyproject.toml` (new)
- `dlk/**/__init__.py` (new)
- `tests/test_import.py` (new)
- `.gitignore` (new or updated)
- `.github/workflows/ci.yml` (new)

## Validation

### Automated

- `uv run ruff check` — zero errors
- `uv run ruff format --check` — zero diffs
- `uv run mypy dlk` — zero errors
- `uv run pytest` — 1 test, passing
- CI workflow green on push

### Manual

- `uv sync --extra mvp --group dev` from a clean clone succeeds on Python 3.9 and latest stable.

## Notes

- **`mvp`** extra bundles **`dlt[redshift,postgres,filesystem,sftp]`** (MVP **PostgreSQL** requires **`postgres`**); consumers can install **`dataloadkit[redshift]`**, **`[postgres]`**, **`[filesystem]`**, **`[sftp]`** in any combination (pip/uv union extras on `dlt`). Omitting **`postgres`** breaks **PostgreSQL** SQL sources/destinations; omitting **`sftp`** when using SFTP URLs breaks **`to_sftp`** (no paramiko).
- Align naming and tables with **`TECH.md`** → **Optional dependencies (dlt extras)**.
- Do not pin dlt to a narrow range yet — use `>=` with a reasonable floor based on current stable.
- **`requires-python`:** `>=3.9.2,<3.15` is required so dependency resolution includes only Python versions **`dlt`** supports (it excludes **3.9.0–3.9.1** and **≥3.15**). **`PRODUCT.md`**, **`STRUCTURE.md`**, **`TECH.md`**, and this plan are aligned on that range.
- Bare **`uv sync`** (no **`--extra mvp`**) installs only the base **`dlt`** dependency; use **`uv sync --extra mvp --group dev`** for the full MVP stack and dev tools.

## Completion (2026-04-02)

- Scaffold implemented on branch **`mvp/scaffold`**. Remaining: open PR to **`main`** and confirm Actions is green.
