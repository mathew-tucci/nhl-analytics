"""NHL Edge player-tracking endpoints (served by the Web API host).

Routes live under ``/v1/edge/...`` on api-web.nhle.com. ``season`` accepts an
8-digit season (e.g. "20252026") or "now"; ``game_type`` is 1=preseason,
2=regular season, 3=playoffs. Tracking data exists from 2024-25 onward.
"""

from __future__ import annotations

from typing import Optional, Union

from .client import NHLClient


class EdgeTrackingEndpoints:
    """High-level methods for NHL Edge puck/player-tracking data.

    Usage:
        client = NHLClient(api="web")
        client.edge.skater_detail(8478402, "20252026")
    """

    def __init__(self, client: NHLClient):
        self.client = client

    # ---- Helpers -----------------------------------------------------

    @staticmethod
    def _path(view: str, player_id: int, season, game_type: int = 2) -> str:
        if season == "now":
            return f"/edge/{view}/{player_id}/now"
        return f"/edge/{view}/{player_id}/{season}/{game_type}"

    # ---- Skater endpoints --------------------------------------------

    def skater_detail(
        self, player_id: int, season: Union[str, int] = "now", game_type: int = 2
    ) -> dict:
        """Base detail: player bio + percentile stats vs league average."""
        return self.client.get(self._path("skater-detail", player_id, season, game_type))

    def skater_comparison(
        self, player_id: int, season: Union[str, int] = "now", game_type: int = 2
    ) -> dict:
        """Comparison bundle: shot speed, skating speed/distance, zone time,
        shot locations vs league averages."""
        return self.client.get(self._path("skater-comparison", player_id, season, game_type))

    def skater_shot_speed_detail(
        self, player_id: int, season: Union[str, int] = "now", game_type: int = 2
    ) -> dict:
        """Shot speed analytics: max/avg speed + attempt buckets."""
        return self.client.get(
            self._path("skater-shot-speed-detail", player_id, season, game_type)
        )

    def skater_skating_speed_detail(
        self, player_id: int, season: Union[str, int] = "now", game_type: int = 2
    ) -> dict:
        """Skating speed metrics: max speed + burst counts."""
        return self.client.get(
            self._path("skater-skating-speed-detail", player_id, season, game_type)
        )

    def skater_shot_location_detail(
        self, player_id: int, season: Union[str, int] = "now", game_type: int = 2
    ) -> dict:
        """Shot location patterns: SOG/goals/pctg by ice area."""
        return self.client.get(
            self._path("skater-shot-location-detail", player_id, season, game_type)
        )

    def skater_skating_distance_detail(
        self, player_id: int, season: Union[str, int] = "now", game_type: int = 2
    ) -> dict:
        """Distance traveled per game and per situation."""
        return self.client.get(
            self._path("skater-skating-distance-detail", player_id, season, game_type)
        )

    def skater_zone_time(
        self, player_id: int, season: Union[str, int] = "now", game_type: int = 2
    ) -> dict:
        """Time spent in offensive/neutral/defensive zones by strength."""
        return self.client.get(self._path("skater-zone-time", player_id, season, game_type))

    # ---- Goalie endpoints --------------------------------------------

    def goalie_detail(
        self, goalie_id: int, season: Union[str, int] = "now", game_type: int = 2
    ) -> dict:
        return self.client.get(self._path("goalie-detail", goalie_id, season, game_type))

    def goalie_comparison(
        self, goalie_id: int, season: Union[str, int] = "now", game_type: int = 2
    ) -> dict:
        return self.client.get(self._path("goalie-comparison", goalie_id, season, game_type))

    def goalie_shot_location_detail(
        self, goalie_id: int, season: Union[str, int] = "now", game_type: int = 2
    ) -> dict:
        """Save % by danger zone (all/highDanger/midRange/longRange)."""
        return self.client.get(
            self._path("goalie-shot-location-detail", goalie_id, season, game_type)
        )

    # ---- Team endpoints ----------------------------------------------

    def team_detail(
        self, team_id: int, season: Union[str, int] = "now", game_type: int = 2
    ) -> dict:
        return self.client.get(self._path("team-detail", team_id, season, game_type))

    def team_comparison(
        self, team_id: int, season: Union[str, int] = "now", game_type: int = 2
    ) -> dict:
        return self.client.get(self._path("team-comparison", team_id, season, game_type))

    def team_zone_time_details(
        self, team_id: int, season: Union[str, int] = "now", game_type: int = 2
    ) -> dict:
        """Zone % + rank + league avg by strength, plus shot differential."""
        return self.client.get(
            self._path("team-zone-time-details", team_id, season, game_type)
        )
