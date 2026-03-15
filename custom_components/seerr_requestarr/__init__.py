"""Seerr Requestarr — Home Assistant integration for Overseerr."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OverseerrAPI
from .const import DOMAIN, CONF_URL, CONF_API_KEY
from .http_api import async_register_views

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    async_register_views(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    session = async_get_clientsession(hass)
    api = OverseerrAPI(
        url=entry.data[CONF_URL],
        api_key=entry.data[CONF_API_KEY],
        session=session,
    )
    try:
        await api.get_status()
    except Exception as err:
        _LOGGER.error("Seerr Requestarr: cannot connect to Overseerr: %s", err)
        return False

    hass.data[DOMAIN][entry.entry_id] = api
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def handle_request_media(call):
        media_type = call.data.get("media_type")
        media_id   = call.data.get("media_id")
        result = await api.request_media(media_type, media_id)
        _LOGGER.info("Seerr request result: %s", result)

    async def handle_search(call):
        query   = call.data.get("query")
        results = await api.search(query)
        hass.bus.async_fire(f"{DOMAIN}_search_results", {"query": query, "results": results})

    hass.services.async_register(DOMAIN, "request_media", handle_request_media)
    hass.services.async_register(DOMAIN, "search", handle_search)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return ok
