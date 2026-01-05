
from __future__ import annotations
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import SIGNAL_STRENGTH_DECIBELS_MILLIWATT, PERCENTAGE, UnitOfTemperature
from .const import DOMAIN
from .base_entity import BaseWLANThermoDeviceEntity



def _pm_list(coordinator):
    return ((coordinator.data or {}).get("pitmaster") or {}).get("pm", []) or []

def _resolve_pm_by_device_id(coordinator, pm_id):
    for p in _pm_list(coordinator):
        if p.get("id") == pm_id:
            return p
    return None
async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coord = data["coordinator"]
    device = data["device"]
    entities: list[SensorEntity] = []

    # Channel temperature sensors
    for ch in coord.data.get('channel', []):
        ch_no = ch['number']
        entities.append(ChannelTemperatureSensor(coord, device, ch_no))
        entities.append(ChannelTemperatureFixedNameSensor(coord, device, ch_no))

    # Pitmaster output sensors
    model_version = entry.data.get("model_version", "Mini-V3")
    pm_list = _pm_list(coord)
    if model_version == "Mini-V2" and len(pm_list) >= 2:
        entities.append(PitmasterOutputSensor(coord, device, pm_id=pm_list[0].get("id", 0), label=1))
        entities.append(PitmasterOutputSensor(coord, device, pm_id=pm_list[1].get("id", 1), label=2))
    else:
        entities.append(PitmasterOutputSensor(coord, device))

    # System sensors
    entities.append(SystemRssiSensor(coord, device))
    model_version = entry.data.get("model_version", "Mini-V3")
    if model_version != "Mini-V2":
        entities.append(SystemBatteryLevel(coord, device))
        entities.append(SystemBatteryCharging(coord, device))
    async_add_entities(entities)

class SystemRssiSensor(BaseWLANThermoDeviceEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "RSSI"
    _attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT
    _attr_icon = "mdi:wifi-strength-2"
    @property
    def unique_id(self) -> str:
        return f"{list(self.device_info['identifiers'])[0][1]}_rssi"
    @property
    def native_value(self):
        sys = (self.coordinator.data or {}).get("system", {})
        return sys.get("rssi")

class SystemBatteryLevel(BaseWLANThermoDeviceEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Battery Level"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:battery"
    @property
    def unique_id(self) -> str:
        return f"{list(self.device_info['identifiers'])[0][1]}_battery_level"
    @property
    def native_value(self):
        sys = (self.coordinator.data or {}).get("system", {})
        return sys.get("soc")

class SystemBatteryCharging(BaseWLANThermoDeviceEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Battery Charging"
    _attr_icon = "mdi:battery-charging"
    @property
    def unique_id(self) -> str:
        return f"{list(self.device_info['identifiers'])[0][1]}_battery_charging"
    @property
    def native_value(self):
        sys = (self.coordinator.data or {}).get("system", {})
        chg = sys.get("charge")
        if isinstance(chg, bool):
            return "charging" if chg else "not charging"
        if isinstance(chg, int):
            return "charging" if chg > 0 else "not charging"
        return None


class ChannelTemperatureSensor(BaseWLANThermoDeviceEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    def __init__(self, coordinator, device, channel_number: int):
        super().__init__(coordinator, device)
        self._ch = channel_number
    @property
    def name(self) -> str:
        # Prefer channel name if set, else "Channel X Temperature"
        ch_name = None
        for ch in (self.coordinator.data or {}).get("channel", []):
            if ch.get("number") == self._ch:
                ch_name = ch.get("name")
                break
        base = ch_name if ch_name else f"Channel {self._ch}"
        return f"{base} Temperature"
    @property
    def unique_id(self) -> str:
        return f"{list(self.device_info['identifiers'])[0][1]}_channel{self._ch}_temp"
    @property
    def native_unit_of_measurement(self):
        unit = ((self.coordinator.data or {}).get("system") or {}).get("unit", "C")
        return UnitOfTemperature.FAHRENHEIT if str(unit).upper().startswith("F") else UnitOfTemperature.CELSIUS
    @property
    def native_value(self):
        for ch in (self.coordinator.data or {}).get("channel", []):
            if ch.get("number") == self._ch:
                temp = ch.get("temp")
                if temp == 999.0:
                    return None  # Home Assistant will treat as unavailable
                return temp
        return None


class ChannelTemperatureFixedNameSensor(BaseWLANThermoDeviceEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    def __init__(self, coordinator, device, channel_number: int):
        super().__init__(coordinator, device)
        self._ch = channel_number
    @property
    def name(self) -> str:
        return f"Channel {self._ch} Temperature"
    @property
    def unique_id(self) -> str:
        return f"{list(self.device_info['identifiers'])[0][1]}_channel{self._ch}_temp_fixed"
    @property
    def native_unit_of_measurement(self):
        unit = ((self.coordinator.data or {}).get("system") or {}).get("unit", "C")
        return UnitOfTemperature.FAHRENHEIT if str(unit).upper().startswith("F") else UnitOfTemperature.CELSIUS
    @property
    def native_value(self):
        for ch in (self.coordinator.data or {}).get("channel", []):
            if ch.get("number") == self._ch:
                temp = ch.get("temp")
                if temp == 999.0:
                    return None  # Home Assistant will treat as unavailable
                return temp
        return None


class PitmasterOutputSensor(BaseWLANThermoDeviceEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_icon = "mdi:gauge"
    _attr_native_unit_of_measurement = PERCENTAGE
    def __init__(self, coordinator, device, pm_id=None, label=1):
        super().__init__(coordinator, device)
        if pm_id is None:
            pm_list = _pm_list(coordinator)
            pm_id = pm_list[0].get("id") if pm_list else 1
        self._pm_id = pm_id
        self._label = label
        self._attr_name = f"Pitmaster {label} Output"
    def _pm(self):
        return _resolve_pm_by_device_id(self.coordinator, self._pm_id)
    @property
    def unique_id(self) -> str:
        dev = self._pm_id if self._pm_id is not None else self._label
        return f"{list(self.device_info['identifiers'])[0][1]}_pm{dev}_output"
    @property
    def native_value(self):
        pm = self._pm()
        if pm is None:
            return None
        return pm.get("value")
    