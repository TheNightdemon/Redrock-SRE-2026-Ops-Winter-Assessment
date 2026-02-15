import asyncio
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.alerts import is_alert
from app.config import CHECK_LOOP_INTERVAL_SECONDS
from app.db import execute, fetch_all, fetch_one, init_db
from app.monitor import run_check
from app.api import router

BASE_DIR = Path(__file__).resolve().parent.parent  # 项目根目录
STATIC_DIR = BASE_DIR / "static"  # 静态文件目录

# FastAPI
app = FastAPI(title="MonitorSystem", version="0.1.0")
app.include_router(router)

# 静态资源挂载
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def index():
    # 控制台首页
    return FileResponse(STATIC_DIR / "index.html")

async def record_result(monitor: dict, status: str, latency_ms: int | None, status_code: int | None, error: str | None):
    # 写入监控结果
    checked_at = datetime.now(timezone.utc).isoformat()
    await execute(
        """
        INSERT INTO results (monitor_id, status, latency_ms, status_code, error, checked_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            monitor["id"],  # 监控项ID
            status,         # 状态
            latency_ms,     # 延迟
            status_code,    # HTTP状态码(非HTTP为None)
            error,          # 错误信息
            checked_at,     # 检查时间
        ),
    )

async def is_due(monitor: dict) -> bool:
    # 判断是否到达检查时间
    last = await fetch_one(
        "SELECT checked_at FROM results WHERE monitor_id = ? ORDER BY id DESC LIMIT 1",
        (monitor["id"],),
    )
    if not last:
        return True  # 没有任何记录，需要检测
    last_time = datetime.fromisoformat(last["checked_at"])
    delta = datetime.now(timezone.utc) - last_time
    # 如果距离上次检查时间超过间隔时间，需要检测
    return delta.total_seconds() >= monitor["interval_seconds"]

async def check_loop() -> None:
    # 后台监控的主循环
    # 取出启用的监控项 → 判断是否到期 → 执行检测 → 记录结果并警告 → 休眠一段时间
    while True:
        monitors = await fetch_all("SELECT * FROM monitors WHERE enabled = 1")
        for monitor in monitors:
            if await is_due(monitor):
                status, latency_ms, status_code, error = await run_check(monitor)
                await record_result(monitor, status, latency_ms, status_code, error)
                await is_alert(monitor, status, latency_ms, status_code, error)
        await asyncio.sleep(CHECK_LOOP_INTERVAL_SECONDS)

@app.on_event("startup")
async def on_startup() -> None:
    # 初始化数据库并启动检查任务
    await init_db()
    asyncio.create_task(check_loop())
