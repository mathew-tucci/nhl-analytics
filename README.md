# NHL Analytics

A Python package for making easy API requests to the public NHL API
([api-web.nhle.com](https://api-web.nhle.com/v1/)) for analytics work.

## Features

- **`NHLClient`** — session-based HTTP client with retries, backoff, and timeout handling
- **`client.endpoints`** — high-level helpers for standings, schedules, games, players, drafts, and awards
- **Raw access** — `client.get(path)` for any endpoint not wrapped
- Optional `NHL_API_KEY` env var support for authenticated endpoints

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Quick Start

```python
from nhl_analytics import NHLClient

with NHLClient() as client:
    # Today's scores
    scores = client.endpoints.get_score_today()

    # Standings
    teams = client.endpoints.get_teams()

    # Schedule for a date range
    schedule = client.endpoints.get_schedule("2025-10-01", "2025-10-31")

    # Game details
    game = client.endpoints.get_game_by_id(2025020001)

    # Raw endpoint access
    raw = client.get("/standings/now")
```

## Project Structure

```
nhl_analytics/
  __init__.py      # package exports
  client.py        # NHLClient — HTTP session, retries, auth
  endpoints.py     # Endpoints — high-level API methods
examples/
  basic_usage.py
  game_analysis.py
tests/
  test_client.py
```

## Tests

```powershell
pip install responses
pytest
```

## Notes

- The public NHL API requires no API key for most endpoints.
- Rate limits apply — the client retries on 429/5xx with exponential backoff.
- For historical data beyond what the public API exposes, consider the
  [NHL API docs](https://github.com/Zmalski/NHL-API-Reference) or paid data feeds.
