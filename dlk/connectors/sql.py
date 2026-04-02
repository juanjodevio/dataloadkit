"""Shape SQL source configs into dlt ``sql_table`` keyword arguments (no I/O)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable

from dlt.common.libs.sql_alchemy import sa
from dlt.extract import Incremental

from dlk.core.extract_config import ExtractConfig
from dlk.core.source_config import SourceConfig
from dlk.core.types import SourceType, SqlDialect

# First simple identifier or dotted identifier after FROM (Postgres / Redshift friendly).
_FROM_TABLE_RE = re.compile(
    r"(?is)\bfrom\s+(?:only\s+)?(?P<ident>(?:\"[^\"]+\"|`[^`]+`|[\w.]+))",
)


def _default_engine_kwargs(dialect: SqlDialect) -> dict[str, Any]:
    """Dialect-specific kwargs for ``sqlalchemy.create_engine`` (no connection I/O here).

    dlt uses the same ``sql_table`` / ``sql_database`` API for both engines; differences
    are mostly connection URL and optional driver behavior.
    """
    if dialect is SqlDialect.POSTGRES:
        return {}
    if dialect is SqlDialect.REDSHIFT:
        # Distinct, low-risk default so adapters/tests can branch on Redshift meaningfully.
        return {"connect_args": {"application_name": "dataloadkit-redshift"}}
    raise ValueError(f"unsupported sql_dialect for SQL connector: {dialect!r}")


def _looks_like_sql_query(table_or_query: str) -> bool:
    t = table_or_query.strip()
    if not t:
        return False
    head = t.lstrip().upper()
    if head.startswith(("SELECT", "WITH", "(", "VALUES")):
        return True
    if any(ch in t for ch in "\n\t;"):
        return True
    # More than a single bare identifier (e.g. "schema.table" is still table-mode).
    if " " in t:
        return True
    return False


def _strip_sql_ident(raw: str) -> str:
    s = raw.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        return s[1:-1]
    if len(s) >= 2 and s[0] == "`" and s[-1] == "`":
        return s[1:-1]
    return s


def _split_schema_and_table(qualified: str) -> tuple[str | None, str]:
    q = _strip_sql_ident(qualified)
    if "." in q:
        schema, name = q.rsplit(".", 1)
        return (_strip_sql_ident(schema) or None, _strip_sql_ident(name))
    return (None, q)


def _infer_from_clause_table(sql: str) -> str | None:
    m = _FROM_TABLE_RE.search(sql)
    if not m:
        return None
    return _strip_sql_ident(m.group("ident"))


def _make_query_adapter(sql: str) -> Callable[..., Any]:
    """Return a ``query_adapter_callback`` compatible with dlt (2- or 4-arg forms)."""

    def adapter(*args: Any) -> Any:
        return sa.text(sql)

    return adapter


@dataclass(frozen=True)
class SqlSourceMaterial:
    """Keyword arguments for ``dlt.sources.sql_database.sql_table`` (plus metadata).

    The adapter is responsible for calling ``sql_table(**as_sql_table_kwargs())``.
    This module does not open connections or run queries.
    """

    credentials: str
    table: str
    schema: str | None
    incremental: Incremental[Any] | None
    primary_key: tuple[str, ...] | None
    chunk_size: int
    defer_table_reflect: bool
    query_adapter_callback: Callable[..., Any] | None
    engine_kwargs: dict[str, Any]
    sql_dialect: SqlDialect

    def as_sql_table_kwargs(self) -> dict[str, Any]:
        """Flatten into kwargs accepted by ``sql_table``."""
        out: dict[str, Any] = {
            "credentials": self.credentials,
            "table": self.table,
            "chunk_size": self.chunk_size,
            "engine_kwargs": self.engine_kwargs,
            "defer_table_reflect": self.defer_table_reflect,
        }
        if self.schema is not None:
            out["schema"] = self.schema
        if self.incremental is not None:
            out["incremental"] = self.incremental
        if self.primary_key is not None:
            out["primary_key"] = list(self.primary_key)
        if self.query_adapter_callback is not None:
            out["query_adapter_callback"] = self.query_adapter_callback
        return out


def build_sql_source(
    source_config: SourceConfig,
    extract_config: ExtractConfig,
) -> SqlSourceMaterial:
    """Map core SQL source + extract options to dlt ``sql_table`` configuration.

    Table mode: ``table_or_query`` is a bare or qualified table name (no SQL keywords).
    Query mode: ``table_or_query`` is a SQL string; a table is inferred from the first
    ``FROM`` clause for reflection and incremental cursor validation; the executed query
    is the full string via ``query_adapter_callback``.
    """
    if source_config.source_type is not SourceType.SQL:
        raise ValueError("build_sql_source requires SourceConfig with source_type sql")
    assert source_config.connection_string is not None
    assert source_config.sql_dialect is not None
    assert source_config.table_or_query is not None

    dialect = source_config.sql_dialect
    engine_kwargs = dict(_default_engine_kwargs(dialect))
    tq = source_config.table_or_query.strip()

    incremental: Incremental[Any] | None = None
    if extract_config.incremental:
        assert extract_config.cursor_field is not None
        incremental = Incremental(extract_config.cursor_field)

    pk = extract_config.primary_key
    chunk_size = extract_config.chunk_size if extract_config.chunk_size is not None else 50000

    if _looks_like_sql_query(tq):
        inferred = _infer_from_clause_table(tq)
        if inferred is None:
            raise ValueError(
                "table_or_query looks like SQL but no FROM clause could be inferred "
                "for reflection; use a table name in table_or_query or include a FROM clause",
            )
        schema, table = _split_schema_and_table(inferred)
        return SqlSourceMaterial(
            credentials=source_config.connection_string,
            table=table,
            schema=schema,
            incremental=incremental,
            primary_key=pk,
            chunk_size=chunk_size,
            defer_table_reflect=False,
            query_adapter_callback=_make_query_adapter(tq),
            engine_kwargs=engine_kwargs,
            sql_dialect=dialect,
        )

    schema, table = _split_schema_and_table(tq)
    return SqlSourceMaterial(
        credentials=source_config.connection_string,
        table=table,
        schema=schema,
        incremental=incremental,
        primary_key=pk,
        chunk_size=chunk_size,
        defer_table_reflect=False,
        query_adapter_callback=None,
        engine_kwargs=engine_kwargs,
        sql_dialect=dialect,
    )
