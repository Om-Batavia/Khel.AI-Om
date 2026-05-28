# Student 5 Assignment 3 - Live Match Scoreboard API

## Objective
Build a live match scoreboard API that accepts a match identifier and returns the latest or active innings scoreboard in clean frontend-ready JSON.

This version reads from the live SQLite database used by the Khel AI Django app instead of hard-coded sample data.

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
- `db.sqlite3`
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
- Live Scoreboard endpoint: `http://127.0.0.1:8000/student5/live-scoreboard/1`

## Database Configuration
By default, the API reads `db.sqlite3` from this API folder. You can override the database path with:

```bash
set KHEL_DB_PATH=C:\path\to\db.sqlite3
```

## Render Deployment
This repo includes a root-level `render.yaml` Blueprint for deploying this API on Render.

Blueprint deployment link:
```text
https://dashboard.render.com/blueprint/new?repo=https://github.com/Om-Batavia/Khel.AI-Om
```

The Blueprint uses these commands:
```bash
cd Student5_LiveScoreboard_API && pip install -r requirements.txt
cd Student5_LiveScoreboard_API && uvicorn main:app --host 0.0.0.0 --port $PORT
```

Manual Render start command:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

After deployment, replace `<render-url>` with the Render service URL:
```text
Docs: https://<render-url>/docs
Endpoint: https://<render-url>/student5/live-scoreboard/1
```

## Input Schema
The endpoint accepts a match identifier as a path parameter.

```text
GET /student5/live-scoreboard/{match_id}
```

Example:

```text
GET /student5/live-scoreboard/1
```

The API also accepts an exact match title, such as:

```text
GET /student5/live-scoreboard/First%20Match
```

## Output Schema
Expected output fields:

```json
{
  "match": "First Match",
  "venue": "Choithram School, Indore",
  "innings_number": 2,
  "batting_team": "Buddha House",
  "bowling_team": "Gandhi House",
  "score": "22/0",
  "overs": "0.4",
  "run_rate": 33.0,
  "top_batter": {
    "name": "Akshat Iyer",
    "runs": 22,
    "balls": 4
  },
  "top_bowler": {
    "name": "Vihaan Patel",
    "wickets": 0,
    "runs_conceded": 22,
    "overs": "0.4"
  },
  "recent_balls": [],
  "message": "Live scoreboard returned from database innings 3."
}
```

## Example Request
```bash
curl "http://127.0.0.1:8000/student5/live-scoreboard/1"
```

## Example Response
```json
{
  "match": "First Match",
  "venue": "Choithram School, Indore",
  "innings_number": 2,
  "batting_team": "Buddha House",
  "bowling_team": "Gandhi House",
  "score": "22/0",
  "overs": "0.4",
  "run_rate": 33.0,
  "top_batter": {
    "name": "Akshat Iyer",
    "runs": 22,
    "balls": 4,
    "wickets": null,
    "runs_conceded": null,
    "overs": null
  },
  "top_bowler": {
    "name": "Vihaan Patel",
    "runs": null,
    "balls": null,
    "wickets": 0,
    "runs_conceded": 22,
    "overs": "0.4"
  },
  "recent_balls": [
    {
      "over": "0.1",
      "striker": "Akshat Iyer",
      "bowler": "Vihaan Patel",
      "runs": 6,
      "wicket": false,
      "description": "6 runs"
    }
  ],
  "message": "Live scoreboard returned from database innings 3."
}
```

## Data Handling
- Unknown `match_id` returns `404` with a clean error message.
- Blank `match_id` returns a safe validation error.
- A match with no innings returns a zero scoreboard with a clear message.
- The API reads matches, innings, teams, players, and ball events from SQLite.
- If an incomplete innings exists, the latest incomplete innings is used.
- If all innings are complete, the latest innings number is used.
- Score, wickets, legal balls, overs, and run rate are calculated from database ball events.
- Recent balls returns the latest six saved ball events.
- Swagger includes example `match_id` values and example success/error responses.

## Admin Handover Documentation

### File Responsibilities
- `main.py`: FastAPI app setup, root route, and live-scoreboard route.
- `schemas.py`: Pydantic response models.
- `services.py`: SQLite database connection, active/latest innings lookup, and scoreboard calculations.
- `requirements.txt`: Python package dependencies.
- `db.sqlite3`: Local SQLite database with saved match, innings, player, team, and ball-event rows.
- `README.md`: Setup, schemas, examples, and handover notes.

### Main Endpoint
`GET /student5/live-scoreboard/{match_id}`

The route accepts `match_id`, then sends it to `get_live_scoreboard()` in `services.py`. The service layer queries SQLite, chooses the latest incomplete innings first, falls back to the latest innings, and calculates the frontend-ready scoreboard.

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
3. Test `GET /student5/live-scoreboard/1`.
4. Test `GET /student5/live-scoreboard/First%20Match`.
5. Test an unknown match ID, such as `999`, to confirm clean `404` handling.
