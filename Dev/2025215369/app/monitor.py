import asyncio
import time
from typing import Tuple, Optional

import dns.resolver
import httpx
from ping3 import ping

from app.config import DEFAULT_TIMEOUT_SECONDS

async def check_http(target: str, timeout: float, expected_status: Optional[int]) -> Tuple[str, int, Optional[int], Optional[str]]:
    # HTTP 监控
    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            # 检测网站可用性、响应时间、状态码
            response = await client.get(target)
            latency_ms = int((time.monotonic() - start) * 1000)
            status_code = response.status_code
            if expected_status and status_code != expected_status:
                return "down", latency_ms, status_code, f"status {status_code} != {expected_status}"
            if status_code >= 400:
                return "down", latency_ms, status_code, f"status {status_code}"
            return "up", latency_ms, status_code, None
    except Exception as exc:
        latency_ms = int((time.monotonic() - start) * 1000)
        return "down", latency_ms, None, str(exc)

async def check_tcp(target: str, timeout: float) -> Tuple[str, int, Optional[int], Optional[str]]:
    # TCP 端口监控
    start = time.monotonic()
    # 检查 TCP 端口连通性
    host, port_str = target.split(":", 1)
    port = int(port_str)
    try:
        await asyncio.wait_for(asyncio.open_connection(host, port), timeout=timeout)
        latency_ms = int((time.monotonic() - start) * 1000)
        return "up", latency_ms, None, None
    except Exception as exc:
        latency_ms = int((time.monotonic() - start) * 1000)
        return "down", latency_ms, None, str(exc)

async def check_ping(target: str, timeout: float) -> Tuple[str, int, Optional[int], Optional[str]]:
    # ICMP Ping 监控
    start = time.monotonic()
    try:
        # ICMP ping 检测网络连通性
        latency = await asyncio.to_thread(ping, target, timeout=timeout, unit="ms")
        if latency is None:
            return "down", int((time.monotonic() - start) * 1000), None, "timeout"
        return "up", int(latency), None, None
    except Exception as exc:
        latency_ms = int((time.monotonic() - start) * 1000)
        return "down", latency_ms, None, str(exc)

async def check_dns(target: str, record_type: str, timeout: float) -> Tuple[str, int, Optional[int], Optional[str]]:
    # DNS 解析监控
    start = time.monotonic()
    resolver = dns.resolver.Resolver()
    resolver.lifetime = timeout
    try:
        # 验证DNS解析是否正常
        answers = await asyncio.to_thread(resolver.resolve, target, record_type)
        if not answers:
            return "down", int((time.monotonic() - start) * 1000), None, "no records"
        return "up", int((time.monotonic() - start) * 1000), None, None
    except Exception as exc:
        latency_ms = int((time.monotonic() - start) * 1000)
        return "down", latency_ms, None, str(exc)

async def run_check(monitor: dict) -> Tuple[str, int, Optional[int], Optional[str]]:
    # 根据监控类型进行监控
    monitor_type = monitor["type"]
    # 获取超时时间，优先使用监控项配置的超时时间，否则使用默认值
    timeout = monitor.get("timeout_seconds") or DEFAULT_TIMEOUT_SECONDS

    if monitor_type == "http":
        return await check_http(monitor["target"], timeout, monitor.get("expected_status"))
    if monitor_type == "tcp":
        return await check_tcp(monitor["target"], timeout)
    if monitor_type == "ping":
        return await check_ping(monitor["target"], timeout)
    if monitor_type == "dns":
        record_type = monitor.get("dns_record") or "A"
        return await check_dns(monitor["target"], record_type, timeout)

    return "down", 0, None, f"unknown type {monitor_type}"
