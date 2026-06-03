from schemas import DerivedPerformancePoint, FormTrendRequest, FormTrendResponse
from utils import round_float, safe_divide, validate_recent_series_length


SCIENTIFIC_PRINCIPLE = (
    "Ordinary Least Squares linear regression is fitted with time_index as the independent "
    "variable and derived performance_score as the dependent variable. The slope measures "
    "direction of form over time; R-squared describes how consistently the recent points "
    "follow that linear direction."
)

ASSUMPTIONS = [
    "Recent performances are ordered from oldest to newest using sequence_number.",
    "If performance_value is provided, it is used directly as the model score.",
    "If performance_value is missing, batting performance_score is derived from runs, strike rate, and dismissal status.",
    "A normalized slope within the stable threshold is interpreted as stable form.",
]


def calculate_form_trend(payload: FormTrendRequest) -> FormTrendResponse:
    ordered_records = sorted(payload.recent_performances, key=lambda record: record.sequence_number)
    validate_recent_series_length(len(ordered_records))

    derived_points = [
        _build_performance_point(record=record, time_index=index + 1)
        for index, record in enumerate(ordered_records)
    ]

    x_values = [point.time_index for point in derived_points]
    y_values = [point.performance_score for point in derived_points]

    slope, r_squared = _ordinary_least_squares(x_values, y_values)
    average_score = safe_divide(sum(y_values), len(y_values))
    volatility = _population_standard_deviation(y_values, average_score)
    normalized_trend_score = safe_divide(slope, average_score) if average_score > 0 else slope
    trend_label, interpretation = _interpret_trend(
        normalized_trend_score=normalized_trend_score,
        slope=slope,
        threshold=payload.stable_slope_threshold,
    )
    trend_confidence = _calculate_trend_confidence(
        r_squared=r_squared,
        volatility=volatility,
        average_score=average_score,
    )

    return FormTrendResponse(
        metric="form_trend",
        label=trend_label,
        explanation=interpretation,
        recent_match_sequence=[point.performance_score for point in derived_points],
        regression_slope=round_float(slope, 3),
        recent_average=round_float(average_score, 2),
        volatility=round_float(volatility, 2),
        trend_confidence=round_float(trend_confidence, 3),
        supporting_values={
            "sample_size": len(derived_points),
            "normalized_trend_score": round_float(normalized_trend_score, 3),
            "r_squared": round_float(r_squared, 3),
            "stable_slope_threshold": payload.stable_slope_threshold,
            "time_index_order": x_values,
            "formula": (
                "performance_score = runs_scored + (0.10 * strike_rate) - dismissal_penalty; "
                "regression_slope = sum((x-x_mean)(y-y_mean)) / sum((x-x_mean)^2); "
                "volatility = sqrt(sum((y-y_mean)^2) / n); "
                "trend_confidence = r_squared * (1 - volatility / (average + volatility))"
            ),
        },
        api_name="Form Trend (Regression) API",
        player_id=payload.player.player_id,
        player_name=payload.player.player_name,
        sample_size=len(derived_points),
        average_performance_score=round_float(average_score, 2),
        normalized_trend_score=round_float(normalized_trend_score, 3),
        r_squared=round_float(r_squared, 3),
        trend_label=trend_label,
        trend_interpretation=interpretation,
        derived_points=derived_points,
        scientific_principle=SCIENTIFIC_PRINCIPLE,
        assumptions=ASSUMPTIONS,
    )


def _build_performance_point(record, time_index: int) -> DerivedPerformancePoint:
    strike_rate = safe_divide(record.runs_scored * 100, record.balls_faced)
    dismissal_penalty = 5.0 if record.was_out else 0.0

    if record.performance_value is None:
        performance_score = record.runs_scored + (0.10 * strike_rate) - dismissal_penalty
    else:
        performance_score = record.performance_value

    return DerivedPerformancePoint(
        sequence_number=record.sequence_number,
        time_index=time_index,
        runs_scored=record.runs_scored,
        balls_faced=record.balls_faced,
        strike_rate=round_float(strike_rate, 2),
        dismissal_penalty=dismissal_penalty,
        performance_score=round_float(max(performance_score, 0), 2),
    )


def _ordinary_least_squares(x_values: list[int], y_values: list[float]) -> tuple[float, float]:
    x_mean = safe_divide(sum(x_values), len(x_values))
    y_mean = safe_divide(sum(y_values), len(y_values))

    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    denominator = sum((x - x_mean) ** 2 for x in x_values)
    slope = safe_divide(numerator, denominator)
    intercept = y_mean - (slope * x_mean)

    predicted_values = [(slope * x) + intercept for x in x_values]
    total_sum_squares = sum((y - y_mean) ** 2 for y in y_values)
    residual_sum_squares = sum((y - predicted) ** 2 for y, predicted in zip(y_values, predicted_values))
    r_squared = 1 - safe_divide(residual_sum_squares, total_sum_squares) if total_sum_squares else 0.0

    return slope, max(0.0, min(r_squared, 1.0))


def _population_standard_deviation(values: list[float], average: float) -> float:
    variance = safe_divide(sum((value - average) ** 2 for value in values), len(values))
    return variance ** 0.5


def _calculate_trend_confidence(r_squared: float, volatility: float, average_score: float) -> float:
    noise_penalty = safe_divide(volatility, average_score + volatility) if average_score or volatility else 0.0
    confidence = r_squared * (1 - noise_penalty)
    return max(0.0, min(confidence, 1.0))


def _interpret_trend(normalized_trend_score: float, slope: float, threshold: float) -> tuple[str, str]:
    if normalized_trend_score > threshold:
        return (
            "Rising",
            f"Recent form is improving because the regression slope is positive ({round_float(slope, 3)}) "
            "and meaningfully above the stable threshold.",
        )
    if normalized_trend_score < -threshold:
        return (
            "Declining",
            f"Recent form is dropping because the regression slope is negative ({round_float(slope, 3)}) "
            "and meaningfully below the stable threshold.",
        )
    return (
        "Stable",
        f"Recent form is broadly steady because the normalized slope is within +/-{threshold}.",
    )
