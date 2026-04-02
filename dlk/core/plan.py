"""Composed load plan."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, model_validator

from dlk.core.destination_config import DestinationConfig
from dlk.core.extract_config import ExtractConfig
from dlk.core.load_config import LoadConfig
from dlk.core.source_config import SourceConfig
from dlk.core.types import WriteMode


class LoadPlan(BaseModel):
    """Validated bundle of source, destination, extract, and load settings."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    pipeline_name: str
    source: SourceConfig
    destination: DestinationConfig
    extract: ExtractConfig
    load: LoadConfig

    @model_validator(mode="after")
    def _check_plan_invariants(self) -> LoadPlan:
        if not (self.pipeline_name and str(self.pipeline_name).strip()):
            raise ValueError("pipeline_name is required and must be non-empty")
        if self.load.write_mode is WriteMode.MERGE:
            pk = self.extract.primary_key
            if not pk or not all(str(c).strip() for c in pk):
                raise ValueError(
                    "extract.primary_key must be a non-empty tuple of non-empty strings "
                    "when write_mode is merge",
                )
        return self
