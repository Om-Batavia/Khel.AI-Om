# Student 5 - Opponent Bayesian Performance Final Output API

## Objective
Create an endpoint that uses Bayesian-derived variables to return opponent-adjusted performance expectation, label, and explanation.

This is formula-based Bayesian analytics, not a trained ML model. It first derives prior and opponent-specific variables, then uses those variables to produce the final opponent-adjusted performance output.

## Endpoint
- Method: `POST`
- Path: `/student5/opponent-bayesian-final`
- Swagger/OpenAPI: `/docs`

## Primary Inputs
- `player`: player id, name, and role.
- `opponent_team_id`, `opponent_team_name`: target opponent.
- `prior_performances`: general historical/recent player samples.
- `opponent_performances`: player samples against the selected opponent.
- `prior_weight`: strength of the prior belief.
- `max_evidence_weight`: maximum allowed opponent evidence strength.

Each performance sample accepts `runs_scored`, `balls_faced`, `was_out`, and optional `performance_value`.

## Derived Variables
- `prior_performance_estimate`: baseline expectation from prior samples.
- `opponent_specific_evidence`: expectation from samples against the target opponent.
- `evidence_strength`: opponent evidence weight based on sample size and consistency.
- `posterior_estimate`: Bayesian updated expectation.
- `prior_to_posterior_change`: amount by which opponent evidence changed the prior.
- `prior_to_posterior_change_percent`: percent change from prior belief.
- `confidence`: numeric confidence used to create `confidence_label`.

## Final Output Fields
- `opponent_adjusted_performance_score`
- `posterior_expectation`
- `confidence_label`
- `derived_variables_used`
- `explanation`

## Formula / Function Code
```python
performance_score = runs_scored + (0.10 * strike_rate) - dismissal_penalty
strike_rate = (runs_scored * 100) / balls_faced
dismissal_penalty = 5 if was_out else 0

prior_estimate = mean(prior_scores)
opponent_evidence = mean(opponent_scores)
volatility = sqrt(sum((score - opponent_evidence)^2) / n)
evidence_strength = min(opponent_sample_size, max_evidence_weight) * (1 - volatility / (opponent_evidence + volatility))

posterior_expectation =
  ((prior_estimate * prior_weight) + (opponent_evidence * evidence_strength))
  / (prior_weight + evidence_strength)

opponent_adjusted_performance_score = posterior_expectation
prior_to_posterior_change = posterior_expectation - prior_estimate
confidence = (0.45 * sample_factor) + (0.55 * evidence_factor)
```

The explanation explicitly states how the prior belief changed after opponent-specific evidence.

## Run Locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Local URLs:
- Root: `http://127.0.0.1:8000/`
- Swagger docs: `http://127.0.0.1:8000/docs`
- Endpoint: `http://127.0.0.1:8000/student5/opponent-bayesian-final`

## Example Request
```bash
curl -X POST "http://127.0.0.1:8000/student5/opponent-bayesian-final" \
  -H "Content-Type: application/json" \
  -d @sample_payload.json
```

## Example Response
```json
{
  "metric": "opponent_bayesian_performance_final_output",
  "label": "Opponent Boost",
  "opponent_adjusted_performance_score": 54.66,
  "posterior_expectation": 54.66,
  "confidence_label": "Medium Confidence",
  "derived_variables_used": {
    "prior_performance_estimate": 49.01,
    "opponent_specific_evidence": 67.63,
    "evidence_strength": 2.612,
    "posterior_estimate": 54.66,
    "prior_to_posterior_change": 5.65,
    "prior_to_posterior_change_percent": 11.53,
    "confidence": 0.406
  },
  "explanation": "The prior belief increased after opponent-specific evidence was applied."
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
8. All derived variables and final output logic are in `services.py`.
