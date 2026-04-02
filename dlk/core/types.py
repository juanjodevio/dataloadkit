"""Enumerations and shared literals for core configuration."""

from __future__ import annotations

from enum import Enum


class SourceType(str, Enum):
    """Where data is read from."""

    SQL = "sql"
    S3 = "s3"


class DestinationType(str, Enum):
    """Where data is written."""

    SQL = "sql"
    S3 = "s3"
    SFTP = "sftp"


class SqlDialect(str, Enum):
    """SQL engine wiring (dlt Redshift vs Postgres source/destination)."""

    REDSHIFT = "redshift"
    POSTGRES = "postgres"


class WriteMode(str, Enum):
    """How rows are applied at the destination."""

    APPEND = "append"
    REPLACE = "replace"
    MERGE = "merge"


class FileFormat(str, Enum):
    """File format for S3 reads or filesystem writes.

    ``JSON`` is document JSON on read; it triggers JSON→JSONL preprocessing before dlt’s JSONL path.
    """

    PARQUET = "parquet"
    CSV = "csv"
    JSONL = "jsonl"
    JSON = "json"


# Formats allowed for S3/SFTP structured dataset writes (not document JSON).
FILESYSTEM_WRITE_FORMATS: frozenset[FileFormat] = frozenset(
    {FileFormat.PARQUET, FileFormat.CSV, FileFormat.JSONL}
)
