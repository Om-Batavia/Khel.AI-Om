# Student 5 - Form Trend Derived Variables API

## Objective
Create an endpoint that converts recent performance sequence inputs into derived variables for Form Trend.

This FastAPI service evaluates ordered recent player performance, not only average performance. It derives a per-match performance score, fits a linear regression trend line over chronological order, and returns a trend label with supporting variables.

## Endpoint
- Method: `POST`
- Path: `/student5/form-trend`
- Swagger/OpenAPI: `/docs`

## Primary Inputs
```json
{
  "player": {
    "player_id": "P-005",
    "player_name": "Sample Batter",
    "role": "batter"
  },
  "recent_performances": [
    {
      "match_id": "M-001",
      "sequence_number": 1,
      "runs_scored": 18,
      "balls_faced": 20,
      "was_out": true,
      "performance_value": null
    }
  ],
  "stable_slope_threshold": 0.15
}
```

Primary fields:
- `sequence_number`: chronological order from oldest to newest.
- `runs_scored`: player runs in that recent match.
- `balls_faced`: balls faced in that recent match.
- `was_out`: whether the batter was dismissed.
- `performance_value`: optional already-computed performance score. If present, it is used directly.

## Derived Variables
Expected output fields are included directly:
- `recent_match_sequence`: ordered derived performance scores.
- `regression_slope`: Ordinary Least Squares slope over the ordered sequence.
- `recent_average`: mean of recent performance scores.
- `volatility`: population standard deviation of recent performance scores.
- `trend_confidence`: R-squared adjusted by volatility.

The response also includes:
- `metric`
- `label`
- `explanation`
- `supporting_values`

## Formula / Function Code
```python
performance_score = runs_scored + (0.10 * strike_rate) - dismissal_penalty
strike_rate = (runs_scored * 100) / balls_faced
dismissal_penalty = 5 if was_out else 0

x = [1, 2, 3, ...]
y = recent_match_sequence
regression_slope = sum((x_i - x_mean) * (y_i - y_mean)) / sum((x_i - x_mean) ** 2)
recent_average = sum(y) / len(y)
volatility = sqrt(sum((y_i - recent_average) ** 2) / len(y))
trend_confidence = r_squared * (1 - volatility / (recent_average + volatility))
```

Trend direction is based on ordered recent performance:
- positive normalized slope above threshold: `Rising`
- negative normalized slope below threshold: `Declining`
- otherwise: `Stable`

## Run Locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Open:
- Root: `http://127.0.0.1:8000/`
- Swagger: `http://127.0.0.1:8000/docs`
- Endpoint: `http://127.0.0.1:8000/student5/form-trend`

## Example Request
```bash
curl -X POST "http://127.0.0.1:8000/student5/form-trend" \
  -H "Content-Type: application/json" \
  -d @sample_payload.json
```

## Example Response
```json
{
  "metric": "form_trend",
  "label": "Rising",
  "explanation": "Recent form is improving because the regression slope is positive (14.135) and meaningfully above the stable threshold.",
  "recent_match_sequence": [22.0, 32.82, 48.17, 64.0],
  "regression_slope": 14.135,
  "recent_average": 41.75,
  "volatility": 15.86,
  "trend_confidence": 0.72
}
```

## Render Deployment
This folder includes `render.yaml`.

Render start command:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Admin Handover
1. Install dependencies with `pip install -r requirements.txt`.
2. Start locally with `uvicorn main:app --reload`.
3. Open `/docs` for Swagger/OpenAPI verification.
4. Test with `sample_payload.json`.
5. Deploy on Render as a Python web service.
6. No database, secrets, or external API calls are needed.
7. All derived variable logic is in `services.py`.
