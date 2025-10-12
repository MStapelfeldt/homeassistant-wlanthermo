
from __future__ import annotations
from typing import Any
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, PLATFORMS, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, CONF_BASE_PATH, CONF_USERNAME, CONF_PASSWORD
from .api import WLANThermoApi
from .coordinator import WLANThermoCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    data = entry.data
    host = data.get("host")
    port = data.get("port", DEFAULT_PORT)
    base_path = data.get(CONF_BASE_PATH, "/")
    username = data.get(CONF_USERNAME)
    password = data.get(CONF_PASSWORD)

    api = WLANThermoApi(host, port, base_path, username=username, password=password)

    try:
        settings = await api.get_settings()
        info = await api.get_info()
    except Exception as err:
        await api.close()
        raise ConfigEntryNotReady(f"Cannot connect to WLANThermo at {host}:{port}: {err}")

    coordinator = WLANThermoCoordinator(hass, api, f"WLANThermo {settings.get('device',{}).get('serial','')}", entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL))
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
        "device": settings.get("device", {}),
        "features": settings.get("features", {}),
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def _set_channel(call):
        obj = {k: v for k, v in call.data.items() if k not in ("use_put",)}
        await api.set_channels(obj, use_put=call.data.get("use_put", True))
        await coordinator.async_request_refresh()

    async def _set_pitmaster(call):
        payload = dict(call.data)
        use_put = payload.pop("use_put", True) if "use_put" in payload else True
        await api.set_pitmaster(payload, use_put=use_put)
        await coordinator.async_request_refresh()

    async def _set_system(call):
        await api.set_system(dict(call.data), use_put=call.data.get("use_put", True))
        await coordinator.async_request_refresh()

    async def _config_reset(call):
        await api.config_reset()
        await coordinator.async_request_refresh()

    hass.services.async_register(DOMAIN, "set_channel", _set_channel)
    hass.services.async_register(DOMAIN, "set_pitmaster", _set_pitmaster)
    hass.services.async_register(DOMAIN, "set_system", _set_system)
    hass.services.async_register(DOMAIN, "config_reset", _config_reset)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        api = hass.data[DOMAIN][entry.entry_id]["api"]
        await api.close()
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
