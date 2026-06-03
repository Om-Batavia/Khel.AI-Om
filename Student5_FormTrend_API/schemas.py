from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class PlayerInfo(BaseModel):
    player_id: Optional[str] = None
    player_name: Optional[str] = None
    role: Optional[str] = Field(default="batter", description="Player role, for example batter or all_rounder.")


class PerformanceRecord(BaseModel):
    match_id: Optional[str] = None
    sequence_number: int = Field(..., ge=1, description="Chronological order number, oldest to newest.")
    runs_scored: int = Field(..., ge=0)
    balls_faced: int = Field(..., ge=0)
    was_out: bool = False
    performance_value: Optional[float] = Field(
        default=None,
        ge=0,
        description="Optional already-computed performance score from the webapp/model extension.",
    )


class FormTrendRequest(BaseModel):
    player: PlayerInfo = Field(default_factory=PlayerInfo)
    recent_performances: list[PerformanceRecord] = Field(..., min_length=3)
    stable_slope_threshold: float = Field(
        default=0.15,
        gt=0,
        description="Absolute normalized slope below this value is interpreted as stable.",
    )

    @field_validator("recent_performances")
    @classmethod
    def sequence_numbers_must_be_unique(cls, records):
        sequence_numbers = [record.sequence_number for record in records]
        if len(sequence_numbers) != len(set(sequence_numbers)):
            raise ValueError("sequence_number values must be unique.")
        return records


class DerivedPerformancePoint(BaseModel):
    sequence_number: int
    time_index: int
    runs_scored: int
    balls_faced: int
    strike_rate: float
    dismissal_penalty: float
    performance_score: float


class FormTrendResponse(BaseModel):
    metric: str
    label: str
    explanation: str
    recent_match_sequence: list[float]
    regression_slope: float
    recent_average: float
    volatility: float
    trend_confidence: float
    supporting_values: dict[str, Any]
    api_name: str
    player_id: Optional[str]
    player_name: Optional[str]
    sample_size: int
    average_performance_score: float
    normalized_trend_score: float
    r_squared: float
    trend_label: str
    trend_interpretation: str
    derived_points: list[DerivedPerformancePoint]
    scientific_principle: str
    assumptions: list[str]
