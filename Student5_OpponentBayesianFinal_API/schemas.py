from typing import Any, Optional

from pydantic import BaseModel, Field


class PlayerInfo(BaseModel):
    player_id: Optional[str] = None
    player_name: Optional[str] = None
    role: Optional[str] = Field(default="batter")


class PerformanceSample(BaseModel):
    match_id: Optional[str] = None
    runs_scored: int = Field(..., ge=0)
    balls_faced: int = Field(..., ge=0)
    was_out: bool = False
    performance_value: Optional[float] = Field(default=None, ge=0)


class OpponentBayesianFinalRequest(BaseModel):
    player: PlayerInfo = Field(default_factory=PlayerInfo)
    opponent_team_id: Optional[str] = None
    opponent_team_name: Optional[str] = None
    prior_performances: list[PerformanceSample] = Field(..., min_length=3)
    opponent_performances: list[PerformanceSample] = Field(..., min_length=1)
    prior_weight: float = Field(default=6.0, gt=0)
    max_evidence_weight: float = Field(default=10.0, gt=0)


class DerivedVariablesUsed(BaseModel):
    prior_performance_estimate: float
    opponent_specific_evidence: float
    evidence_strength: float
    posterior_estimate: float
    prior_to_posterior_change: float
    prior_to_posterior_change_percent: float
    confidence: float


class OpponentBayesianFinalResponse(BaseModel):
    metric: str
    label: str
    opponent_adjusted_performance_score: float
    posterior_expectation: float
    confidence_label: str
    derived_variables_used: DerivedVariablesUsed
    explanation: str
    supporting_values: dict[str, Any]
    player_id: Optional[str]
    player_name: Optional[str]
    opponent_team_id: Optional[str]
    opponent_team_name: Optional[str]
