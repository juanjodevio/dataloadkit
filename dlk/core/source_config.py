"""Configuration for the data source side of a load."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from dlk.core.types import FileFormat, SourceType, SqlDialect


@dataclass(frozen=True)
class SourceConfig:
    """Describes where and how to read source data."""

    source_type: SourceType
    connection_string: str | None = None
    s3_path: str | None = None
    table_or_query: str | None = None
    glob_pattern: str | None = None
    file_format: FileFormat | None = None
    credentials: Mapping[str, Any] | None = None
    sql_dialect: SqlDialect | None = None
