from schemas import MatchStateRequest, MatchStateResponse


def get_match_state(payload: MatchStateRequest) -> MatchStateResponse:
    target = _first_present(payload.innings.target, payload.match.target)
    total_overs = _first_present(payload.innings.total_overs_limit, payload.match.total_overs, 20)
    match_name = payload.match.title or payload.match.match_id or "Unknown match"

    total_runs = sum(ball.runs_off_bat + ball.extras for ball in payload.balls)
    legal_balls = sum(1 for ball in payload.balls if ball.is_legal_delivery)
    wickets = min(sum(1 for ball in payload.balls if ball.wicket_fell), 10)
    wickets_remaining = max(10 - wickets, 0)

    total_balls = int(total_overs) * 6
    balls_remaining = max(total_balls - legal_balls, 0)
    overs_completed = legal_balls / 6
    current_run_rate = round(total_runs / overs_completed, 2) if overs_completed else 0

    runs_needed = max(target - total_runs, 0) if target else None
    required_run_rate = (
        round((runs_needed / balls_remaining) * 6, 2)
        if runs_needed and balls_remaining
        else 0 if target else None
    )
    match_state, chase_status, message = _state_text(
        innings_number=payload.innings.innings_number,
        total_runs=total_runs,
        target=target,
        balls_remaining=balls_remaining,
        wickets_remaining=wickets_remaining,
        runs_needed=runs_needed,
        batting_team=payload.innings.batting_team,
        bowling_team=payload.innings.bowling_team,
    )

    return MatchStateResponse(
        match=match_name,
        innings_number=payload.innings.innings_number,
        score=f"{total_runs}/{wickets}",
        overs=_overs_display(legal_balls),
        wickets=wickets,
        batting_team=payload.innings.batting_team,
        bowling_team=payload.innings.bowling_team,
        target=target,
        runs=total_runs,
        legal_balls=legal_balls,
        total_balls=total_balls,
        balls_remaining=balls_remaining,
        current_run_rate=current_run_rate,
        runs_needed=runs_needed,
        required_run_rate=required_run_rate,
        wickets_remaining=wickets_remaining,
        match_state=match_state,
        chase_status=chase_status,
        message=message,
    )


def _state_text(
    innings_number,
    total_runs,
    target,
    balls_remaining,
    wickets_remaining,
    runs_needed,
    batting_team,
    bowling_team,
):
    batting_label = batting_team or "Batting team"
    bowling_label = bowling_team or "Bowling team"

    if not target:
        if balls_remaining == 0 or wickets_remaining == 0:
            return (
                "Innings complete",
                "No chase target available",
                f"{batting_label} finished on {total_runs}.",
            )
        return (
            "First innings in progress" if innings_number == 1 else "Innings in progress",
            "No chase target available",
            f"{batting_label} are setting a total with {balls_remaining} balls remaining.",
        )

    if total_runs >= target:
        return (
            "Target reached",
            "Chase complete",
            f"{batting_label} reached the target with {balls_remaining} balls remaining.",
        )

    if balls_remaining == 0 or wickets_remaining == 0:
        first_innings_score = target - 1
        if total_runs == first_innings_score:
            result = "Match tied"
            message = f"{batting_label} finished level with the target score."
        else:
            result = "Defending team ahead"
            message = f"{bowling_label} defended the target; {batting_label} fell {runs_needed} runs short."
        return (result, "Chase ended", message)

    return (
        "Chase in progress",
        "Chase in progress",
        f"{batting_label} need {runs_needed} runs from {balls_remaining} balls.",
    )


def _overs_display(legal_balls):
    return f"{legal_balls // 6}.{legal_balls % 6}"


def _first_present(*values):
    for value in values:
        if value is not None:
            return value
    return None
