#!/bin/bash

# 脚本目录
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 使用说明
usage() {
  cat <<EOF
用法: $0 {dhcp|static|rollback|isolation-on|isolation-off|monitor-start|monitor-stop|monitor-status}
  dhcp            切换到办公网络(DHCP)
  static          切换到生产网络(静态IP)
  rollback        回滚到上一次配置
  isolation-on    启用生产网络访问控制
  isolation-off   关闭生产网络访问控制
  monitor-start   启动公网检测
  monitor-stop    停止公网检测
  monitor-status  查看检测状态
EOF
}

case "$1" in
  dhcp)
    "$DIR/config.sh" dhcp
    ;;
  static)
    "$DIR/config.sh" static
    ;;
  rollback)
    "$DIR/config.sh" rollback
    ;;
  isolation-on)
    "$DIR/isolation.sh" enable
    ;;
  isolation-off)
    "$DIR/isolation.sh" disable
    ;;
  monitor-start)
    "$DIR/monitor.sh" start
    ;;
  monitor-stop)
    "$DIR/monitor.sh" stop
    ;;
  monitor-status)
    "$DIR/monitor.sh" status
    ;;
  *)
    usage
    exit 1
    ;;
esac
