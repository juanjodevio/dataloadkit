"""Configuration for the load destination."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from dlk.core.types import DestinationType, FileFormat, SqlDialect


@dataclass(frozen=True)
class DestinationConfig:
    """Describes where and how to write data."""

    destination_type: DestinationType
    dataset_name: str
    table_name: str
    connection_string: str | None = None
    filesystem_url: str | None = None
    file_format: FileFormat | None = None
    credentials: Mapping[str, Any] | None = None
    sql_dialect: SqlDialect | None = None
