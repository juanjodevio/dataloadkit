"""Validation rules for :func:`validate_load_plan`."""

from __future__ import annotations

import pytest
from dlk.core import (
    DestinationConfig,
    DestinationType,
    ExtractConfig,
    FileFormat,
    LoadConfig,
    LoadPlan,
    SourceConfig,
    SourceType,
    SqlDialect,
    ValidationError,
    WriteMode,
    validate_load_plan,
)


def _valid_sql_to_sql() -> LoadPlan:
    return LoadPlan(
        pipeline_name="p",
        source=SourceConfig(
            source_type=SourceType.SQL,
            connection_string="postgresql:///",
            table_or_query="SELECT 1",
            sql_dialect=SqlDialect.POSTGRES,
        ),
        destination=DestinationConfig(
            destination_type=DestinationType.SQL,
            dataset_name="ds",
            table_name="t",
            connection_string="postgresql:///",
            sql_dialect=SqlDialect.POSTGRES,
        ),
        extract=ExtractConfig(),
        load=LoadConfig(),
    )


def test_validate_happy_sql_to_sql() -> None:
    validate_load_plan(_valid_sql_to_sql())


def test_validate_happy_s3_to_s3_parquet() -> None:
    plan = LoadPlan(
        pipeline_name="s3-load",
        source=SourceConfig(source_type=SourceType.S3, s3_path="s3://b/p/"),
        destination=DestinationConfig(
            destination_type=DestinationType.S3,
            dataset_name="ds",
            table_name="t",
            filesystem_url="s3://b/out/",
            file_format=FileFormat.PARQUET,
        ),
        extract=ExtractConfig(),
        load=LoadConfig(),
    )
    validate_load_plan(plan)


def test_pipeline_name_required() -> None:
    base = _valid_sql_to_sql()
    plan = LoadPlan(
        pipeline_name="   ",
        source=base.source,
        destination=base.destination,
        extract=base.extract,
        load=base.load,
    )
    with pytest.raises(ValidationError, match="pipeline_name"):
        validate_load_plan(plan)


def test_sql_source_requires_dialect_and_connection() -> None:
    plan = LoadPlan(
        pipeline_name="p",
        source=SourceConfig(
            source_type=SourceType.SQL,
            connection_string="postgresql:///",
            table_or_query="SELECT 1",
            sql_dialect=None,
        ),
        destination=DestinationConfig(
            destination_type=DestinationType.SQL,
            dataset_name="ds",
            table_name="t",
            connection_string="postgresql:///",
            sql_dialect=SqlDialect.POSTGRES,
        ),
        extract=ExtractConfig(),
        load=LoadConfig(),
    )
    with pytest.raises(ValidationError, match="sql_dialect"):
        validate_load_plan(plan)


def test_sql_source_rejects_s3_path() -> None:
    plan = LoadPlan(
        pipeline_name="p",
        source=SourceConfig(
            source_type=SourceType.SQL,
            connection_string="postgresql:///",
            table_or_query="SELECT 1",
            sql_dialect=SqlDialect.POSTGRES,
            s3_path="s3://x",
        ),
        destination=DestinationConfig(
            destination_type=DestinationType.SQL,
            dataset_name="ds",
            table_name="t",
            connection_string="postgresql:///",
            sql_dialect=SqlDialect.POSTGRES,
        ),
        extract=ExtractConfig(),
        load=LoadConfig(),
    )
    with pytest.raises(ValidationError, match="s3_path"):
        validate_load_plan(plan)


def test_s3_source_requires_path_and_no_sql_fields() -> None:
    plan = LoadPlan(
        pipeline_name="p",
        source=SourceConfig(source_type=SourceType.S3, s3_path=""),
        destination=DestinationConfig(
            destination_type=DestinationType.SQL,
            dataset_name="ds",
            table_name="t",
            connection_string="postgresql:///",
            sql_dialect=SqlDialect.POSTGRES,
        ),
        extract=ExtractConfig(),
        load=LoadConfig(),
    )
    with pytest.raises(ValidationError, match="s3_path"):
        validate_load_plan(plan)

    plan2 = LoadPlan(
        pipeline_name="p",
        source=SourceConfig(
            source_type=SourceType.S3,
            s3_path="s3://b/",
            sql_dialect=SqlDialect.POSTGRES,
        ),
        destination=DestinationConfig(
            destination_type=DestinationType.SQL,
            dataset_name="ds",
            table_name="t",
            connection_string="postgresql:///",
            sql_dialect=SqlDialect.POSTGRES,
        ),
        extract=ExtractConfig(),
        load=LoadConfig(),
    )
    with pytest.raises(ValidationError, match="sql_dialect"):
        validate_load_plan(plan2)


def test_sql_destination_requires_dialect() -> None:
    plan = LoadPlan(
        pipeline_name="p",
        source=SourceConfig(
            source_type=SourceType.SQL,
            connection_string="postgresql:///",
            table_or_query="SELECT 1",
            sql_dialect=SqlDialect.POSTGRES,
        ),
        destination=DestinationConfig(
            destination_type=DestinationType.SQL,
            dataset_name="ds",
            table_name="t",
            connection_string="postgresql:///",
            sql_dialect=None,
        ),
        extract=ExtractConfig(),
        load=LoadConfig(),
    )
    with pytest.raises(ValidationError, match="sql_dialect"):
        validate_load_plan(plan)


def test_filesystem_destination_requires_url_no_sql_dialect() -> None:
    plan = LoadPlan(
        pipeline_name="p",
        source=SourceConfig(source_type=SourceType.S3, s3_path="s3://b/"),
        destination=DestinationConfig(
            destination_type=DestinationType.SFTP,
            dataset_name="ds",
            table_name="t",
            filesystem_url="",
        ),
        extract=ExtractConfig(),
        load=LoadConfig(),
    )
    with pytest.raises(ValidationError, match="filesystem_url"):
        validate_load_plan(plan)

    plan2 = LoadPlan(
        pipeline_name="p",
        source=SourceConfig(source_type=SourceType.S3, s3_path="s3://b/"),
        destination=DestinationConfig(
            destination_type=DestinationType.S3,
            dataset_name="ds",
            table_name="t",
            filesystem_url="s3://out/",
            sql_dialect=SqlDialect.POSTGRES,
        ),
        extract=ExtractConfig(),
        load=LoadConfig(),
    )
    with pytest.raises(ValidationError, match="sql_dialect"):
        validate_load_plan(plan2)


def test_filesystem_destination_rejects_json_write_format() -> None:
    plan = LoadPlan(
        pipeline_name="p",
        source=SourceConfig(source_type=SourceType.S3, s3_path="s3://b/"),
        destination=DestinationConfig(
            destination_type=DestinationType.S3,
            dataset_name="ds",
            table_name="t",
            filesystem_url="s3://out/",
            file_format=FileFormat.JSON,
        ),
        extract=ExtractConfig(),
        load=LoadConfig(),
    )
    with pytest.raises(ValidationError, match="file_format"):
        validate_load_plan(plan)


def test_sql_destination_rejects_file_format() -> None:
    plan = LoadPlan(
        pipeline_name="p",
        source=SourceConfig(
            source_type=SourceType.SQL,
            connection_string="postgresql:///",
            table_or_query="SELECT 1",
            sql_dialect=SqlDialect.POSTGRES,
        ),
        destination=DestinationConfig(
            destination_type=DestinationType.SQL,
            dataset_name="ds",
            table_name="t",
            connection_string="postgresql:///",
            sql_dialect=SqlDialect.POSTGRES,
            file_format=FileFormat.CSV,
        ),
        extract=ExtractConfig(),
        load=LoadConfig(),
    )
    with pytest.raises(ValidationError, match="file_format"):
        validate_load_plan(plan)


def test_incremental_requires_cursor() -> None:
    plan = LoadPlan(
        pipeline_name="p",
        source=SourceConfig(
            source_type=SourceType.SQL,
            connection_string="postgresql:///",
            table_or_query="SELECT 1",
            sql_dialect=SqlDialect.POSTGRES,
        ),
        destination=DestinationConfig(
            destination_type=DestinationType.SQL,
            dataset_name="ds",
            table_name="t",
            connection_string="postgresql:///",
            sql_dialect=SqlDialect.POSTGRES,
        ),
        extract=ExtractConfig(incremental=True, cursor_field=None),
        load=LoadConfig(),
    )
    with pytest.raises(ValidationError, match="cursor_field"):
        validate_load_plan(plan)


def test_merge_requires_primary_key() -> None:
    plan = LoadPlan(
        pipeline_name="p",
        source=SourceConfig(
            source_type=SourceType.SQL,
            connection_string="postgresql:///",
            table_or_query="SELECT 1",
            sql_dialect=SqlDialect.POSTGRES,
        ),
        destination=DestinationConfig(
            destination_type=DestinationType.SQL,
            dataset_name="ds",
            table_name="t",
            connection_string="postgresql:///",
            sql_dialect=SqlDialect.POSTGRES,
        ),
        extract=ExtractConfig(primary_key=None),
        load=LoadConfig(write_mode=WriteMode.MERGE),
    )
    with pytest.raises(ValidationError, match="primary_key"):
        validate_load_plan(plan)


def test_chunk_size_positive() -> None:
    plan = LoadPlan(
        pipeline_name="p",
        source=SourceConfig(
            source_type=SourceType.SQL,
            connection_string="postgresql:///",
            table_or_query="SELECT 1",
            sql_dialect=SqlDialect.POSTGRES,
        ),
        destination=DestinationConfig(
            destination_type=DestinationType.SQL,
            dataset_name="ds",
            table_name="t",
            connection_string="postgresql:///",
            sql_dialect=SqlDialect.POSTGRES,
        ),
        extract=ExtractConfig(chunk_size=0),
        load=LoadConfig(),
    )
    with pytest.raises(ValidationError, match="chunk_size"):
        validate_load_plan(plan)
