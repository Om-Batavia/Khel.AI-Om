from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Khel AI Match Summary API",
    version="1.0.0",
    description="A simple example API for deployment and workflow integration"
)

class MatchInput(BaseModel):
    team_name: str
    runs: int
    wickets: int
    overs: float

@app.get("/")
def home():
    return {"message": "Khel AI Match Summary API is live"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/match-summary")
def match_summary(data: MatchInput):
    if data.overs <= 0:
        return {"error": "Overs must be greater than 0"}

    run_rate = round(data.runs / data.overs, 2)

    if data.wickets >= 10:
        innings_status = "All out"
    else:
        innings_status = "Innings in progress"

    summary = (
        f"{data.team_name} scored {data.runs}/{data.wickets} "
        f"in {data.overs} overs at a run rate of {run_rate}."
    )

    return {
        "team_name": data.team_name,
        "summary": summary,
        "run_rate": run_rate,
        "status": innings_status
    }