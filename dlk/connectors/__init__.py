"""Source wiring into dlt (no parallel extract path).

SQL helpers live in ``dlk.connectors.sql`` and require SQLAlchemy (via dlt). Names are
re-exported lazily so ``import dlk.connectors`` does not import SQL stack until used.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

__all__ = ["SqlSourceMaterial", "build_sql_source"]

if TYPE_CHECKING:
    from dlk.connectors.sql import SqlSourceMaterial, build_sql_source


def __getattr__(name: str) -> Any:
    if name in __all__:
        from dlk.connectors import sql as _sql

        return getattr(_sql, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
