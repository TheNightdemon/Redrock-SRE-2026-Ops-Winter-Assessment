#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/lib.sh"

# 生产网络静态配置参数
ETH_DEV="eth0"
STATIC_IP="172.22.146.150/24"
STATIC_GW="172.22.146.1"
STATIC_DNS1="172.22.146.53"
STATIC_DNS2="172.22.146.54"

# 设置DHCP模式（办公网络）
set_dhcp() {
  log "INFO" "切换到DHCP模式"
  local con
  con="$(nmcli -t -f NAME,DEVICE con show --active | awk -F: '$2=="'$ETH_DEV'" {print $1; exit}')"
  if [[ -z "$con" ]]; then
    con="$(nmcli -t -f NAME,DEVICE con show | awk -F: '$2=="'$ETH_DEV'" {print $1; exit}')"
  fi
  if [[ -z "$con" ]]; then
    con="oam-$ETH_DEV"
    nmcli con add type ethernet ifname "$ETH_DEV" con-name "$con" >/dev/null
  fi
  nmcli con modify "$con" ipv4.method auto ipv4.addresses "" ipv4.gateway "" ipv4.dns ""
  nmcli con up "$con"
  log "INFO" "DHCP配置完成"
}

# 设置静态IP模式（生产网络）
set_static() {
  local ip="${1:-$STATIC_IP}"
  local gw="${2:-$STATIC_GW}"
  local dns1="${3:-$STATIC_DNS1}"
  local dns2="${4:-$STATIC_DNS2}"

  log "INFO" "切换到静态IP模式: $ip"
  local con
  con="$(nmcli -t -f NAME,DEVICE con show --active | awk -F: '$2=="'$ETH_DEV'" {print $1; exit}')"
  if [[ -z "$con" ]]; then
    con="$(nmcli -t -f NAME,DEVICE con show | awk -F: '$2=="'$ETH_DEV'" {print $1; exit}')"
  fi
  if [[ -z "$con" ]]; then
    con="oam-$ETH_DEV"
    nmcli con add type ethernet ifname "$ETH_DEV" con-name "$con" >/dev/null
  fi
  nmcli con modify "$con" ipv4.method manual ipv4.addresses "$ip" ipv4.gateway "$gw" ipv4.dns "$dns1 $dns2"
  nmcli con up "$con"
  log "INFO" "静态IP配置完成"
}

# 回滚到上一配置
rollback() {
  if ! load_state; then
    log "ERROR" "未找到可回滚状态"
    exit 1
  fi

  log "INFO" "回滚到上一次配置: $PREV_MODE"
  if [[ -n "${PREV_CONN:-}" ]]; then
    nmcli con up "$PREV_CONN" || true
    log "INFO" "已恢复连接 $PREV_CONN"
    exit 0
  fi

  case "${PREV_MODE:-unknown}" in
    dhcp)
      set_dhcp
      ;;
    static)
      local dns_line dns1 dns2
      dns_line="${PREV_DNS:-$STATIC_DNS1 $STATIC_DNS2}"
      dns_line="${dns_line//,/ }"
      read -r dns1 dns2 <<<"$dns_line"
      set_static "${PREV_IPADDR:-$STATIC_IP}" "${PREV_GATEWAY:-$STATIC_GW}" "${dns1:-$STATIC_DNS1}" "${dns2:-$STATIC_DNS2}"
      ;;
    *)
      log "WARN" "无法识别上一次配置，未执行回滚"
      exit 1
      ;;
  esac
}

main() {
  require_root
  case "${1:-}" in
    dhcp)
      save_state
      set_dhcp
      ;;
    static)
      save_state
      set_static
      ;;
    rollback)
      rollback
      ;;
    *)
      log "ERROR" "参数不合法"
      exit 1
      ;;
  esac
}

main "$@"
