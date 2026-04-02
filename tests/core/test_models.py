"""Dataclass construction, defaults, and annotations."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

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
from dlk.results import LoadResult


def test_source_config_sql_defaults() -> None:
    s = SourceConfig(
        source_type=SourceType.SQL,
        connection_string="postgresql://localhost/db",
        table_or_query="public.users",
        sql_dialect=SqlDialect.POSTGRES,
    )
    assert s.glob_pattern is None
    assert s.file_format is None
    assert s.credentials is None
    assert s.s3_path is None


def test_source_config_s3_with_formats() -> None:
    s = SourceConfig(
        source_type=SourceType.S3,
        s3_path="s3://bucket/prefix/",
        file_format=FileFormat.JSON,
    )
    assert s.file_format is FileFormat.JSON


def test_destination_config_filesystem() -> None:
    d = DestinationConfig(
        destination_type=DestinationType.S3,
        dataset_name="ds",
        table_name="out",
        filesystem_url="s3://bucket/out/",
        file_format=FileFormat.PARQUET,
    )
    assert d.sql_dialect is None


def test_extract_load_config_defaults() -> None:
    e = ExtractConfig()
    assert e.incremental is False
    assert e.cursor_field is None
    assert e.chunk_size is None
    assert e.primary_key is None

    load_cfg = LoadConfig()
    assert load_cfg.write_mode is WriteMode.APPEND
    assert load_cfg.partitioning is None


def test_load_plan_is_frozen() -> None:
    plan = LoadPlan(
        pipeline_name="pipe",
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
    assert plan.pipeline_name == "pipe"
    with pytest.raises(FrozenInstanceError):
        plan.pipeline_name = "other"  # type: ignore[misc]


def test_load_result_fields() -> None:
    r = LoadResult(success=True, row_count=10, execution_time=1.5)
    assert r.error_message is None
    assert r.raw_metadata is None

    r2 = LoadResult(
        success=False,
        error_message="boom",
        raw_metadata={"trace": "x"},
    )
    assert r2.row_count is None
