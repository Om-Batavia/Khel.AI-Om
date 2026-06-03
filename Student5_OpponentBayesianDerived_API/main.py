from fastapi import FastAPI

from schemas import OpponentBayesianRequest, OpponentBayesianResponse
from services import calculate_opponent_bayesian_variables


app = FastAPI(
    title="Student 5 - Opponent Bayesian Performance Derived Variables API",
    description=(
        "Converts prior player performance and opponent-specific evidence into "
        "Bayesian derived variables for opponent-adjusted performance."
    ),
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "api_name": "Opponent Bayesian Performance Derived Variables API",
        "student": "Student 5",
        "endpoint": "/student5/opponent-bayesian-derived",
        "swagger_docs": "/docs",
    }


@app.post("/student5/opponent-bayesian-derived", response_model=OpponentBayesianResponse)
def opponent_bayesian_derived(payload: OpponentBayesianRequest):
    return calculate_opponent_bayesian_variables(payload)
