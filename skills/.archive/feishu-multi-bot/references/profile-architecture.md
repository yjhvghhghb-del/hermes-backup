# Profile Architecture (as of 2026.08.15)

## Active Profiles (2026.08.25)

| Profile | Platform | app_id | Model | Status | Notes |
|---------|----------|--------|-------|--------|-------|
| `default` | Telegram + QQ | — | MiniMax-M2.7 | ✅ multiplexed | home_channel=胖蝦球 |
| `geekwife` | Telegram | — | MiniMax-M2.7 | ✅ multiplexed | token: 8637317610 |
| `siliconflow` | Telegram | — | Qwen/Qwen3-14B | ✅ multiplexed | token: 8363232963 |
| `licai` | 飞书 | `cli_aafa2c6a83b85bee` | MiniMax-M2.7 | ✅ multiplexed | 理财Bot |
| `wenyu` | 飞书 | `cli_aae7a3ad78b8dbe3` | **MiniMax-M2.7** | ✅ multiplexed | 文娱bot（原Groq llama-3.3） |
| `libai` | 飞书 | `cli_aafa2c6a83b85bee` | — | ❌ blocked | 与licai同app_id |
| `cutegirl` | 飞书 | `cli_aae7a3ad78b8dbe3` | — | ❌ blocked | 与wenyu同app_id |

## app_id Collision Groups

```
Group A: cli_aae7a0320738dbeb → default (飞书DM凭证，但主bot走QQ+Telegram)
Group B: cli_aafa2c6a83b85bee → libai / licai（二选一）
Group C: cli_aae7a3ad78b8dbe3 → cutegirl / wenyu（二选一）
```

**当前模式 (2026.08.25):** `gateway.multiplex_profiles: true`，所有 profiles 跑在单一 gateway 进程内，不再需要分别启动。只需：
```bash
hermes gateway  # 单进程，连接所有7个profiles
```

## Startup Commands (2026.08.25)

```bash
# 标准启动（multiplexed 单 gateway 模式）
pkill -f "hermes gateway" 2>/dev/null; sleep 2
hermes gateway 2>&1 &

# 验证所有连接
grep "feishu.*connected.*profile" ~/.hermes/logs/gateway.log
```

## Log Locations

```
所有profiles: ~/.hermes/logs/gateway.log（统一日志）
           ~/.hermes/profiles/<name>/logs/gateway.log（各profile独立日志，等效）
```

## Diagnostic Commands

```bash
# 查 gateway 进程（最可靠）
ps aux | grep 'hermes gateway' | grep -v grep

# 查飞书连接状态
grep "feishu.*connected" ~/.hermes/logs/gateway.log | grep -E 'licai|wenyu|libai|cutegirl'

# 查最近消息（看是否在响应）
grep "inbound message.*feishu" ~/.hermes/logs/gateway.log | tail -5

# 查 auth 错误
grep "minimax.*auth\|auth.*minim" ~/.hermes/logs/gateway.log | tail -5
```
