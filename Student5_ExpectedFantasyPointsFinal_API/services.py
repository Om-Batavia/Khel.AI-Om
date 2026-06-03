from schemas import ComponentBreakdown, DerivedVariablesUsed, ExpectedFantasyFinalRequest, ExpectedFantasyFinalResponse


BATTING_EVENTS = ["run_0", "run_1", "run_2", "run_3", "four", "six", "dismissal"]
BOWLING_EVENTS = ["dot_ball", "wicket", "maiden_over", "economy_bonus"]
FIELDING_EVENTS = ["catch", "run_out", "stumping"]


def calculate_expected_fantasy_final(payload: ExpectedFantasyFinalRequest) -> ExpectedFantasyFinalResponse:
    batting_probabilities = payload.batting_event_probabilities.model_dump()
    bowling_probabilities = payload.bowling_event_probabilities.model_dump()
    fielding_probabilities = payload.fielding_event_probabilities.model_dump()
    point_values = payload.event_point_values.model_dump()
    thresholds = payload.selection_thresholds.model_dump()

    batting_breakdown = _expected_breakdown(batting_probabilities, point_values, BATTING_EVENTS)
    bowling_breakdown = _expected_breakdown(bowling_probabilities, point_values, BOWLING_EVENTS)
    fielding_breakdown = _expected_breakdown(fielding_probabilities, point_values, FIELDING_EVENTS)

    batting_expected = sum(batting_breakdown.values())
    bowling_expected = sum(bowling_breakdown.values())
    fielding_expected = sum(fielding_breakdown.values())
    expected_points = batting_expected + bowling_expected + fielding_expected
    event_breakdown = {**batting_breakdown, **bowling_breakdown, **fielding_breakdown}
    selection_label = _selection_label(expected_points, thresholds)

    return ExpectedFantasyFinalResponse(
        metric="expected_fantasy_points_final_output",
        label=selection_label,
        expected_fantasy_points=_round_float(expected_points, 2),
        selection_value_label=selection_label,
        component_breakdown=ComponentBreakdown(
            batting_expected_points=_round_float(batting_expected, 2),
            bowling_expected_points=_round_float(bowling_expected, 2),
            fielding_expected_points=_round_float(fielding_expected, 2),
            event_breakdown={key: _round_float(value, 3) for key, value in event_breakdown.items()},
        ),
        derived_variables_used=DerivedVariablesUsed(
            batting_event_probabilities=batting_probabilities,
            bowling_event_probabilities=bowling_probabilities,
            fielding_event_probabilities=fielding_probabilities,
            event_point_values=point_values,
            selection_thresholds=thresholds,
        ),
        explanation=_build_explanation(expected_points, selection_label, thresholds),
        supporting_values={
            "formula": "expected_fantasy_points = sum(event_probability * event_point_value)",
            "decision_rule": "Strong Pick if >= strong_pick_min; Playable Pick if >= playable_min; Avoid Pick otherwise.",
            "uncertainty_note": "Selection is based on expected value because each event is uncertain and represented by probability.",
        },
        player_id=payload.player.player_id,
        player_name=payload.player.player_name,
    )


def _expected_breakdown(probabilities: dict[str, float], point_values: dict[str, float], events: list[str]) -> dict[str, float]:
    return {event: probabilities[event] * point_values[event] for event in events}


def _selection_label(expected_points: float, thresholds: dict[str, float]) -> str:
    if expected_points >= thresholds["strong_pick_min"]:
        return "Strong Fantasy Pick"
    if expected_points >= thresholds["playable_min"]:
        return "Playable Fantasy Pick"
    return "Avoid / Low Value Pick"


def _build_explanation(expected_points: float, label: str, thresholds: dict[str, float]) -> str:
    return (
        f"The expected fantasy points are {_round_float(expected_points, 2)}. "
        "This is a decision under uncertainty because every possible batting, bowling, and fielding event "
        "is weighted by its probability and point value before selection is judged. "
        f"Using thresholds strong_pick_min={thresholds['strong_pick_min']} and playable_min={thresholds['playable_min']}, "
        f"the selection value label is {label}."
    )


def _round_float(value: float, decimals: int = 3) -> float:
    return round(float(value), decimals)
