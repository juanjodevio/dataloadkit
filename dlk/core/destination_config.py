"""Configuration for the load destination."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator

from dlk.core.types import (
    FILESYSTEM_WRITE_FORMATS,
    DestinationType,
    FileFormat,
    SqlDialect,
)


class DestinationConfig(BaseModel):
    """Describes where and how to write data."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    destination_type: DestinationType
    dataset_name: str
    table_name: str
    connection_string: str | None = None
    filesystem_url: str | None = None
    file_format: FileFormat | None = None
    credentials: dict[str, Any] | None = None
    sql_dialect: SqlDialect | None = None

    @model_validator(mode="after")
    def _check_destination_invariants(self) -> DestinationConfig:
        if not (self.dataset_name and str(self.dataset_name).strip()):
            raise ValueError(
                "destination.dataset_name is required and must be non-empty",
            )
        if not (self.table_name and str(self.table_name).strip()):
            raise ValueError(
                "destination.table_name is required and must be non-empty",
            )

        if self.destination_type is DestinationType.SQL:
            if not (self.connection_string and str(self.connection_string).strip()):
                raise ValueError(
                    "destination.connection_string is required and must be non-empty",
                )
            if self.sql_dialect is None:
                raise ValueError(
                    "destination.sql_dialect is required when destination_type is sql",
                )
            if self.filesystem_url is not None and str(self.filesystem_url).strip():
                raise ValueError(
                    "destination.filesystem_url must be unset when destination_type is sql",
                )
            if self.file_format is not None:
                raise ValueError(
                    "destination.file_format must be unset when destination_type is sql",
                )
        elif self.destination_type in (DestinationType.S3, DestinationType.SFTP):
            if not (self.filesystem_url and str(self.filesystem_url).strip()):
                raise ValueError(
                    "destination.filesystem_url is required and must be non-empty",
                )
            if self.sql_dialect is not None:
                raise ValueError(
                    "destination.sql_dialect must be unset for non-sql destinations",
                )
            if self.connection_string is not None and str(self.connection_string).strip():
                raise ValueError(
                    "destination.connection_string must be unset when destination_type is "
                    f"{self.destination_type.value}",
                )
            if self.file_format is not None and self.file_format not in FILESYSTEM_WRITE_FORMATS:
                allowed = sorted(f.value for f in FILESYSTEM_WRITE_FORMATS)
                raise ValueError(
                    "destination.file_format for s3/sftp must be one of "
                    f"{allowed}; got {self.file_format.value!r}",
                )
        else:
            raise ValueError(f"unsupported destination_type: {self.destination_type!r}")
        return self
