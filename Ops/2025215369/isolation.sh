#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/lib.sh"

# 防火墙规则
ETH_DEV="eth0"
ZONE="oam-prod"

# 启用访问控制
firewalld_enable() {
  # 检查 firewalld 是否可用
  if ! firewall-cmd --state >/dev/null 2>&1; then
    log "ERROR" "firewalld未运行或命令不可用"
    exit 1
  fi

  # 配置一个新的防火墙 zone
  firewall-cmd --permanent --new-zone="$ZONE" >/dev/null 2>&1
  # 设置 zone 的默认策略 DROP
  # 所有不匹配规则的流量 直接丢弃
  firewall-cmd --permanent --zone="$ZONE" --set-target=DROP
  firewall-cmd --permanent --zone="$ZONE" --add-interface="$ETH_DEV"

  # 允许访问 172.22.146.0/24
  firewall-cmd --permanent --zone="$ZONE" --add-rich-rule='rule family="ipv4" destination address="172.22.146.0/24" accept'
  # 允许访问 172.16.0.0/12
  firewall-cmd --permanent --zone="$ZONE" --add-rich-rule='rule family="ipv4" destination address="172.16.0.0/12" accept'

  # 重新加载防火墙配置
  firewall-cmd --reload
}

# 关闭访问控制
firewalld_disable() {
  # 从 防火墙zone 中解绑网卡eth0
  firewall-cmd --permanent --zone="$ZONE" --remove-interface="$ETH_DEV" >/dev/null 2>&1
  
  # 删除设置的防火墙规则
  firewall-cmd --permanent --zone="$ZONE" --remove-rich-rule='rule family="ipv4" destination address="172.22.146.0/24" accept' >/dev/null 2>&1
  firewall-cmd --permanent --zone="$ZONE" --remove-rich-rule='rule family="ipv4" destination address="172.16.0.0/12" accept' >/dev/null 2>&1
  # 删除防火墙zone
  firewall-cmd --permanent --delete-zone="$ZONE" >/dev/null 2>&1

  # 重新加载防火墙配置
  firewall-cmd --reload
}

# 启用隔离(调用)
enable_isolation() {
  log "INFO" "启用生产网络访问控制"
  firewalld_enable
  log "INFO" "访问控制已启用"
}

# 关闭隔离(调用)
disable_isolation() {
  log "INFO" "关闭生产网络访问控制"
  firewalld_disable
  log "INFO" "访问控制已关闭"
}

main() {
  require_root
  case "$1" in
    enable)
      enable_isolation
      ;;
    disable)
      disable_isolation
      ;;
    *)
      log "ERROR" "参数不合法"
      exit 1
      ;;
  esac
}

main "$@"
