from fastapi import FastAPI

from schemas import FormTrendFinalRequest, FormTrendFinalResponse
from services import calculate_form_trend_final


app = FastAPI(
    title="Student 5 - Form Trend Final Output API",
    description=(
        "Uses derived trend variables from recent performance inputs to return "
        "a final Form Trend score, label, confidence, and explanation."
    ),
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "api_name": "Form Trend Final Output API",
        "student": "Student 5",
        "endpoint": "/student5/form-trend-final",
        "swagger_docs": "/docs",
    }


@app.post("/student5/form-trend-final", response_model=FormTrendFinalResponse)
def form_trend_final(payload: FormTrendFinalRequest):
    return calculate_form_trend_final(payload)
