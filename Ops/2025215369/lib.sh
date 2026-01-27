#!/bin/bash

# 日志文件与保存当前网络状态文件的位置
LOG_FILE="/log/netctl.log"
STATE_FILE="/var/netctl_state.env"

# 日志输出
log() {
  # shift: 把位置参数往左挪一位 丢掉 $1
  # msg = 当前所有位置参数拼成一个字符串
  local level="$1"; shift
  local msg="$*"
  local ts
  ts="$(date '+%Y-%m-%d %H:%M:%S')"
  # 同时写入文件与标准输出
  mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null
  echo "[$ts] [$level] $msg" | tee -a "$LOG_FILE" >/dev/null
}

# 运行权限检查
require_root() {
  if [[ $EUID -ne 0 ]]; then
    log "ERROR" "必须以root权限运行"
    exit 1
  fi
}

# 保存当前网络状态，为回滚使用
save_state() {
  local mode="unknown"
  local ipaddr=""
  local gateway=""
  local dns=""
  local prev_conn=""
  local prev_method=""

  # 找出 eth0 当前正在使用的连接
  prev_conn="$(nmcli -t -f NAME,DEVICE,STATE con show --active | awk -F: '$2=="eth0" && $3=="activated" {print $1; exit}')"
  if [[ -n "$prev_conn" ]]; then
    prev_method="$(nmcli -t -f ipv4.method con show "$prev_conn" | awk -F: '{print $2}')"
    # 判断是 DHCP模式 还是 静态IP模式
    if [[ "$prev_method" == "auto" ]]; then  # DHCP模式
      mode="dhcp"
    elif [[ "$prev_method" == "manual" ]]; then  # 静态IP模式
      mode="static"
    fi
    ipaddr="$(nmcli -t -f ipv4.addresses con show "$prev_conn" | awk -F: '{print $2}')"
    gateway="$(nmcli -t -f ipv4.gateway con show "$prev_conn" | awk -F: '{print $2}')"
    dns="$(nmcli -t -f ipv4.dns con show "$prev_conn" | awk -F: '{print $2}')"
  else
    log "WARN" "未找到eth0活动连接，网络状态可能不完整"
  fi

  cat >"$STATE_FILE" <<EOF
PREV_MODE="$mode"
PREV_IPADDR="$ipaddr"
PREV_GATEWAY="$gateway"
PREV_DNS="$dns"
PREV_CONN="$prev_conn"
PREV_METHOD="$prev_method"
EOF

  log "INFO" "已保存当前网络状态到 $STATE_FILE"
}

# 加载上次保存的网络状态
load_state() {
  if [[ -f "$STATE_FILE" ]]; then
    # 加载上次保存的网络状态
    source "$STATE_FILE"
    return 0
  fi
  return 1
}
