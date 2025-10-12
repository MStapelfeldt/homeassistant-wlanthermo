
from __future__ import annotations
from homeassistant.components.button import ButtonEntity
from .const import DOMAIN
from .base_entity import BaseWLANThermoDeviceEntity

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coord = data["coordinator"]
    device = data["device"]
    async_add_entities([ConfigResetButton(coord, device)])

class ConfigResetButton(BaseWLANThermoDeviceEntity, ButtonEntity):
    _attr_has_entity_name = True
    _attr_name = "Config Reset"

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{device.get('serial')}_config_reset"

    async def async_press(self) -> None:
        api = self.hass.data[DOMAIN][self.coordinator.config_entry.entry_id]["api"]
        await api.config_reset()
        await self.coordinator.async_request_refresh()
