"""Composed load plan."""

from __future__ import annotations

from dataclasses import dataclass

from dlk.core.destination_config import DestinationConfig
from dlk.core.extract_config import ExtractConfig
from dlk.core.load_config import LoadConfig
from dlk.core.source_config import SourceConfig


@dataclass(frozen=True)
class LoadPlan:
    """Validated bundle of source, destination, extract, and load settings."""

    pipeline_name: str
    source: SourceConfig
    destination: DestinationConfig
    extract: ExtractConfig
    load: LoadConfig
