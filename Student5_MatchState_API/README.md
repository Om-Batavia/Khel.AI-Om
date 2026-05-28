# Student 5 Assignment 3 - Match State API

## Objective
Build a current match state API that returns the competitive state of a cricket match.

## API Summary
- API name: Match State API
- Framework: FastAPI
- Endpoint: `POST /student5/match-state`
- Swagger/OpenAPI docs: `/docs`

## Deliverables
- `main.py`
- `schemas.py`
- `services.py`
- `requirements.txt`
- `README.md`
- GitHub repo URL: `https://github.com/Om-Batavia/Khel.AI-Om`
- Render deployment URL: Add deployed Render URL here after deployment
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
- Match State endpoint: `http://127.0.0.1:8000/student5/match-state`

## Render Deployment
Use this start command on Render:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Input Schema
The endpoint accepts match, innings, and ball-by-ball data.

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
    "bowling_team": "Alpha",
    "total_overs_limit": 20,
    "target": 121
  },
  "balls": [
    {
      "over_number": 1,
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
  "match": "string",
  "innings_number": 2,
  "score": "string",
  "overs": "string",
  "wickets": 0,
  "batting_team": "string",
  "bowling_team": "string",
  "target": 121,
  "runs": 0,
  "legal_balls": 0,
  "total_balls": 120,
  "balls_remaining": 120,
  "current_run_rate": 0.0,
  "runs_needed": 121,
  "required_run_rate": 6.05,
  "wickets_remaining": 10,
  "match_state": "string",
  "chase_status": "string",
  "message": "string"
}
```

## Example Request
```bash
curl -X POST "http://127.0.0.1:8000/student5/match-state" \
  -H "Content-Type: application/json" \
  -d @sample_payload.json
```

## Example Response
```json
{
  "match": "Alpha vs Bravo",
  "innings_number": 2,
  "score": "11/1",
  "overs": "0.4",
  "wickets": 1,
  "batting_team": "Bravo",
  "bowling_team": "Alpha",
  "target": 121,
  "runs": 11,
  "legal_balls": 4,
  "total_balls": 120,
  "balls_remaining": 116,
  "current_run_rate": 16.5,
  "runs_needed": 110,
  "required_run_rate": 5.69,
  "wickets_remaining": 9,
  "match_state": "Chase in progress",
  "chase_status": "Chase in progress",
  "message": "Bravo need 110 runs from 116 balls."
}
```

## Data Handling
- Empty ball list is handled safely and returns `0/0`, `0.0` overs, and zero run rate.
- Missing match title falls back to `match_id`, then `Unknown match`.
- Missing innings target falls back to match-level target.
- Missing overs limit falls back to match total overs, then 20 overs.
- Negative runs, extras, invalid over limits, and invalid targets are rejected by the request schema.
- Wickets are counted from ball events where `wicket_fell` is true.
- Wickets are capped at 10 and wickets remaining are returned.
- Overs are calculated from legal deliveries only.
- Chase responses include runs needed, required run rate, and a message with target context.

## Admin Handover Documentation

### File Responsibilities
- `main.py`: FastAPI app setup, root route, and Match State route.
- `schemas.py`: Pydantic request and response models.
- `services.py`: Match state calculation logic.
- `requirements.txt`: Python package dependencies.
- `sample_payload.json`: Ready-to-use test request body.

### Main Endpoint
`POST /student5/match-state`

The route accepts the request body, validates it through Pydantic schemas, and sends the payload to `get_match_state()` in `services.py`.

### Business Logic
The service layer calculates:
- total runs
- wickets
- wickets remaining
- legal balls
- overs display
- balls remaining
- current run rate
- runs needed
- required run rate
- target context
- chase status
- current match state

### Testing Checklist
1. Run `uvicorn main:app --reload`.
2. Open `http://127.0.0.1:8000/docs`.
3. Test `POST /student5/match-state` with `sample_payload.json`.
4. Confirm the response contains clean JSON with match, innings number, score, overs, wickets, teams, and target.
5. Test with an empty `balls` array to confirm safe handling.
