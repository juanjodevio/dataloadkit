"""Extraction options (incremental, chunking, keys)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, model_validator


class ExtractConfig(BaseModel):
    """Options that influence how data is extracted."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    incremental: bool = False
    cursor_field: str | None = None
    chunk_size: int | None = None
    # Tuple (not list): frozen models do not prevent in-place list mutation, which could
    # invalidate merge invariants after LoadPlan construction.
    primary_key: tuple[str, ...] | None = None

    @model_validator(mode="after")
    def _check_extract_invariants(self) -> ExtractConfig:
        if self.incremental:
            if not (self.cursor_field and str(self.cursor_field).strip()):
                raise ValueError(
                    "extract.cursor_field is required and must be non-empty "
                    "when incremental is true",
                )
        if self.chunk_size is not None and self.chunk_size <= 0:
            raise ValueError("extract.chunk_size must be positive when set")
        return self
