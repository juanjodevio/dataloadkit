"""SQL connector: dlt ``sql_table`` kwargs shape (no database I/O)."""

from __future__ import annotations

import pytest
from dlk.connectors.sql import SqlSourceMaterial, build_sql_source
from dlk.core import ExtractConfig, SourceConfig, SourceType, SqlDialect
from dlt.common.libs.sql_alchemy import sa
from dlt.extract import Incremental


def _sql_src(table_or_query: str, dialect: SqlDialect = SqlDialect.POSTGRES) -> SourceConfig:
    return SourceConfig(
        source_type=SourceType.SQL,
        connection_string="postgresql://user:pass@localhost:5432/db",
        table_or_query=table_or_query,
        sql_dialect=dialect,
    )


def test_table_mode_plain_postgres() -> None:
    m = build_sql_source(_sql_src("users"), ExtractConfig())
    assert m.table == "users"
    assert m.schema is None
    assert m.query_adapter_callback is None
    assert m.incremental is None
    assert m.primary_key is None
    assert m.chunk_size == 50000
    assert m.engine_kwargs == {}
    assert m.sql_dialect is SqlDialect.POSTGRES


def test_table_mode_qualified_schema() -> None:
    m = build_sql_source(_sql_src("public.users"), ExtractConfig())
    assert m.schema == "public"
    assert m.table == "users"


def test_table_mode_redshift_engine_kwargs() -> None:
    m = _sql_src("events", SqlDialect.REDSHIFT)
    material = build_sql_source(m, ExtractConfig())
    assert material.engine_kwargs == {
        "connect_args": {"application_name": "dataloadkit-redshift"},
    }
    assert material.sql_dialect is SqlDialect.REDSHIFT


def test_query_mode_postgres() -> None:
    sql = "SELECT id, name FROM public.users WHERE active = true"
    m = build_sql_source(_sql_src(sql), ExtractConfig())
    assert m.schema == "public"
    assert m.table == "users"
    assert m.query_adapter_callback is not None
    out = m.query_adapter_callback(None, None)
    assert str(out) == sql


def test_query_mode_redshift_same_shape_plus_dialect_kwargs() -> None:
    sql = "SELECT id FROM analytics.events"
    m = build_sql_source(_sql_src(sql, SqlDialect.REDSHIFT), ExtractConfig())
    assert m.schema == "analytics"
    assert m.table == "events"
    assert m.engine_kwargs["connect_args"]["application_name"] == "dataloadkit-redshift"
    wrapped = m.query_adapter_callback(None, None, None, None)
    assert isinstance(wrapped, sa.sql.elements.TextClause)


def test_incremental_wraps_incremental() -> None:
    ext = ExtractConfig(incremental=True, cursor_field="updated_at")
    m = build_sql_source(_sql_src("orders"), ext)
    assert isinstance(m.incremental, Incremental)
    assert m.incremental.cursor_path == "updated_at"


def test_primary_key_passthrough() -> None:
    ext = ExtractConfig(primary_key=("id", "region"))
    m = build_sql_source(_sql_src("orders"), ext)
    assert m.primary_key == ("id", "region")
    kwargs = m.as_sql_table_kwargs()
    assert kwargs["primary_key"] == ["id", "region"]


def test_chunk_size_override() -> None:
    m = build_sql_source(_sql_src("t"), ExtractConfig(chunk_size=1000))
    assert m.chunk_size == 1000


def test_as_sql_table_kwargs_roundtrip_keys() -> None:
    m = SqlSourceMaterial(
        credentials="postgresql:///",
        table="t",
        schema="s",
        incremental=None,
        primary_key=None,
        chunk_size=50_000,
        defer_table_reflect=False,
        query_adapter_callback=None,
        engine_kwargs={},
        sql_dialect=SqlDialect.POSTGRES,
    )
    k = m.as_sql_table_kwargs()
    assert k["credentials"] == "postgresql:///"
    assert k["table"] == "t"
    assert k["schema"] == "s"
    assert k["chunk_size"] == 50_000
    assert k["defer_table_reflect"] is False
    assert "query_adapter_callback" not in k


def test_rejects_non_sql_source() -> None:
    s3 = SourceConfig(
        source_type=SourceType.S3,
        s3_path="s3://b/p/",
        file_format=None,
    )
    with pytest.raises(ValueError, match="source_type sql"):
        build_sql_source(s3, ExtractConfig())


def test_query_without_from_raises() -> None:
    with pytest.raises(ValueError, match="FROM clause"):
        build_sql_source(_sql_src("SELECT 1 AS x"), ExtractConfig())
