---
name: termux-hermes
description: "Termux Hermes startup and platform constraints."
---

# termux-hermes

Manage Hermes Agent on Android/Termux — platform-specific constraints, boot workflow, and gotchas.

## Platform Constraint (CRITICAL)
**Termux kills background processes forked from shell commands.**
The OS sends SIGKILL to any process started with `nohup ... &`, `setsid ...`, or terminal background=true inside a Hermes session. The background session exits immediately and the child gateway process gets SIGKILL'd.

**HOW TO RUN GATEWAY IN TERMUX:**
The user must manually run gateway in their own Termux terminal (not through the AI session):
```
hermes gateway run
```
Then press **Ctrl+A D** to detach to screen (NOT Ctrl+C). This leaves the gateway running in a screen/pts session that survives the AI tool returning.

- WRONG: `nohup hermes gateway run &` → SIGKILL'd
- WRONG: `setsid hermes gateway run &` → SIGKILL'd
- WRONG: `terminal(background=true)` → SIGKILL'd
- WRONG: `hermes gateway restart` → times out and gateway exits with SIGTERM
- RIGHT: User types `hermes gateway run` in their own terminal, then Ctrl+A D

## Gateway Self-Termination Is Blocked

**The gateway BLOCKS self-termination from inside its own process.** All of the following fail when called from within a running gateway session (whether via terminal, cron, or execute_code):

- `pkill -9 -f "hermes gateway"` → denied
- `pkill -9 -f "<profile_name>"` → denied (even for individual profiles)
- `hermes gateway restart` → denied
- Cron jobs containing gateway/process lifecycle commands → denied
- `execute_code` subprocess calls to kill gateway → denied

**WORKAROUND**: When the user asks to restart the gateway, tell them explicitly to open a **separate terminal window** outside the running gateway:

```bash
# Restart main gateway
pkill -9 hermes; sleep 2 && hermes gateway run
```

Do NOT attempt to restart from within — always redirect the user to a separate window.

## Startup Sequence

### CORRECT startup order (2026-09-17，实测):

**关键认知：`gateway.multiplex_profiles: true` 默认开启，主 gateway 自动托管所有 profiles，不需要单独启动任何 profile 的 gateway 进程。**

```bash
# 1. 杀掉所有旧进程
pkill -9 hermes; sleep 2

# 2. 直接启动主 gateway
hermes gateway run
```

Done。主 gateway 启动后自动 multiplex 所有 profile 的 Telegram/Feishu 连接。

### 如果需要强制独立运行某个 profile（非 multiplex）

```bash
hermes --profile siliconflow gateway run --force
```

但这样做会让该 profile 与主 gateway 的 multiplex 冲突（同一 bot token 双重连接），不推荐。

### 验证状态

```bash
ps aux | grep "hermes gateway run" | grep -v grep
hermes gateway status
tail -30 ~/.hermes/logs/gateway.log | grep -E '✓|✗|connected|failed'
```

## Command syntax (critical — 踩坑实录)

- WRONG: `hermes start siliconflow` → `invalid choice 'start'`
- WRONG: `hermes profile use siliconflow && hermes gateway run` → profile use 只改默认 profile，不影响 gateway run 的行为
- WRONG: `hermes serve` → `serve` 不是有效命令
- WRONG: `hermes --profile siliconflow gateway run`（在 multiplex 开启时）→ 报错 "already serves profile 'siliconflow'"
- RIGHT: `hermes gateway run` → 启动主 gateway，multiplex 自动生效

**`--replace` flag**：不是废弃的，是**正确的**重启方式。Gateway 约3分钟被 Termux session timeout SIGTERM 杀掉时，`--replace` 会自动拉起新进程。multiplex 模式下不需要分别启动独立 profile 的 gateway。

## Launching Multiple Isolated Profiles (multi-bot on one machine)

**已过时（2026-09-17）：** `gateway.multiplex_profiles: true` 默认开启，所有 profiles 已由主 gateway 统一托管，不需要（也不能）单独启动各 profile 的 gateway 进程。

各 profile 的 bot token 连接由主 gateway 的 multiplex 统一管理，每个 profile 的状态通过参数查询：
```
curl "http://127.0.0.1:9119/api/health?profile=geekwife"
curl "http://127.0.0.1:9119/api/health?profile=siliconflow"
```

## Architecture
- **One gateway, many platforms**: Telegram, Feishu, QQBot all multiplex through one gateway process
- Per-profile `hermes --profile X` = independent agent, not an additional platform connector
- Each profile's platforms are configured in `~/.hermes/profiles/<name>/config.yaml`

## ⚠️ Profile Process Stability — Profiles Can Die Silently

在 multiplex_profiles: true 模式下，**没有独立 profile gateway 进程**，只有主 gateway。所有 profile 都被 multiplexed，不需要监控多个进程。

**诊断主 gateway 是否在跑：**
```bash
ps aux | grep "hermes gateway run" | grep -v grep
```

**如果主 gateway 挂了**：重新启动即可，multiplex 会自动恢复所有 profile 连接：
```bash
pkill -9 hermes; sleep 2; hermes gateway run
```

## Telegram Bot 无响应 — 如何诊断

**症状：** Telegram bot 不回消息

**诊断步骤：**
1. 检查主 gateway 是否在跑：`ps aux | grep "hermes gateway run" | grep -v grep`
2. 检查 gateway 日志：`tail -30 ~/.hermes/logs/gateway.log | grep -i "telegram\|error\|disconnect"`
3. 确认 token 有效：`curl -s "https://api.telegram.org/bot<TOKEN>/getMe"`

**如果 bot token 有效但仍无响应**：在另一个 terminal 重启主 gateway（不要在 gateway 运行的 session 里杀进程）。

## Verifying Connections
```bash
tail -20 ~/.hermes/logs/gateway.log
```
Look for: `✓ qqbot connected`, `✓ feishu connected`, `✓ telegram connected`

## Cron Jobs on Termux
`deliver='origin'` saves locally only. Use `deliver='telegram'` or `deliver='all'` for live notification.

## Known Working Free Models (as of 2026-08)

| Provider | Free Models | Setup |
|----------|-------------|-------|
| OpenRouter | `stealth/ox-alpha` (1M ctx, coding很强), 27+ `:free` models | `OPENROUTER_API_KEY` in `.env` |
| Groq | `llama-3.3-70b-versatile`, `mixtral-8x7b-32768`, `gemma-7b` | `GROQ_API_KEY` in `.env`, `base_url: https://api.groq.com/openai/v1` |
| NVIDIA NIM | Llama 4, Qwen, Mistral, Hermes 3 | `$NIM_API_KEY`, register at nvidianim.ai |

**Ox Alpha** (`stealth/ox-alpha`): appeared 2026-08-20 on OpenRouter, anonymous GLM-family stealth model, 1,048,576 token context, multimodal (text+image+video), tool calling, coding能力超过 GPT-5.6 Sol。免费预览期约一周。

**Groq 最简单** — 只需在 `config.yaml` 的 `providers:` 下加 groq 配置块，重启即可切换。

## Troubleshooting
- Gateway not running: `hermes gateway run`
- Stale state: `Recorded state 'running' but the recorded process is gone` → restart gateway
- Platform stuck: `tail -50 ~/.hermes/logs/gateway.log`
- `moa_aggregator` OpenRouter error: profile needs `OPENROUTER_API_KEY` configured, or switch its aggregator model to a configured provider
