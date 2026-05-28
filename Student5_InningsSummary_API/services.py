from collections import defaultdict
from copy import deepcopy

from fastapi import HTTPException

from schemas import BatterSummary, BowlerSummary, InningsSummaryResponse, RecentBall


SAVED_BALL_EVENTS = {
    101: [
        {
            "over_number": 0,
            "ball_number": 1,
            "striker": "Aarav Shah",
            "bowler": "Rohan Mehta",
            "runs_off_bat": 4,
            "extras": 0,
            "is_legal_delivery": True,
            "wicket_fell": False,
            "wicket_type": "",
        },
        {
            "over_number": 0,
            "ball_number": 2,
            "striker": "Aarav Shah",
            "bowler": "Rohan Mehta",
            "runs_off_bat": 1,
            "extras": 0,
            "is_legal_delivery": True,
            "wicket_fell": False,
            "wicket_type": "",
        },
        {
            "over_number": 0,
            "ball_number": 3,
            "striker": "Vihaan Patel",
            "bowler": "Rohan Mehta",
            "runs_off_bat": 0,
            "extras": 1,
            "is_legal_delivery": False,
            "wicket_fell": False,
            "wicket_type": "wide",
        },
        {
            "over_number": 0,
            "ball_number": 3,
            "striker": "Vihaan Patel",
            "bowler": "Rohan Mehta",
            "runs_off_bat": 6,
            "extras": 0,
            "is_legal_delivery": True,
            "wicket_fell": False,
            "wicket_type": "",
        },
        {
            "over_number": 0,
            "ball_number": 4,
            "striker": "Vihaan Patel",
            "bowler": "Rohan Mehta",
            "runs_off_bat": 0,
            "extras": 0,
            "is_legal_delivery": True,
            "wicket_fell": True,
            "wicket_type": "caught",
        },
        {
            "over_number": 0,
            "ball_number": 5,
            "striker": "Kabir Rao",
            "bowler": "Rohan Mehta",
            "runs_off_bat": 2,
            "extras": 0,
            "is_legal_delivery": True,
            "wicket_fell": False,
            "wicket_type": "",
        },
        {
            "over_number": 0,
            "ball_number": 6,
            "striker": "Kabir Rao",
            "bowler": "Rohan Mehta",
            "runs_off_bat": 1,
            "extras": 0,
            "is_legal_delivery": True,
            "wicket_fell": False,
            "wicket_type": "",
        },
        {
            "over_number": 1,
            "ball_number": 1,
            "striker": "Kabir Rao",
            "bowler": "Dev Singh",
            "runs_off_bat": 4,
            "extras": 0,
            "is_legal_delivery": True,
            "wicket_fell": False,
            "wicket_type": "",
        },
    ],
    102: [],
}


def get_innings_summary(innings_id: int) -> InningsSummaryResponse:
    if innings_id <= 0:
        raise HTTPException(status_code=422, detail="innings_id must be a positive integer.")
    if innings_id not in SAVED_BALL_EVENTS:
        raise HTTPException(status_code=404, detail="No saved ball-event data found for this innings_id.")

    balls = deepcopy(SAVED_BALL_EVENTS[innings_id])
    return _build_summary(innings_id, balls)


def _build_summary(innings_id: int, balls: list[dict]) -> InningsSummaryResponse:
    total_runs = sum(_total_runs(ball) for ball in balls)
    wickets = min(sum(1 for ball in balls if ball.get("wicket_fell")), 10)
    legal_balls = sum(1 for ball in balls if ball.get("is_legal_delivery", True))
    run_rate = round((total_runs / legal_balls) * 6, 2) if legal_balls else 0

    batters = _batter_summaries(balls)
    bowlers = _bowler_summaries(balls)
    top_batter = max(batters, key=lambda batter: (batter.runs, batter.strike_rate), default=None)
    top_bowler = max(bowlers, key=lambda bowler: (bowler.wickets, -bowler.runs_conceded), default=None)

    return InningsSummaryResponse(
        innings_id=innings_id,
        total_runs=total_runs,
        wickets=wickets,
        legal_balls=legal_balls,
        overs=_overs_display(legal_balls),
        run_rate=run_rate,
        batters=batters,
        bowlers=bowlers,
        top_batter=top_batter,
        top_bowler=top_bowler,
        recent_balls=_recent_balls(balls),
        message=_message(innings_id, balls),
    )


def _batter_summaries(balls: list[dict]) -> list[BatterSummary]:
    stats = defaultdict(lambda: {"runs": 0, "balls": 0, "fours": 0, "sixes": 0})

    for ball in balls:
        striker = ball.get("striker") or "Unknown batter"
        runs = int(ball.get("runs_off_bat") or 0)
        stats[striker]["runs"] += runs
        if ball.get("is_legal_delivery", True):
            stats[striker]["balls"] += 1
        if runs == 4:
            stats[striker]["fours"] += 1
        if runs == 6:
            stats[striker]["sixes"] += 1

    return [
        BatterSummary(
            name=name,
            runs=data["runs"],
            balls=data["balls"],
            fours=data["fours"],
            sixes=data["sixes"],
            strike_rate=round((data["runs"] / data["balls"]) * 100, 2) if data["balls"] else 0,
        )
        for name, data in sorted(stats.items())
    ]


def _bowler_summaries(balls: list[dict]) -> list[BowlerSummary]:
    stats = defaultdict(lambda: {"balls": 0, "runs_conceded": 0, "wickets": 0})

    for ball in balls:
        bowler = ball.get("bowler") or "Unknown bowler"
        stats[bowler]["runs_conceded"] += _total_runs(ball)
        if ball.get("is_legal_delivery", True):
            stats[bowler]["balls"] += 1
        if ball.get("wicket_fell") and ball.get("wicket_type") != "run_out":
            stats[bowler]["wickets"] += 1

    return [
        BowlerSummary(
            name=name,
            balls=data["balls"],
            overs=_overs_display(data["balls"]),
            runs_conceded=data["runs_conceded"],
            wickets=data["wickets"],
            economy=round((data["runs_conceded"] / data["balls"]) * 6, 2) if data["balls"] else 0,
        )
        for name, data in sorted(stats.items())
    ]


def _recent_balls(balls: list[dict], limit: int = 6) -> list[RecentBall]:
    recent = sorted(balls, key=lambda ball: (ball.get("over_number", 0), ball.get("ball_number", 0)))[-limit:]
    return [
        RecentBall(
            over=f"{ball.get('over_number', 0)}.{ball.get('ball_number', 0)}",
            striker=ball.get("striker") or "Unknown batter",
            bowler=ball.get("bowler") or "Unknown bowler",
            runs=_total_runs(ball),
            wicket=bool(ball.get("wicket_fell")),
            description=_ball_description(ball),
        )
        for ball in recent
    ]


def _ball_description(ball: dict) -> str:
    runs = _total_runs(ball)
    if ball.get("wicket_fell"):
        return f"{runs} run, wicket ({ball.get('wicket_type') or 'unknown'})"
    if not ball.get("is_legal_delivery", True):
        return f"{runs} run extra"
    return f"{runs} run" if runs == 1 else f"{runs} runs"


def _message(innings_id: int, balls: list[dict]) -> str:
    if not balls:
        return f"Innings {innings_id} exists, but no ball events are saved yet."
    return f"Innings {innings_id} summary calculated from {len(balls)} saved ball events."


def _total_runs(ball: dict) -> int:
    return int(ball.get("runs_off_bat") or 0) + int(ball.get("extras") or 0)


def _overs_display(legal_balls: int) -> str:
    return f"{legal_balls // 6}.{legal_balls % 6}"
