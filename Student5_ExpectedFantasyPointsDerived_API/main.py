from fastapi import FastAPI

from schemas import ExpectedFantasyRequest, ExpectedFantasyResponse
from services import calculate_expected_fantasy_variables


app = FastAPI(
    title="Student 5 - Expected Fantasy Points Derived Variables API",
    description="Converts event probabilities and fantasy point weights into expected value components.",
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "api_name": "Expected Fantasy Points Derived Variables API",
        "student": "Student 5",
        "endpoint": "/student5/expected-fantasy-derived",
        "swagger_docs": "/docs",
    }


@app.post("/student5/expected-fantasy-derived", response_model=ExpectedFantasyResponse)
def expected_fantasy_derived(payload: ExpectedFantasyRequest):
    return calculate_expected_fantasy_variables(payload)
