# Student 5 Assignment 3 - Chase Intelligence API

## Objective
Build a chase intelligence API that explains the required run rate equation.

## API Summary
- API name: Chase Intelligence API
- Framework: FastAPI
- Endpoint: `POST /student5/required-run-rate`
- Swagger/OpenAPI docs: `/docs`

## Deliverables
- `main.py`
- `schemas.py`
- `services.py`
- `requirements.txt`
- `README.md`
- GitHub repo URL: `https://github.com/Om-Batavia/Khel.AI-Om`
- Render deployment URL: Add deployed Render URL after deployment
- Admin handover documentation: Included below

## Setup
```bash
pip install -r requirements.txt
```

## Run Locally
```bash
uvicorn main:app --reload
```

Local URLs:
- API root: `http://127.0.0.1:8000/`
- Swagger docs: `http://127.0.0.1:8000/docs`
- Chase Intelligence endpoint: `http://127.0.0.1:8000/student5/required-run-rate`

## Render Deployment
Use this start command on Render:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Input Schema
The endpoint accepts match data, innings data, and ball-by-ball scoring data.

```json
{
  "match": {
    "match_id": "match-001",
    "title": "Alpha vs Bravo",
    "total_overs": 20,
    "target": 121
  },
  "innings": {
    "innings_number": 2,
    "batting_team": "Bravo",
    "total_overs_limit": 20,
    "target": 121
  },
  "balls": [
    {
      "over_number": 0,
      "ball_number": 1,
      "runs_off_bat": 4,
      "extras": 0,
      "is_legal_delivery": true,
      "wicket_fell": false
    }
  ]
}
```

## Output Schema
Expected output fields:

```json
{
  "target": 121,
  "current_score": "11/1",
  "runs_needed": 110,
  "balls_remaining": 116,
  "required_run_rate": 5.69,
  "equation": "Required run rate = (110 runs needed / 116 balls remaining) x 6 = 5.69",
  "message": "Chasing side needs 110 runs from 116 balls at 5.69 runs per over."
}
```

## Example Request
```bash
curl -X POST "http://127.0.0.1:8000/student5/required-run-rate" \
  -H "Content-Type: application/json" \
  -d @sample_payload.json
```

## Example Response
```json
{
  "target": 121,
  "current_score": "11/1",
  "runs_needed": 110,
  "balls_remaining": 116,
  "required_run_rate": 5.69,
  "equation": "Required run rate = (110 runs needed / 116 balls remaining) x 6 = 5.69",
  "message": "Chasing side needs 110 runs from 116 balls at 5.69 runs per over."
}
```

## Data Handling
- Empty ball list returns current score `0/0`, full balls remaining, and safe required run rate output.
- Missing innings target falls back to match-level target.
- Missing target returns a graceful non-chase response instead of crashing.
- Missing overs limit falls back to match total overs, then 20 overs.
- Negative runs, negative extras, invalid over limits, and invalid targets are rejected by the schema.
- Balls remaining is calculated from legal deliveries only.
- Wickets are capped at 10 for the current score.

## Admin Handover Documentation

### File Responsibilities
- `main.py`: FastAPI app setup, root route, and chase intelligence route.
- `schemas.py`: Pydantic request and response models.
- `services.py`: Required run rate calculation and helper logic.
- `requirements.txt`: Python package dependencies.
- `sample_payload.json`: Ready-to-use test request body.

### Main Endpoint
`POST /student5/required-run-rate`

The route accepts the request body, validates it through Pydantic schemas, and sends the payload to `calculate_required_run_rate()` in `services.py`.

### Business Logic
The service layer calculates:
- target
- current score
- runs needed
- legal balls used
- balls remaining
- required run rate
- required run rate equation text
- graceful non-chase messages

### Required Run Rate Equation
```text
required_run_rate = (runs_needed / balls_remaining) * 6
```

### Testing Checklist
1. Run `uvicorn main:app --reload`.
2. Open `http://127.0.0.1:8000/docs`.
3. Test `POST /student5/required-run-rate` with `sample_payload.json`.
4. Confirm the response contains target, current score, runs needed, balls remaining, and required run rate.
5. Test with no target to confirm non-chase situations fail gracefully.
6. Test with negative runs to confirm validation rejects invalid data.
