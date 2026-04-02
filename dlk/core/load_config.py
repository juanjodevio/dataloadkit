"""Load / write options at the destination."""

from __future__ import annotations

from dataclasses import dataclass

from dlk.core.types import WriteMode


@dataclass(frozen=True)
class LoadConfig:
    """Options that influence how data is written."""

    write_mode: WriteMode = WriteMode.APPEND
    partitioning: tuple[str, ...] | None = None
