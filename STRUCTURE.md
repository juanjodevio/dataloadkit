---
status: DRAFT
---

# Structure

## Repository Organization
The repository is organized as a Python-first library with clear separation between public API, core logic, and integrations.

Top-level structure:

- dlk/                 # main library package
- tests/               # unit and integration tests
- examples/            # usage examples
- docs/                # additional documentation (optional)
- pyproject.toml       # package configuration
- README.md            # project overview

**Runtime:** CPython **3.9.2+** (below **3.15** per **`dlt`**); supported range, CI matrix, and tool versions—**`uv`**, ruff, mypy—are defined in **`TECH.md`**; `requires-python` in `pyproject.toml` must stay aligned.

---

## Architectural Style

- Modular monolith
- Layered architecture

The system is organized into clear layers:
- Public API (builders)
- Planning layer (LoadPlan)
- Execution layer (dlt adapter—the only runtime that performs extract and load)
- Integration shaping (how domain configs map to dlt sources and destinations; no second execution path)

No microservices, no distributed components.

---

## Module Boundaries

### api/
Public entry points and user-facing API.

Owns:
- `from_sql`, `from_s3`
- user-facing builder interfaces

---

### builders/
Fluent builder objects that collect configuration.

Owns:
- SQLSourceBuilder
- S3SourceBuilder
- destination chaining (`to_sql`, `to_s3`, `to_sftp`)
- user configuration methods (`with_incremental`, etc.)

---

### core/
Core domain models and shared logic.

Owns:
- LoadPlan
- SourceConfig
- DestinationConfig
- ExtractConfig
- LoadConfig
- validation logic (models are **`dataclasses`** per **`TECH.md`**)

---

### adapters/
Integration with external systems.

Owns:
- DltAdapter (ONLY execution engine)
- mapping LoadPlan → dlt pipeline, dlt sources, and dlt destinations

---

### connectors/
Source-specific **wiring** into dlt (not a parallel extractor). Aligns with PRODUCT: SQL and S3 sources are dlt-backed.

Owns:
- helpers to express **Redshift** / **PostgreSQL** table-or-query inputs as dlt source/resource material the adapter runs
- helpers to express S3 path/glob inputs as dlt filesystem-oriented source material the adapter runs

Note:
- connectors must NOT perform bulk extract or I/O outside a dlt-driven pipeline
- no business logic; thin translation from `SourceConfig` (and related options) into what the adapter attaches to dlt

---

### results/
Execution results and metadata.

Owns:
- LoadResult
- result formatting
- summary helpers

---

### utils/
Shared utilities.

Owns:
- format detection
- path parsing
- schema helpers
- credential helpers
- **JSON→JSONL** normalization for S3 `.json` inputs (stdlib `json` only; see **`PRODUCT.md`** / **`spec/mvp/DESIGN.md`**)

---

## Dependency Rules

Strict dependency flow:

```text
api → builders → core → adapters → external (dlt)
             ↘ connectors ↗
```

Connectors only shape dlt sources from config; extract/load runs inside adapters + dlt.