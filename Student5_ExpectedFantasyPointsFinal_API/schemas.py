from typing import Any, Optional

from pydantic import BaseModel, Field


class PlayerInfo(BaseModel):
    player_id: Optional[str] = None
    player_name: Optional[str] = None
    role: Optional[str] = Field(default="all_rounder")


class BattingEventProbabilities(BaseModel):
    run_0: float = Field(..., ge=0, le=1)
    run_1: float = Field(..., ge=0, le=1)
    run_2: float = Field(..., ge=0, le=1)
    run_3: float = Field(..., ge=0, le=1)
    four: float = Field(..., ge=0, le=1)
    six: float = Field(..., ge=0, le=1)
    dismissal: float = Field(..., ge=0, le=1)


class BowlingEventProbabilities(BaseModel):
    dot_ball: float = Field(..., ge=0, le=1)
    wicket: float = Field(..., ge=0, le=1)
    maiden_over: float = Field(..., ge=0, le=1)
    economy_bonus: float = Field(..., ge=0, le=1)


class FieldingEventProbabilities(BaseModel):
    catch: float = Field(..., ge=0, le=1)
    run_out: float = Field(..., ge=0, le=1)
    stumping: float = Field(..., ge=0, le=1)


class EventPointValues(BaseModel):
    run_0: float = 0
    run_1: float = 1
    run_2: float = 2
    run_3: float = 3
    four: float = 5
    six: float = 8
    dismissal: float = -2
    dot_ball: float = 1
    wicket: float = 25
    maiden_over: float = 12
    economy_bonus: float = 6
    catch: float = 8
    run_out: float = 12
    stumping: float = 12


class SelectionThresholds(BaseModel):
    strong_pick_min: float = 30
    playable_min: float = 15


class ExpectedFantasyFinalRequest(BaseModel):
    player: PlayerInfo = Field(default_factory=PlayerInfo)
    batting_event_probabilities: BattingEventProbabilities
    bowling_event_probabilities: BowlingEventProbabilities
    fielding_event_probabilities: FieldingEventProbabilities
    event_point_values: EventPointValues = Field(default_factory=EventPointValues)
    selection_thresholds: SelectionThresholds = Field(default_factory=SelectionThresholds)


class ComponentBreakdown(BaseModel):
    batting_expected_points: float
    bowling_expected_points: float
    fielding_expected_points: float
    event_breakdown: dict[str, float]


class DerivedVariablesUsed(BaseModel):
    batting_event_probabilities: dict[str, float]
    bowling_event_probabilities: dict[str, float]
    fielding_event_probabilities: dict[str, float]
    event_point_values: dict[str, float]
    selection_thresholds: dict[str, float]


class ExpectedFantasyFinalResponse(BaseModel):
    metric: str
    label: str
    expected_fantasy_points: float
    selection_value_label: str
    component_breakdown: ComponentBreakdown
    derived_variables_used: DerivedVariablesUsed
    explanation: str
    supporting_values: dict[str, Any]
    player_id: Optional[str]
    player_name: Optional[str]
