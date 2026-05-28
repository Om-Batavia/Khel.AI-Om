from fastapi import FastAPI

from schemas import RequiredRunRateRequest, RequiredRunRateResponse
from services import calculate_required_run_rate


app = FastAPI(
    title="Student 5 - Chase Intelligence API",
    description="Explains the required run rate equation for a cricket chase.",
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "api_name": "Chase Intelligence API",
        "student": "Student 5",
        "endpoint": "/student5/required-run-rate",
        "swagger_docs": "/docs",
    }


@app.post("/student5/required-run-rate", response_model=RequiredRunRateResponse)
def required_run_rate(payload: RequiredRunRateRequest):
    return calculate_required_run_rate(payload)
