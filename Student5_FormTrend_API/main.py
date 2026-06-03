from fastapi import FastAPI

from schemas import FormTrendRequest, FormTrendResponse
from services import calculate_form_trend


app = FastAPI(
    title="Student 5 - Form Trend Regression API",
    description=(
        "Identifies whether a player's recent performance trend is rising, stable, "
        "or declining using linear regression over an ordered performance series."
    ),
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "api_name": "Form Trend (Regression) API",
        "student": "Student 5",
        "endpoint": "/student5/form-trend",
        "swagger_docs": "/docs",
    }


@app.post("/student5/form-trend", response_model=FormTrendResponse)
def form_trend(payload: FormTrendRequest):
    return calculate_form_trend(payload)
