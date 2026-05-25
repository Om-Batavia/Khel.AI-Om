from schemas import MatchState, WinProbabilityRequest, WinProbabilityResponse


def calculate_win_probability_label(payload: WinProbabilityRequest) -> WinProbabilityResponse:
    innings = payload.innings
    match = payload.match
    balls = payload.balls

    target = innings.target or match.target
    total_overs = innings.total_overs_limit or match.total_overs or 20

    total_runs = sum(_int(ball.runs_off_bat) + _int(ball.extras) for ball in balls)
    legal_balls = sum(1 for ball in balls if ball.is_legal_delivery)
    wickets = sum(1 for ball in balls if ball.wicket_fell)
    total_balls = int(total_overs) * 6
    balls_remaining = max(total_balls - legal_balls, 0)
    overs_completed = legal_balls / 6
    current_run_rate = round(total_runs / overs_completed, 2) if overs_completed else 0

    if not target:
        return WinProbabilityResponse(
            prediction="Medium Chance",
            label="Medium Chance",
            confidence_score=50,
            reason="No chase target is available, so the API returns a neutral outlook.",
            rule="Target missing -> Medium Chance.",
            match_state=_match_state(total_runs, wickets, legal_balls, target, balls_remaining, None),
        )

    runs_needed = max(_int(target) - total_runs, 0)
    wickets_remaining = max(10 - wickets, 0)
    required_run_rate = (
        round((runs_needed / balls_remaining) * 6, 2)
        if balls_remaining and runs_needed
        else 0
    )

    if runs_needed == 0:
        prediction = "High Chance"
        confidence = 100
        reason = "The chasing team has already reached the target."
    elif balls_remaining == 0 or wickets_remaining == 0:
        prediction = "Low Chance"
        confidence = 95
        reason = "The chase is no longer realistically available because balls or wickets are exhausted."
    elif _is_high_chance(required_run_rate, current_run_rate, wickets_remaining, runs_needed, balls_remaining):
        prediction = "High Chance"
        confidence = 75
        reason = "Required run rate is controlled compared with the current scoring rate and wickets in hand."
    elif _is_low_chance(required_run_rate, current_run_rate, wickets_remaining, runs_needed):
        prediction = "Low Chance"
        confidence = 70
        reason = "Required run rate is far above the current scoring rate or wickets in hand are very low."
    else:
        prediction = "Medium Chance"
        confidence = 60
        reason = "The chase is still open, but the required rate and wicket position are not clearly favorable."

    return WinProbabilityResponse(
        prediction=prediction,
        label=prediction,
        confidence_score=confidence,
        reason=reason,
        rule=(
            "High Chance when RRR <= current RR + 1.5 with at least 4 wickets left, "
            "or when <= 12 runs are needed with at least 12 balls left. "
            "Low Chance when RRR > current RR + 4, or when 2 or fewer wickets remain "
            "and more than 20 runs are needed. Otherwise Medium Chance."
        ),
        match_state=_match_state(
            total_runs,
            wickets,
            legal_balls,
            target,
            balls_remaining,
            required_run_rate,
        ),
        inputs_used={
            "runs_needed": runs_needed,
            "wickets_remaining": wickets_remaining,
            "current_run_rate": current_run_rate,
            "required_run_rate": required_run_rate,
        },
    )


def _is_high_chance(required_run_rate, current_run_rate, wickets_remaining, runs_needed, balls_remaining):
    return (
        required_run_rate <= current_run_rate + 1.5
        and wickets_remaining >= 4
    ) or (
        runs_needed <= 12
        and balls_remaining >= 12
        and wickets_remaining >= 3
    )


def _is_low_chance(required_run_rate, current_run_rate, wickets_remaining, runs_needed):
    return (
        required_run_rate > current_run_rate + 4
    ) or (
        wickets_remaining <= 2
        and runs_needed > 20
    )


def _match_state(total_runs, wickets, legal_balls, target, balls_remaining, required_run_rate):
    return MatchState(
        score=f"{total_runs}/{wickets}",
        overs=_overs_display(legal_balls),
        target=target,
        balls_remaining=balls_remaining,
        required_run_rate=required_run_rate,
    )


def _overs_display(legal_balls):
    return f"{legal_balls // 6}.{legal_balls % 6}"


def _int(value):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0
