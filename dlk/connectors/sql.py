"""Shape SQL source configs into dlt ``sql_table`` keyword arguments (no I/O)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable

from dlt.common.libs.sql_alchemy import sa
from dlt.extract import Incremental
from sqlalchemy.sql import literal_column, visitors
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.schema import Column as SAColumn
from sqlalchemy.sql.util import ClauseAdapter

from dlk.core.extract_config import ExtractConfig
from dlk.core.source_config import SourceConfig
from dlk.core.types import SourceType, SqlDialect

# After a FROM relation, these tokens mean the qualified name has ended (join, alias, etc.).
_AFTER_FROM_RELATION = re.compile(
    r"^("
    r"(?:cross|natural)\s+(?:join|apply)\b|"
    r"(?:inner|left|right|full|cross)\s+join\b|"
    r"join\b|"
    r"where|group|order|limit|having|union|intersect|except|offset|fetch|lateral\b|"
    r"pivot\b|as\b"
    r")",
    re.I,
)

# One identifier segment: double-quoted, backtick-quoted, or unquoted word.
_FROM_IDENT_SEGMENT = re.compile(r'"[^"]+"|`[^`]+`|\w+')
# Same pattern for schema.table paths in table-mode ``table_or_query`` (split before unquoting).
_QUALIFIED_PATH_SEGMENT = _FROM_IDENT_SEGMENT

# Whole-token match only (avoids classifying ``selective_users`` / ``with_events`` as SQL).
_SQL_STATEMENT_START = re.compile(r"(?is)\b(SELECT|WITH|VALUES)\b")


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
    """Treat input as a SQL statement when tokens indicate a query, not a table name.

    Uses word-boundary keyword detection so identifiers like ``selective_users`` stay
    table-mode. Whitespace, newlines, or ``;`` imply a fragment/statement rather than
    a single dotted identifier path.
    """
    t = table_or_query.strip()
    if not t:
        return False
    if any(ch in t for ch in "\n;"):
        return True
    if "\t" in t or re.search(r"\s", t):
        return True
    if _SQL_STATEMENT_START.search(t):
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
    """Split a dotted schema path; unquote each segment (not the whole string).

    ``"public"."users"`` → ``("public", "users")``. Stripping quotes from the full input
    first would corrupt names (e.g. ``public"`` / ``"users``).
    """
    q = qualified.strip()
    if not q:
        return (None, "")
    segments: list[str] = []
    pos = 0
    n = len(q)
    while pos < n:
        c = q[pos]
        if c.isspace():
            pos += 1
            continue
        if c == ".":
            pos += 1
            continue
        mo = _QUALIFIED_PATH_SEGMENT.match(q, pos)
        if not mo:
            break
        segments.append(_strip_sql_ident(mo.group(0)))
        pos = mo.end()
    if not segments:
        return (None, _strip_sql_ident(q))
    if len(segments) == 1:
        return (None, segments[0])
    return (".".join(segments[:-1]), segments[-1])


def _table_column_names_referenced_in_select(base_select: Any, table: Any) -> frozenset[str]:
    """Column names from ``table`` used in WHERE / ORDER BY of dlt's incremental select."""
    names: set[str] = set()

    def collect(clause: Any) -> None:
        if clause is None:
            return
        for elem in visitors.iterate(clause):
            if isinstance(elem, SAColumn) and elem.table is table:
                names.add(elem.name)

    collect(base_select.whereclause)
    ob = getattr(base_select, "_order_by_clause", None)
    if ob is not None:
        for part in ob:
            collect(part)
    return frozenset(names)


def _infer_from_schema_table(sql: str) -> tuple[str | None, str] | None:
    """Parse schema + table from the first ``FROM`` relation.

    Supports quoted qualified names such as ``"public"."users"`` (each segment is one
    identifier), unqualified names, and dotted unquoted ``schema.table``. Stops before
    ``AS``, join keywords, ``WHERE``, etc.
    """
    m = re.search(r"(?is)\bfrom\s+(?:only\s+)?", sql)
    if not m:
        return None
    pos = m.end()
    n = len(sql)
    segments: list[str] = []

    def relation_boundary_at(i: int) -> bool:
        rest = sql[i:].lstrip()
        return bool(_AFTER_FROM_RELATION.match(rest))

    while pos < n:
        c = sql[pos]
        if c.isspace():
            if segments:
                rest_from_space = sql[pos:]
                alias_m = re.match(r"\s+(\w+)\b", rest_from_space, re.I)
                if alias_m:
                    tail = rest_from_space[alias_m.end() :].lstrip()
                    if not tail.startswith("."):
                        break
            if segments and relation_boundary_at(pos):
                break
            pos += 1
            continue
        if c == ".":
            pos += 1
            continue
        if c in "),":
            break
        if segments and relation_boundary_at(pos):
            break
        mo = _FROM_IDENT_SEGMENT.match(sql, pos)
        if not mo:
            break
        segments.append(_strip_sql_ident(mo.group(0)))
        pos = mo.end()

    if not segments:
        return None
    if len(segments) == 1:
        return _split_schema_and_table(segments[0])
    return (".".join(segments[:-1]), segments[-1])


def _merge_user_sql_with_incremental_select(
    user_sql: str,
    base_select: Any,
    table: Any,
) -> Any:
    """Wrap ``user_sql`` as a subquery and re-apply WHERE/ORDER/LIMIT from ``base_select``.

    dlt builds ``base_select`` from the reflected table with incremental predicates.
    Returning bare ``text(user_sql)`` drops those clauses; this keeps them on the outer
    query over the user's statement.

    Only columns referenced in incremental WHERE/ORDER are declared on the inner
    ``text()`` subquery so custom ``SELECT`` lists (subset of table columns) stay valid;
    the outer query uses ``SELECT *`` from that subquery.
    """
    needed = _table_column_names_referenced_in_select(base_select, table)
    if not needed:
        needed = frozenset(c.name for c in table.columns)
    typed_cols = [sa.column(name, table.c[name].type) for name in sorted(needed)]
    inner = sa.text(user_sql).columns(*typed_cols).subquery("dlk_inner")
    equiv: dict[ColumnElement[Any], set[ColumnElement[Any]]] = {
        table.c[name]: {inner.c[name]} for name in needed
    }
    clause_adapt = ClauseAdapter(inner, equivalents=equiv)

    out: Any = sa.select(literal_column("*")).select_from(inner)
    if base_select.whereclause is not None:
        out = out.where(clause_adapt.traverse(base_select.whereclause))
    ob = getattr(base_select, "_order_by_clause", None)
    if ob is not None:
        order_parts = list(ob)
        if order_parts:
            out = out.order_by(*[clause_adapt.traverse(x) for x in order_parts])
    lim = getattr(base_select, "_limit", None)
    if lim is not None:
        out = out.limit(lim)
    return out


def _make_query_adapter(sql: str, *, incremental_extract: bool) -> Callable[..., Any]:
    """Return a ``query_adapter_callback`` compatible with dlt (2- or 4-arg forms)."""

    def adapter(*args: Any) -> Any:
        if not incremental_extract:
            return sa.text(sql)
        if len(args) < 4:
            raise RuntimeError(
                "query_adapter_callback received fewer than 4 arguments; "
                "cannot preserve incremental SQL filters for custom queries",
            )
        base_select, table, incremental, _engine = args[0], args[1], args[2], args[3]
        if incremental is None:
            return sa.text(sql)
        return _merge_user_sql_with_incremental_select(sql, base_select, table)

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
    Query mode: ``table_or_query`` is a SQL string (detected by statement keywords as whole
    tokens, not string prefixes); a table is inferred from the first ``FROM`` clause for
    reflection and incremental cursor validation. The ``query_adapter_callback`` runs the
    user's SQL; when incremental extraction is enabled it merges dlt's incremental
    WHERE/ORDER/LIMIT onto a subquery wrapping that SQL instead of replacing the generated
    select with plain ``text()`` (which would drop incremental filters).
    """
    if source_config.source_type is not SourceType.SQL:
        raise ValueError("build_sql_source requires SourceConfig with source_type sql")
    if not (source_config.connection_string and str(source_config.connection_string).strip()):
        raise ValueError(
            "source.connection_string is required and must be non-empty for SQL sources",
        )
    if source_config.sql_dialect is None:
        raise ValueError("source.sql_dialect is required when source_type is sql")
    if not (source_config.table_or_query and str(source_config.table_or_query).strip()):
        raise ValueError(
            "source.table_or_query is required and must be non-empty for SQL sources",
        )

    dialect = source_config.sql_dialect
    engine_kwargs = dict(_default_engine_kwargs(dialect))
    tq = source_config.table_or_query.strip()

    incremental: Incremental[Any] | None = None
    if extract_config.incremental:
        if not (extract_config.cursor_field and str(extract_config.cursor_field).strip()):
            raise ValueError(
                "extract.cursor_field is required and must be non-empty when incremental is true",
            )
        incremental = Incremental(extract_config.cursor_field)

    pk = extract_config.primary_key
    chunk_size = extract_config.chunk_size if extract_config.chunk_size is not None else 50000

    if _looks_like_sql_query(tq):
        parsed = _infer_from_schema_table(tq)
        if parsed is None:
            raise ValueError(
                "table_or_query looks like SQL but no FROM clause could be inferred "
                "for reflection; use a table name in table_or_query or include a FROM clause",
            )
        schema, table = parsed
        return SqlSourceMaterial(
            credentials=source_config.connection_string,
            table=table,
            schema=schema,
            incremental=incremental,
            primary_key=pk,
            chunk_size=chunk_size,
            defer_table_reflect=False,
            query_adapter_callback=_make_query_adapter(
                tq,
                incremental_extract=extract_config.incremental,
            ),
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
