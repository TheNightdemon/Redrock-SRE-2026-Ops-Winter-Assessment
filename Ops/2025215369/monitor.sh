#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/lib.sh"

# 监控参数
PID_FILE="/var/net_monitor.pid"
CHECK_HOST="114.114.114.114"
CHECK_INTERVAL=60

# 检测公网可达性
check_public() {
  ping -c 1 -W 2 -I eth0 "$CHECK_HOST" >/dev/null 2>&1
}

# 监控循环
run_loop() {
  log "INFO" "开始监控生产网络"
  trap 'rm -f "$PID_FILE"' EXIT
  while true; do
    if check_public; then
      # 检测到公网可达
      log "WARN" "检测到公网可达，自动切换回办公网络"
      "$DIR/networkctl.sh" dhcp
      log "INFO" "已切换到办公网络，停止监控"
      break
    else
      # 公网不可达
      log "INFO" "公网不可达"
    fi
    sleep "$CHECK_INTERVAL"
  done
}

# 启动后台监控
start() {
  nohup "$0" run >/dev/null 2>&1 &
  echo $! >"$PID_FILE"
  log "INFO" "监控已启动，PID=$(cat "$PID_FILE")"
}

# 停止后台监控
stop() {
  # 关闭监控进程
  if [[ -f "$PID_FILE" ]]; then
    kill "$(cat "$PID_FILE")"
  fi
  # 删除PID文件
  rm -f "$PID_FILE"
  log "INFO" "监控已停止"
}

# 检查运行状态
status() {
  # 检查PID文件及进程状态
  if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "running (PID=$(cat "$PID_FILE"))"
  else
    echo "stopped"
  fi
}

main() {
  require_root
  case "$1" in
    start)
      start
      ;;
    stop)
      stop
      ;;
    status)
      status
      ;;
    run)
      run_loop
      ;;
    *)
      log "ERROR" "参数不合法"
      exit 1
      ;;
  esac
}

main "$@"
