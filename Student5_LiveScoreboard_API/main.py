from fastapi import FastAPI

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


@app.get("/student5/live-scoreboard/{match_id}", response_model=LiveScoreboardResponse)
def live_scoreboard(match_id: str):
    return get_live_scoreboard(match_id)
