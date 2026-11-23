"""Endpoint wrappers for the public NHL APIs."""

from __future__ import annotations

from typing import Any, Optional

from .client import NHLClient


class WebEndpoints:
    """High-level methods for the NHL Web API (api-web.nhle.com).

    All methods return parsed JSON (dict or list). For raw access to any
    endpoint, use ``client.get(path)`` directly.
    """

    def __init__(self, client: NHLClient):
        self.client = client

    # ---- Standings / Teams -------------------------------------------

    def get_teams(self) -> list[dict]:
        """Return all NHL teams."""
        data = self.client.get("/standings/now")
        return data.get("standings", [])

    def get_team_by_id(self, team_id: int) -> dict:
        """Return a single team by its NHL team ID."""
        return self.client.get(f"/standings/now/{team_id}")

    def get_team_schedule(
        self, team_abbr: str, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> dict:
        """Return schedule for a team abbreviation (e.g. 'TOR', 'BOS')."""
        params = {}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self.client.get(f"/club-schedule-season/{team_abbr}/now", params=params)

    # ---- Schedule ----------------------------------------------------

    def get_schedule(
        self, start_date: str, end_date: str
    ) -> dict:
        """Return the league-wide schedule for a date range (YYYY-MM-DD)."""
        return self.client.get(
            "/schedule",
            params={"startDate": start_date, "endDate": end_date},
        )

    def get_score_today(self) -> dict:
        """Return today's scores."""
        return self.client.get("/score/now")

    # ---- Games -------------------------------------------------------

    def get_game_by_id(self, game_id: int) -> dict:
        """Return details for a single game by ID."""
        return self.client.get(f"/gamecenter/{game_id}/landing")

    def get_game_boxscore(self, game_id: int) -> dict:
        """Return the boxscore for a game."""
        return self.client.get(f"/gamecenter/{game_id}/boxscore")

    def get_game_play_by_play(self, game_id: int) -> dict:
        """Return play-by-play for a game."""
        return self.client.get(f"/gamecenter/{game_id}/play-by-play")

    # ---- Players -----------------------------------------------------

    def get_player_by_id(self, player_id: int) -> dict:
        """Return a player's landing page data."""
        return self.client.get(f"/player/{player_id}/landing")

    def search_players(self, query: str) -> dict:
        """Search players by name."""
        return self.client.get("/player", params={"q": query})

    # ---- Draft -------------------------------------------------------

    def get_draft_year(self, year: int) -> dict:
        """Return draft results for a given year."""
        return self.client.get(f"/draft/{year}")

    # ---- Awards ------------------------------------------------------

    def get_awards(self) -> dict:
        """Return current NHL awards."""
        return self.client.get("/awards")


class EdgeEndpoints:
    """High-level methods for the NHL Edge stats API (api.nhle.com).

    Uses the ``cayenneExp`` query parameter for filtering, e.g.
    ``seasonId=20252026``, ``gameTypeId=2`` (regular season).
    """

    def __init__(self, client: NHLClient):
        self.client = client

    # ---- Teams -------------------------------------------------------

    def get_teams(self) -> dict:
        """Return all teams (including historical franchises)."""
        return self.client.get("/team")

    def get_team_by_id(self, team_id: int) -> dict:
        """Return a single team by ID."""
        return self.client.get(f"/team/{team_id}")

    # ---- Skaters -----------------------------------------------------

    def get_skater_summary(
        self,
        season_id: str,
        game_type: Optional[int] = None,
        limit: int = 100,
        start: int = 0,
    ) -> dict:
        """Return skater season summary stats.

        Args:
            season_id: e.g. "20252026"
            game_type: 2 = regular season, 3 = playoffs (optional)
            limit/start: pagination
        """
        exp = f"seasonId={season_id}"
        if game_type is not None:
            exp += f" and gameTypeId={game_type}"
        return self.client.get(
            "/skater/summary",
            params={"cayenneExp": exp, "limit": limit, "start": start},
        )

    def get_skater_leaders(
        self, season_id: str, sort_field: str = "points", limit: int = 10
    ) -> dict:
        """Return top skaters sorted by a stat field (e.g. 'points', 'goals')."""
        return self.client.get(
            "/skater/summary",
            params={
                "cayenneExp": f"seasonId={season_id}",
                "sort": sort_field,
                "dir": "DESC",
                "limit": limit,
            },
        )

    def get_seasons(self) -> dict:
        """Return all NHL seasons."""
        return self.client.get("/season")

    def get_config(self) -> dict:
        """Return stats API configuration (available reports/columns)."""
        return self.client.get("/config")

    # ---- Goalies -----------------------------------------------------

    def get_goalie_summary(
        self,
        season_id: str,
        game_type: Optional[int] = None,
        limit: int = 100,
        start: int = 0,
    ) -> dict:
        """Return goalie season summary stats."""
        exp = f"seasonId={season_id}"
        if game_type is not None:
            exp += f" and gameTypeId={game_type}"
        return self.client.get(
            "/goalie/summary",
            params={"cayenneExp": exp, "limit": limit, "start": start},
        )
