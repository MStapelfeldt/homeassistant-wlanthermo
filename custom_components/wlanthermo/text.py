
from __future__ import annotations
from homeassistant.components.text import TextEntity
from .const import DOMAIN
from .base_entity import BaseWLANThermoDeviceEntity

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coord = data["coordinator"]
    device = data["device"]
    entities = [ChannelNameText(coord, device, ch["number"]) for ch in coord.data.get("channel", [])]
    async_add_entities(entities)

class ChannelNameText(BaseWLANThermoDeviceEntity, TextEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, device, ch_no: int):
        super().__init__(coordinator, device)
        self._ch = ch_no
        self._attr_name = f"Channel {ch_no} Name"
        self._attr_unique_id = f"{device.get('serial')}_ch_{ch_no}_name"
        self._attr_min = 0
        self._attr_max = 32

    @property
    def native_value(self):
        for ch in self.coordinator.data.get("channel", []):
            if ch.get("number") == self._ch:
                return ch.get("name")
        return None

    async def async_set_value(self, value: str) -> None:
        api = self.hass.data[DOMAIN][self.coordinator.config_entry.entry_id]["api"]
        await api.set_channels({"number": self._ch, "name": value})
        await self.coordinator.async_request_refresh()
