from schemas import RequiredRunRateRequest, RequiredRunRateResponse


def calculate_required_run_rate(payload: RequiredRunRateRequest) -> RequiredRunRateResponse:
    target = _first_present(payload.innings.target, payload.match.target)
    total_overs = _first_present(payload.innings.total_overs_limit, payload.match.total_overs, 20)

    total_runs = sum(ball.runs_off_bat + ball.extras for ball in payload.balls)
    legal_balls = sum(1 for ball in payload.balls if ball.is_legal_delivery)
    wickets = min(sum(1 for ball in payload.balls if ball.wicket_fell), 10)

    total_balls = int(total_overs) * 6
    balls_remaining = max(total_balls - legal_balls, 0)
    current_score = f"{total_runs}/{wickets}"

    if target is None:
        return RequiredRunRateResponse(
            target=None,
            current_score=current_score,
            runs_needed=0,
            balls_remaining=balls_remaining,
            required_run_rate=0,
            equation="Required run rate cannot be calculated without a chase target.",
            message="No target was provided, so this is treated as a non-chase situation.",
        )

    runs_needed = max(target - total_runs, 0)
    required_run_rate = _required_run_rate(runs_needed, balls_remaining)
    equation = _equation_text(runs_needed, balls_remaining, required_run_rate)

    if runs_needed == 0:
        message = "Target has already been reached."
    elif balls_remaining == 0:
        message = "No balls are remaining, so the chase requirement cannot improve."
    else:
        message = (
            f"Chasing side needs {runs_needed} runs from {balls_remaining} balls "
            f"at {required_run_rate} runs per over."
        )

    return RequiredRunRateResponse(
        target=target,
        current_score=current_score,
        runs_needed=runs_needed,
        balls_remaining=balls_remaining,
        required_run_rate=required_run_rate,
        equation=equation,
        message=message,
    )


def _required_run_rate(runs_needed: int, balls_remaining: int) -> float:
    if runs_needed == 0 or balls_remaining == 0:
        return 0
    return round((runs_needed / balls_remaining) * 6, 2)


def _equation_text(runs_needed: int, balls_remaining: int, required_run_rate: float) -> str:
    if runs_needed == 0:
        return "Required run rate = 0 because the target has already been reached."
    if balls_remaining == 0:
        return "Required run rate = 0 because there are no balls remaining."
    return f"Required run rate = ({runs_needed} runs needed / {balls_remaining} balls remaining) x 6 = {required_run_rate}"


def _first_present(*values):
    for value in values:
        if value is not None:
            return value
    return None
