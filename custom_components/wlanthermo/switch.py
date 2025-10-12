
from __future__ import annotations
from typing import Any
from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN
from .base_entity import BaseWLANThermoDeviceEntity

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coord = data["coordinator"]
    device = data["device"]

    entities = [SystemFlagSwitch(coord, device, flag) for flag in ("autoupd", "prerelease")]
    async_add_entities(entities)

class SystemFlagSwitch(BaseWLANThermoDeviceEntity, SwitchEntity):
    def __init__(self, coordinator, device, flag: str):
        super().__init__(coordinator, device)
        self._flag = flag
        self._attr_unique_id = f"{device.get('serial')}_system_{flag}"
        self._attr_name = f"System {flag}"

    @property
    def is_on(self) -> bool:
        sys = (self.coordinator.data.get("system", {}) or {})
        return bool(sys.get(self._flag))

    async def async_turn_on(self, **kwargs: Any) -> None:
        api = self.hass.data[DOMAIN][self.coordinator.config_entry.entry_id]["api"]
        await api.set_system({self._flag: True})
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        api = self.hass.data[DOMAIN][self.coordinator.config_entry.entry_id]["api"]
        await api.set_system({self._flag: False})
        await self.coordinator.async_request_refresh()
