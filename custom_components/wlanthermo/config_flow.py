
from __future__ import annotations
from typing import Any
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, CONF_BASE_PATH, CONF_USERNAME, CONF_PASSWORD
from .api import WLANThermoApi

class WLANThermoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors = {}
        if user_input is not None:
            host = user_input["host"]
            port = user_input.get("port", DEFAULT_PORT)
            base_path = user_input.get(CONF_BASE_PATH, "/")
            username = user_input.get(CONF_USERNAME)
            password = user_input.get(CONF_PASSWORD)
            api = WLANThermoApi(host, port, base_path, username=username, password=password)
            try:
                settings = await api.get_settings()
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                await api.close()
                return self.async_create_entry(title=f"WLANThermo {settings.get('device',{}).get('serial','')}", data=user_input)

        schema = vol.Schema({
            vol.Required("host"): str,
            vol.Optional("port", default=DEFAULT_PORT): int,
            vol.Optional(CONF_BASE_PATH, default="/"): str,
            vol.Optional(CONF_USERNAME): str,
            vol.Optional(CONF_PASSWORD): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return WLANThermoOptionsFlowHandler(config_entry)

class WLANThermoOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(title="Options", data=user_input)

        schema = vol.Schema({
            vol.Optional("scan_interval", default=self.config_entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)): int,
        })
        return self.async_show_form(step_id="init", data_schema=schema)
