"""Validation rules for load plans (Pydantic model validators)."""

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
    WriteMode,
)
from pydantic import ValidationError


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
    _valid_sql_to_sql()


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
    assert plan.pipeline_name == "s3-load"


def test_pipeline_name_required() -> None:
    base = _valid_sql_to_sql()
    with pytest.raises(ValidationError, match="pipeline_name"):
        LoadPlan(
            pipeline_name="   ",
            source=base.source,
            destination=base.destination,
            extract=base.extract,
            load=base.load,
        )


def test_sql_source_requires_dialect_and_connection() -> None:
    with pytest.raises(ValidationError, match="sql_dialect"):
        LoadPlan(
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


def test_sql_source_rejects_s3_path() -> None:
    with pytest.raises(ValidationError, match="s3_path"):
        LoadPlan(
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


def test_sql_source_rejects_s3_only_file_format() -> None:
    with pytest.raises(ValidationError, match="file_format"):
        SourceConfig(
            source_type=SourceType.SQL,
            connection_string="postgresql:///",
            table_or_query="SELECT 1",
            sql_dialect=SqlDialect.POSTGRES,
            file_format=FileFormat.PARQUET,
        )


def test_sql_source_rejects_s3_only_glob_pattern() -> None:
    with pytest.raises(ValidationError, match="glob_pattern"):
        SourceConfig(
            source_type=SourceType.SQL,
            connection_string="postgresql:///",
            table_or_query="SELECT 1",
            sql_dialect=SqlDialect.POSTGRES,
            glob_pattern="*.parquet",
        )


def test_s3_source_requires_path_and_no_sql_fields() -> None:
    with pytest.raises(ValidationError, match="s3_path"):
        SourceConfig(source_type=SourceType.S3, s3_path="")

    with pytest.raises(ValidationError, match="sql_dialect"):
        SourceConfig(
            source_type=SourceType.S3,
            s3_path="s3://b/",
            sql_dialect=SqlDialect.POSTGRES,
        )


def test_sql_destination_requires_dialect() -> None:
    with pytest.raises(ValidationError, match="sql_dialect"):
        LoadPlan(
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


def test_filesystem_destination_requires_url_no_sql_dialect() -> None:
    with pytest.raises(ValidationError, match="filesystem_url"):
        DestinationConfig(
            destination_type=DestinationType.SFTP,
            dataset_name="ds",
            table_name="t",
            filesystem_url="",
        )

    with pytest.raises(ValidationError, match="sql_dialect"):
        DestinationConfig(
            destination_type=DestinationType.S3,
            dataset_name="ds",
            table_name="t",
            filesystem_url="s3://out/",
            sql_dialect=SqlDialect.POSTGRES,
        )


def test_filesystem_destination_rejects_json_write_format() -> None:
    with pytest.raises(ValidationError, match="file_format"):
        DestinationConfig(
            destination_type=DestinationType.S3,
            dataset_name="ds",
            table_name="t",
            filesystem_url="s3://out/",
            file_format=FileFormat.JSON,
        )


def test_sql_destination_rejects_file_format() -> None:
    with pytest.raises(ValidationError, match="file_format"):
        DestinationConfig(
            destination_type=DestinationType.SQL,
            dataset_name="ds",
            table_name="t",
            connection_string="postgresql:///",
            sql_dialect=SqlDialect.POSTGRES,
            file_format=FileFormat.CSV,
        )


def test_incremental_requires_cursor() -> None:
    with pytest.raises(ValidationError, match="cursor_field"):
        ExtractConfig(incremental=True, cursor_field=None)


def test_merge_requires_primary_key() -> None:
    with pytest.raises(ValidationError, match="primary_key"):
        LoadPlan(
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


def test_merge_primary_key_stored_as_immutable_tuple() -> None:
    """Lists allow in-place mutation after validation; tuple does not."""
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
        extract=ExtractConfig(primary_key=["id", "region"]),
        load=LoadConfig(write_mode=WriteMode.MERGE),
    )
    pk = plan.extract.primary_key
    assert isinstance(pk, tuple)
    assert pk == ("id", "region")
    assert not hasattr(pk, "clear")


def test_chunk_size_positive() -> None:
    with pytest.raises(ValidationError, match="chunk_size"):
        ExtractConfig(chunk_size=0)


def test_revalidation_after_model_construct_fails() -> None:
    """Bypass model validation then fail on explicit re-validation."""
    src = SourceConfig.model_construct(
        source_type=SourceType.SQL,
        connection_string="postgresql:///",
        table_or_query="SELECT 1",
        sql_dialect=None,
    )
    plan = LoadPlan.model_construct(
        pipeline_name="ok",
        source=src,
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
    with pytest.raises(ValidationError):
        LoadPlan.model_validate(plan.model_dump(mode="python"))
