from collections import defaultdict
from copy import deepcopy

from fastapi import HTTPException

from schemas import LiveScoreboardResponse, Performer, RecentBall


def _ball(over_number, ball_number, striker, bowler, runs_off_bat, extras, legal, wicket, wicket_type=""):
    return {
        "over_number": over_number,
        "ball_number": ball_number,
        "striker": striker,
        "bowler": bowler,
        "runs_off_bat": runs_off_bat,
        "extras": extras,
        "is_legal_delivery": legal,
        "wicket_fell": wicket,
        "wicket_type": wicket_type,
    }


SAVED_MATCHES = {
    "match-001": {
        "title": "Alpha vs Bravo",
        "venue": "Khel AI Arena",
        "innings": [
            {
                "innings_number": 1,
                "batting_team": "Alpha",
                "bowling_team": "Bravo",
                "is_active": False,
                "balls": [
                    _ball(0, 1, "Aarav Shah", "Rohan Mehta", 4, 0, True, False),
                    _ball(0, 2, "Aarav Shah", "Rohan Mehta", 1, 0, True, False),
                    _ball(0, 3, "Vihaan Patel", "Rohan Mehta", 6, 0, True, False),
                    _ball(0, 4, "Vihaan Patel", "Rohan Mehta", 0, 0, True, True, "caught"),
                    _ball(0, 5, "Kabir Rao", "Rohan Mehta", 2, 0, True, False),
                    _ball(0, 6, "Kabir Rao", "Rohan Mehta", 1, 0, True, False),
                ],
            },
            {
                "innings_number": 2,
                "batting_team": "Bravo",
                "bowling_team": "Alpha",
                "is_active": True,
                "balls": [
                    _ball(0, 1, "Dev Singh", "Kabir Rao", 4, 0, True, False),
                    _ball(0, 2, "Dev Singh", "Kabir Rao", 0, 1, False, False, "wide"),
                    _ball(0, 2, "Dev Singh", "Kabir Rao", 1, 0, True, False),
                    _ball(0, 3, "Rohan Mehta", "Kabir Rao", 0, 0, True, False),
                    _ball(0, 4, "Rohan Mehta", "Kabir Rao", 6, 0, True, False),
                    _ball(0, 5, "Rohan Mehta", "Kabir Rao", 0, 0, True, True, "bowled"),
                    _ball(0, 6, "Nikhil Jain", "Kabir Rao", 2, 0, True, False),
                    _ball(1, 1, "Nikhil Jain", "Aarav Shah", 1, 0, True, False),
                ],
            },
        ],
    },
    "match-empty": {
        "title": "Empty Match",
        "venue": "Practice Ground",
        "innings": [],
    },
}


def get_live_scoreboard(match_id: str) -> LiveScoreboardResponse:
    clean_match_id = (match_id or "").strip()
    if not clean_match_id:
        raise HTTPException(status_code=422, detail="match_id is required.")
    if clean_match_id not in SAVED_MATCHES:
        raise HTTPException(status_code=404, detail="No saved match found for this match_id.")

    match = deepcopy(SAVED_MATCHES[clean_match_id])
    innings = _active_or_latest_innings(match.get("innings", []))
    if innings is None:
        return LiveScoreboardResponse(
            match=match.get("title", clean_match_id),
            venue=match.get("venue", ""),
            innings_number=None,
            batting_team=None,
            bowling_team=None,
            score="0/0",
            overs="0.0",
            run_rate=0,
            top_batter=None,
            top_bowler=None,
            recent_balls=[],
            message="Match exists, but no innings data is saved yet.",
        )

    balls = innings.get("balls", [])
    total_runs = sum(_total_runs(ball) for ball in balls)
    wickets = min(sum(1 for ball in balls if ball.get("wicket_fell")), 10)
    legal_balls = sum(1 for ball in balls if ball.get("is_legal_delivery", True))
    run_rate = round((total_runs / legal_balls) * 6, 2) if legal_balls else 0

    return LiveScoreboardResponse(
        match=match.get("title", clean_match_id),
        venue=match.get("venue", ""),
        innings_number=innings.get("innings_number"),
        batting_team=innings.get("batting_team"),
        bowling_team=innings.get("bowling_team"),
        score=f"{total_runs}/{wickets}",
        overs=_overs_display(legal_balls),
        run_rate=run_rate,
        top_batter=_top_batter(balls),
        top_bowler=_top_bowler(balls),
        recent_balls=_recent_balls(balls),
        message=f"Live scoreboard returned for innings {innings.get('innings_number')}.",
    )


def _active_or_latest_innings(innings_list: list[dict]) -> dict | None:
    active = [innings for innings in innings_list if innings.get("is_active")]
    if active:
        return max(active, key=lambda innings: innings.get("innings_number", 0))
    if not innings_list:
        return None
    return max(innings_list, key=lambda innings: innings.get("innings_number", 0))


def _top_batter(balls: list[dict]) -> Performer | None:
    stats = defaultdict(lambda: {"runs": 0, "balls": 0})
    for ball in balls:
        striker = ball.get("striker") or "Unknown batter"
        stats[striker]["runs"] += int(ball.get("runs_off_bat") or 0)
        if ball.get("is_legal_delivery", True):
            stats[striker]["balls"] += 1
    if not stats:
        return None
    name, data = max(stats.items(), key=lambda item: (item[1]["runs"], item[1]["balls"]))
    return Performer(name=name, runs=data["runs"], balls=data["balls"])


def _top_bowler(balls: list[dict]) -> Performer | None:
    stats = defaultdict(lambda: {"balls": 0, "runs_conceded": 0, "wickets": 0})
    for ball in balls:
        bowler = ball.get("bowler") or "Unknown bowler"
        stats[bowler]["runs_conceded"] += _total_runs(ball)
        if ball.get("is_legal_delivery", True):
            stats[bowler]["balls"] += 1
        if ball.get("wicket_fell") and ball.get("wicket_type") != "run_out":
            stats[bowler]["wickets"] += 1
    if not stats:
        return None
    name, data = max(stats.items(), key=lambda item: (item[1]["wickets"], -item[1]["runs_conceded"]))
    return Performer(
        name=name,
        wickets=data["wickets"],
        runs_conceded=data["runs_conceded"],
        overs=_overs_display(data["balls"]),
    )


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


def _total_runs(ball: dict) -> int:
    return int(ball.get("runs_off_bat") or 0) + int(ball.get("extras") or 0)


def _overs_display(legal_balls: int) -> str:
    return f"{legal_balls // 6}.{legal_balls % 6}"
