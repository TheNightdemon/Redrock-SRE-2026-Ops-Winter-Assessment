from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db import execute, fetch_all, fetch_one

router = APIRouter()

class MonitorCreate(BaseModel):
    # 创建监控项
    name: str                                            # 监控项名称
    type: str = Field(pattern="^(http|tcp|ping|dns)$")   # 监控类型
    target: str                                          # 监控目标
    interval_seconds: int = 60                           # 检查间隔
    timeout_seconds: float = 5                           # 超时时间
    latency_threshold_ms: Optional[int] = None           # 延迟阈值
    enabled: bool = True                                 # 是否启用

class MonitorUpdate(BaseModel):
    # 更新监控项
    name: Optional[str] = None                                                  # 监控项名称
    type: Optional[str] = Field(default=None, pattern="^(http|tcp|ping|dns)$")  # 监控类型
    target: Optional[str] = None                                                # 监控目标
    interval_seconds: Optional[int] = None                                      # 检查间隔
    timeout_seconds: Optional[float] = None                                     # 超时时间
    latency_threshold_ms: Optional[int] = None                                  # 延迟阈值
    enabled: Optional[bool] = None                                              # 是否启用

@router.get("/api/monitors")
async def list_monitors():
    # 获取监控项列表
    return await fetch_all("SELECT * FROM monitors ORDER BY id DESC")

@router.post("/api/monitors")
async def create_monitor(payload: MonitorCreate):
    # 创建监控项
    created_at = datetime.now(timezone.utc).isoformat()
    monitor_id = await execute(
        """
        INSERT INTO monitors (name, type, target, interval_seconds, timeout_seconds,
                              latency_threshold_ms, enabled, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload.name,
            payload.type,
            payload.target,
            payload.interval_seconds,
            payload.timeout_seconds,
            payload.latency_threshold_ms,
            1 if payload.enabled else 0,
            created_at,
        ),
    )
    return await fetch_one("SELECT * FROM monitors WHERE id = ?", (monitor_id,))

@router.put("/api/monitors/{monitor_id}")
async def update_monitor(monitor_id: int, payload: MonitorUpdate):
    # 更新监控项
    existing = await fetch_one("SELECT * FROM monitors WHERE id = ?", (monitor_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="Monitor not found")

    updates = payload.dict(exclude_unset=True)
    if not updates:
        return existing

    columns = []
    values = []
    for key, value in updates.items():
        if key == "enabled":
            value = 1 if value else 0
        columns.append(f"{key} = ?")
        values.append(value)
    values.append(monitor_id)

    await execute(f"UPDATE monitors SET {', '.join(columns)} WHERE id = ?", tuple(values))
    return await fetch_one("SELECT * FROM monitors WHERE id = ?", (monitor_id,))

@router.delete("/api/monitors/{monitor_id}")
async def delete_monitor(monitor_id: int):
    # 删除监控项及其结果
    existing = await fetch_one("SELECT * FROM monitors WHERE id = ?", (monitor_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="Monitor not found")
    await execute("DELETE FROM monitors WHERE id = ?", (monitor_id,))
    await execute("DELETE FROM results WHERE monitor_id = ?", (monitor_id,))
    return {"ok": True}

@router.get("/api/monitors/{monitor_id}/results")
async def get_results(monitor_id: int, limit: int = 50):
    # 获取监控项最近结果
    return await fetch_all(
        "SELECT * FROM results WHERE monitor_id = ? ORDER BY id DESC LIMIT ?",
        (monitor_id, limit),
    )

@router.get("/api/status")
async def status_page_data():
    # 返回状态页上的数据
    monitors = await fetch_all("SELECT * FROM monitors WHERE enabled = 1 ORDER BY id DESC")
    results = await fetch_all(
        """
        SELECT r.* FROM results r
        INNER JOIN (
            SELECT monitor_id, MAX(id) AS max_id
            FROM results
            GROUP BY monitor_id
        ) latest ON r.id = latest.max_id
        """
    )
    # 返回监控项及其最新结果
    latest_map = {row["monitor_id"]: row for row in results}
    output = []
    for monitor in monitors:
        latest = latest_map.get(monitor["id"])
        output.append({
            "monitor": monitor,
            "latest": latest,
        })
    return output