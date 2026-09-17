# 飞书多Bot并发冲突诊断

## 症状
启动多个飞书 bot 时，日志出现：
```
Another local Hermes gateway is already using this Feishu app_id (PID XXXX)
```
该 bot 的 gateway 会立即退出（exit cleanly）。

## 根因
同一 `app_id` 的飞书 WebSocket 连接只能有一个。Hermes 不做端口隔离，直接共享同一个飞书 WebSocket 客户端。

## 已知冲突组合（2026-08-29）
| app_id | Profile A | Profile B | 同时只能跑1个 |
|--------|-----------|-----------|-------------|
| `cli_aae7a3ad78b8dbe3` | wenyu | cutegirl | ✓ |
| `cli_aafa2c6a83b85bee` | licai | libai | ✓ |

## 排查命令
```bash
# 看哪个 profile 在用哪个 app_id
grep -A5 'feishu\|app_id' ~/.hermes/profiles/*/config.yaml

# 看 gateway 状态
hermes gateway status

# 看实时日志
tail -f ~/.hermes/profiles/<profile>/gateway.log
```

## 解决方案
跑哪个就 kill 掉冲突的那个：
```bash
kill -9 <冲突PID>
nohup hermes --profile <wanted> gateway run > ~/.hermes/profiles/<wanted>/gateway.log 2>&1 &
```
