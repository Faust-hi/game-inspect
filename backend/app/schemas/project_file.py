"""Versioned project exchange; legacy snapshots remain explicitly incomplete."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .catalog import ProjectProfile, RecommendationResult, input_fingerprint


class ProjectFile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    format: Literal["gamedev-dss-project"]
    version: Literal[1, 2]
    exported_at: datetime
    profile: ProjectProfile
    basket: list[str] = Field(max_length=200)
    result: RecommendationResult | None = None

    @model_validator(mode="after")
    def consistent_snapshot(self):
        if any(not code or len(code) > 64 for code in self.basket):
            raise ValueError("Некорректный код метода в корзине")
        if self.result is not None:
            snapshot = self.result
            if input_fingerprint(self.profile, self.basket) != input_fingerprint(
                snapshot.profile, snapshot.basket_codes,
            ):
                raise ValueError("Снимок относится к другой анкете или корзине")
        return self
