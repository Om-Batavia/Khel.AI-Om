# Student 5 - Opponent Bayesian Performance Derived Variables API

## Objective
Create an endpoint that converts prior performance and opponent-specific evidence into derived variables for Bayesian opponent performance.

This is formula-based Bayesian analytics, not a trained ML model. The endpoint updates a prior performance belief using opponent-specific evidence and returns the derived variables used in that update.

## Endpoint
- Method: `POST`
- Path: `/student5/opponent-bayesian-derived`
- Swagger/OpenAPI: `/docs`

## Primary Inputs
- `player`: player id, name, and role.
- `opponent_team_id`, `opponent_team_name`: opponent being evaluated.
- `prior_performances`: general recent/historical player performance samples.
- `opponent_performances`: player samples against the target opponent.
- `prior_weight`: strength of the prior belief.
- `max_evidence_weight`: cap on opponent-specific evidence strength.

Each performance sample accepts:
- `runs_scored`
- `balls_faced`
- `was_out`
- optional `performance_value`

## Derived Variables
- `prior_performance_estimate`: average performance from prior samples.
- `opponent_specific_evidence`: average performance from target-opponent samples.
- `evidence_strength`: opponent sample size weighted by consistency.
- `posterior_estimate`: Bayesian weighted update of prior and opponent evidence.
- `confidence`: confidence based on total sample size and evidence strength.

## Formula / Function Code
```python
performance_score = runs_scored + (0.10 * strike_rate) - dismissal_penalty
strike_rate = (runs_scored * 100) / balls_faced
dismissal_penalty = 5 if was_out else 0

prior_performance_estimate = mean(prior_scores)
opponent_specific_evidence = mean(opponent_scores)
volatility = sqrt(sum((score - opponent_average)^2) / n)
consistency_factor = 1 - volatility / (opponent_average + volatility)
evidence_strength = min(opponent_sample_size, max_evidence_weight) * consistency_factor

posterior_estimate =
  ((prior_performance_estimate * prior_weight)
   + (opponent_specific_evidence * evidence_strength))
  / (prior_weight + evidence_strength)

confidence = (0.45 * sample_factor) + (0.55 * evidence_factor)
```

This avoids guessing from one match because the prior remains part of the posterior, and opponent-specific evidence only gets more weight when there are enough consistent opponent samples.

## Run Locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Local URLs:
- Root: `http://127.0.0.1:8000/`
- Swagger docs: `http://127.0.0.1:8000/docs`
- Endpoint: `http://127.0.0.1:8000/student5/opponent-bayesian-derived`

## Example Request
```bash
curl -X POST "http://127.0.0.1:8000/student5/opponent-bayesian-derived" \
  -H "Content-Type: application/json" \
  -d @sample_payload.json
```

## Example Response
```json
{
  "metric": "opponent_bayesian_performance_derived_variables",
  "label": "Opponent Advantage",
  "prior_performance_estimate": 49.01,
  "opponent_specific_evidence": 67.63,
  "evidence_strength": 2.612,
  "posterior_estimate": 54.66,
  "confidence": 0.406,
  "explanation": "The prior belief is updated using opponent-specific evidence instead of guessing from one match."
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
8. All derived variable logic is in `services.py`.
