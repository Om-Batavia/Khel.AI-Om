# Student 5 Assignment 3 - Match Outlook API

## Objective
Build a simple explainable match-outlook API using a declared heuristic based on wickets in hand, overs left, current rate, and required rate.

## API Summary
- API name: Match Outlook API
- Framework: FastAPI
- Endpoint: `POST /student5/match-outlook`
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
- Match Outlook endpoint: `http://127.0.0.1:8000/student5/match-outlook`

## Render Deployment
Use this start command on Render:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Declared Heuristic
This API returns a simple label, not a scientific win probability.

```text
High Chance:
- target is already reached, OR
- required run rate <= current run rate + 1.5 and at least 4 wickets are in hand

Low Chance:
- no balls or wickets remain before the target, OR
- required run rate > current run rate + 4, OR
- 2 or fewer wickets remain and more than 20 runs are needed

Medium Chance:
- all other chase states
```

## Input Schema
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
  "runs_needed": 110,
  "balls_remaining": 116,
  "required_run_rate": 5.69,
  "prediction": "High Chance",
  "wickets_in_hand": 9,
  "overs_left": "19.2",
  "current_run_rate": 16.5,
  "heuristic": "Declared rule text",
  "reason": "Required rate is close to the current rate and wickets are in hand."
}
```

## Example Request
```bash
curl -X POST "http://127.0.0.1:8000/student5/match-outlook" \
  -H "Content-Type: application/json" \
  -d @sample_payload.json
```

## Example Response
```json
{
  "runs_needed": 110,
  "balls_remaining": 116,
  "required_run_rate": 5.69,
  "prediction": "High Chance",
  "wickets_in_hand": 9,
  "overs_left": "19.2",
  "current_run_rate": 16.5,
  "heuristic": "High Chance when target is reached, or required rate is within current rate + 1.5 with at least 4 wickets in hand. Low Chance when no balls/wickets remain before the target, required rate is more than current rate + 4, or 2 or fewer wickets remain while more than 20 runs are needed. Otherwise Medium Chance.",
  "reason": "Required rate is close to the current rate and wickets are in hand."
}
```

## Data Handling
- Empty ball list returns safe values with zero current run rate.
- Missing target returns a neutral `Medium Chance` non-chase outlook.
- Missing overs limit falls back to match total overs, then 20 overs.
- Negative runs, negative extras, invalid over limits, and invalid targets are rejected by the schema.
- Balls remaining is calculated from legal deliveries only.
- Wickets are capped at 10 before calculating wickets in hand.

## Admin Handover Documentation

### File Responsibilities
- `main.py`: FastAPI app setup, root route, and match-outlook route.
- `schemas.py`: Pydantic request and response models.
- `services.py`: Match-outlook heuristic and helper calculations.
- `requirements.txt`: Python package dependencies.
- `sample_payload.json`: Ready-to-use test request body.

### Main Endpoint
`POST /student5/match-outlook`

The route accepts the request body, validates it through Pydantic schemas, and sends the payload to `calculate_match_outlook()` in `services.py`.

### Business Logic
The service layer calculates:
- runs needed
- balls remaining
- required run rate
- current run rate
- wickets in hand
- overs left
- prediction label
- explanation reason

### Testing Checklist
1. Run `uvicorn main:app --reload`.
2. Open `http://127.0.0.1:8000/docs`.
3. Test `POST /student5/match-outlook` with `sample_payload.json`.
4. Confirm the response includes runs needed, balls remaining, required run rate, and prediction.
5. Test with no target to confirm it returns a graceful neutral outlook.
6. Test with negative runs to confirm validation rejects invalid data.
