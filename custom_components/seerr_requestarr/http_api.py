"""HTTP proxy views for Seerr Requestarr — forwards card requests to Overseerr server-side."""
from __future__ import annotations

import json
import logging
from urllib.parse import urlencode, quote
from typing import Any

from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def async_register_views(hass: HomeAssistant) -> None:
    hass.http.register_view(SeerrProxyView)
    hass.http.register_view(SeerrDebugView)


class SeerrProxyView(HomeAssistantView):
    """Proxies card API calls to Overseerr, avoiding CORS entirely."""

    url = "/api/seerr_proxy/{path:.*}"
    name = "api:seerr_proxy"
    requires_auth = True

    async def get(self, request: web.Request, path: str) -> web.Response:
        return await self._proxy(request, path, "GET")

    async def post(self, request: web.Request, path: str) -> web.Response:
        return await self._proxy(request, path, "POST")

    async def _proxy(self, request: web.Request, path: str, method: str) -> web.Response:
        hass: HomeAssistant = request.app["hass"]

        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            return self._json_error(503, "Seerr Requestarr integration not configured")

        api = hass.data.get(DOMAIN, {}).get(entries[0].entry_id)
        if not api:
            return self._json_error(503, "Seerr Requestarr API not available")

        # Build target URL.
        # Use urlencode(quote_via=quote) so spaces become %20, not +.
        # aiohttp params= uses urllib which produces + for spaces — Overseerr rejects that.
        base = f"{api._url}/api/v1/{path}"
        if request.rel_url.query:
            qs = urlencode(dict(request.rel_url.query), quote_via=quote)
            target = f"{base}?{qs}"
        else:
            target = base

        _LOGGER.warning("Seerr proxy %s %s", method, target)

        try:
            if method == "GET":
                kwargs: dict[str, Any] = {"headers": dict(api.get_headers)}
            else:
                try:
                    body = await request.json()
                    kwargs = {"headers": dict(api.post_headers), "json": body}
                except Exception:
                    kwargs = {"headers": dict(api.post_headers), "data": await request.read()}

            async with api._session.request(method, target, **kwargs) as resp:
                raw = await resp.read()
                if resp.status >= 400:
                    _LOGGER.warning(
                        "Seerr proxy upstream %s %s -> HTTP %s body: %s",
                        method, target, resp.status,
                        raw[:500].decode("utf-8", errors="replace"),
                    )
                else:
                    _LOGGER.warning("Seerr proxy %s %s -> HTTP %s OK", method, target, resp.status)
                return web.Response(status=resp.status, content_type="application/json", body=raw)

        except Exception as err:
            _LOGGER.error("Seerr proxy exception %s %s: %s", method, target, err)
            return self._json_error(502, str(err))

    @staticmethod
    def _json_error(status: int, msg: str) -> web.Response:
        return web.Response(
            status=status,
            content_type="application/json",
            text=json.dumps({"error": msg}),
        )


class SeerrDebugView(HomeAssistantView):
    """Debug endpoint — visit /api/seerr_debug to verify proxy config."""

    url = "/api/seerr_debug"
    name = "api:seerr_debug"
    requires_auth = True

    async def get(self, request: web.Request) -> web.Response:
        hass: HomeAssistant = request.app["hass"]
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            return web.Response(
                content_type="application/json",
                text=json.dumps({"status": "error", "reason": "no config entries"}),
            )
        api = hass.data.get(DOMAIN, {}).get(entries[0].entry_id)
        info: dict[str, Any] = {
            "status": "ok" if api else "error",
            "domain": DOMAIN,
            "entries": len(entries),
            "api_loaded": api is not None,
            "overseerr_url": api._url if api else None,
        }
        if api:
            try:
                s = await api.get_status()
                info["overseerr_version"] = s.get("version")
                info["overseerr_reachable"] = True
            except Exception as e:
                info["overseerr_reachable"] = False
                info["overseerr_error"] = str(e)
        return web.Response(content_type="application/json", text=json.dumps(info))
