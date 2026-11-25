"""Core HTTP client for the public NHL APIs.

Supports two APIs:
  - "web"  -> https://api-web.nhle.com/v1  (powers nhl.com)
  - "edge" -> https://api.nhle.com/stats/rest/en  (NHL Edge stats API)
"""

from __future__ import annotations

import os
import time
from typing import Any, Literal, Optional

import requests

# the sprite URL might be best w/o a base URL
API_BASE_URLS = {
    "web": "https://api-web.nhle.com/v1",
    "edge": "https://api.nhle.com/stats/rest/en",
    "sprites": "https://wsr.nhle.com/sprites/"
}

class NHLAPIError(Exception):
    """Raised when the NHL API returns an error response."""

    def __init__(self, status_code: int, message: str, url: str):
        self.status_code = status_code
        self.message = message
        self.url = url
        super().__init__(f"NHL API error {status_code} for {url}: {message}")


class NHLClient:
    """Thin wrapper around the public NHL APIs.

    Usage:
        web = NHLClient(api="web")    # api-web.nhle.com
        edge = NHLClient(api="edge")  # api.nhle.com stats API

        teams = web.endpoints.get_teams()
        skaters = edge.endpoints.get_skater_summary("20252026")
    """

    def __init__(
        self,
        api: Literal["web", "edge", "sprites"] = "web",
        base_url: Optional[str] = None,
        timeout: float = 15.0,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        api_key: Optional[str] = None,
    ):
        if api not in API_BASE_URLS:
            raise ValueError(f"Unknown API '{api}'. Choose from: {list(API_BASE_URLS)}")
        self.api = api
        self.base_url = (base_url or API_BASE_URLS[api]).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "nhl-analytics/0.1 (github.com/tucci)",
            "Accept": "application/json",
        })

        key = api_key or os.getenv("NHL_API_KEY")
        if key:
            self.session.headers["Authorization"] = f"Bearer {key}"

        # Lazy imports to avoid circular dependency
        from .edge import EdgeTrackingEndpoints
        from .endpoints import EdgeEndpoints, WebEndpoints

        if api == "edge":
            self.endpoints = EdgeEndpoints(self)
            self.stats = self.endpoints
            self.edge = None  # tracking endpoints are served by the web host
        else:
            self.endpoints = WebEndpoints(self)
            self.web = self.endpoints
            # NHL Edge tracking routes live under /v1/edge on the web host
            self.edge = EdgeTrackingEndpoints(self)

    # ------------------------------------------------------------------
    # Low-level request helpers
    # ------------------------------------------------------------------

    def _request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        last_exc: Optional[Exception] = None

        for attempt in range(self.max_retries):
            try:
                resp = self.session.request(
                    method, url, timeout=self.timeout, **kwargs
                )
            except requests.RequestException as exc:
                last_exc = exc
                self._sleep(attempt)
                continue

            if resp.status_code == 429 or resp.status_code >= 500:
                last_exc = NHLAPIError(resp.status_code, resp.text[:200], url)
                self._sleep(attempt)
                continue

            if resp.status_code >= 400:
                raise NHLAPIError(resp.status_code, resp.text[:200], url)

            if not resp.content:
                return None
            return resp.json()

        raise NHLAPIError(
            getattr(last_exc, "status_code", 0),
            f"Max retries exceeded. Last error: {last_exc}",
            url,
        )

    def get(self, path: str, params: Optional[dict] = None) -> Any:
        return self._request("GET", path, params=params)

    def _sleep(self, attempt: int) -> None:
        time.sleep(self.backoff_factor * (2 ** attempt))

    # ------------------------------------------------------------------
    # Convenience context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> "NHLClient":
        return self

    def __exit__(self, *exc_info) -> None:
        self.session.close()
