from schemas import OpponentBayesianRequest, OpponentBayesianResponse


def calculate_opponent_bayesian_variables(payload: OpponentBayesianRequest) -> OpponentBayesianResponse:
    prior_scores = [_derive_performance_score(sample) for sample in payload.prior_performances]
    opponent_scores = [_derive_performance_score(sample) for sample in payload.opponent_performances]

    prior_estimate = _mean(prior_scores)
    opponent_evidence = _mean(opponent_scores)
    opponent_volatility = _population_standard_deviation(opponent_scores, opponent_evidence)
    evidence_strength = _calculate_evidence_strength(
        sample_size=len(opponent_scores),
        volatility=opponent_volatility,
        average_score=opponent_evidence,
        max_evidence_weight=payload.max_evidence_weight,
    )
    posterior_estimate = _calculate_posterior_estimate(
        prior_estimate=prior_estimate,
        opponent_evidence=opponent_evidence,
        prior_weight=payload.prior_weight,
        evidence_strength=evidence_strength,
    )
    confidence = _calculate_confidence(
        prior_sample_size=len(prior_scores),
        opponent_sample_size=len(opponent_scores),
        evidence_strength=evidence_strength,
        max_evidence_weight=payload.max_evidence_weight,
    )
    label = _classify_posterior_shift(
        prior_estimate=prior_estimate,
        posterior_estimate=posterior_estimate,
    )

    return OpponentBayesianResponse(
        metric="opponent_bayesian_performance_derived_variables",
        label=label,
        explanation=_build_explanation(
            label=label,
            prior_estimate=prior_estimate,
            opponent_evidence=opponent_evidence,
            evidence_strength=evidence_strength,
            posterior_estimate=posterior_estimate,
            confidence=confidence,
        ),
        prior_performance_estimate=_round_float(prior_estimate, 2),
        opponent_specific_evidence=_round_float(opponent_evidence, 2),
        evidence_strength=_round_float(evidence_strength, 3),
        posterior_estimate=_round_float(posterior_estimate, 2),
        confidence=_round_float(confidence, 3),
        supporting_values={
            "prior_sample_size": len(prior_scores),
            "opponent_sample_size": len(opponent_scores),
            "prior_weight": payload.prior_weight,
            "max_evidence_weight": payload.max_evidence_weight,
            "opponent_volatility": _round_float(opponent_volatility, 2),
            "prior_scores": [_round_float(score, 2) for score in prior_scores],
            "opponent_scores": [_round_float(score, 2) for score in opponent_scores],
            "posterior_formula": (
                "posterior = ((prior_estimate * prior_weight) + "
                "(opponent_specific_evidence * evidence_strength)) / "
                "(prior_weight + evidence_strength)"
            ),
            "evidence_strength_formula": (
                "evidence_strength = min(opponent_sample_size, max_evidence_weight) "
                "* consistency_factor, where consistency_factor = 1 - "
                "volatility / (opponent_average + volatility)"
            ),
        },
        player_id=payload.player.player_id,
        player_name=payload.player.player_name,
        opponent_team_id=payload.opponent_team_id,
        opponent_team_name=payload.opponent_team_name,
    )


def _derive_performance_score(sample) -> float:
    if sample.performance_value is not None:
        return max(float(sample.performance_value), 0.0)

    strike_rate = _safe_divide(sample.runs_scored * 100, sample.balls_faced)
    dismissal_penalty = 5.0 if sample.was_out else 0.0
    score = sample.runs_scored + (0.10 * strike_rate) - dismissal_penalty
    return max(score, 0.0)


def _calculate_evidence_strength(
    sample_size: int,
    volatility: float,
    average_score: float,
    max_evidence_weight: float,
) -> float:
    consistency_factor = 1 - _safe_divide(volatility, average_score + volatility) if average_score or volatility else 0.0
    raw_strength = min(float(sample_size), max_evidence_weight) * consistency_factor
    return max(0.0, min(raw_strength, max_evidence_weight))


def _calculate_posterior_estimate(
    prior_estimate: float,
    opponent_evidence: float,
    prior_weight: float,
    evidence_strength: float,
) -> float:
    return _safe_divide(
        (prior_estimate * prior_weight) + (opponent_evidence * evidence_strength),
        prior_weight + evidence_strength,
    )


def _calculate_confidence(
    prior_sample_size: int,
    opponent_sample_size: int,
    evidence_strength: float,
    max_evidence_weight: float,
) -> float:
    sample_factor = min((prior_sample_size + opponent_sample_size) / 12, 1.0)
    evidence_factor = _safe_divide(evidence_strength, max_evidence_weight)
    confidence = (0.45 * sample_factor) + (0.55 * evidence_factor)
    return max(0.0, min(confidence, 1.0))


def _classify_posterior_shift(prior_estimate: float, posterior_estimate: float) -> str:
    shift_ratio = _safe_divide(posterior_estimate - prior_estimate, prior_estimate)
    if shift_ratio >= 0.10:
        return "Opponent Advantage"
    if shift_ratio <= -0.10:
        return "Opponent Risk"
    return "Neutral Opponent Adjustment"


def _build_explanation(
    label: str,
    prior_estimate: float,
    opponent_evidence: float,
    evidence_strength: float,
    posterior_estimate: float,
    confidence: float,
) -> str:
    return (
        f"The prior performance estimate is {_round_float(prior_estimate, 2)}. "
        f"Opponent-specific evidence is {_round_float(opponent_evidence, 2)} with evidence strength "
        f"{_round_float(evidence_strength, 3)}. The Bayesian weighted update gives posterior_estimate="
        f"{_round_float(posterior_estimate, 2)} and confidence={_round_float(confidence, 3)}. "
        f"The final label is {label}, so the result updates prior belief using opponent evidence "
        "instead of guessing from a single match."
    )


def _mean(values: list[float]) -> float:
    return _safe_divide(sum(values), len(values))


def _population_standard_deviation(values: list[float], average: float) -> float:
    variance = _safe_divide(sum((value - average) ** 2 for value in values), len(values))
    return variance ** 0.5


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _round_float(value: float, decimals: int = 3) -> float:
    return round(float(value), decimals)
