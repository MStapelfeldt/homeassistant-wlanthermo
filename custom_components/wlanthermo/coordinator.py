
from __future__ import annotations
import logging
from datetime import timedelta
from typing import Any, Dict
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

class WLANThermoCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, api, name: str, interval: int | None):
        super().__init__(hass, _LOGGER, name=name, update_interval=timedelta(seconds=interval or DEFAULT_SCAN_INTERVAL))
        self.api = api
        self.settings: Dict[str, Any] | None = None

    async def _async_update_data(self) -> Dict[str, Any]:
        data = await self.api.get_data()
        try:
            if not self.settings:
                self.settings = await self.api.get_settings()
        except Exception as err:
            _LOGGER.debug("Reading settings failed (will retry): %s", err)
        data["_settings"] = self.settings
        return data
