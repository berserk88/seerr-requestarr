"""Sensors for Seerr Requestarr."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    api = hass.data[DOMAIN][entry.entry_id]
    coordinator = SeerrCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([
        SeerrPendingSensor(coordinator, entry),
        SeerrTotalSensor(coordinator, entry),
    ])


class SeerrCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api):
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(minutes=5))
        self.api = api

    async def _async_update_data(self):
        try:
            pending = await self.api.get_requests(take=1, filter_="pending")
            total   = await self.api.get_requests(take=1, filter_="all")
            return {
                "pending": pending.get("pageInfo", {}).get("results", 0),
                "total":   total.get("pageInfo", {}).get("results", 0),
            }
        except Exception as err:
            raise UpdateFailed(f"Overseerr error: {err}") from err


class SeerrPendingSensor(CoordinatorEntity, SensorEntity):
    _attr_name = "Seerr Requestarr Pending"
    _attr_icon = "mdi:clock-outline"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_pending"

    @property
    def native_value(self):
        return self.coordinator.data.get("pending", 0)


class SeerrTotalSensor(CoordinatorEntity, SensorEntity):
    _attr_name = "Seerr Requestarr Total"
    _attr_icon = "mdi:movie-open"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_total"

    @property
    def native_value(self):
        return self.coordinator.data.get("total", 0)
