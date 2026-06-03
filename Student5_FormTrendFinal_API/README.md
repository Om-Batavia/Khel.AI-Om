# Student 5 - Form Trend Final Output API

## Objective
Create an endpoint that uses trend-derived variables to return Form Trend score, label, and explanation.

This API calculates derived variables from recent ordered performance inputs, then converts those variables into a final form trend output. It clearly separates Rising, Stable, and Declining form based on the direction of the ordered recent sequence.

## Endpoint
- Method: `POST`
- Path: `/student5/form-trend-final`
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

Primary input explanation:
- `sequence_number`: chronological order from oldest to newest.
- `runs_scored`: batter runs in the match.
- `balls_faced`: balls faced in the match.
- `was_out`: dismissal flag.
- `performance_value`: optional precomputed performance score.
- `stable_slope_threshold`: normalized slope band used to classify Stable form.

## Derived Variables
- `recent_match_sequence`: ordered performance scores derived from each match.
- `regression_slope`: Ordinary Least Squares slope of performance over time.
- `recent_average`: average of derived performance scores.
- `volatility`: standard deviation of derived performance scores.
- `normalized_trend_score`: regression slope divided by recent average.
- `r_squared`: how well the line fits the recent sequence.
- `trend_confidence`: confidence after adjusting fit quality for volatility.

## Final Output Fields
- `form_trend_score`
- `trend_label`
- `trend_confidence`
- `derived_variables_used`
- `explanation`

The response also includes `metric`, `label`, and `supporting_values` for review.

## Formula / Function Code
```python
performance_score = runs_scored + (0.10 * strike_rate) - dismissal_penalty
strike_rate = (runs_scored * 100) / balls_faced
dismissal_penalty = 5 if was_out else 0

regression_slope = sum((x_i - x_mean) * (y_i - y_mean)) / sum((x_i - x_mean) ** 2)
recent_average = sum(y) / len(y)
volatility = sqrt(sum((y_i - recent_average) ** 2) / len(y))
normalized_trend_score = regression_slope / recent_average
trend_confidence = r_squared * (1 - volatility / (recent_average + volatility))
form_trend_score = clamp(50 + (normalized_trend_score * 100), 0, 100)
```

Label rule:
- `Rising` if `normalized_trend_score > stable_slope_threshold`
- `Declining` if `normalized_trend_score < -stable_slope_threshold`
- `Stable` otherwise

## Run Locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Local URLs:
- Root: `http://127.0.0.1:8000/`
- Swagger docs: `http://127.0.0.1:8000/docs`
- Endpoint: `http://127.0.0.1:8000/student5/form-trend-final`

## Example Request
```bash
curl -X POST "http://127.0.0.1:8000/student5/form-trend-final" \
  -H "Content-Type: application/json" \
  -d @sample_payload.json
```

## Example Response
```json
{
  "metric": "form_trend_final_output",
  "label": "Rising",
  "form_trend_score": 83.86,
  "trend_label": "Rising",
  "trend_confidence": 0.72,
  "derived_variables_used": {
    "recent_match_sequence": [22.0, 32.82, 48.17, 64.0],
    "regression_slope": 14.135,
    "recent_average": 41.75,
    "volatility": 15.86,
    "normalized_trend_score": 0.339,
    "r_squared": 0.993
  },
  "explanation": "Form is classified as Rising because the ordered recent sequence has a positive normalized trend score above the stable threshold."
}
```

## Admin Handover
1. Install dependencies with `pip install -r requirements.txt`.
2. Run locally with `uvicorn main:app --reload`.
3. Open Swagger at `http://127.0.0.1:8000/docs`.
4. Test with `sample_payload.json`.
5. Deploy on Render as a Python web service.
6. Render start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`.
7. No database, secrets, or external APIs are required.
8. All derived variable and final score logic is in `services.py`.
