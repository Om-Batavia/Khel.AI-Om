from fastapi import FastAPI

from schemas import ExpectedFantasyFinalRequest, ExpectedFantasyFinalResponse
from services import calculate_expected_fantasy_final


app = FastAPI(
    title="Student 5 - Expected Fantasy Points Final Output API",
    description="Returns expected fantasy points, selection label, component breakdown, and explanation.",
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "api_name": "Expected Fantasy Points Final Output API",
        "student": "Student 5",
        "endpoint": "/student5/expected-fantasy-final",
        "swagger_docs": "/docs",
    }


@app.post("/student5/expected-fantasy-final", response_model=ExpectedFantasyFinalResponse)
def expected_fantasy_final(payload: ExpectedFantasyFinalRequest):
    return calculate_expected_fantasy_final(payload)
