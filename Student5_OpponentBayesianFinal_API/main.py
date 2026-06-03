from fastapi import FastAPI

from schemas import OpponentBayesianFinalRequest, OpponentBayesianFinalResponse
from services import calculate_opponent_bayesian_final


app = FastAPI(
    title="Student 5 - Opponent Bayesian Performance Final Output API",
    description=(
        "Uses Bayesian-derived variables to return opponent-adjusted performance "
        "expectation, label, confidence, and explanation."
    ),
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "api_name": "Opponent Bayesian Performance Final Output API",
        "student": "Student 5",
        "endpoint": "/student5/opponent-bayesian-final",
        "swagger_docs": "/docs",
    }


@app.post("/student5/opponent-bayesian-final", response_model=OpponentBayesianFinalResponse)
def opponent_bayesian_final(payload: OpponentBayesianFinalRequest):
    return calculate_opponent_bayesian_final(payload)
