"""Cross-field validation for load plans."""

from __future__ import annotations

from dlk.core.plan import LoadPlan
from dlk.core.types import (
    FILESYSTEM_WRITE_FORMATS,
    DestinationType,
    FileFormat,
    SourceType,
    WriteMode,
)


class ValidationError(ValueError):
    """Raised when a :class:`LoadPlan` or nested config violates invariants."""


def _non_empty(value: str | None, field: str) -> str:
    if value is None or not str(value).strip():
        raise ValidationError(f"{field} is required and must be non-empty")
    return str(value).strip()


def validate_load_plan(plan: LoadPlan) -> None:
    """Validate ``plan`` before execution.

    Raises:
        ValidationError: if any invariant fails.
    """
    _non_empty(plan.pipeline_name, "pipeline_name")
    _validate_source(plan)
    _validate_destination(plan)
    _validate_extract_and_load(plan)


def _validate_source(plan: LoadPlan) -> None:
    src = plan.source
    if src.source_type is SourceType.SQL:
        _non_empty(src.connection_string, "source.connection_string")
        _non_empty(src.table_or_query, "source.table_or_query")
        if src.sql_dialect is None:
            raise ValidationError("source.sql_dialect is required when source_type is sql")
        if src.s3_path is not None and str(src.s3_path).strip():
            raise ValidationError("source.s3_path must be unset when source_type is sql")
    elif src.source_type is SourceType.S3:
        _non_empty(src.s3_path, "source.s3_path")
        if src.sql_dialect is not None:
            raise ValidationError("source.sql_dialect must be unset when source_type is s3")
        if src.connection_string is not None and str(src.connection_string).strip():
            raise ValidationError("source.connection_string must be unset when source_type is s3")
        if src.table_or_query is not None and str(src.table_or_query).strip():
            raise ValidationError("source.table_or_query must be unset when source_type is s3")
    else:  # pragma: no cover - enum exhaustiveness
        raise ValidationError(f"unsupported source_type: {src.source_type!r}")

    if src.file_format is not None and not isinstance(src.file_format, FileFormat):
        raise ValidationError("source.file_format must be a FileFormat value when set")


def _validate_destination(plan: LoadPlan) -> None:
    dest = plan.destination
    _non_empty(dest.dataset_name, "destination.dataset_name")
    _non_empty(dest.table_name, "destination.table_name")

    if dest.destination_type is DestinationType.SQL:
        _non_empty(dest.connection_string, "destination.connection_string")
        if dest.sql_dialect is None:
            raise ValidationError(
                "destination.sql_dialect is required when destination_type is sql"
            )
        if dest.filesystem_url is not None and str(dest.filesystem_url).strip():
            raise ValidationError(
                "destination.filesystem_url must be unset when destination_type is sql"
            )
        if dest.file_format is not None:
            raise ValidationError(
                "destination.file_format must be unset when destination_type is sql"
            )
    elif dest.destination_type in (DestinationType.S3, DestinationType.SFTP):
        _non_empty(dest.filesystem_url, "destination.filesystem_url")
        if dest.sql_dialect is not None:
            raise ValidationError(
                "destination.sql_dialect must be unset for non-sql destinations"
            )
        if dest.connection_string is not None and str(dest.connection_string).strip():
            raise ValidationError(
                "destination.connection_string must be unset when destination_type is "
                f"{dest.destination_type.value}"
            )
        if dest.file_format is not None and dest.file_format not in FILESYSTEM_WRITE_FORMATS:
            raise ValidationError(
                "destination.file_format for s3/sftp must be one of "
                f"{sorted(f.value for f in FILESYSTEM_WRITE_FORMATS)}; "
                f"got {dest.file_format.value!r}"
            )
    else:  # pragma: no cover
        raise ValidationError(f"unsupported destination_type: {dest.destination_type!r}")


def _validate_extract_and_load(plan: LoadPlan) -> None:
    ext = plan.extract
    if ext.incremental:
        _non_empty(ext.cursor_field, "extract.cursor_field (required when incremental is true)")

    if ext.chunk_size is not None and ext.chunk_size <= 0:
        raise ValidationError("extract.chunk_size must be positive when set")

    if plan.load.write_mode is WriteMode.MERGE:
        pk = ext.primary_key
        if not pk or not all(str(c).strip() for c in pk):
            raise ValidationError(
                "extract.primary_key must be a non-empty list of non-empty strings "
                "when write_mode is merge"
            )
