---
status: DRAFT
---

# Product

## Summary
dataloadkit (dlk) is a Python library that simplifies data ingestion by providing a clean, fluent API on top of dlt. **Sources and destinations are dlt-backed:** SQL (**Redshift** and **PostgreSQL**) and S3 inputs map to dlt sources; SQL, S3 (filesystem), and SFTP outputs map to dlt destinations—all behind a consistent, minimal interface.

## Vision
dataloadkit should become the default Python SDK for data ingestion. It aims to standardize how developers move and load data across systems while leveraging dlt for reliability, scalability, and state management.

## Problem Statement
Data engineers frequently need to move data between systems such as Redshift, PostgreSQL, S3, and remote endpoints like SFTP. Existing tools:

- require deep knowledge of frameworks like dlt
- are overly complex (Airbyte, Meltano)
- or lack a simple Python-first interface

Key problems:
- High cognitive overhead for simple ingestion tasks
- Repeated boilerplate across pipelines
- Inconsistent patterns across sources and destinations
- Lack of a unified abstraction for ingestion workflows

## Target Users

### Primary User
Data engineers working with Redshift, PostgreSQL, and S3 who need to build ingestion pipelines quickly using Python.

### Secondary User
- Backend engineers handling data workflows
- Analytics engineers building ingestion scripts

### Initial Market
- AWS-based data stacks
- Startups and mid-size companies
- Python-first engineering teams

## MVP Goal
Allow a developer to load data from SQL (**Redshift** or **PostgreSQL**) or S3 into SQL (**Redshift** or **PostgreSQL**), S3, or SFTP targets using a simple, fluent Python API where **every source and every destination is implemented through dlt** (dlt sources and dlt destinations), not custom extractors or writers beside dlt.

## Core Value Proposition
- Reduce ingestion complexity to a few lines of code
- Provide a consistent API across sources and destinations
- Rely on dlt for both extraction and loading (dlt-backed sources and destinations) without exposing dlt’s internal complexity
- Enable structured data loading into databases and filesystems

## MVP Scope

### Domain 1: SQL Source (Redshift & PostgreSQL, dlt-backed)
- Load from **Redshift** or **PostgreSQL** tables or queries (caller selects SQL engine via config; dlt `sql_database` / engine-appropriate wiring)
- Support incremental loading via cursor
- Support append, replace, merge semantics (as surfaced through dlt for the chosen source)

### Domain 2: S3 Source (dlt-backed)
- Load files from S3 paths
- Support **CSV, Parquet, JSONL, and JSON** as S3 inputs:
  - **CSV, Parquet, JSONL** map directly to dlt’s [filesystem verified source](https://dlthub.com/docs/dlt-ecosystem/verified-sources/filesystem/basic) readers.
  - **JSON** (`.json` or explicit format): MVP includes a **JSON→JSONL preprocessing** step using **stdlib `json` only**—normalize to newline-delimited JSON objects, then feed **dlt’s JSONL reader** (no second extract/load engine; no custom table extraction).
- Support glob patterns
- Infer schema when possible
- **JSON preprocessing limits (MVP):** the `.json` file must be readable in one pass by **`json.loads`** (whole document in memory); unsupported shapes (e.g. array of scalars, non-object array elements) fail with a clear error; document this limit in user-facing docs

### Domain 3: Destinations (dlt-backed)

#### SQL Destination
- Load into **Redshift** or **PostgreSQL** via dlt’s **`redshift`** vs **`postgres`** destinations (explicit per-target choice—see data model)
- Support dataset and table naming
- Support append, replace, merge

#### S3 Destination (filesystem via dlt)
- Write structured datasets using dlt filesystem destination
- Support Parquet, JSONL, and CSV formats
- Support partitioning and dataset layout

#### SFTP Destination (filesystem via dlt)
- Write structured datasets to SFTP using dlt filesystem destination
- Use SFTP URLs via fsspec-compatible configuration
- Support Parquet, JSONL, and CSV formats
- Managed dataset layout consistent with other filesystem destinations

## Out of Scope
- SFTP as a source
- **S3 JSON:** streaming parse of arbitrarily large single `.json` files without loading the document into memory (MVP preprocessing may require a documented size/memory bound)
- Raw file transfer or sync semantics
- Real-time or streaming ingestion
- Complex transformations
- Multi-source joins
- Orchestration (Airflow, Step Functions)
- CLI or UI
- Full connector ecosystem

## Core User Flow
1. User imports `dlk`
2. User defines a source (`from_sql` or `from_s3`)
3. User defines a destination (`to_sql`, `to_s3`, or `to_sftp`)
4. User configures optional parameters (incremental, format, write mode)
5. User calls `.load()`
6. dlk builds and executes a dlt pipeline
7. Data is loaded into destination
8. A result object is returned

## Functional Requirements

### Authentication and Access
- Support credentials via environment variables
- Support explicit credentials when needed
- Support:
  - SQLAlchemy connections
  - AWS credentials
  - SFTP credentials (password or key via filesystem config)

### Domain 1: SQL Source
- Map to dlt SQL/database source patterns for **Redshift** and **PostgreSQL** (engine selected via **`SourceConfig`** / `sql_dialect`)
- Accept table or query input
- Support incremental loading via cursor field
- Support chunked reads for large datasets
- Support primary key definition for merge operations

### Domain 2: S3 Source
- Map to dlt filesystem or S3-oriented source patterns as appropriate
- Accept S3 paths and glob patterns
- Support **CSV, Parquet, JSONL** (native dlt filesystem readers) and **JSON** via **JSON→JSONL preprocessing** then dlt’s JSONL reader
- Infer format from file extension where unambiguous (e.g. `.csv`, `.jsonl`, `.json`, `.parquet`); **`.json`** triggers preprocessing, **`.jsonl`** does not
- Support multiple file ingestion per run

### Domain 3: Destinations

#### SQL
- Map to dlt **`redshift`** or **`postgres`** destination per **`DestinationConfig.sql_dialect`**
- Support dataset and table naming
- Support write modes: append, replace, merge

#### S3
- Use dlt filesystem destination
- Support format selection (Parquet, JSONL, CSV)
- Support partitioning

#### SFTP
- Use dlt filesystem destination with SFTP protocol
- Support standard filesystem configuration via URL
- Support format selection
- Maintain consistent dataset layout with S3 destination

## AI Requirements
Not applicable for MVP.

## Security and Privacy Requirements
- Do not persist credentials internally
- Avoid logging sensitive data
- Support IAM-based access for AWS
- Support secure key-based authentication for SFTP
- Ensure compatibility with least-privilege setups

## Product Principles
- Simplicity over flexibility
- Opinionated defaults over configuration overload
- Python-first developer experience
- Transparent execution over hidden abstractions
- dlt-native, not dlt-replacement

## Data Model Overview
Implement as **Pydantic models** with validation in `core/` (see **`TECH.md`**).

- SourceConfig (SQL, S3)—each resolves to a dlt source; **SQL** sources carry **`sql_dialect`** (**Redshift** vs **PostgreSQL**) for correct dlt source wiring
- DestinationConfig (SQL, S3, SFTP)—each resolves to a dlt destination; **SQL** targets carry **`sql_dialect`** so the adapter selects **`dlt.destinations.redshift`** vs **`dlt.destinations.postgres`**
- ExtractConfig
- LoadConfig
- LoadPlan
- LoadResult

## Success Metrics
- Time to first successful load (< 5 minutes)
- Lines of code required per ingestion
- Number of successful pipeline executions
- Developer adoption (GitHub stars, installs)
- Reuse across projects

## Risks

### Product Risks
- API may not cover all edge cases
- Users may expect full ETL capabilities
- Misunderstanding of structured vs raw file behavior

### Technical Risks
- dlt API changes affecting compatibility
- Memory constraints for large datasets
- SFTP filesystem performance variability
- Schema inference inconsistencies

### Market Risks
- Competition from ingestion platforms (Airbyte, Meltano)
- Users preferring declarative tools over Python APIs
- Limited distribution initially

## Future Roadmap Ideas
- Add SFTP as source
- Transfer mode (S3 ↔ SFTP)
- Streaming ingestion
- CLI interface
- Connector plugins
- Observability integrations
- dbt integration

## Positioning
dataloadkit (dlk) is the easiest way to load data using Python.

It provides a clean, fluent API for ingestion powered by dlt, inspired by awswrangler.

## MVP Release Standard
- SQL → SQL works end-to-end (**Redshift** and **PostgreSQL** paths, including **Postgres → Postgres**)
- SQL → S3 works end-to-end
- S3 → SQL works end-to-end (to **Redshift** or **PostgreSQL** per config)
- SQL/S3 → SFTP works end-to-end
- Clear documentation and examples
- Robust and actionable error handling

## Implementation Guidance
- Keep public API minimal and fluent
- Use a unified LoadPlan abstraction
- Isolate dlt integration in a single adapter layer
- Treat **all sources and all destinations** consistently via dlt (no parallel non-dlt extract/load paths for MVP scope)
- For S3 reads, use dlt’s filesystem readers for **CSV, Parquet, and JSONL**; for **JSON** documents, use **stdlib `json`** only to normalize to **JSONL**, then the same dlt **JSONL** path—no custom extract engine or non-dlt loaders
- Optimize for developer experience over flexibility
- **Runtime:** target **CPython 3.9.2+** (below **3.15** per **`dlt`**); full matrix, dependencies, and dev tooling live in **`TECH.md`**
- **Packaging:** expose dlt’s optional stacks as **`dataloadkit`** optional extras (`redshift`, **`postgres`**, `filesystem`, `sftp`, bundled **`mvp`**) per **`TECH.md`**; document **`pip install dataloadkit[mvp]`** (or `uv add 'dataloadkit[mvp]'`) for the full MVP install (**includes PostgreSQL**)