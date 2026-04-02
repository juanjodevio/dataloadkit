"""Normalized execution outcome."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LoadResult:
    """Structured result after a load attempt."""

    success: bool
    row_count: int | None = None
    execution_time: float | None = None
    error_message: str | None = None
    raw_metadata: Mapping[str, Any] | None = None
