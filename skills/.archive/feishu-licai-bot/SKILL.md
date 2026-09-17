---
name: feishu-licai-bot
description: 理财Bot (licai/libai profile) 启动、排错、SSL断开修复、群里无响应诊断。
tags: [feishu, licai, libai, 理财]
---

# 飞书理财Bot

## 基本信息
- **Profile**: `~/.hermes/profiles/licai/`
- **App ID**: `cli_aafa2c6a83b85bee`
- **App Secret**: `<LARK_SECRET_EXAMPLE>`
- **Gateway**: `hermes --profile licai serve`（multiplexed 模式，注册到主 gateway 9119 端口）
- **日志**: `~/.hermes/profiles/licai/logs/gateway.log`
### .env 文件（重要！每个 profile 必须有自己专属的）
licai 的 `.env` 必须包含该 bot 自己的飞书凭证和用户白名单，不能从其他 profile 复制：

```
# ~/.hermes/profiles/licai/.env
MINIMAX_CN_API_KEY=sk-cp-K9L_eq3zCw9gn1y4dA48fEjdlsvQiwzN21P8b9Te2sKwdXCsfLwQS3oR941l6WvSVGNmH2qSQZRH3_xImS3dRH3JSOGVBocYqwhd3fGx9tES60hqSXXopK4
FEISHU_APP_ID=cli_aafa2c6a83b85bee
FEISHU_APP_SECRET=<LARK_SECRET>
FEISHU_ALLOWED_USERS=ou_2fcb5a59369405d74cf386b349aff96c,ou_a023ae4173052b881d472190d32065e2
FEISHU_GROUP_ALLOWED_USERS=ou_2fcb5a59369405d74cf386b349aff96c,ou_a023ae4173052b881d472190d32065e2
```

⚠️ 如果复用了 default 的 `.env`（含 app_id `cli_aae7a0320738dbeb`），会出现"提供商身份验证失败"——因为 app_id 与实际连接的 bot 不符。Bot 能连上飞书 WebSocket，但模型请求被拒。

**症状**：`hermes gateway list` 显示 ✓ feishu connected，但发消息后立即报"提供商身份验证失败"。
## ⚠️ 重启限制：不能从 gateway 内部杀自己
gateway 进程收到 SIGTERM 会同时杀掉所有子进程（包括启动新进程的 shell），所以：
- ❌ `terminal()` 里直接 `pkill hermes` — 被自己拦截，命令还没跑完进程就死了
- ❌ `execute_code` 里 `subprocess.run("pkill ...") ` — 同样被 SIGTERM 拦截
- ❌ `cronjob` 里放 `pkill -f "hermes gateway"` — cron 在 gateway 内部运行，同样会被杀
- ✅ **正确做法：从另一个 Termux 窗口手动执行，或者在主机层面用 `nohup` 独立跑**

**⚠️ Command form: `gateway run`, NOT `serve`!**
`hermes --profile <name> serve` starts only the web dashboard (port 9119), NOT the bot. Always use `hermes --profile <name> gateway run`.

**Profile 启动命令速查**
| Profile | 命令 | 平台 |
|---------|------|------|
| default | `hermes gateway run` | - |
| cutegirl | `hermes --profile cutegirl gateway run` | 飞书 |
| geekwife | `hermes --profile geekwife gateway run` | Telegram |
| libai | `hermes --profile libai gateway run` | 飞书 |
| licai | `hermes --profile licai gateway run` | 飞书 |
| siliconflow | `hermes --profile siliconflow gateway run` | Telegram |
| wenyu | `hermes --profile wenyu gateway run` | 飞书 |

**启动/重启（通用规则）**
```bash
# 查看所有 profile 的 gateway 状态（参考 — 可能有误）
hermes gateway list

# 查看哪个 bot 在跑（最可靠）
ps aux | grep hermes | grep -v grep

# 默认 profile 启动
hermes gateway run

# 指定 profile 启动（所有非 default profile 必须这样）
hermes --profile <name> gateway run

# 重启（先杀后启）— 必须从另一个终端窗口执行，不能从 gateway 内部
pkill -f "hermes.*profile/<name>" && sleep 2 && hermes --profile <name> gateway run
```

## 配对审批（新用户首次使用）
每个 profile 的审批码需要用 `--profile` 指定，否则会找不到：
```bash
# 查看待审批
hermes --profile <name> pairing list

# 审批（用 request-id，不是配对码）
hermes --profile <name> pairing approve feishu <request-id>
```

审批后，还需要在 config.yaml 两处加入用户的 open_id 才能在群里发言（见下一节）。

## 飞书 access control 架构（重要！）

飞书 adapter **不自己执行白名单**——它没有实现 `enforces_own_access_policy`，所以 config.yaml 里的 `allowed_group_users`、`group_rules`、`allow_from` 对飞书**完全无效**！

飞书的白名单必须通过环境变量配置：

```bash
# ~/.hermes/profiles/<name>/.env
FEISHU_ALLOWED_USERS=ou_xxx1,ou_xxx2        # DM 白名单
FEISHU_GROUP_ALLOWED_USERS=ou_xxx1,ou_xxx2  # 群内发言白名单
```

**DM 白名单字段演进**（已废弃的写法，不要用）：
- ❌ `dm_policy: allowlist` — 单独写无效
- ❌ `dm_whitelist: [...]` — 字段名不对
- ❌ `allowed_dm_users: [...]` — 字段名不对
- ✅ `allow_from: [...]` + `dm_policy: allowlist` — 需要同时有，且 env var 也要有

**群里无响应最常见原因**：用户 ID 不在 `FEISHU_ALLOWED_USERS` 或 `FEISHU_GROUP_ALLOWED_USERS` 里。

## 群白名单配置（新用户加入群聊）
licai 的群白名单策略是 `allowlist`，每个新用户需要在 config.yaml 两处都加上 open_id：

```yaml
platforms:
  feishu:
    extra:
      allowed_group_users:
      - ou_2fcb5a59369405d74cf386b349aff96c   # 老公
      - ou_a023ae4173052b881d472190d32065e2   # 新用户
      group_rules:
        oc_4c9d07126349124f942e382f7501b189:
          allowlist:
          - ou_2fcb5a59369405d74cf386b349aff96c
          - ou_a023ae4173052b881d472190d32065e2
          policy: allowlist
```

加完后重启 licai gateway：
```bash
kill <PID> && hermes --profile licai serve
```

## 快速诊断 checklist
```bash
# 1. 查所有 gateway 进程（最可靠）
ps aux | grep "hermes.*gateway" | grep -v grep
# 两行输出（bash wrapper + python进程）= 正常运行

# 2. 确认飞书是否连上
grep "feishu connected\|connected to wss" ~/.hermes/profiles/licai/logs/gateway.log

# 3. 是否有收到消息
grep "inbound message" ~/.hermes/profiles/licai/logs/gateway.log

# 4. 是否有新用户待审批
hermes --profile licai pairing list
```

## 启动检查
```bash
# 确认飞书连接成功
grep "feishu connected" ~/.hermes/profiles/licai/logs/gateway.log

# 确认收到消息（licai 收到消息才会有 inbound 日志）
grep "inbound message" ~/.hermes/profiles/licai/logs/gateway.log
```

**重启 gateway 必须杀两个进程 (2026.08.25):** `terminal(background=true)` 启动的 gateway 有两层进程：bash wrapper（父）+ python child（子）。`kill -9 <python_pid>` 只杀子进程，bash wrapper 存活并持有 tty 引用，后续启动会报 "Another gateway instance already running"。**正确做法：** `pkill -f "hermes gateway"` 一次杀两个，或者先杀 python 子进程再杀 bash wrapper，然后再启动。

### SSL EOFError 导致 WebSocket 断开
`errors.log` 大量 `Lark: receive message loop exit` + `SSLEOFError`。Bot 进程可能还活着但群消息停了。
```bash
tail -10 ~/.hermes/profiles/libai/logs/errors.log
grep "Inbound group" ~/.hermes/profiles/libai/logs/gateway.log
```

### 群里 @ 不响应——两种可能
**可能1: `require_mention: true`（默认）导致静默忽略**
飞书 adapter 默认 `require_mention: true`，即使 `default_group_policy: open` 也只响应被 @ 的消息。在 config 里加：
```yaml
platforms:
  feishu:
    extra:
      require_mention: false  # 不需要 @ 就能回复群消息
      default_group_policy: open
```

**可能2: 飞书平台限制——同群多 bot @事件只推给最早加入的**
当两个 bot（理财bot + 嗨妹小老婆）在同一个群时，**@mention 事件只推给最早加入群的 bot**，后加的 bot 永远收不到任何 @事件。这是飞书平台级限制，非配置问题。
诊断：
```bash
# 看 libai 是否有收到群消息（不应该有，因为被嗨妹抢了）
grep "Inbound group" ~/.hermes/profiles/libai/logs/gateway.log

# 看嗨妹小老婆的（应该有）
grep "Inbound group" ~/.hermes/logs/gateway.log
```
如果 libai 的 log 里群消息为空 → 确认是这个平台限制。

**解决方案**：把理财bot 和 嗨妹小老婆 放在不同群；或者接受只有嗨妹小老婆能响应 @，理财bot 只能 DM。

### app_id 冲突（飞书平台限制）
飞书每个 app_id 只能有一个 Hermes 实例连接 WebSocket。先启动的占位，后启动的报错 `Another local Hermes gateway is already using this Feishu app_id (PID NNN)` 并 exit。

**已知冲突组：**
| 组 | Profile | App ID | 状态 |
|----|---------|--------|------|
| A | libai + licai | `cli_aafa2c6a83b85bee` | **不能同时跑** |
| B | cutegirl + wenyu | `cli_aae7a3ad78b8dbe3` | **不能同时跑** |

### 切换 profile 模型（model/provider）
修改 profile 的 `config.yaml` 后需要重启 gateway：

```yaml
# ~/.hermes/profiles/wenyu/config.yaml 示例（文娱bot换MiniMax）
model:
  default: MiniMax-M2.7
  provider: minimax-cn
providers:
  minimax-cn:
    api_key: ${MINIMAX_CN_API_KEY}
    base_url: https://api.minimaxi.com/anthropic
```

重启后确认日志无 `auth failed` 错误。

### MINIMAX_CN_API_KEY 更新后 gateway 不会自动重载
`.env` 里的 `MINIMAX_CN_API_KEY` 是 gateway **启动时**读取的。运行中修改 .env 不会生效，必须完整重启：

```bash
# 杀两个进程（bash wrapper + python child）
pkill -f "hermes gateway"
sleep 2
hermes gateway
```

**验证是否生效**：`grep MINIMAX ~/.hermes/.env` 确认 key 已更新，同时 `tail ~/.hermes/logs/gateway.log | grep auth` 确认无报错。

**原则：不要同时启动同一组的两个 profile。** 启动前先 `ps aux | grep hermes.*gateway` 确认对方没在跑。

诊断：
```bash
# 查所有 gateway 进程
ps aux | grep "hermes.*gateway" | grep -v grep

# 确认 app_id 归属
grep -r 'app_id' ~/.hermes/profiles/*/config.yaml
```

要跑冲突组的另一个：先 `pkill -f "hermes gateway.*<other>"`，再启动目标。
