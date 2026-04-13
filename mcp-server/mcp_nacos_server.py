#!/usr/bin/env python3
"""
基于 FastMCP 的 MCP Server，启动时向 Nacos **命名服务**注册实例，退出时注销。

与网关 `server.py`（从 Nacos 读 MCP 配置并代理）配合时，可将本服务暴露的 URL 写入
Nacos 配置中心的 `mcp-servers.json`，或通过命名发现后自行拼接 URL。

环境变量：
  NACOS_BASE          Nacos 地址，默认 http://localhost:8848
  NACOS_REGISTER_FAIL_OPEN  注册失败时仍启动 MCP（默认 false）；服务端返回 4xx/5xx 或网络错误时可用
  NACOS_SERVICE_NAME  注册的服务名，默认 mcp-demo
  NACOS_GROUP         分组，默认 DEFAULT_GROUP
  NACOS_NAMESPACE     命名空间 ID，留空为 public
  NACOS_EPHEMERAL     是否临时实例，默认 true（需心跳；为 false 时可不配心跳，依赖服务端策略）

  LISTEN_HOST / LISTEN_PORT  监听地址与端口（与 FASTMCP_* 二选一，本脚本优先读 LISTEN_*）
  FASTMCP_HOST / FASTMCP_PORT  FastMCP 监听（未设 LISTEN_* 时使用）

  REGISTER_IP         注册到 Nacos 的 IP（客户端可访问的地址）。未设置且监听 0.0.0.0 时尝试探测本机 IP。

  HEARTBEAT_INTERVAL  心跳间隔秒数，默认 5（仅 ephemeral=true 时使用）
  NACOS_REGISTER      是否向 Nacos 注册，默认 true；设为 false/0 则只启动 MCP（无 Nacos 时用）

传输方式由 MCP_TRANSPORT 指定：sse（默认）或 streamable-http。
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import socket
from contextlib import suppress
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger("mcp-nacos")


def _env_int(name: str, default: int) -> int:
    v = os.environ.get(name)
    if v is None or v == "":
        return default
    return int(v)


def _env_bool(name: str, default: bool) -> bool:
    v = os.environ.get(name)
    if v is None or v == "":
        return default
    return v.lower() in ("1", "true", "yes", "on")


def _listen_host() -> str:
    return os.environ.get("LISTEN_HOST") or os.environ.get("FASTMCP_HOST", "127.0.0.1")


def _listen_port() -> int:
    if os.environ.get("LISTEN_PORT"):
        return int(os.environ["LISTEN_PORT"])
    return _env_int("FASTMCP_PORT", 8765)


def _guess_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def resolve_register_ip(listen_host: str) -> str:
    explicit = os.environ.get("REGISTER_IP", "").strip()
    if explicit:
        return explicit
    if listen_host not in ("0.0.0.0", "::", "[::]"):
        return listen_host
    return _guess_local_ip()


def build_mcp_public_url(
    register_ip: str,
    port: int,
    mount_path: str,
    transport: str,
) -> str:
    mount = mount_path.rstrip("/") or ""
    if transport in ("http", "streamable_http", "streamable-http"):
        path = os.environ.get("FASTMCP_STREAMABLE_HTTP_PATH", "/mcp")
        return f"http://{register_ip}:{port}{mount}{path}"
    sse_path = os.environ.get("FASTMCP_SSE_PATH", "/sse")
    return f"http://{register_ip}:{port}{mount}{sse_path}"


class NacosNaming:
    def __init__(
        self,
        base: str,
        service_name: str,
        group: str,
        namespace: str,
        ip: str,
        port: int,
        ephemeral: bool,
        metadata: dict[str, str],
    ) -> None:
        self.base = base.rstrip("/")
        self.service_name = service_name
        self.group = group
        self.namespace = namespace
        self.ip = ip
        self.port = port
        self.ephemeral = ephemeral
        self.metadata = metadata
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=15.0)
        return self._client

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _common_params(self) -> dict[str, Any]:
        p: dict[str, Any] = {
            "serviceName": self.service_name,
            "ip": self.ip,
            "port": str(self.port),
            "groupName": self.group,
            "ephemeral": str(self.ephemeral).lower(),
        }
        if self.namespace:
            p["namespaceId"] = self.namespace
        return p

    async def register(self) -> None:
        client = await self._get_client()
        params = self._common_params()
        params["weight"] = os.environ.get("NACOS_WEIGHT", "1")
        params["enabled"] = "true"
        params["healthy"] = "true"
        if self.metadata:
            params["metadata"] = json.dumps(self.metadata, ensure_ascii=False)
        url = f"{self.base}/nacos/v1/ns/instance"
        r = await client.post(url, data=params)
        r.raise_for_status()
        body = r.text.strip().lower()
        if body and body not in ("ok", "true"):
            raise RuntimeError(f"Nacos 注册未返回 ok: {r.text!r}")

    async def deregister(self) -> None:
        client = await self._get_client()
        params = self._common_params()
        url = f"{self.base}/nacos/v1/ns/instance"
        r = await client.request("DELETE", url, params=params)
        if r.status_code not in (200, 204):
            r.raise_for_status()

    async def beat(self) -> None:
        client = await self._get_client()
        params = self._common_params()
        url = f"{self.base}/nacos/v1/ns/instance/beat"
        r = await client.put(url, params=params)
        if r.status_code != 200:
            logger.warning("Nacos 心跳异常: %s %s", r.status_code, r.text)


async def heartbeat_loop(naming: NacosNaming, interval: float) -> None:
    while True:
        await asyncio.sleep(interval)
        with suppress(Exception):
            await naming.beat()


def build_app() -> FastMCP:
    host = _listen_host()
    port = _listen_port()

    return FastMCP(
        "mcp-nacos-demo",
        instructions="示例 MCP 服务，实例已注册到 Nacos 命名服务。",
        host=host,
        port=port,
    )


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    def ping() -> str:
        """健康检查，返回 pong。"""
        return "pong"

    @mcp.tool()
    def echo(message: str) -> str:
        """回显传入的文本。"""
        return message


async def run() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    transport = (os.environ.get("MCP_TRANSPORT") or "sse").lower().replace("_", "-")
    if transport not in ("sse", "streamable-http"):
        raise ValueError("MCP_TRANSPORT 应为 sse 或 streamable-http")

    mcp = build_app()
    register_tools(mcp)

    listen_host = _listen_host()
    listen_port = _listen_port()
    reg_ip = resolve_register_ip(listen_host)
    mount_path = os.environ.get("FASTMCP_MOUNT_PATH", "/")

    meta_transport = "streamable_http" if transport == "streamable-http" else "sse"
    public_url = build_mcp_public_url(reg_ip, listen_port, mount_path, meta_transport)

    nacos_base = os.environ.get("NACOS_BASE", "http://localhost:8848")
    service_name = os.environ.get("NACOS_SERVICE_NAME", "mcp-demo")
    group = os.environ.get("NACOS_GROUP", "DEFAULT_GROUP")
    namespace = os.environ.get("NACOS_NAMESPACE", "")
    ephemeral = _env_bool("NACOS_EPHEMERAL", True)

    metadata = {
        "mcp.transport": meta_transport,
        "mcp.url": public_url,
        "preserved.register.source": "PYTHON_MCP",
    }
    extra = os.environ.get("NACOS_METADATA_JSON")
    if extra:
        try:
            metadata.update(json.loads(extra))
        except json.JSONDecodeError as e:
            raise ValueError("NACOS_METADATA_JSON 必须是 JSON 对象") from e

    do_nacos = _env_bool("NACOS_REGISTER", True)
    naming: NacosNaming | None = None
    if do_nacos:
        naming = NacosNaming(
            base=nacos_base,
            service_name=service_name,
            group=group,
            namespace=namespace,
            ip=reg_ip,
            port=listen_port,
            ephemeral=ephemeral,
            metadata=metadata,
        )

    hb_task: asyncio.Task[None] | None = None
    interval = float(os.environ.get("HEARTBEAT_INTERVAL", "5"))
    fail_open = _env_bool("NACOS_REGISTER_FAIL_OPEN", False)
    registered = False

    try:
        if naming is not None:
            try:
                await naming.register()
                registered = True
            except httpx.HTTPError as e:
                await naming.aclose()
                naming = None
                if fail_open:
                    logger.warning("Nacos 注册失败，仍启动 MCP（NACOS_REGISTER_FAIL_OPEN=true）: %s", e)
                    logger.info("MCP: %s", public_url)
                else:
                    raise
            if naming is not None and registered:
                logger.info(
                    "已注册 Nacos: service=%s ip=%s port=%s url=%s",
                    service_name,
                    reg_ip,
                    listen_port,
                    public_url,
                )
                if ephemeral:
                    hb_task = asyncio.create_task(heartbeat_loop(naming, interval))
                    logger.info("已启动 Nacos 心跳，间隔 %.1fs", interval)
        else:
            logger.info("已跳过 Nacos 注册（NACOS_REGISTER=false），MCP: %s", public_url)

        import uvicorn

        if transport == "sse":
            starlette_app = mcp.sse_app()
        else:
            starlette_app = mcp.streamable_http_app()

        config = uvicorn.Config(
            starlette_app,
            host=listen_host,
            port=listen_port,
            log_level=os.environ.get("FASTMCP_LOG_LEVEL", "info").lower(),
        )
        server = uvicorn.Server(config)
        await server.serve()
    finally:
        if hb_task is not None:
            hb_task.cancel()
            with suppress(asyncio.CancelledError):
                await hb_task
        if naming is not None:
            if registered:
                with suppress(Exception):
                    await naming.deregister()
                    logger.info("已从 Nacos 注销实例")
            await naming.aclose()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
