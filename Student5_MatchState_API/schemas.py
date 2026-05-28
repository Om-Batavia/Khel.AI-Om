from typing import Optional

from pydantic import BaseModel, Field


class BallEvent(BaseModel):
    over_number: int = Field(..., ge=0)
    ball_number: int = Field(..., ge=1)
    runs_off_bat: int = Field(default=0, ge=0)
    extras: int = Field(default=0, ge=0)
    is_legal_delivery: bool = True
    wicket_fell: bool = False


class MatchInfo(BaseModel):
    match_id: Optional[str] = None
    title: Optional[str] = None
    total_overs: Optional[int] = Field(default=20, gt=0)
    target: Optional[int] = Field(default=None, gt=0)


class InningsInfo(BaseModel):
    innings_number: Optional[int] = Field(default=None, ge=1)
    batting_team: Optional[str] = None
    bowling_team: Optional[str] = None
    total_overs_limit: Optional[int] = Field(default=None, gt=0)
    target: Optional[int] = Field(default=None, gt=0)


class MatchStateRequest(BaseModel):
    match: MatchInfo = Field(default_factory=MatchInfo)
    innings: InningsInfo = Field(default_factory=InningsInfo)
    balls: list[BallEvent] = Field(default_factory=list)


class MatchStateResponse(BaseModel):
    match: str
    innings_number: Optional[int] = None
    score: str
    overs: str
    wickets: int
    batting_team: Optional[str] = None
    bowling_team: Optional[str] = None
    target: Optional[int] = None
    runs: int
    legal_balls: int
    total_balls: int
    balls_remaining: int
    current_run_rate: float
    runs_needed: Optional[int] = None
    required_run_rate: Optional[float] = None
    wickets_remaining: int
    match_state: str
    chase_status: str
    message: str
