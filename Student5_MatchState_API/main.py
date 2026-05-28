from fastapi import FastAPI

from schemas import MatchStateRequest, MatchStateResponse
from services import get_match_state


app = FastAPI(
    title="Student 5 - Match State API",
    description="Returns the current competitive state of a cricket match.",
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "api_name": "Match State API",
        "student": "Student 5",
        "endpoint": "/student5/match-state",
        "swagger_docs": "/docs",
    }


@app.post("/student5/match-state", response_model=MatchStateResponse)
def match_state(payload: MatchStateRequest):
    return get_match_state(payload)
