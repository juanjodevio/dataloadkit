"""Extraction options (incremental, chunking, keys)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractConfig:
    """Options that influence how data is extracted."""

    incremental: bool = False
    cursor_field: str | None = None
    chunk_size: int | None = None
    primary_key: list[str] | None = None
