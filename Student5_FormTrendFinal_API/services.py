from schemas import DerivedVariables, FormTrendFinalRequest, FormTrendFinalResponse


def calculate_form_trend_final(payload: FormTrendFinalRequest) -> FormTrendFinalResponse:
    ordered_records = sorted(payload.recent_performances, key=lambda record: record.sequence_number)
    performance_sequence = [
        _derive_performance_score(record)
        for record in ordered_records
    ]

    x_values = list(range(1, len(performance_sequence) + 1))
    regression_slope, r_squared = _ordinary_least_squares(x_values, performance_sequence)
    recent_average = _safe_divide(sum(performance_sequence), len(performance_sequence))
    volatility = _population_standard_deviation(performance_sequence, recent_average)
    normalized_trend_score = _safe_divide(regression_slope, recent_average) if recent_average > 0 else regression_slope
    trend_confidence = _calculate_trend_confidence(
        r_squared=r_squared,
        volatility=volatility,
        recent_average=recent_average,
    )
    form_trend_score = _calculate_form_trend_score(normalized_trend_score)
    trend_label = _classify_trend(
        normalized_trend_score=normalized_trend_score,
        threshold=payload.stable_slope_threshold,
    )

    derived_variables = DerivedVariables(
        recent_match_sequence=[_round_float(value, 2) for value in performance_sequence],
        regression_slope=_round_float(regression_slope, 3),
        recent_average=_round_float(recent_average, 2),
        volatility=_round_float(volatility, 2),
        normalized_trend_score=_round_float(normalized_trend_score, 3),
        r_squared=_round_float(r_squared, 3),
    )

    explanation = _build_explanation(
        trend_label=trend_label,
        form_trend_score=form_trend_score,
        regression_slope=regression_slope,
        normalized_trend_score=normalized_trend_score,
        trend_confidence=trend_confidence,
        threshold=payload.stable_slope_threshold,
    )

    return FormTrendFinalResponse(
        metric="form_trend_final_output",
        label=trend_label,
        form_trend_score=_round_float(form_trend_score, 2),
        trend_label=trend_label,
        trend_confidence=_round_float(trend_confidence, 3),
        derived_variables_used=derived_variables,
        explanation=explanation,
        supporting_values={
            "sample_size": len(performance_sequence),
            "stable_slope_threshold": payload.stable_slope_threshold,
            "score_formula": "form_trend_score = clamp(50 + (normalized_trend_score * 100), 0, 100)",
            "label_rule": "Rising if normalized_trend_score > threshold; Declining if below -threshold; otherwise Stable.",
            "confidence_formula": "trend_confidence = r_squared * (1 - volatility / (recent_average + volatility))",
        },
        player_id=payload.player.player_id,
        player_name=payload.player.player_name,
    )


def _derive_performance_score(record) -> float:
    if record.performance_value is not None:
        return max(float(record.performance_value), 0.0)

    strike_rate = _safe_divide(record.runs_scored * 100, record.balls_faced)
    dismissal_penalty = 5.0 if record.was_out else 0.0
    performance_score = record.runs_scored + (0.10 * strike_rate) - dismissal_penalty
    return max(performance_score, 0.0)


def _ordinary_least_squares(x_values: list[int], y_values: list[float]) -> tuple[float, float]:
    x_mean = _safe_divide(sum(x_values), len(x_values))
    y_mean = _safe_divide(sum(y_values), len(y_values))

    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    denominator = sum((x - x_mean) ** 2 for x in x_values)
    slope = _safe_divide(numerator, denominator)
    intercept = y_mean - (slope * x_mean)

    predicted_values = [(slope * x) + intercept for x in x_values]
    total_sum_squares = sum((y - y_mean) ** 2 for y in y_values)
    residual_sum_squares = sum((y - predicted) ** 2 for y, predicted in zip(y_values, predicted_values))
    r_squared = 1 - _safe_divide(residual_sum_squares, total_sum_squares) if total_sum_squares else 0.0

    return slope, max(0.0, min(r_squared, 1.0))


def _population_standard_deviation(values: list[float], average: float) -> float:
    variance = _safe_divide(sum((value - average) ** 2 for value in values), len(values))
    return variance ** 0.5


def _calculate_trend_confidence(r_squared: float, volatility: float, recent_average: float) -> float:
    noise_penalty = _safe_divide(volatility, recent_average + volatility) if recent_average or volatility else 0.0
    confidence = r_squared * (1 - noise_penalty)
    return max(0.0, min(confidence, 1.0))


def _calculate_form_trend_score(normalized_trend_score: float) -> float:
    score = 50 + (normalized_trend_score * 100)
    return max(0.0, min(score, 100.0))


def _classify_trend(normalized_trend_score: float, threshold: float) -> str:
    if normalized_trend_score > threshold:
        return "Rising"
    if normalized_trend_score < -threshold:
        return "Declining"
    return "Stable"


def _build_explanation(
    trend_label: str,
    form_trend_score: float,
    regression_slope: float,
    normalized_trend_score: float,
    trend_confidence: float,
    threshold: float,
) -> str:
    return (
        f"Form is classified as {trend_label} with a score of {_round_float(form_trend_score, 2)}. "
        f"The ordered recent sequence produced regression_slope={_round_float(regression_slope, 3)} "
        f"and normalized_trend_score={_round_float(normalized_trend_score, 3)}. "
        f"The label uses threshold +/-{threshold}, so positive values above the threshold are Rising, "
        "negative values below the threshold are Declining, and values inside the band are Stable. "
        f"Trend confidence is {_round_float(trend_confidence, 3)} after adjusting trend fit for volatility."
    )


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _round_float(value: float, decimals: int = 3) -> float:
    return round(float(value), decimals)
