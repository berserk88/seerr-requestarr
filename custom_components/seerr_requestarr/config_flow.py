"""Config flow for Seerr Requestarr."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OverseerrAPI
from .const import DOMAIN, CONF_URL, CONF_API_KEY

_LOGGER = logging.getLogger(__name__)

STEP_SCHEMA = vol.Schema({
    vol.Required(CONF_URL): str,
    vol.Required(CONF_API_KEY): str,
})


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            api = OverseerrAPI(url=user_input[CONF_URL], api_key=user_input[CONF_API_KEY], session=session)
            try:
                status = await api.get_status()
                title  = f"Seerr Requestarr ({status.get('version', 'unknown')})"
                return self.async_create_entry(title=title, data=user_input)
            except aiohttp.ClientResponseError as e:
                errors["base"] = "invalid_auth" if e.status == 401 else "cannot_connect"
            except Exception:
                errors["base"] = "cannot_connect"

        return self.async_show_form(step_id="user", data_schema=STEP_SCHEMA, errors=errors)
