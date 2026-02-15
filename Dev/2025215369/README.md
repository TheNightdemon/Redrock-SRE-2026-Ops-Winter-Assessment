# MonitorSystem

轻量级运维监控系统（Python/FastAPI）。支持 HTTP、TCP、Ping、DNS 监控，提供告警 Webhook、控制台与监控列表。

## 功能覆盖

- 监控能力：HTTP(s)、TCP、Ping、DNS
- 异常检测：状态码异常、延迟阈值、宕机检测
- 告警通知：Webhook
- 容器化：Dockerfile

## 监控面板展示

![](https://cloudflare-imgbed-dkw.pages.dev/file/1771115952932_PixPin_2026-02-15_08-38-43.png)



![](https://cloudflare-imgbed-dkw.pages.dev/file/1771115489261_image-20260215082842023.png)



## 快速开始（本地）

1. 安装依赖

```shell
pip install -r requirements.txt
```

2. 启动服务

```shell
python start.py
```

> start.py 会同时启动主服务（8000）与 Webhook 接收器（8001）。

3. 访问

- 控制台：http://localhost:8000/
- Webhook 面板：http://localhost:8001/

## Webhook 接收器

### 配置告警地址

配置环境变量`WEBHOOK_URL`-接收器地址 ，例如：

```shell
$env:WEBHOOK_URL="http://127.0.0.1:8001/webhook"
python start.py
```

### 使用

当监控触发告警时，主服务会向 `/webhook` 发送 POST 请求。接收器会在控制台打印收到的内容，并在页面展示错误告警。

访问接收器前端页面：

- http://localhost:8001/

## 环境变量

- `DATABASE_URL`：SQLite 文件路径（默认 ./monitor.db）
- `WEBHOOK_URL`：告警 Webhook 地址
- `CHECK_LOOP_INTERVAL_SECONDS`：后台循环间隔
- `DEFAULT_TIMEOUT_SECONDS`：默认超时时间

## Docker

Docker镜像已推送至GitHub Container Registry

```shell
docker pull ghcr.io/thenightdemon/monitorsystem:latest

docker run -p 8000:8000 -p 8001:8001 \
  -e WEBHOOK_URL="http://host.docker.internal:8001/webhook" \
  monitorsystem
  
> 容器内同时启动 8000（主服务）与 8001（Webhook 接收器）。
```

