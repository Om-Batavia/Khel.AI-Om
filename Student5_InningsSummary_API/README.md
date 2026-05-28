# Student 5 Assignment 3 - Innings Summary API

## Objective
Build an innings summary API that accepts an innings identifier and returns complete innings-level statistics computed from saved ball-event data.

## API Summary
- API name: Innings Summary API
- Framework: FastAPI
- Endpoint: `GET /student5/innings-summary/{innings_id}`
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
- Innings Summary endpoint: `http://127.0.0.1:8000/student5/innings-summary/101`

## Render Deployment
Use this start command on Render:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Input Schema
The endpoint accepts an innings identifier as a path parameter.

```text
GET /student5/innings-summary/{innings_id}
```

Example:

```text
GET /student5/innings-summary/101
```

## Output Schema
Expected output fields:

```json
{
  "innings_id": 101,
  "total_runs": 19,
  "wickets": 1,
  "legal_balls": 7,
  "overs": "1.1",
  "run_rate": 16.29,
  "batters": [],
  "bowlers": [],
  "top_batter": null,
  "top_bowler": null,
  "recent_balls": [],
  "message": "Innings 101 summary calculated from saved ball events."
}
```

## Example Request
```bash
curl "http://127.0.0.1:8000/student5/innings-summary/101"
```

## Example Response
```json
{
  "innings_id": 101,
  "total_runs": 19,
  "wickets": 1,
  "legal_balls": 7,
  "overs": "1.1",
  "run_rate": 16.29,
  "batters": [
    {
      "name": "Aarav Shah",
      "runs": 5,
      "balls": 2,
      "fours": 1,
      "sixes": 0,
      "strike_rate": 250.0
    }
  ],
  "bowlers": [
    {
      "name": "Rohan Mehta",
      "balls": 6,
      "overs": "1.0",
      "runs_conceded": 15,
      "wickets": 1,
      "economy": 15.0
    }
  ],
  "top_batter": {
    "name": "Kabir Rao",
    "runs": 7,
    "balls": 3,
    "fours": 1,
    "sixes": 0,
    "strike_rate": 233.33
  },
  "top_bowler": {
    "name": "Rohan Mehta",
    "balls": 6,
    "overs": "1.0",
    "runs_conceded": 15,
    "wickets": 1,
    "economy": 15.0
  },
  "recent_balls": [
    {
      "over": "0.3",
      "striker": "Vihaan Patel",
      "bowler": "Rohan Mehta",
      "runs": 1,
      "wicket": false,
      "description": "1 run extra"
    }
  ],
  "message": "Innings 101 summary calculated from 8 saved ball events."
}
```

## Data Handling
- Unknown `innings_id` returns `404` with a clean error message.
- Invalid non-integer `innings_id` is rejected by FastAPI validation.
- Non-positive `innings_id` returns a safe validation error.
- Empty saved innings data returns zero totals, empty summaries, and a clear message.
- Legal balls and overs are calculated only from legal deliveries.
- Batter summaries include runs, balls, fours, sixes, and strike rate.
- Bowler summaries include balls, overs, runs conceded, wickets, and economy.
- Recent balls returns the latest six saved ball events.

## Admin Handover Documentation

### File Responsibilities
- `main.py`: FastAPI app setup, root route, and innings-summary route.
- `schemas.py`: Pydantic response models.
- `services.py`: Saved ball-event data store and innings summary calculations.
- `requirements.txt`: Python package dependencies.
- `README.md`: Setup, schemas, examples, and handover notes.

### Main Endpoint
`GET /student5/innings-summary/{innings_id}`

The route accepts `innings_id`, then sends it to `get_innings_summary()` in `services.py`. The service layer loads the saved ball events and computes all innings-level statistics.

### Business Logic
The service layer calculates:
- total runs
- wickets
- legal balls
- overs
- run rate
- batter summaries
- bowler summaries
- top batter
- top bowler
- recent balls

### Testing Checklist
1. Run `uvicorn main:app --reload`.
2. Open `http://127.0.0.1:8000/docs`.
3. Test `GET /student5/innings-summary/101`.
4. Test `GET /student5/innings-summary/102` for an empty saved innings.
5. Test an unknown innings ID, such as `999`, to confirm clean `404` handling.
