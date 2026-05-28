import os
import sqlite3
from collections import defaultdict
from pathlib import Path

from fastapi import HTTPException

from schemas import LiveScoreboardResponse, Performer, RecentBall


LOCAL_DB_PATH = Path(__file__).with_name("db.sqlite3")
WORKSPACE_DB_PATH = Path(__file__).resolve().parents[1] / "livestream_ksjd-main" / "db.sqlite3"


def get_live_scoreboard(match_id: str) -> LiveScoreboardResponse:
    clean_match_id = (match_id or "").strip()
    if not clean_match_id:
        raise HTTPException(status_code=422, detail="match_id is required.")

    with _connect() as conn:
        match = _fetch_match(conn, clean_match_id)
        if match is None:
            raise HTTPException(status_code=404, detail="No saved match found for this match_id.")

        innings = _fetch_active_or_latest_innings(conn, match["id"])
        if innings is None:
            return LiveScoreboardResponse(
                match=match["title"],
                venue=match["venue"] or "",
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

        balls = _fetch_ball_events(conn, innings["id"])

    total_runs = sum(_total_runs(ball) for ball in balls)
    wickets = min(sum(1 for ball in balls if ball["wicket_fell"]), 10)
    legal_balls = sum(1 for ball in balls if ball["is_legal_delivery"])
    run_rate = round((total_runs / legal_balls) * 6, 2) if legal_balls else 0

    return LiveScoreboardResponse(
        match=match["title"],
        venue=match["venue"] or "",
        innings_number=innings["innings_number"],
        batting_team=innings["batting_team"],
        bowling_team=innings["bowling_team"],
        score=f"{total_runs}/{wickets}",
        overs=_overs_display(legal_balls),
        run_rate=run_rate,
        top_batter=_top_batter(balls),
        top_bowler=_top_bowler(balls),
        recent_balls=_recent_balls(balls),
        message=f"Live scoreboard returned from database innings {innings['id']}.",
    )


def _connect() -> sqlite3.Connection:
    db_path = Path(os.getenv("KHEL_DB_PATH", LOCAL_DB_PATH if LOCAL_DB_PATH.exists() else WORKSPACE_DB_PATH))
    if not db_path.exists():
        raise HTTPException(status_code=500, detail=f"Database file not found: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _fetch_match(conn: sqlite3.Connection, match_id: str) -> sqlite3.Row | None:
    if match_id.isdigit():
        return conn.execute(
            "select id, title, venue from matches_match where id = ?",
            (int(match_id),),
        ).fetchone()

    return conn.execute(
        "select id, title, venue from matches_match where lower(title) = lower(?)",
        (match_id,),
    ).fetchone()


def _fetch_active_or_latest_innings(conn: sqlite3.Connection, match_pk: int) -> sqlite3.Row | None:
    return conn.execute(
        """
        select
            innings.id,
            innings.innings_number,
            batting_team.name as batting_team,
            bowling_team.name as bowling_team
        from matches_innings innings
        join matches_team batting_team on batting_team.id = innings.batting_team_id
        join matches_team bowling_team on bowling_team.id = innings.bowling_team_id
        where innings.match_id = ?
        order by innings.is_complete asc, innings.innings_number desc, innings.id desc
        limit 1
        """,
        (match_pk,),
    ).fetchone()


def _fetch_ball_events(conn: sqlite3.Connection, innings_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        """
        select
            ball.id,
            ball.over_number,
            ball.ball_number,
            ball.runs_off_bat,
            ball.extras,
            ball.is_legal_delivery,
            ball.wicket_fell,
            ball.wicket_type,
            striker.name as striker,
            bowler.name as bowler
        from matches_ballevent ball
        join matches_player striker on striker.id = ball.striker_id
        join matches_player bowler on bowler.id = ball.bowler_id
        where ball.innings_id = ?
        order by ball.over_number, ball.ball_number, ball.id
        """,
        (innings_id,),
    ).fetchall()


def _top_batter(balls: list[sqlite3.Row]) -> Performer | None:
    stats = defaultdict(lambda: {"runs": 0, "balls": 0})
    for ball in balls:
        stats[ball["striker"]]["runs"] += int(ball["runs_off_bat"] or 0)
        if ball["is_legal_delivery"]:
            stats[ball["striker"]]["balls"] += 1

    if not stats:
        return None

    name, data = max(stats.items(), key=lambda item: (item[1]["runs"], item[1]["balls"]))
    return Performer(name=name, runs=data["runs"], balls=data["balls"])


def _top_bowler(balls: list[sqlite3.Row]) -> Performer | None:
    stats = defaultdict(lambda: {"balls": 0, "runs_conceded": 0, "wickets": 0})
    for ball in balls:
        stats[ball["bowler"]]["runs_conceded"] += _total_runs(ball)
        if ball["is_legal_delivery"]:
            stats[ball["bowler"]]["balls"] += 1
        if ball["wicket_fell"] and ball["wicket_type"] != "run_out":
            stats[ball["bowler"]]["wickets"] += 1

    if not stats:
        return None

    name, data = max(stats.items(), key=lambda item: (item[1]["wickets"], -item[1]["runs_conceded"]))
    return Performer(
        name=name,
        wickets=data["wickets"],
        runs_conceded=data["runs_conceded"],
        overs=_overs_display(data["balls"]),
    )


def _recent_balls(balls: list[sqlite3.Row], limit: int = 6) -> list[RecentBall]:
    return [
        RecentBall(
            over=f"{ball['over_number']}.{ball['ball_number']}",
            striker=ball["striker"],
            bowler=ball["bowler"],
            runs=_total_runs(ball),
            wicket=bool(ball["wicket_fell"]),
            description=_ball_description(ball),
        )
        for ball in balls[-limit:]
    ]


def _ball_description(ball: sqlite3.Row) -> str:
    runs = _total_runs(ball)
    if ball["wicket_fell"]:
        return f"{runs} run, wicket ({ball['wicket_type'] or 'unknown'})"
    if not ball["is_legal_delivery"]:
        return f"{runs} run extra"
    return f"{runs} run" if runs == 1 else f"{runs} runs"


def _total_runs(ball: sqlite3.Row) -> int:
    return int(ball["runs_off_bat"] or 0) + int(ball["extras"] or 0)


def _overs_display(legal_balls: int) -> str:
    return f"{legal_balls // 6}.{legal_balls % 6}"
