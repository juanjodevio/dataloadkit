"""Load / write options at the destination."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from dlk.core.types import WriteMode


class LoadConfig(BaseModel):
    """Options that influence how data is written."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    write_mode: WriteMode = WriteMode.APPEND
    partitioning: tuple[str, ...] | None = None
