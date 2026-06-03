from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class PlayerInfo(BaseModel):
    player_id: Optional[str] = None
    player_name: Optional[str] = None
    role: Optional[str] = Field(default="batter")


class PerformanceRecord(BaseModel):
    match_id: Optional[str] = None
    sequence_number: int = Field(..., ge=1)
    runs_scored: int = Field(..., ge=0)
    balls_faced: int = Field(..., ge=0)
    was_out: bool = False
    performance_value: Optional[float] = Field(default=None, ge=0)


class FormTrendFinalRequest(BaseModel):
    player: PlayerInfo = Field(default_factory=PlayerInfo)
    recent_performances: list[PerformanceRecord] = Field(..., min_length=3)
    stable_slope_threshold: float = Field(default=0.15, gt=0)

    @field_validator("recent_performances")
    @classmethod
    def sequence_numbers_must_be_unique(cls, records):
        sequence_numbers = [record.sequence_number for record in records]
        if len(sequence_numbers) != len(set(sequence_numbers)):
            raise ValueError("sequence_number values must be unique.")
        return records


class DerivedVariables(BaseModel):
    recent_match_sequence: list[float]
    regression_slope: float
    recent_average: float
    volatility: float
    normalized_trend_score: float
    r_squared: float


class FormTrendFinalResponse(BaseModel):
    metric: str
    label: str
    form_trend_score: float
    trend_label: str
    trend_confidence: float
    derived_variables_used: DerivedVariables
    explanation: str
    supporting_values: dict[str, Any]
    player_id: Optional[str]
    player_name: Optional[str]
