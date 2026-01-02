
from __future__ import annotations
from typing import Any, Dict, List, Optional, Iterable

import logging
from aiohttp import ClientSession, BasicAuth
from yarl import URL

_LOGGER = logging.getLogger(__name__)

class WLANThermoApi:
    def __init__(self, host: str, port: int = 80, base_path: str = "/", *, username: Optional[str] = None, password: Optional[str] = None, verify_ssl: bool = True, timeout: int = 8) -> None:
        self._base = URL.build(scheme="http", host=host, port=port) / base_path.strip("/")
        self._auth = BasicAuth(username or "", password) if password else None
        self._verify_ssl = verify_ssl
        self._timeout = timeout
        self._session: Optional[ClientSession] = None

    def _url(self, path: str) -> URL:
        return self._base / path.strip("/")

    async def _ensure(self) -> ClientSession:
        if self._session is None:
            self._session = ClientSession()
        return self._session

    async def _req(self, method: str, path: str, json: Any | None = None) -> Any:
        session = await self._ensure()
        url = self._url(path)
        async with session.request(method, url, json=json, auth=self._auth, ssl=self._verify_ssl, timeout=self._timeout) as resp:
            if resp.content_type == "application/json":
                data = await resp.json()
            else:
                data = await resp.text()
            if resp.status >= 400:
                raise RuntimeError(f"HTTP {resp.status} for {url}: {data}")
            return data

    async def close(self) -> None:
        if self._session:
            await self._session.close()
            self._session = None

    async def get_data(self) -> Dict[str, Any]:
        return await self._req("GET", "/data")

    async def get_settings(self) -> Dict[str, Any]:
        return await self._req("GET", "/settings")

    async def get_info(self) -> Dict[str, Any]:
        return await self._req("GET", "/info")

    async def _try_write(self, paths: Iterable[str], json: Any, methods: Iterable[str]) -> bool:
        last_exc: Exception | None = None
        for path in paths:
            for method in methods:
                try:
                    res = await self._req(method, path, json=json)
                    if str(res).strip().lower() == "true":
                        return True
                except Exception as exc:
                    last_exc = exc
                    continue
        if last_exc:
            raise last_exc
        return False

    async def set_channels(self, channel_obj: Dict[str, Any], *, use_put: bool = True) -> bool:
        methods = ("PUT","POST") if use_put else ("POST","PUT")
        paths = ("/setchannels", "/setchannels")
        return await self._try_write(paths, channel_obj, methods)

    async def set_pitmaster(self, pm_obj: Dict[str, Any] | List[Dict[str, Any]], *, use_put: bool = True, coordinator=None, model_version=None) -> bool:
        methods = ("PUT","POST") if use_put else ("POST","PUT")
        payload = pm_obj if isinstance(pm_obj, list) else [pm_obj]
        # For Mini-V2, always send both pitmasters if available
        if model_version == "Mini-V2" and coordinator is not None:
            pm_list = ((coordinator.data or {}).get("pitmaster") or {}).get("pm", []) or []
            pm_dict = {pm.get("id"): dict(pm) for pm in pm_list}
            for p in payload:
                pm_dict[p.get("id")] = dict(p)
            payload = [pm_dict[k] for k in sorted(pm_dict.keys())]
        # Only send the first/changed pitmaster for others
        elif model_version != "Mini-V2":
            payload = [payload[0]]
        #_LOGGER.warning("[WLANThermoApi.set_pitmaster]  Model: %s Payload: %s", model_version, payload)
        paths = ("/setpitmaster", "/setpitmaster")
        return await self._try_write(paths, payload, methods)

    async def set_system(self, sys_obj: Dict[str, Any], *, use_put: bool = True) -> bool:
        methods = ("PUT","POST") if use_put else ("POST","PUT")
        paths = ("/setsystem", "/setsystem")
        return await self._try_write(paths, sys_obj, methods)

    async def set_pid(self, pid_objs: List[Dict[str, Any]], *, use_put: bool = True) -> bool:
        methods = ("PUT","POST") if use_put else ("POST","PUT")
        paths = ("/setpid", "/setpid")
        return await self._try_write(paths, pid_objs, methods)

    async def set_iot(self, iot_obj: Dict[str, Any], *, use_put: bool = True) -> bool:
        methods = ("PUT","POST") if use_put else ("POST","PUT")
        paths = ("/setiot", "/setiot")
        return await self._try_write(paths, iot_obj, methods)

    async def config_reset(self) -> bool:
        res = await self._req("POST", "/configreset")
        return str(res).strip().lower() == "true"
