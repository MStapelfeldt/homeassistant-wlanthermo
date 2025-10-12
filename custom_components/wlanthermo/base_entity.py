
from __future__ import annotations
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN

class BaseWLANThermoDeviceEntity(CoordinatorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._device = device or {}
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device.get("serial", "unknown"))},
            manufacturer="WLANThermo",
            name=self._device.get("device", "WLANThermo"),
            model=self._device.get("hw_version", "ESP32"),
            sw_version=self._device.get("sw_version"),
        )
