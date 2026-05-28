from fastapi import FastAPI

from schemas import InningsSummaryResponse
from services import get_innings_summary


app = FastAPI(
    title="Student 5 - Innings Summary API",
    description="Returns complete innings-level statistics from saved ball-event data.",
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "api_name": "Innings Summary API",
        "student": "Student 5",
        "endpoint": "/student5/innings-summary/{innings_id}",
        "swagger_docs": "/docs",
    }


@app.get("/student5/innings-summary/{innings_id}", response_model=InningsSummaryResponse)
def innings_summary(innings_id: int):
    return get_innings_summary(innings_id)
