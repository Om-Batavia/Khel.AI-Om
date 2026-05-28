# Student 5 Assignment 3 - Live Match Scoreboard API

## Objective
Build a live match scoreboard API that accepts a match identifier and returns the latest or active innings scoreboard in clean frontend-ready JSON.

## API Summary
- API name: Live Match Scoreboard API
- Framework: FastAPI
- Endpoint: `GET /student5/live-scoreboard/{match_id}`
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
- Live Scoreboard endpoint: `http://127.0.0.1:8000/student5/live-scoreboard/match-001`

## Render Deployment
Use this start command on Render:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Input Schema
The endpoint accepts a match identifier as a path parameter.

```text
GET /student5/live-scoreboard/{match_id}
```

Example:

```text
GET /student5/live-scoreboard/match-001
```

## Output Schema
Expected output fields:

```json
{
  "match": "Alpha vs Bravo",
  "venue": "Khel AI Arena",
  "innings_number": 2,
  "batting_team": "Bravo",
  "bowling_team": "Alpha",
  "score": "15/1",
  "overs": "1.1",
  "run_rate": 12.86,
  "top_batter": {
    "name": "Rohan Mehta",
    "runs": 6,
    "balls": 3
  },
  "top_bowler": {
    "name": "Kabir Rao",
    "wickets": 1,
    "runs_conceded": 14,
    "overs": "1.0"
  },
  "recent_balls": [],
  "message": "Live scoreboard returned for innings 2."
}
```

## Example Request
```bash
curl "http://127.0.0.1:8000/student5/live-scoreboard/match-001"
```

## Example Response
```json
{
  "match": "Alpha vs Bravo",
  "venue": "Khel AI Arena",
  "innings_number": 2,
  "batting_team": "Bravo",
  "bowling_team": "Alpha",
  "score": "15/1",
  "overs": "1.1",
  "run_rate": 12.86,
  "top_batter": {
    "name": "Rohan Mehta",
    "runs": 6,
    "balls": 3,
    "wickets": null,
    "runs_conceded": null,
    "overs": null
  },
  "top_bowler": {
    "name": "Kabir Rao",
    "runs": null,
    "balls": null,
    "wickets": 1,
    "runs_conceded": 14,
    "overs": "1.0"
  },
  "recent_balls": [
    {
      "over": "0.2",
      "striker": "Dev Singh",
      "bowler": "Kabir Rao",
      "runs": 1,
      "wicket": false,
      "description": "1 run extra"
    }
  ],
  "message": "Live scoreboard returned for innings 2."
}
```

## Data Handling
- Unknown `match_id` returns `404` with a clean error message.
- Blank `match_id` returns a safe validation error.
- A match with no innings returns a zero scoreboard with a clear message.
- If an active innings exists, that innings is used.
- If no innings is marked active, the latest innings number is used.
- Score, wickets, legal balls, overs, and run rate are calculated from saved ball events.
- Recent balls returns the latest six saved ball events.

## Admin Handover Documentation

### File Responsibilities
- `main.py`: FastAPI app setup, root route, and live-scoreboard route.
- `schemas.py`: Pydantic response models.
- `services.py`: Saved match data store, active/latest innings lookup, and scoreboard calculations.
- `requirements.txt`: Python package dependencies.
- `README.md`: Setup, schemas, examples, and handover notes.

### Main Endpoint
`GET /student5/live-scoreboard/{match_id}`

The route accepts `match_id`, then sends it to `get_live_scoreboard()` in `services.py`. The service layer chooses the active innings first, falls back to the latest innings, and calculates the frontend-ready scoreboard.

### Business Logic
The service layer calculates:
- active/latest innings
- match and venue details
- score and wickets
- legal balls and overs
- run rate
- top batter
- top bowler
- recent balls

### Testing Checklist
1. Run `uvicorn main:app --reload`.
2. Open `http://127.0.0.1:8000/docs`.
3. Test `GET /student5/live-scoreboard/match-001`.
4. Test `GET /student5/live-scoreboard/match-empty` for a no-innings case.
5. Test an unknown match ID, such as `unknown-match`, to confirm clean `404` handling.
