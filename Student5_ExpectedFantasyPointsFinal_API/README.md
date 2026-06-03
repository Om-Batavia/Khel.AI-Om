# Student 5 - Expected Fantasy Points Final Output API

## Objective
Create an endpoint that uses expected-value derived variables to return Expected Fantasy Points, selection label, and explanation.

This is formula-based expected value analytics, not a trained ML model. It treats fantasy selection as a decision problem under uncertainty by weighting each possible event by probability and fantasy point value.

## Endpoint
- Method: `POST`
- Path: `/student5/expected-fantasy-final`
- Swagger/OpenAPI: `/docs`

## Primary Inputs
- `batting_event_probabilities`: probabilities for batting events.
- `bowling_event_probabilities`: probabilities for bowling events.
- `fielding_event_probabilities`: probabilities for fielding events.
- `event_point_values`: fantasy points assigned to each event.
- `selection_thresholds`: thresholds used to label selection value.

## Derived Variables
- `batting_event_probabilities`
- `bowling_event_probabilities`
- `fielding_event_probabilities`
- `event_point_values`
- `selection_thresholds`
- component expected values calculated from probability times point value.

## Final Output Fields
- `expected_fantasy_points`
- `selection_value_label`
- `component_breakdown`
- `derived_variables_used`
- `explanation`

## Formula / Function Code
```python
event_expected_points = event_probability * event_point_value
batting_expected_points = sum(batting event expected points)
bowling_expected_points = sum(bowling event expected points)
fielding_expected_points = sum(fielding event expected points)
expected_fantasy_points =
  batting_expected_points + bowling_expected_points + fielding_expected_points
```

Selection rule:
- `Strong Fantasy Pick` if expected points >= `strong_pick_min`
- `Playable Fantasy Pick` if expected points >= `playable_min`
- `Avoid / Low Value Pick` otherwise

## Run Locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Local URLs:
- Root: `http://127.0.0.1:8000/`
- Swagger docs: `http://127.0.0.1:8000/docs`
- Endpoint: `http://127.0.0.1:8000/student5/expected-fantasy-final`

## Example Request
```bash
curl -X POST "http://127.0.0.1:8000/student5/expected-fantasy-final" \
  -H "Content-Type: application/json" \
  -d @sample_payload.json
```

## Example Response
```json
{
  "metric": "expected_fantasy_points_final_output",
  "label": "Avoid / Low Value Pick",
  "expected_fantasy_points": 7.43,
  "selection_value_label": "Avoid / Low Value Pick",
  "component_breakdown": {
    "batting_expected_points": 1.61,
    "bowling_expected_points": 3.82,
    "fielding_expected_points": 2.0
  },
  "explanation": "Selection is based on expected value under uncertainty."
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
8. Final expected value and selection logic are in `services.py`.
