"""Tests for NHLClient using mocked responses."""

import pytest
import responses

from nhl_analytics import NHLClient

BASE = "https://api-web.nhle.com/v1"


@pytest.fixture
def client():
    return NHLClient(max_retries=1, backoff_factor=0)


@responses.activate
def test_get_teams(client):
    responses.add(
        responses.GET,
        f"{BASE}/standings/now",
        json={"standings": [{"teamAbbrev": {"default": "TOR"}}]},
        status=200,
    )
    teams = client.endpoints.get_teams()
    assert len(teams) == 1
    assert teams[0]["teamAbbrev"]["default"] == "TOR"


@responses.activate
def test_get_schedule_params(client):
    responses.add(
        responses.GET,
        f"{BASE}/schedule",
        json={"gameWeek": []},
        status=200,
    )
    client.endpoints.get_schedule("2025-10-01", "2025-10-31")
    req = responses.calls[0].request
    assert "startDate=2025-10-01" in req.url
    assert "endDate=2025-10-31" in req.url


@responses.activate
def test_api_error_raises(client):
    responses.add(responses.GET, f"{BASE}/gamecenter/999/landing", json={}, status=404)
    with pytest.raises(Exception):
        client.endpoints.get_game_by_id(999)
