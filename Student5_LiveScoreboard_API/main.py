from fastapi import FastAPI, Path

from schemas import LiveScoreboardResponse
from services import get_live_scoreboard


app = FastAPI(
    title="Student 5 - Live Match Scoreboard API",
    description="Returns the latest active innings scoreboard for a match.",
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "api_name": "Live Match Scoreboard API",
        "student": "Student 5",
        "endpoint": "/student5/live-scoreboard/{match_id}",
        "swagger_docs": "/docs",
    }


@app.get(
    "/student5/live-scoreboard/{match_id}",
    response_model=LiveScoreboardResponse,
    summary="Get live match scoreboard",
    description=(
        "Accepts a database match id, or exact match title, and returns the active/latest "
        "innings scoreboard computed from saved ball-event rows."
    ),
    responses={
        200: {
            "description": "Live scoreboard found",
            "content": {
                "application/json": {
                    "example": {
                        "match": "First Match",
                        "venue": "Choithram School, Indore",
                        "innings_number": 2,
                        "batting_team": "Buddha House",
                        "bowling_team": "Gandhi House",
                        "score": "22/0",
                        "overs": "0.4",
                        "run_rate": 33.0,
                        "top_batter": {
                            "name": "Akshat Iyer",
                            "runs": 22,
                            "balls": 4,
                            "wickets": None,
                            "runs_conceded": None,
                            "overs": None,
                        },
                        "top_bowler": {
                            "name": "Vihaan Patel",
                            "runs": None,
                            "balls": None,
                            "wickets": 0,
                            "runs_conceded": 22,
                            "overs": "0.4",
                        },
                        "recent_balls": [
                            {
                                "over": "0.1",
                                "striker": "Akshat Iyer",
                                "bowler": "Vihaan Patel",
                                "runs": 6,
                                "wicket": False,
                                "description": "6 runs",
                            }
                        ],
                        "message": "Live scoreboard returned from database innings 3.",
                    }
                }
            },
        },
        404: {
            "description": "No match found",
            "content": {"application/json": {"example": {"detail": "No saved match found for this match_id."}}},
        },
    },
)
def live_scoreboard(
    match_id: str = Path(
        ...,
        description="Database match id or exact match title.",
        openapi_examples={
            "numeric_id": {
                "summary": "Database match id",
                "value": "1",
            },
            "match_title": {
                "summary": "Exact match title",
                "value": "First Match",
            },
        },
    )
):
    return get_live_scoreboard(match_id)
