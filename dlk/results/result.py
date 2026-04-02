"""Normalized execution outcome."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class LoadResult(BaseModel):
    """Structured result after a load attempt."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    success: bool
    row_count: int | None = None
    execution_time: float | None = None
    error_message: str | None = None
    raw_metadata: dict[str, Any] | None = None
