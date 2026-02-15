from collections import deque
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="MonitorSystem Webhook", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

ALERTS = deque(maxlen=200)

@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/api/alerts")
async def list_alerts():
    return list(ALERTS)

@app.post("/webhook")
async def receive_webhook(request: Request):
    payload = await request.json()
    received_at = datetime.now(timezone.utc).isoformat()
    ALERTS.appendleft({"received_at": received_at, "payload": payload})
    print(f"[{received_at}] webhook received: {payload}")
    return {"ok": True, "received_at": received_at}
