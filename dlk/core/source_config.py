"""Configuration for the data source side of a load."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator

from dlk.core.types import FileFormat, SourceType, SqlDialect


class SourceConfig(BaseModel):
    """Describes where and how to read source data."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source_type: SourceType
    connection_string: str | None = None
    s3_path: str | None = None
    table_or_query: str | None = None
    glob_pattern: str | None = None
    file_format: FileFormat | None = None
    credentials: dict[str, Any] | None = None
    sql_dialect: SqlDialect | None = None

    @model_validator(mode="after")
    def _check_source_invariants(self) -> SourceConfig:
        if self.source_type is SourceType.SQL:
            if not (self.connection_string and str(self.connection_string).strip()):
                raise ValueError(
                    "source.connection_string is required and must be non-empty",
                )
            if not (self.table_or_query and str(self.table_or_query).strip()):
                raise ValueError(
                    "source.table_or_query is required and must be non-empty",
                )
            if self.sql_dialect is None:
                raise ValueError("source.sql_dialect is required when source_type is sql")
            if self.s3_path is not None:
                raise ValueError("source.s3_path must be unset when source_type is sql")
            if self.glob_pattern is not None:
                raise ValueError(
                    "source.glob_pattern must be unset when source_type is sql",
                )
            if self.file_format is not None:
                raise ValueError(
                    "source.file_format must be unset when source_type is sql",
                )
        elif self.source_type is SourceType.S3:
            if not (self.s3_path and str(self.s3_path).strip()):
                raise ValueError("source.s3_path is required and must be non-empty")
            if self.sql_dialect is not None:
                raise ValueError("source.sql_dialect must be unset when source_type is s3")
            if self.connection_string is not None:
                raise ValueError(
                    "source.connection_string must be unset when source_type is s3",
                )
            if self.table_or_query is not None:
                raise ValueError(
                    "source.table_or_query must be unset when source_type is s3",
                )
        else:
            raise ValueError(f"unsupported source_type: {self.source_type!r}")
        return self
