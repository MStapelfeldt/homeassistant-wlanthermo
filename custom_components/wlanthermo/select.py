
from __future__ import annotations
from typing import List, Dict, Any
from homeassistant.components.select import SelectEntity
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

    entities: List[SelectEntity] = []
    model_version = entry.data.get("model_version", "Mini-V3")
    pm_list = _pm_list(coord)
    if model_version == "Mini-V2" and len(pm_list) >= 2:
        entities.append(PitmasterModeSelect(coord, device, pm_id=pm_list[0].get("id", 0), label=1))
        entities.append(PitmasterChannelSelect(coord, device, pm_id=pm_list[0].get("id", 0), label=1))
        entities.append(PitmasterProfileSelect(coord, device, pm_id=pm_list[0].get("id", 0), label=1))
        entities.append(PitmasterModeSelect(coord, device, pm_id=pm_list[1].get("id", 1), label=2))
        entities.append(PitmasterChannelSelect(coord, device, pm_id=pm_list[1].get("id", 1), label=2))
        entities.append(PitmasterProfileSelect(coord, device, pm_id=pm_list[1].get("id", 1), label=2))
    else:
        entities.append(PitmasterModeSelect(coord, device))
        entities.append(PitmasterChannelSelect(coord, device))
        entities.append(PitmasterProfileSelect(coord, device))

    sensors = ((coord.data.get("_settings") or {}).get("sensors") or [])
    for ch in coord.data.get("channel", []):
        entities.append(ChannelTypeSelect(coord, device, ch["number"], sensors))
        entities.append(ChannelAlarmSelect(coord, device, ch["number"]))

    async_add_entities(entities)


class _BasePmSelect(BaseWLANThermoDeviceEntity, SelectEntity):
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

class PitmasterModeSelect(_BasePmSelect):
    _attr_name = "Pitmaster {pm} Mode"
    _uid_suffix = "mode"
    @property
    def name(self) -> str:
        return self._attr_name.format(pm=self._label)
    @property
    def options(self) -> List[str]:
        return (self.coordinator.data.get("pitmaster") or {}).get("type", ["off","manual","auto"])
    @property
    def current_option(self) -> str | None:
        pm = self._pm()
        return None if pm is None else pm.get("typ")
    async def async_select_option(self, option: str) -> None:
        coord = self.coordinator
        pm = self._pm()
        if pm is None: return
        payload = [{
            "id": pm.get("id"),
            "channel": pm.get("channel"),
            "pid": pm.get("pid", 0),
            "value": pm.get("value", 0),
            "set": pm.get("set", 0.0),
            "typ": option
        }]
        api = self.hass.data[DOMAIN][coord.config_entry.entry_id]["api"]
        await api.set_pitmaster(payload)
        await coord.async_request_refresh()

class PitmasterChannelSelect(_BasePmSelect):
    _attr_name = "Pitmaster {pm} Channel"
    _uid_suffix = "channel"
    @property
    def name(self) -> str:
        return self._attr_name.format(pm=self._label)
    @property
    def options(self) -> List[str]:
        return [str(ch.get("number")) for ch in self.coordinator.data.get("channel", [])]
    @property
    def current_option(self) -> str | None:
        pm = self._pm()
        return None if pm is None else str(pm.get("channel"))
    async def async_select_option(self, option: str) -> None:
        coord = self.coordinator
        pm = self._pm()
        if pm is None: return
        channel = int(option)
        payload = [{
            "id": pm.get("id"),
            "channel": channel,
            "pid": pm.get("pid", 0),
            "value": pm.get("value", 0),
            "set": pm.get("set", 0.0),
            "typ": pm.get("typ", "auto")
        }]
        api = self.hass.data[DOMAIN][coord.config_entry.entry_id]["api"]
        await api.set_pitmaster(payload)
        await coord.async_request_refresh()

class PitmasterProfileSelect(_BasePmSelect):
    _attr_name = "Pitmaster {pm} Profile"
    _uid_suffix = "profile"
    @property
    def name(self) -> str:
        return self._attr_name.format(pm=self._label)
    @property
    def _pid_list(self) -> List[Dict[str, Any]]:
        return (self.coordinator.data.get("_settings") or {}).get("pid") or []
    @property
    def options(self) -> List[str]:
        return [p.get("name") for p in self._pid_list]
    @property
    def current_option(self) -> str | None:
        pm = self._pm()
        if pm is None: return None
        for p in self._pid_list:
            if p.get("id") == pm.get("pid"):
                return p.get("name")
        return None
    async def async_select_option(self, option: str) -> None:
        pm = self._pm()
        if pm is None: return
        pid_id = None
        for p in self._pid_list:
            if p.get("name") == option:
                pid_id = p.get("id"); break
        if pid_id is None: return
        coord = self.coordinator
        payload = [{
            "id": pm.get("id"),
            "channel": pm.get("channel"),
            "pid": int(pid_id),
            "value": pm.get("value", 0),
            "set": pm.get("set", 0.0),
            "typ": pm.get("typ", "auto")
        }]
        api = self.hass.data[DOMAIN][coord.config_entry.entry_id]["api"]
        await api.set_pitmaster(payload)
        await coord.async_request_refresh()

class ChannelTypeSelect(BaseWLANThermoDeviceEntity, SelectEntity):
    _attr_has_entity_name = True
    _uid_suffix = "chtyp"
    def __init__(self, coordinator, device, channel_number: int, sensors: List[Dict[str, Any]]):
        super().__init__(coordinator, device)
        self._ch = channel_number
        self._sensors = sensors
    @property
    def name(self) -> str:
        return f"Channel {self._ch} Sensor Type"
    @property
    def unique_id(self) -> str:
        return f"{list(self.device_info['identifiers'])[0][1]}_channel{self._ch}_type"
    @property
    def options(self) -> List[str]:
        return [s.get("name") for s in self._sensors]
    @property
    def current_option(self) -> str | None:
        ch_typ = None
        for ch in self.coordinator.data.get("channel", []):
            if ch.get("number") == self._ch:
                ch_typ = ch.get("typ"); break
        if ch_typ is None: return None
        for s in self._sensors:
            if s.get("type") == ch_typ:
                return s.get("name", str(ch_typ))
        return str(ch_typ)
    async def async_select_option(self, option: str) -> None:
        type_id = None
        for s in self._sensors:
            if s.get("name") == option:
                type_id = s.get("type"); break
        if type_id is None: return
        api = self.hass.data[DOMAIN][self.coordinator.config_entry.entry_id]["api"]
        await api.set_channels({"number": self._ch, "typ": int(type_id)})
        await self.coordinator.async_request_refresh()

class ChannelAlarmSelect(BaseWLANThermoDeviceEntity, SelectEntity):
    _attr_has_entity_name = True
    _uid_suffix = "alarm"
    _ALARM_MAP = {0: "off", 1: "push", 2: "buzzer", 3: "push+buzzer"}
    _REV_MAP = {v: k for k, v in _ALARM_MAP.items()}
    def __init__(self, coordinator, device, channel_number: int):
        super().__init__(coordinator, device)
        self._ch = channel_number
    @property
    def name(self) -> str:
        return f"Channel {self._ch} Alarm"
    @property
    def unique_id(self) -> str:
        return f"{list(self.device_info['identifiers'])[0][1]}_channel{self._ch}_alarm"
    @property
    def options(self):
        return list(self._REV_MAP.keys())
    @property
    def current_option(self):
        for ch in self.coordinator.data.get("channel", []):
            if ch.get("number") == self._ch:
                return self._ALARM_MAP.get(ch.get("alarm", 0), "off")
        return None
    async def async_select_option(self, option: str) -> None:
        val = self._REV_MAP.get(option, 0)
        api = self.hass.data[DOMAIN][self.coordinator.config_entry.entry_id]["api"]
        await api.set_channels({"number": self._ch, "alarm": int(val)})
        await self.coordinator.async_request_refresh()
