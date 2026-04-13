#!/usr/bin/env python3
"""
从 Nacos 拉取 MCP 远端地址，作为 MCP Client 连接、列举工具、调用工具（HTTP 网关）。

数据来源（可同时使用）：

1) 配置中心（CS）：dataId 指向的 JSON

   单服务：{"url": "http://127.0.0.1:3000/sse", "transport": "sse"}

   多服务：
   {
     "default": "demo",
     "servers": {
       "demo": {"url": "http://127.0.0.1:3000/sse", "transport": "sse"},
       "http": {"url": "http://127.0.0.1:3000/mcp", "transport": "streamable_http"}
     }
   }

2) 命名服务（可选）：环境变量 NACOS_DISCOVER_SERVICES 为逗号分隔的服务名，
   网关会请求 /nacos/v1/ns/instance/list，从健康实例 metadata 读取 mcp.url、mcp.transport
   （与 mcp_nacos_server.py 注册时写入的字段一致），合并到 servers，键为 naming.<服务名>.<序号>。

transport：sse（默认）、streamable_http（或 http）。

环境变量：
  NACOS_BASE                 默认 http://localhost:8848
  NACOS_DATA_ID              dataId，默认 mcp-servers.json
  NACOS_GROUP                默认 DEFAULT_GROUP
  NACOS_NAMESPACE            命名空间 ID，留空为 public
  NACOS_DISCOVER_SERVICES    可选，逗号分隔，从命名服务发现 MCP 实例
  MCP_SERVERS_JSON           可选，与配置中心同格式的 JSON；若设置则**不请求 Nacos**（本地联调或 Nacos API 不可用时使用）
  LISTEN_HOST                默认 127.0.0.1
  LISTEN_PORT                默认 1234
"""

from __future__ import annotations

import json
import logging
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

import httpx
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from mcp import McpError
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamable_http_client

logger = logging.getLogger("mcp-gateway")


@dataclass
class GatewayState:
    raw: str | None = None
    parsed: dict[str, Any] | None = None
    error: str | None = None
    nacos_url: str = ""

    def servers(self) -> dict[str, dict[str, Any]]:
        if not self.parsed:
            return {}
        return self.parsed.get("servers", {})

    def default_name(self) -> str | None:
        if not self.parsed:
            return None
        return self.parsed.get("default")

    def resolve_server(self, name: str | None) -> tuple[str, dict[str, Any]]:
        s = self.servers()
        if not s:
            raise ValueError("Nacos 中尚无有效 MCP 配置")
        if name:
            if name not in s:
                raise ValueError(f"未知 server: {name!r}，可选: {list(s.keys())}")
            return name, s[name]
        d = self.default_name()
        if d and d in s:
            return d, s[d]
        first = next(iter(s.items()))
        return first


def _parse_mcp_json(text: str) -> dict[str, Any]:
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("配置必须是 JSON 对象")

    if "servers" in data:
        servers = data["servers"]
        if not isinstance(servers, dict) or not servers:
            raise ValueError("servers 必须为非空对象")
        out: dict[str, Any] = {"servers": {}, "default": data.get("default")}
        for k, v in servers.items():
            if not isinstance(v, dict) or "url" not in v:
                raise ValueError(f"servers[{k!r}] 需要包含 url")
            out["servers"][k] = {
                "url": str(v["url"]),
                "transport": str(v.get("transport") or "sse").lower(),
            }
        d = out["default"]
        if d is not None and d not in out["servers"]:
            raise ValueError(f"default={d!r} 不在 servers 中")
        if out["default"] is None:
            out["default"] = next(iter(out["servers"]))
        return out

    if "url" in data:
        url = data["url"]
        if not isinstance(url, str):
            raise ValueError("url 必须是字符串")
        tr = str(data.get("transport") or "sse").lower()
        return {"default": "default", "servers": {"default": {"url": url, "transport": tr}}}

    raise ValueError("需要 {url,...} 或 {servers:{...}}")


def _parse_metadata(meta: Any) -> dict[str, str]:
    if meta is None:
        return {}
    if isinstance(meta, dict):
        return {str(k): str(v) for k, v in meta.items()}
    if isinstance(meta, str):
        try:
            d = json.loads(meta)
        except json.JSONDecodeError:
            return {}
        if isinstance(d, dict):
            return {str(k): str(v) for k, v in d.items()}
    return {}


async def discover_naming_mcp_servers(
    base: str,
    group: str,
    namespace: str,
    service_names: list[str],
) -> dict[str, dict[str, Any]]:
    """从命名服务拉取带 mcp.url 的健康实例，键形如 naming.<服务名>.<序号>。"""
    out: dict[str, dict[str, Any]] = {}
    root = base.rstrip("/")
    url = f"{root}/nacos/v1/ns/instance/list"
    async with httpx.AsyncClient() as client:
        for svc in service_names:
            params: dict[str, str] = {"serviceName": svc.strip(), "groupName": group}
            if namespace:
                params["namespaceId"] = namespace
            if not svc.strip():
                continue
            r = await client.get(url, params=params, timeout=30.0)
            r.raise_for_status()
            data = r.json()
            hosts = data.get("hosts") or []
            idx = 0
            for h in hosts:
                if not h.get("healthy", True):
                    continue
                meta = _parse_metadata(h.get("metadata"))
                mcp_url = meta.get("mcp.url") or meta.get("mcp_url")
                if not mcp_url:
                    continue
                tr = (meta.get("mcp.transport") or meta.get("mcp_transport") or "sse").lower()
                if tr in ("streamable-http", "http"):
                    tr = "streamable_http"
                out[f"naming.{svc.strip()}.{idx}"] = {"url": mcp_url, "transport": tr}
                idx += 1
    return out


async def fetch_nacos_config(
    base: str,
    data_id: str,
    group: str,
    namespace: str,
) -> str:
    params: dict[str, str] = {"dataId": data_id, "group": group}
    if namespace:
        params["tenant"] = namespace
    url = f"{base.rstrip('/')}/nacos/v1/cs/configs"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params, timeout=30.0)
        if r.status_code == 404:
            return ""
        r.raise_for_status()
        return r.text or ""


@asynccontextmanager
async def mcp_client_session(url: str, transport: str):
    t = (transport or "sse").lower()
    if t in ("http", "streamable_http"):
        async with streamable_http_client(url) as (read, write, _get_sid):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session
    elif t == "sse":
        async with sse_client(url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session
    else:
        raise ValueError(f"不支持的 transport: {transport!r}，使用 sse 或 streamable_http")


async def _with_session(
    server: dict[str, Any],
    fn: Callable[[ClientSession], Awaitable[Any]],
) -> Any:
    url = server["url"]
    transport = server.get("transport", "sse")
    async with mcp_client_session(url, transport) as session:
        return await fn(session)


def _tool_result_to_json(obj: Any) -> Any:
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json", exclude_none=False)
    return obj


@dataclass
class AppContext:
    nacos_base: str
    data_id: str
    group: str
    namespace: str
    discover_services: list[str]
    state: GatewayState = field(default_factory=GatewayState)

    async def refresh(self) -> None:
        self.state.error = None
        inline = os.environ.get("MCP_SERVERS_JSON", "").strip()
        if inline:
            self.state.nacos_url = "(env MCP_SERVERS_JSON)"
            try:
                self.state.raw = inline
                self.state.parsed = _parse_mcp_json(inline)
                logger.info("已从 MCP_SERVERS_JSON 加载: %s", list(self.state.servers().keys()))
            except Exception as e:
                self.state.error = str(e)
                self.state.parsed = None
                logger.exception("解析 MCP_SERVERS_JSON 失败")
            return

        self.state.nacos_url = (
            f"{self.nacos_base.rstrip('/')}/nacos/v1/cs/configs"
            f"?dataId={self.data_id}&group={self.group}"
            + (f"&tenant={self.namespace}" if self.namespace else "")
        )
        try:
            raw = await fetch_nacos_config(self.nacos_base, self.data_id, self.group, self.namespace)
            self.state.raw = raw
            if raw.strip():
                parsed = _parse_mcp_json(raw)
            else:
                parsed = {"servers": {}, "default": None}

            if self.discover_services:
                discovered = await discover_naming_mcp_servers(
                    self.nacos_base,
                    self.group,
                    self.namespace,
                    self.discover_services,
                )
                merged = dict(parsed.get("servers") or {})
                merged.update(discovered)
                parsed = {**parsed, "servers": merged}
                if parsed.get("default") is None and merged:
                    parsed["default"] = next(iter(merged.keys()))

            if not parsed.get("servers"):
                raise ValueError("配置与命名发现均未得到任何 MCP 服务（请配置 CS 或 NACOS_DISCOVER_SERVICES）")

            self.state.parsed = parsed
            logger.info("已加载 MCP 服务: %s", list(self.state.servers().keys()))
        except Exception as e:
            self.state.error = str(e)
            self.state.parsed = None
            if isinstance(e, httpx.HTTPStatusError):
                logger.warning("Nacos 配置请求失败: %s", e)
            else:
                logger.exception("拉取或解析 Nacos 配置失败")


ctx: AppContext | None = None


def _parse_discover_services() -> list[str]:
    raw = os.environ.get("NACOS_DISCOVER_SERVICES", "").strip()
    if not raw:
        return []
    return [s.strip() for s in raw.split(",") if s.strip()]


async def lifespan(app: Starlette):
    global ctx
    ctx = AppContext(
        nacos_base=os.environ.get("NACOS_BASE", "http://localhost:8848"),
        data_id=os.environ.get("NACOS_DATA_ID", "mcp-servers.json"),
        group=os.environ.get("NACOS_GROUP", "DEFAULT_GROUP"),
        namespace=os.environ.get("NACOS_NAMESPACE", ""),
        discover_services=_parse_discover_services(),
    )
    await ctx.refresh()
    yield


async def health(_: Request) -> JSONResponse:
    assert ctx is not None
    ok = ctx.state.parsed is not None and not ctx.state.error
    return JSONResponse(
        {
            "ok": ok,
            "nacos": ctx.state.nacos_url,
            "error": ctx.state.error,
            "servers": list(ctx.state.servers().keys()) if ctx.state.parsed else [],
        }
    )


async def admin_refresh(_: Request) -> JSONResponse:
    assert ctx is not None
    await ctx.refresh()
    if ctx.state.error:
        return JSONResponse({"ok": False, "error": ctx.state.error}, status_code=502)
    return JSONResponse({"ok": True, "servers": list(ctx.state.servers().keys())})


async def list_servers(_: Request) -> JSONResponse:
    assert ctx is not None
    if ctx.state.error:
        return JSONResponse({"error": ctx.state.error}, status_code=502)
    return JSONResponse(
        {
            "default": ctx.state.default_name(),
            "servers": list(ctx.state.servers().keys()),
        }
    )


async def list_tools(request: Request) -> JSONResponse:
    assert ctx is not None
    if ctx.state.error:
        return JSONResponse({"error": ctx.state.error}, status_code=502)
    try:
        name = request.query_params.get("server")
        _, srv = ctx.state.resolve_server(name or None)

        async def run(session: ClientSession):
            res = await session.list_tools()
            return _tool_result_to_json(res)

        result = await _with_session(srv, run)
        return JSONResponse(result)
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    except McpError as e:
        return JSONResponse({"error": str(e)}, status_code=502)
    except Exception as e:
        logger.exception("list_tools")
        return JSONResponse({"error": str(e)}, status_code=502)


async def call_tool(request: Request) -> JSONResponse:
    assert ctx is not None
    if ctx.state.error:
        return JSONResponse({"error": ctx.state.error}, status_code=502)
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "请求体必须是 JSON"}, status_code=400)

    tool_name = body.get("name")
    if not tool_name or not isinstance(tool_name, str):
        return JSONResponse({"error": '需要字符串字段 "name"（工具名）'}, status_code=400)
    arguments = body.get("arguments")
    if arguments is not None and not isinstance(arguments, dict):
        return JSONResponse({"error": '"arguments" 必须是对象'}, status_code=400)
    server_q = body.get("server")
    if server_q is not None and not isinstance(server_q, str):
        return JSONResponse({"error": '"server" 必须是字符串'}, status_code=400)

    try:
        _, srv = ctx.state.resolve_server(server_q)

        async def run(session: ClientSession):
            res = await session.call_tool(tool_name, arguments or {})
            return _tool_result_to_json(res)

        result = await _with_session(srv, run)
        return JSONResponse(result)
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    except McpError as e:
        return JSONResponse({"error": str(e)}, status_code=502)
    except Exception as e:
        logger.exception("call_tool")
        return JSONResponse({"error": str(e)}, status_code=502)


app = Starlette(
    lifespan=lifespan,
    routes=[
        Route("/health", health, methods=["GET"]),
        Route("/servers", list_servers, methods=["GET"]),
        Route("/tools", list_tools, methods=["GET"]),
        Route("/tools/call", call_tool, methods=["POST"]),
        Route("/admin/refresh", admin_refresh, methods=["POST"]),
    ],
)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    host = os.environ.get("LISTEN_HOST", "127.0.0.1")
    port = int(os.environ.get("LISTEN_PORT", "1234"))
    import uvicorn

    uvicorn.run(
        "server:app",
        host=host,
        port=port,
        factory=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
