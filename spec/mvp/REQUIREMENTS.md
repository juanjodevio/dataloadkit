---
status: DRAFT
---

# Requirements

## Purpose
Define the functional and non-functional requirements for dataloadkit (dlk) MVP, a Python library that enables simple and consistent data ingestion from SQL (**Redshift** and **PostgreSQL**) and S3 into SQL (**Redshift** and **PostgreSQL**), S3, and SFTP destinations using a fluent API where **sources and destinations are dlt-backed** (see **`PRODUCT.md`**, **`spec/mvp/DESIGN.md`**).

---

## Scope
Included:

- SQL (**Redshift** and **PostgreSQL**) as source
- S3 as source
- SQL (**Redshift** and **PostgreSQL**) as destination
- S3 (filesystem) as destination
- SFTP (filesystem via dlt) as destination
- Fluent Python API (`dlk.from_*().to_*().load()`)
- Incremental loading (SQL)
- Write modes (append, replace, merge)
- Structured dataset output

---

## Out of Scope

- SFTP as source
- Streaming ingestion
- Transformations (dbt-like logic)
- Multi-source joins
- CLI or UI
- Orchestration
- Raw file transfer semantics
- Full connector ecosystem

---

## Actors

- Data Engineer (primary)
- Backend Engineer (secondary)
- External systems (Redshift, PostgreSQL, S3, SFTP server, dlt runtime)

---

## Preconditions

- Valid credentials exist for:
  - SQL source/destination (including SQLAlchemy-compatible connections where used; see **`PRODUCT.md`** / **`TECH.md`**)
  - AWS (S3), IAM preferred
  - SFTP (if used; password or key via filesystem config)
- Network access to sources and destinations
- dlt is installed and configured
- Source data exists and is accessible

---

## Functional Requirements

### Ubiquitous Requirements

- The system shall expose a fluent API for defining ingestion pipelines.
- The system shall execute **all extraction and loading** through dlt (dlt sources and dlt destinations; no parallel extract/load engine).
- The system shall validate required configuration before execution.
- The system shall return a structured `LoadResult` after execution.
- The system shall support SQL (**Redshift** and **PostgreSQL**) and S3 as sources, each mapped to dlt source patterns with an explicit **SQL engine** selection on **`SourceConfig`**.
- The system shall support SQL (**Redshift** and **PostgreSQL** via dlt **`redshift`** vs **`postgres`** destinations), S3 (filesystem), and SFTP (filesystem via dlt/fsspec) as destinations, each mapped to dlt destination patterns with an explicit **SQL engine** on **`DestinationConfig`** where applicable.
- The system shall support **JSON** S3 inputs only through **JSON→JSONL** normalization (stdlib `json`) before dlt’s JSONL reader, as specified in **`PRODUCT.md`** and **`spec/mvp/DESIGN.md`**.

---

### Event-Driven Requirements

- When a user calls `.load()`, the system shall validate the configuration and execute the pipeline.
- When a SQL source is defined, the system shall extract data via dlt using the provided query or table and the configured **Redshift** vs **PostgreSQL** source wiring.
- When an S3 source is defined, the system shall read files via dlt from the provided path(s), including glob patterns when configured.
- When a destination is defined, the system shall route data to the appropriate dlt destination (**`redshift`**, **`postgres`**, or filesystem as configured).
- When execution completes, the system shall return execution metadata.
- When execution fails, the system shall raise a meaningful error.

---

### Conditional Requirements

- If incremental loading is configured, the system shall load only new or updated records.
- If write mode is `replace`, the system shall overwrite existing data.
- If write mode is `append`, the system shall append data.
- If write mode is `merge`, the system shall upsert based on a configured primary key (primary key shall be required when merge is selected, per **`PRODUCT.md`**).
- If SFTP destination is used, the system shall write data using filesystem protocol via dlt.
- If S3 source input format is not specified, the system shall infer format from file extension where possible (CSV, JSONL, JSON, Parquet per **`PRODUCT.md`**); **`.json`** shall trigger **JSON→JSONL** preprocessing before dlt’s JSONL reader.

---

### State-Driven Requirements

- While execution is in progress, the system shall maintain a consistent pipeline state.
- While validation fails, the system shall prevent execution.
- While data is being processed, the system shall not expose partial results.

---

### Optional / Feature-Scoped Requirements

- Where SQL incremental loading is enabled, the system shall require a cursor field.
- Where S3 source is used, the system shall support glob patterns and multiple files per run where applicable (per **`PRODUCT.md`**).
- Where S3 source format is **JSON** (explicit or inferred from `.json`), the system shall normalize content to **JSONL** using **stdlib `json` only** (single object → one line; array of objects → one line per object), then load via dlt’s **JSONL** filesystem reader (per **`spec/mvp/DESIGN.md`**).
- Where filesystem destinations (S3, SFTP) are used, the system shall output structured datasets (not raw file-copy semantics).
- Where format is specified for filesystem destinations, the system shall respect the requested output format (Parquet, CSV, JSONL per **`PRODUCT.md`**).
- Where S3 filesystem destination is used, the system shall support partitioning and dataset layout options aligned with **`PRODUCT.md`**.

---

## Data Requirements

- Configuration and plan types shall be **stdlib `dataclasses`** with validation in `core/` (see **`PRODUCT.md`**, **`TECH.md`**, **`spec/mvp/DESIGN.md`**).
- The system shall define:
  - `SourceConfig`
  - `DestinationConfig`
  - `ExtractConfig`
  - `LoadConfig`
  - `LoadPlan`
  - `LoadResult`

- The system shall support:
  - dataset names
  - table names
  - file paths (S3/SFTP)
  - format types (parquet, csv, jsonl, json for S3 source where `json` means “document JSON” before JSONL normalization)

- The system shall not persist user configuration internally.

- The system shall preserve:
  - row counts
  - execution metadata
  - error messages

---

## Interface / Contract Requirements

### Public API (illustrative)

```python
dlk.from_sql(..., sql_dialect=...)  # Redshift vs PostgreSQL (source)
dlk.from_s3(...)
.to_sql(..., sql_dialect=...)  # Redshift vs PostgreSQL (SQL destination)
.to_s3(...)
.to_sftp(...)
.with_incremental(...)
.with_write_mode(...)
.with_primary_key(...)
.with_format(...)
.load()
```

### Validation rules

- Required parameters shall be present before `.load()`.
- Invalid combinations shall raise clear, actionable errors.
- A destination shall be defined before execution.

### File formats

- **S3 source (read):** CSV, JSONL, Parquet via dlt filesystem readers; **JSON** (`.json` / explicit) via **JSON→JSONL preprocessing** (stdlib `json`) then dlt **JSONL** reader (per **`PRODUCT.md`**, **`spec/mvp/DESIGN.md`**).
- **Filesystem destinations (S3, SFTP write):** Parquet, CSV, JSONL (per **`PRODUCT.md`**).

---

## Non-Functional Requirements

### Performance

- The system shall support **chunked reads** for large SQL sources where applicable (per **`PRODUCT.md`**), without introducing a separate streaming-ingestion product feature (streaming remains out of scope).
- The system shall complete typical ingestion jobs in reasonable time relative to source size and network (no fixed SLO in MVP).

### Reliability

- The system shall not silently fail.
- The system shall propagate dlt errors with sufficient context to debug (see **`TECH.md`**).
- The system shall ensure idempotent behavior where supported by dlt.

### Security / privacy

- The system shall not store credentials (see **`PRODUCT.md`** / **`TECH.md`**).
- The system shall not log sensitive information.
- The system shall support secure authentication mechanisms (IAM for AWS, keys/passwords for SFTP, least-privilege-friendly SQL access).

### Usability

- The system shall allow a user to define a typical pipeline in a small amount of code (target: on the order of 10 lines; success metric in **`PRODUCT.md`** emphasizes time-to-first-load).
- The system shall provide clear and actionable error messages.
- The system shall maintain a consistent API across sources and destinations.

### Observability

- The system shall use standard Python logging for execution steps (per **`TECH.md`**).
- The system shall expose execution results via `LoadResult`.
- The system shall allow users to debug failures through logs and propagated errors.

---

## Acceptance criteria

Aligned with **`PRODUCT.md`** MVP release standard:

- A user can load data from SQL to SQL (**Postgres → Postgres** and **Redshift → Redshift** paths demonstrably work).
- A user can load data from SQL to S3.
- A user can load data from S3 to SQL (**PostgreSQL** and **Redshift** targets per config).
- A user can load data from SQL or S3 to SFTP.
- A user can configure incremental loading (SQL).
- A user can configure write modes (append, replace, merge).
- A user receives a `LoadResult` after execution.
- Documentation and examples exist for the above paths.

---

## Edge cases

- Invalid credentials
- Empty datasets
- Large datasets exceeding memory
- Unsupported file formats
- Malformed JSON or JSON array elements that are not objects (JSON→JSONL preprocessing)
- Invalid SQL query
- Missing required parameters
- Network failures during execution
- SFTP connection issues
- Schema mismatch between source and destination

---

## Assumptions

- Users are familiar with Python.
- Users understand basic data concepts (tables, files, schemas).
- dlt handles low-level pipeline execution; dlk does not replace dlt.

---

## Open questions

- Should S3 incremental loading be supported in MVP?
- Should `LoadResult` expose raw dlt metadata?
- Should schema validation be enforced upfront?
- How much control over file layout should users have for filesystem destinations?

---

## Notes

- Simplicity is prioritized over flexibility.
- All flows must go through dlt (see **STRUCTURE.md**, **spec/mvp/DESIGN.md**).
- Filesystem destinations (S3, SFTP) are structured datasets, not raw file copies.
- API consistency is critical to adoption.