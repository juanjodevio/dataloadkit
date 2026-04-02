---
status: DRAFT
---

# Design

## Goal
Design a minimal, fluent, and consistent Python API for `dataloadkit` (`dlk`) that allows developers to load data from SQL (Redshift) and S3 into SQL, S3, and SFTP destinations through a single dlt-backed execution path.

## Context
This feature is needed now to establish the first implementation-ready design for the MVP.

The product goal is to simplify common ingestion workflows that today require direct dlt knowledge and repetitive boilerplate. The current gap is not capability in dlt itself, but usability: developers need a smaller and more approachable API that covers common Redshift and S3-centric workflows without exposing dlt concepts too early.

This design addresses:
- repetitive ingestion code across projects
- cognitive overhead of raw dlt usage
- lack of a consistent source/destination builder model
- need for a stable internal architecture before implementation

## Scope Summary
In scope:
- source builders for SQL and S3
- destination builders for SQL, S3, and SFTP
- one fluent public API
- one internal execution model based on dlt
- a normalized `LoadPlan` that captures source, extraction, and destination config
- a `DltAdapter` that translates `LoadPlan` into executable dlt resources and pipeline runs
- result normalization into a `LoadResult`
- **JSON→JSONL preprocessing** for S3 `.json` inputs (stdlib `json` only; then dlt JSONL reader)

Out of scope:
- SFTP as a source
- raw file transfer semantics
- multiple execution engines
- CLI, UI, or daemon/service runtime
- streaming ingestion
- transformation framework
- orchestration features
- connector plugin system

## User / System Flow
Main flow:

1. User imports `dlk`
2. User creates a source via `dlk.from_sql(...)` or `dlk.from_s3(...)`
3. User chains a destination via `to_sql(...)`, `to_s3(...)`, or `to_sftp(...)`
4. User optionally adds execution modifiers such as:
   - `with_incremental(...)`
   - `with_write_mode(...)`
   - `with_primary_key(...)`
   - `with_format(...)` (S3 source: includes `json` vs `jsonl`—`json` selects preprocessing)
5. User calls `.load()`
6. Builder / `core` validates required config (dataclass invariants and cross-field rules)
7. Terminal step materializes a `LoadPlan` (`SourceConfig`, `DestinationConfig`, `ExtractConfig`, `LoadConfig`)
8. `DltAdapter` maps the `LoadPlan` to dlt pipeline + source/resource configuration (if S3 source format is **JSON**, run **JSON→JSONL** normalization first—see below)
9. dlt executes the load
10. dlk converts the execution output into `LoadResult`
11. User receives structured metadata about the run

## Solution Shape
The solution is a layered Python library with a small public API and a single internal execution path. It follows **`STRUCTURE.md`** (package layout under `dlk/`) and **`TECH.md`** (CPython 3.9+, `uv`, dlt-only execution, **dataclasses** for config/plan types). Product scope and acceptance are anchored in **`PRODUCT.md`**.

### Modules (see `STRUCTURE.md`)
- **`api/`** — `from_sql`, `from_s3`, and stable entrypoints that delegate to builders.
- **`builders/`** — `SQLSourceBuilder`, `S3SourceBuilder`, destination chaining (`to_sql`, `to_s3`, `to_sftp`), and modifiers (`with_incremental`, `with_write_mode`, `with_primary_key`, `with_format`, etc.).
- **`core/`** — `LoadPlan` and dataclass configs: `SourceConfig`, `DestinationConfig`, `ExtractConfig`, `LoadConfig`; validation before planning completes.
- **`connectors/`** — thin SQL/S3 → dlt source/resource wiring from `SourceConfig` (no extract outside dlt; used by the adapter).
- **`adapters/`** — `DltAdapter` only: maps `LoadPlan` to dlt pipeline + sources + destinations and runs execution.
- **`results/`** — `LoadResult` and helpers (normalized run metadata for callers).
- **`utils/`** — format detection, paths/globs, schema/credential helpers, and **JSON→JSONL normalization** (stdlib `json` only) shared by builders and the adapter.

### JSON → JSONL preprocessing (MVP)

**Why:** dlt’s filesystem source exposes **JSONL**, not arbitrary JSON documents. MVP still accepts `.json` by normalizing to JSONL so the **same dlt JSONL reader** runs—no second extract engine.

**Trigger:** `SourceConfig` / inferred extension indicates **JSON** (not **JSONL**).

**Behavior (stdlib `json` only):**
- **Single JSON object** → one output line (compact JSON object, UTF-8).
- **JSON array of objects** → one output line per element (each element must be a JSON object; otherwise fail with a clear error).

**Where it runs:** `utils/` exposes a pure function (e.g. `json_document_to_jsonl_lines(bytes | str) -> bytes` or generator of lines). **`DltAdapter`** (or the S3 connector wiring it calls) invokes this **before** building the resource dlt treats as **JSONL** (e.g. in-memory buffer or tempfile; document MVP memory bound in **`PRODUCT.md`**).

**Out of MVP:** incremental/streaming parse of huge `.json` without full-file read; arrays of non-objects.

### Data materialization
- Builders collect user input; validation errors surface before `.load()` commits.
- `.load()` (or equivalent terminal step) builds a **`LoadPlan`** that bundles `SourceConfig`, `DestinationConfig`, and extraction/load options (`ExtractConfig` / `LoadConfig` as in **`PRODUCT.md`**).
- **`DltAdapter`** uses **`connectors/`** for source shape and dlt for both extract and load—no second engine (per **`PRODUCT.md`** implementation guidance). For S3 **JSON**, the adapter applies **`utils/`** JSON→JSONL normalization first, then the same dlt **JSONL** extract path.

### Credentials and security
- Align with **`PRODUCT.md`** / **`TECH.md`**: env-based and explicit credentials; SQLAlchemy for SQL; AWS IAM preferred for S3; SFTP via fsspec-style URLs/config. dlk does not persist secrets; avoid logging sensitive values.

### Failure posture
- Validate early in builders/`core` where possible; on dlt failures, return or raise errors with enough context to act (maps to **`PRODUCT.md`** “robust and actionable error handling” and MVP release standard).

### MVP acceptance (cross-check)
End-to-end paths in **`PRODUCT.md`** MVP release standard must hold: SQL→SQL, SQL→S3, S3→SQL, SQL/S3→SFTP, plus docs/examples.

High-level request/response flow:

```text
User code
  -> dlk.from_sql(...) / dlk.from_s3(...)
  -> builder chain
  -> LoadPlan (SourceConfig, DestinationConfig, ExtractConfig, LoadConfig)
  -> DltAdapter (+ connectors/ for source wiring; JSON→JSONL if needed)
  -> dlt pipeline execution
  -> LoadResult
```
