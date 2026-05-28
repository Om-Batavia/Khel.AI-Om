from typing import Optional

from pydantic import BaseModel


class BatterSummary(BaseModel):
    name: str
    runs: int
    balls: int
    fours: int
    sixes: int
    strike_rate: float


class BowlerSummary(BaseModel):
    name: str
    balls: int
    overs: str
    runs_conceded: int
    wickets: int
    economy: float


class RecentBall(BaseModel):
    over: str
    striker: str
    bowler: str
    runs: int
    wicket: bool
    description: str


class InningsSummaryResponse(BaseModel):
    innings_id: int
    total_runs: int
    wickets: int
    legal_balls: int
    overs: str
    run_rate: float
    batters: list[BatterSummary]
    bowlers: list[BowlerSummary]
    top_batter: Optional[BatterSummary] = None
    top_bowler: Optional[BowlerSummary] = None
    recent_balls: list[RecentBall]
    message: str
