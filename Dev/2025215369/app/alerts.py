from typing import Optional
import httpx
from app.config import WEBHOOK_URL

async def send_webhook(payload: dict) -> None:
    # 发送 Webhook 警告
    if not WEBHOOK_URL:
        return
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            await client.post(WEBHOOK_URL, json=payload)
    except Exception:
        return

async def is_alert(monitor: dict, status: str, latency_ms: Optional[int], status_code: Optional[int], error: Optional[str]) -> None:
    # 根据状态与阈值判断是否触发警告
    if status == "up" and not error:
        if monitor.get("latency_threshold_ms") and latency_ms:
            if latency_ms <= monitor["latency_threshold_ms"]:
                # 延迟未超过阈值，不警告
                return
        else:
            # 状态正常且无延迟阈值，不警告
            return

    # 状态错误或超出阈值，构造警告并发送
    payload = {
        "monitor_id": monitor["id"],  # 监控项ID
        "name": monitor["name"],      # 监控项名称
        "type": monitor["type"],      # 监控类型
        "target": monitor["target"],  # 监控目标
        "status": status,             # 状态
        "latency_ms": latency_ms,     # 延迟
        "status_code": status_code,   # HTTP状态码(非HTTP为None)
        "error": error,               # 错误信息
    }
    await send_webhook(payload)
