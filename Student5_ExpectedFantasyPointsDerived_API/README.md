# Student 5 - Expected Fantasy Points Derived Variables API

## Objective
Create an endpoint that converts event probabilities into derived variables for Expected Fantasy Points.

This is formula-based expected value analytics, not a trained ML model. The endpoint multiplies event probabilities by fantasy point weights and returns batting, bowling, fielding, and total expected fantasy components.

## Endpoint
- Method: `POST`
- Path: `/student5/expected-fantasy-derived`
- Swagger/OpenAPI: `/docs`

## Primary Inputs
- `batting_event_probabilities`: probabilities for batting events such as 1 run, 2 runs, four, six, and dismissal.
- `bowling_event_probabilities`: probabilities for bowling events such as dot ball, wicket, maiden over, and economy bonus.
- `fielding_event_probabilities`: probabilities for catch, run out, and stumping.
- `event_point_values`: fantasy point weights for each event.

## Derived Variables
- `batting_event_probabilities`
- `bowling_event_probabilities`
- `fielding_event_probabilities`
- `event_point_values`
- `expected_value_components`

`expected_value_components` contains batting, bowling, fielding, total expected fantasy points, and per-event expected point breakdown.

## Formula / Function Code
```python
event_expected_points = event_probability * event_point_value
batting_expected_points = sum(batting event expected points)
bowling_expected_points = sum(bowling event expected points)
fielding_expected_points = sum(fielding event expected points)
total_expected_fantasy_points =
  batting_expected_points + bowling_expected_points + fielding_expected_points
```

This directly models fantasy points as expected value from event probabilities and point weights.

## Run Locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Local URLs:
- Root: `http://127.0.0.1:8000/`
- Swagger docs: `http://127.0.0.1:8000/docs`
- Endpoint: `http://127.0.0.1:8000/student5/expected-fantasy-derived`

## Example Request
```bash
curl -X POST "http://127.0.0.1:8000/student5/expected-fantasy-derived" \
  -H "Content-Type: application/json" \
  -d @sample_payload.json
```

## Example Response
```json
{
  "metric": "expected_fantasy_points_derived_variables",
  "label": "Low Expected Fantasy Value",
  "expected_value_components": {
    "batting_expected_points": 1.61,
    "bowling_expected_points": 3.82,
    "fielding_expected_points": 2.0,
    "total_expected_fantasy_points": 7.43
  }
}
```

## Admin Handover
1. Install dependencies with `pip install -r requirements.txt`.
2. Run locally with `uvicorn main:app --reload`.
3. Open Swagger at `http://127.0.0.1:8000/docs`.
4. Test with `sample_payload.json`.
5. Deploy on Render as a Python web service.
6. Render start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`.
7. No database, secrets, ML model file, or external API calls are required.
8. Expected value logic is in `services.py`.
