"""Source wiring into dlt (no parallel extract path)."""

from dlk.connectors.sql import SqlSourceMaterial, build_sql_source

__all__ = ["SqlSourceMaterial", "build_sql_source"]
