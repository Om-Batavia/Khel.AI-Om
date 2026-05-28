from schemas import MatchOutlookRequest, MatchOutlookResponse


HEURISTIC = (
    "High Chance when target is reached, or required rate is within current rate + 1.5 "
    "with at least 4 wickets in hand. Low Chance when no balls/wickets remain before "
    "the target, required rate is more than current rate + 4, or 2 or fewer wickets "
    "remain while more than 20 runs are needed. Otherwise Medium Chance."
)


def calculate_match_outlook(payload: MatchOutlookRequest) -> MatchOutlookResponse:
    target = _first_present(payload.innings.target, payload.match.target)
    total_overs = _first_present(payload.innings.total_overs_limit, payload.match.total_overs, 20)

    total_runs = sum(ball.runs_off_bat + ball.extras for ball in payload.balls)
    legal_balls = sum(1 for ball in payload.balls if ball.is_legal_delivery)
    wickets_lost = min(sum(1 for ball in payload.balls if ball.wicket_fell), 10)
    wickets_in_hand = max(10 - wickets_lost, 0)

    total_balls = int(total_overs) * 6
    balls_remaining = max(total_balls - legal_balls, 0)
    overs_completed = legal_balls / 6
    current_run_rate = round(total_runs / overs_completed, 2) if overs_completed else 0

    if target is None:
        return MatchOutlookResponse(
            runs_needed=0,
            balls_remaining=balls_remaining,
            required_run_rate=0,
            prediction="Medium Chance",
            wickets_in_hand=wickets_in_hand,
            overs_left=_overs_display(balls_remaining),
            current_run_rate=current_run_rate,
            heuristic=HEURISTIC,
            reason="No target was provided, so the API returns a neutral non-chase outlook.",
        )

    runs_needed = max(target - total_runs, 0)
    required_run_rate = _required_run_rate(runs_needed, balls_remaining)
    prediction, reason = _prediction_label(
        runs_needed=runs_needed,
        balls_remaining=balls_remaining,
        wickets_in_hand=wickets_in_hand,
        current_run_rate=current_run_rate,
        required_run_rate=required_run_rate,
    )

    return MatchOutlookResponse(
        runs_needed=runs_needed,
        balls_remaining=balls_remaining,
        required_run_rate=required_run_rate,
        prediction=prediction,
        wickets_in_hand=wickets_in_hand,
        overs_left=_overs_display(balls_remaining),
        current_run_rate=current_run_rate,
        heuristic=HEURISTIC,
        reason=reason,
    )


def _prediction_label(
    runs_needed: int,
    balls_remaining: int,
    wickets_in_hand: int,
    current_run_rate: float,
    required_run_rate: float,
) -> tuple[str, str]:
    if runs_needed == 0:
        return "High Chance", "The chasing team has already reached the target."
    if balls_remaining == 0 or wickets_in_hand == 0:
        return "Low Chance", "The chase is not available because balls or wickets are exhausted."
    if required_run_rate <= current_run_rate + 1.5 and wickets_in_hand >= 4:
        return "High Chance", "Required rate is close to the current rate and wickets are in hand."
    if required_run_rate > current_run_rate + 4:
        return "Low Chance", "Required rate is much higher than the current scoring rate."
    if wickets_in_hand <= 2 and runs_needed > 20:
        return "Low Chance", "Very few wickets remain with more than 20 runs still needed."
    return "Medium Chance", "The chase is open, but rate pressure and wickets are not clearly favorable."


def _required_run_rate(runs_needed: int, balls_remaining: int) -> float:
    if runs_needed == 0 or balls_remaining == 0:
        return 0
    return round((runs_needed / balls_remaining) * 6, 2)


def _overs_display(balls: int) -> str:
    return f"{balls // 6}.{balls % 6}"


def _first_present(*values):
    for value in values:
        if value is not None:
            return value
    return None
