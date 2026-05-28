from typing import Optional

from pydantic import BaseModel


class Performer(BaseModel):
    name: str
    runs: Optional[int] = None
    balls: Optional[int] = None
    wickets: Optional[int] = None
    runs_conceded: Optional[int] = None
    overs: Optional[str] = None


class RecentBall(BaseModel):
    over: str
    striker: str
    bowler: str
    runs: int
    wicket: bool
    description: str


class LiveScoreboardResponse(BaseModel):
    match: str
    venue: str
    innings_number: Optional[int] = None
    batting_team: Optional[str] = None
    bowling_team: Optional[str] = None
    score: str
    overs: str
    run_rate: float
    top_batter: Optional[Performer] = None
    top_bowler: Optional[Performer] = None
    recent_balls: list[RecentBall]
    message: str
