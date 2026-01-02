
from __future__ import annotations
from homeassistant.components.number import NumberEntity
from homeassistant.const import UnitOfTemperature
from .const import DOMAIN
from .base_entity import BaseWLANThermoDeviceEntity

def _pm_list(coordinator):
    return (coordinator.data.get("pitmaster") or {}).get("pm", []) or []



def _resolve_pm_by_device_id(coordinator, device_pm_id):
    for p in _pm_list(coordinator):
        if p.get("id") == device_pm_id:
            return p
    return None

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coord = data["coordinator"]
    device = data["device"]
    entities: list[NumberEntity] = []

    # Pitmaster entities
    model_version = entry.data.get("model_version", "Mini-V3")
    pm_list = _pm_list(coord)
    if model_version == "Mini-V2" and len(pm_list) >= 2:
        # Add both pitmasters
        entities.append(PitmasterSetpointNumber(coord, device, pm_id=pm_list[0].get("id", 0), label=1))
        entities.append(PitmasterManualValueNumber(coord, device, pm_id=pm_list[0].get("id", 0), label=1))
        entities.append(PitmasterSetpointNumber(coord, device, pm_id=pm_list[1].get("id", 1), label=2))
        entities.append(PitmasterManualValueNumber(coord, device, pm_id=pm_list[1].get("id", 1), label=2))
    else:
        # Only Pitmaster 1
        entities.append(PitmasterSetpointNumber(coord, device))
        entities.append(PitmasterManualValueNumber(coord, device))

    # Channel min/max
    for ch in coord.data.get("channel", []):
        entities.append(ChannelMinNumber(coord, device, ch["number"]))
        entities.append(ChannelMaxNumber(coord, device, ch["number"]))

    async_add_entities(entities)


class _BasePmNumber(BaseWLANThermoDeviceEntity, NumberEntity):
    _attr_has_entity_name = True
    def __init__(self, coordinator, device, pm_id=None, label=1):
        super().__init__(coordinator, device)
        if pm_id is None:
            pm_list = _pm_list(coordinator)
            pm_id = pm_list[0].get("id") if pm_list else 1
        self._device_pm_id = pm_id
        self._label = label
    def _pm(self):
        return _resolve_pm_by_device_id(self.coordinator, self._device_pm_id)
    @property
    def unique_id(self) -> str:
        dev = self._device_pm_id if self._device_pm_id is not None else self._label
        return f"{list(self.device_info['identifiers'])[0][1]}_pm{dev}_{self._uid_suffix}"
    @property
    def name(self):
        return self._attr_name.format(pm=self._label)

class PitmasterSetpointNumber(_BasePmNumber):
    _attr_name = "Pitmaster {pm} Setpoint"
    _uid_suffix = "set"
    _attr_native_step = 0.5
    _attr_native_min_value = 0
    _attr_native_max_value = 400
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    @property
    def native_value(self):
        pm = self._pm()
        return None if pm is None else pm.get("set")
    async def async_set_native_value(self, value: float) -> None:
        coord = self.coordinator
        pm = self._pm()
        if pm is None:
            return
        payload = [{
            "id": pm.get("id"),
            "channel": pm.get("channel"),
            "pid": pm.get("pid", 0),
            "value": pm.get("value", 0),
            "set": float(value),
            "typ": pm.get("typ", "auto")
        }]
        api = self.hass.data[DOMAIN][coord.config_entry.entry_id]["api"]
        await api.set_pitmaster(payload)
        await coord.async_request_refresh()

class PitmasterManualValueNumber(_BasePmNumber):
    _attr_name = "Pitmaster {pm} Manual Output"
    _uid_suffix = "value"
    _attr_native_step = 1
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    @property
    def native_value(self):
        pm = self._pm()
        return None if pm is None else pm.get("value")
    async def async_set_native_value(self, value: float) -> None:
        coord = self.coordinator
        pm = self._pm()
        if pm is None:
            return
        payload = [{
            "id": pm.get("id"),
            "channel": pm.get("channel"),
            "pid": pm.get("pid", 0),
            "value": int(value),
            "set": pm.get("set", 0.0),
            "typ": "manual"
        }]
        api = self.hass.data[DOMAIN][coord.config_entry.entry_id]["api"]
        await api.set_pitmaster(payload)
        await coord.async_request_refresh()

class _BaseChNumber(BaseWLANThermoDeviceEntity, NumberEntity):
    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_native_step = 0.5
    _attr_native_min_value = -30
    _attr_native_max_value = 350
    def __init__(self, coordinator, device, ch_no: int):
        super().__init__(coordinator, device)
        self._ch = ch_no
    @property
    def unique_id(self) -> str:
        return f"{list(self.device_info['identifiers'])[0][1]}_channel{self._ch}_{self._uid_suffix}"
    def _get(self, key):
        for c in self.coordinator.data.get("channel", []):
            if c.get("number") == self._ch:
                return c.get(key)
        return None
    async def _write(self, key, value):
        api = self.hass.data[DOMAIN][self.coordinator.config_entry.entry_id]["api"]
        await api.set_channels({"number": self._ch, key: float(value)})

class ChannelMinNumber(_BaseChNumber):
    _uid_suffix = "min"
    @property
    def name(self): return f"Channel {self._ch} Min"
    @property
    def native_value(self): return self._get("min")
    async def async_set_native_value(self, value: float) -> None:
        await self._write("min", value)
        await self.coordinator.async_request_refresh()

class ChannelMaxNumber(_BaseChNumber):
    _uid_suffix = "max"
    @property
    def name(self): return f"Channel {self._ch} Max"
    @property
    def native_value(self): return self._get("max")
    async def async_set_native_value(self, value: float) -> None:
        await self._write("max", value)
        await self.coordinator.async_request_refresh()
