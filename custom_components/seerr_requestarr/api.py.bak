"""Overseerr API client for Seerr Requestarr."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class OverseerrAPI:
    """Overseerr API client."""

    def __init__(self, url: str, api_key: str, session: aiohttp.ClientSession) -> None:
        self._url = url.rstrip("/")
        self._api_key = api_key
        self._session = session
        # GET requests: only the API key — NO Content-Type (causes HTTP 400 on Overseerr)
        self.get_headers = {"X-Api-Key": api_key}
        # POST/PUT requests: API key + JSON content type
        self.post_headers = {
            "X-Api-Key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _get(self, endpoint: str, params: dict | None = None) -> Any:
        url = f"{self._url}/api/v1{endpoint}"
        _LOGGER.debug("Seerr GET %s params=%s", url, params)
        async with self._session.get(url, headers=self.get_headers, params=params) as r:
            _LOGGER.debug("Seerr GET %s -> %s", url, r.status)
            r.raise_for_status()
            return await r.json()

    async def _post(self, endpoint: str, data: dict) -> Any:
        url = f"{self._url}/api/v1{endpoint}"
        async with self._session.post(url, headers=self.post_headers, json=data) as r:
            r.raise_for_status()
            return await r.json()

    async def get_status(self) -> dict:
        return await self._get("/status")

    async def search(self, query: str, page: int = 1) -> dict:
        return await self._get("/search", params={"query": query, "page": page})

    async def get_trending(self) -> dict:
        return await self._get("/discover/trending")

    async def get_trending_movies(self) -> dict:
        return await self._get("/discover/movies")

    async def get_trending_tv(self) -> dict:
        return await self._get("/discover/tv")

    async def get_movie(self, tmdb_id: int) -> dict:
        return await self._get(f"/movie/{tmdb_id}")

    async def get_tv(self, tmdb_id: int) -> dict:
        return await self._get(f"/tv/{tmdb_id}")

    async def get_requests(self, take: int = 20, skip: int = 0, filter_: str = "all") -> dict:
        return await self._get("/request", params={"take": take, "skip": skip, "filter": filter_})

    async def request_media(self, media_type: str, media_id: int) -> dict:
        payload: dict[str, Any] = {"mediaType": media_type, "mediaId": media_id}
        if media_type == "tv":
            payload["seasons"] = "all"
        return await self._post("/request", payload)
