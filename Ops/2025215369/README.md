# 网络配置与隔离脚本说明

## 目录结构
- lib.sh：日志、网络状态的保存/加载
- config.sh：DHCP/静态IP切换与回滚
- isolation.sh：生产网络访问控制
- monitor.sh：生产网络下，检测公网是否可达
- networkctl.sh：统一脚本入口

## 依赖说明
- NetworkManager（`nmcli`）
- 防火墙使用 `firewalld`

## 使用方法

```bash
sudo ./networkctl.sh dhcp
sudo ./networkctl.sh static
sudo ./networkctl.sh rollback
sudo ./networkctl.sh isolation-on
sudo ./networkctl.sh isolation-off
sudo ./networkctl.sh monitor-start
sudo ./networkctl.sh monitor-stop
sudo ./networkctl.sh monitor-status
```

## 生产网络参数
- 网卡：eth0
- IP：172.22.146.150/24
- 网关：172.22.146.1
- DNS：172.22.146.53、172.22.146.54

