from fastapi import FastAPI

from schemas import MatchOutlookRequest, MatchOutlookResponse
from services import calculate_match_outlook


app = FastAPI(
    title="Student 5 - Match Outlook API",
    description="Returns an explainable match-outlook label from a declared cricket chase heuristic.",
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "api_name": "Match Outlook API",
        "student": "Student 5",
        "endpoint": "/student5/match-outlook",
        "swagger_docs": "/docs",
    }


@app.post("/student5/match-outlook", response_model=MatchOutlookResponse)
def match_outlook(payload: MatchOutlookRequest):
    return calculate_match_outlook(payload)
