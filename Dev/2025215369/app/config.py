import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据库连接地址（SQLite）
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'monitor.db')}")
# 告警 Webhook 地址
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
# 后台循环检查间隔
CHECK_LOOP_INTERVAL_SECONDS = int(os.getenv("CHECK_LOOP_INTERVAL_SECONDS", "5"))
# 默认请求超时
DEFAULT_TIMEOUT_SECONDS = float(os.getenv("DEFAULT_TIMEOUT_SECONDS", "5"))
