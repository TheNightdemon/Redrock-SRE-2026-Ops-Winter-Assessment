import aiosqlite
from app.config import DATABASE_URL

# SQLite 文件路径
DB_PATH = DATABASE_URL.removeprefix("sqlite:///")

# 数据库表结构
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS monitors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    target TEXT NOT NULL,
    interval_seconds INTEGER NOT NULL DEFAULT 60,
    timeout_seconds REAL NOT NULL DEFAULT 5,
    latency_threshold_ms INTEGER,
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    monitor_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    latency_ms INTEGER,
    status_code INTEGER,
    error TEXT,
    checked_at TEXT NOT NULL,
    FOREIGN KEY(monitor_id) REFERENCES monitors(id)
);
"""

async def init_db() -> None:
    # 初始化数据库表结构
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA_SQL)
        await db.commit()

async def fetch_all(query: str, params: tuple = ()):
    # 查询多行结果并转为 dict 列表
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def fetch_one(query: str, params: tuple = ()):
    # 查询单行结果并转为 dict
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, params) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def execute(query: str, params: tuple = ()):
    # 执行写入语句并返回最后插入的id
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(query, params)
        await db.commit()
        return cursor.lastrowid
