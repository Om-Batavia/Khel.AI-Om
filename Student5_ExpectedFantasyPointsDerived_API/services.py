from schemas import ExpectedFantasyRequest, ExpectedFantasyResponse, ExpectedValueComponents


BATTING_EVENTS = ["run_0", "run_1", "run_2", "run_3", "four", "six", "dismissal"]
BOWLING_EVENTS = ["dot_ball", "wicket", "maiden_over", "economy_bonus"]
FIELDING_EVENTS = ["catch", "run_out", "stumping"]


def calculate_expected_fantasy_variables(payload: ExpectedFantasyRequest) -> ExpectedFantasyResponse:
    batting_probabilities = payload.batting_event_probabilities.model_dump()
    bowling_probabilities = payload.bowling_event_probabilities.model_dump()
    fielding_probabilities = payload.fielding_event_probabilities.model_dump()
    point_values = payload.event_point_values.model_dump()

    batting_breakdown = _expected_breakdown(batting_probabilities, point_values, BATTING_EVENTS)
    bowling_breakdown = _expected_breakdown(bowling_probabilities, point_values, BOWLING_EVENTS)
    fielding_breakdown = _expected_breakdown(fielding_probabilities, point_values, FIELDING_EVENTS)

    batting_expected = sum(batting_breakdown.values())
    bowling_expected = sum(bowling_breakdown.values())
    fielding_expected = sum(fielding_breakdown.values())
    total_expected = batting_expected + bowling_expected + fielding_expected
    event_breakdown = {**batting_breakdown, **bowling_breakdown, **fielding_breakdown}

    return ExpectedFantasyResponse(
        metric="expected_fantasy_points_derived_variables",
        label=_classify_expected_points(total_expected),
        explanation=(
            f"Expected fantasy points are calculated as sum(probability * point_value) across batting, "
            f"bowling, and fielding events. The total expected value is {_round_float(total_expected, 2)}."
        ),
        batting_event_probabilities=batting_probabilities,
        bowling_event_probabilities=bowling_probabilities,
        fielding_event_probabilities=fielding_probabilities,
        event_point_values=point_values,
        expected_value_components=ExpectedValueComponents(
            batting_expected_points=_round_float(batting_expected, 2),
            bowling_expected_points=_round_float(bowling_expected, 2),
            fielding_expected_points=_round_float(fielding_expected, 2),
            total_expected_fantasy_points=_round_float(total_expected, 2),
            event_breakdown={key: _round_float(value, 3) for key, value in event_breakdown.items()},
        ),
        supporting_values={
            "formula": "expected_points = sum(event_probability * event_point_value)",
            "batting_events": BATTING_EVENTS,
            "bowling_events": BOWLING_EVENTS,
            "fielding_events": FIELDING_EVENTS,
        },
        player_id=payload.player.player_id,
        player_name=payload.player.player_name,
    )


def _expected_breakdown(probabilities: dict[str, float], point_values: dict[str, float], events: list[str]) -> dict[str, float]:
    return {
        event: probabilities[event] * point_values[event]
        for event in events
    }


def _classify_expected_points(total_expected: float) -> str:
    if total_expected >= 30:
        return "High Expected Fantasy Value"
    if total_expected >= 15:
        return "Medium Expected Fantasy Value"
    return "Low Expected Fantasy Value"


def _round_float(value: float, decimals: int = 3) -> float:
    return round(float(value), decimals)
