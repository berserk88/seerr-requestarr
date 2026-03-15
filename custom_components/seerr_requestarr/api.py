"""Overseerr API client for Seerr Requestarr."""
from __future__ import annotations
from typing import Any
import aiohttp

class OverseerrAPI:
    def __init__(self, url: str, api_key: str, session: aiohttp.ClientSession) -> None:
        self._url     = url.rstrip("/")
        self._session = session
        # GET: no Content-Type (Overseerr rejects it on GETs)
        self.get_headers  = {"X-Api-Key": api_key}
        self.post_headers = {"X-Api-Key": api_key, "Content-Type": "application/json", "Accept": "application/json"}

    async def _get(self, endpoint: str, params: dict | None = None) -> Any:
        async with self._session.get(
            f"{self._url}/api/v1{endpoint}", headers=self.get_headers, params=params
        ) as r:
            r.raise_for_status()
            return await r.json()

    async def _post(self, endpoint: str, data: dict) -> Any:
        async with self._session.post(
            f"{self._url}/api/v1{endpoint}", headers=self.post_headers, json=data
        ) as r:
            r.raise_for_status()
            return await r.json()

    async def get_status(self) -> dict:
        return await self._get("/status")

    async def get_requests(self, take: int = 20, skip: int = 0, filter_: str = "all") -> dict:
        return await self._get("/request", params={"take": take, "skip": skip, "filter": filter_})

    async def request_media(self, media_type: str, media_id: int) -> dict:
        payload: dict[str, Any] = {"mediaType": media_type, "mediaId": media_id}
        if media_type == "tv":
            payload["seasons"] = "all"
        return await self._post("/request", payload)

    async def search(self, query: str, page: int = 1) -> dict:
        return await self._get("/search", params={"query": query, "page": page})
