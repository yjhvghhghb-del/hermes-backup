---
name: feishu-multi-bot
description: Add multiple Feishu bots as independent Hermes profiles.
tags: [feishu, multi-bot, gateway, profile]
---

# Feishu Multi-Bot Setup

Add multiple Feishu bots (different personalities/instances) to the same or different Feishu groups, each running as an independent Hermes gateway under its own profile.

## Trigger
Use when: user wants a second (or third…) Feishu bot with a different personality,性格, or config.

## Architecture
Two modes: **multiplexed** (one gateway, all profiles) and **multi-gateway** (separate process per profile).

**→ Preferred on Android/Termux: `gateway.multiplex_profiles: true`** (see Startup section below).

**⚠️ CRITICAL: Every profile that needs model access MUST have a `.env` file with API keys AND that profile's own Feishu credentials.**
The gateway reads credentials from each profile's own `.env` via `set_secret_scope`.
Profiles without `.env` fail with "No usable credentials found for provider 'minimax-cn'".
**More subtle**: if you COPY `.env` from another profile (e.g. `cp ~/.hermes/.env ~/.hermes/profiles/licai/.env`), the Feishu `app_id`/`app_secret` will be WRONG for that profile, causing every message to fail with "提供商身份验证失败" — even though the API key itself is correct. Each profile's `.env` must contain THAT profile's own `FEISHU_APP_ID` and `FEISHU_APP_SECRET`. See `.env setup` below.**

Each bot = one Hermes profile with its own config.yaml + .env. With `multiplex_profiles: true`, all profiles share a SINGLE gateway process. Without it, each profile needs its own gateway process.

**App_id collision map — CRITICAL (updated 2026.08.29 this session):**
**App_id collision map — CRITICAL (updated 2026.08.29 this session):**
⚠️ licai 和 libai 本次都连接成功了（之前认为互斥，但实测可同时连接 — 可能其中一个静默丢失事件）。wenyu 和 cutegirl 同组，仍然互斥。
| Profile | app_id | This session | Notes |
|---------|--------|-------------|-------|
| `licai` | `cli_aafa2c6a83b85bee` | ✅ connected (先启动) | 可能与libai静默冲突 |
| `libai` | `cli_aafa2c6a83b85bee` | ✅ connected (后启动抢走连接) | 可能静默丢事件 |
| `cutegirl` | `cli_aae7a3ad78b8dbe3` | ✅ connected (先启动拿到连接) | 与wenyu冲突 |
| `wenyu` | `cli_aae7a3ad78b8dbe3` | ❌ exit — cutegirl已占用 | 与cutegirl冲突 |
| `geekwife` | (Telegram only) | ✅ connected | |
| `siliconflow` | (Telegram only) | ✅ connected | |

**User conflict attitude (重要 — 2026.08.29 confirmed):** 老公明确表示"所有bot都启动就对了不用管冲突"。冲突时部分bot会退出，这是预期行为，不需要主动停掉冲突的进程来腾 app_id。直接启动全部，汇报哪些在跑哪些退出即可。

**"启动文娱bot" specific:** 文娱bot = `wenyu` profile（app_id `cli_aae7a3ad78b8dbe3`，与 cutegirl 冲突）。要先停 cutegirl 再起 wenyu，或者接受 wenyu 退出。

**Current running (2026.08.29 confirmed — multi-process mode):**
- `default` (主bot) ✅ — PID 19463, Telegram enabled in config.yaml
- `licai` ✅ — 飞书理财bot (PID 20339, app_id `cli_aafa2c6a83b85bee`, connected)
- `libai` ✅ — 飞书备用bot (PID 20342, app_id `cli_aafa2c6a83b85bee`, connected)
  - ⚠️ libai logs show `ModuleNotFoundError: No module named 'nemo_relay'` — non-fatal, WebSocket still connects
- `wenyu` ✅ — 飞书文娱bot (PID 24084, app_id `cli_aae7a3ad78b8dbe3`, connected)
- `geekwife` / `siliconflow` — check with `ps aux | grep hermes | grep -v grep`

**"主bot" means the `default` profile** (no --profile flag), which has Telegram enabled in `~/.hermes/config.yaml`. It was already running before this session's "主bot和文娱bot启动" request — no action needed if `ps aux` shows it alive.

**"启动飞书bib" means licai + libai** (both app_id `cli_aafa2c6a83b85bee`, both connected this session confirmed).

**启动所有bot (multi-process, no multiplex):** `hermes --profile <name> gateway run` for each named profile; `hermes gateway run` for default. No --replace needed when multiple bots are already up.

**"启动所有bot" 时：** 直接全部 `hermes --profile <name> gateway run`，不用事先检查/停掉冲突进程。冲突的bot会自己退出（`Another local Hermes gateway is already using this Feishu app_id`），老公接受这个结果。

**Telegram profiles on this system (2026.08.24):**
- `default` (主bot) — Telegram token in `~/.hermes/config.yaml`, home_channel=胖蝦球 (chat_id=877708648)
- `geekwife` (极客老婆) — Telegram token `8637317610:AAFMUvm6-KLLslBLWLV8lRSFbhZDhGsdzVw` ✅
- `siliconflow` — Telegram token `8363232963` ✅
- All other profiles (libai, licai, cutegirl, wenyu) have Feishu only — no Telegram.

**With `multiplex_profiles: true`, all 7 profiles connect inside ONE gateway process.
The gateway runs the default profile, then secondary profiles as multiplexed adapters.
Telegram credential conflicts are detected and logged as errors — affected profiles are skipped but others continue.**

> ⚠️ **Telegram duplicate credential error** (multiplexed mode): When two profiles share the same Telegram bot token, the gateway logs:
> `Profile 'default' and 'licai' both configure telegram with the same credential — refusing to start the duplicate`
> The affected profile is skipped. Fix: give each profile its own Telegram bot token, or accept that only the first-loaded profile will use Telegram.

> ⚠️ > ⚠️ **App_id cli_aae7a3ad78b8dbe3 IS VALID**: Confirmed 2026.08.15 — wenyu connected successfully using this app_id with its own app_secret. Both cutegirl and wenyu share this app_id (same Feishu app, different secrets) — only ONE can hold the Feishu WebSocket connection at a time. The "invalid" error on cutegirl was likely a stale/restarted connection state, not a credential problem. The app_id itself is fine; the collision is the only blocker.

> ⚠️ **app_id conflict order of precedence (updated 2026.08.15)**: When multiple profiles share an app_id, whichever gateway STARTS LAST gets the Feishu WebSocket connection and ALL events. The earlier one shows "connected" in logs but receives ZERO events. This is NOT a bug — it's how Feishu platform routing works per app. libai and licai share `cli_aafa2c6a83b85bee`; wenyu and cutegirl share `cli_aae7a3ad78b8dbe3`. **libai is the main Feishu bot and takes precedence over licai** — stop licai before starting libai.

**Telegram profiles on this system (2026.08.15):**
- `default` (主bot) — Telegram token `8800919754:AAFdNkpAGSI6M5ahwd3_5g-SuZzusH7ybp4`, home_channel=胖蝦球 (chat_id=877708648, thread_id=103519). Config in `~/.hermes/config.yaml` `platforms.telegram` block. **Successfully started 2026.08.15.**
- `geekwife` (极客老婆) — Telegram token `8637317610:AAFMUvm6-KLLslBLWLV8lRSFbhZDhGsdzVw` ✅
- `siliconflow` — Telegram token `8363232963` ✅
- All other profiles (libai, licai, cutegirl, wenyu) have Feishu only — no Telegram.

**Currently verified running (2026.08.18):**
- `default` ✓ — Telegram主bot (PID 6116)
- `cutegirl` ✗ — blocked by wenyu (same app_id `cli_aae7a3ad78b8dbe3`)
- `geekwife` ✓ — Telegram (PID 20087)
- `libai` ✗ — blocked by licai (same app_id `cli_aafa2c6a83b85bee`)
- `licai` ✓ — 飞书理财bot (PID 20090)
- `siliconflow` ✓ — Telegram新bot (PID 20091)
- `wenyu` ✓ — 飞书文娱bot (PID 15395)

**Currently verified running (2026.08.24 — multiplex_profiles mode):**
- `default` ✓ — single gateway process, connects QQ + Telegram + Feishu (app_id `cli_aae7a0320738dbeb`)
- `licai` ✓ — connected inside multiplexed gateway (飞书理财bot, app_id `cli_aafa2c6a83b85bee`)
- `wenyu` ✓ — connected inside multiplexed gateway (飞书文娱bot, app_id `cli_aae7a3ad78b8dbe3`)
- `geekwife` ✓ — Telegram only, connected via multiplexed gateway
- `siliconflow` ✓ — Telegram only, connected via multiplexed gateway
- `cutegirl` ✗ — Telegram only (no Feishu), not in multiplex
- `libai` ✗ — blocked by licai (same app_id `cli_aafa2c6a83b85bee`)

**"启动飞书主bot" specific procedure:**
libai 和 licai 共用 `cli_aafa2c6a83b85bee`，必须先停 licai 再启动 libai：
```bash
# 1. 停掉licai（因为共享app_id）
kill -9 <licai_pid>
# 2. 启动libai
hermes -p libai gateway run
```

**"启动所有bot" — Termux/Android standard startup (2026.08.29 confirmed):**

⚠️ **CRITICAL: Use `gateway run`, NOT `serve`!**
- `hermes serve` — only starts the web dashboard (port 9119). Does NOT start the bot/gateway. Processes appear alive but no messages are processed.
- `hermes gateway run` — starts the actual bot gateway that processes messages.
- On Android/Termux, `hermes serve` exits immediately if port 9119 is already in use (common — the default profile's dashboard is usually already running).

```bash
# Kill stale processes first
pkill -f "hermes" 2>/dev/null; sleep 2

# CORRECT — starts actual bot gateway (one per profile)
terminal(background=true, command="hermes -p siliconflow gateway run")
terminal(background=true, command="hermes -p wenyu gateway run")
terminal(background=true, command="hermes -p geekwife gateway run")
terminal(background=true, command="hermes -p libai gateway run")
terminal(background=true, command="hermes -p cutegirl gateway run")
terminal(background=true, command="hermes -p licai gateway run")
# default (main bot — no -p flag):
terminal(background=true, command="hermes gateway run")
```

Verify: after `sleep 8`, check `tail -3 ~/.hermes/profiles/<name>/logs/gateway.log` — you should see `✓ telegram connected` or `✓ feishu connected`. If the log is unchanged from days ago, the gateway didn't start.

**⚠ App_id collision is the real blocker**: Even with separate gateway processes, profiles sharing the same app_id cannot both be active. The conflict pairs (updated 2026.08.29):
- `cutegirl` ↔ `wenyu` (both app_id `cli_aae7a3ad78b8dbe3`)
- `licai` ↔ `libai` (both app_id `cli_aafa2c6a83b85bee`)

For each collision pair, pick ONE profile to run — the other will fail with "Another local Hermes gateway is already using this Feishu app_id".

**Currently verified running (2026.08.24 — multiplexed single-gateway):**
- `default` ✓ — single gateway process (PID 24363), connects QQ + Telegram + Feishu (app_id `cli_aae7a0320738dbeb`)
- `licai` ✓ — connected inside multiplexed gateway (飞书理财bot, app_id `cli_aafa2c6a83b85bee`)
- `wenyu` ✓ — connected inside multiplexed gateway (飞书文娱bot, app_id `cli_aae7a3ad78b8dbe3`)
- `geekwife` ✓ — Telegram only, connected via multiplexed gateway
- `siliconflow` ✓ — Telegram only, connected via multiplexed gateway
- `cutegirl` ✗ — blocked by wenyu (same app_id)
- `libai` ✗ — blocked by licai (same app_id)

**⚠ WRONG startup form (tried and failed this session — do not repeat):**
```bash
# WRONG — exits immediately on Termux: "Input is not a terminal (fd=0). Shutting down…"
hermes --profile cutegirl          # ✗ wrong — TUI mode, needs TTY
hermes --profile geekwife          # ✗ same
hermes --profile libai             # ✗ same

# CORRECT — stays running as daemon:
hermes --profile cutegirl gateway run    # ✓ correct form
hermes --profile geekwife gateway run    # ✓ correct form
hermes --profile libai gateway run       # ✓ correct form
```

**⚠️ CRITICAL: Every profile that needs model access MUST have a .env file with API keys.**
The gateway reads credentials from each profile's own `.env` via `set_secret_scope`.
Profiles without `.env` fail with "No usable credentials found for provider 'minimini-cn'. Set MINIMAX_CN_API_KEY."

Symptom: Feishu bot connects fine but every message fails with "提供商身份验证失败" (provider auth failed).
Fix: `cp ~/.hermes/.env ~/.hermes/profiles/<name>/.env`

**Verify all connected:**
```bash
hermes gateway list
# Output:  ✓ default — PID NNN
#          ✓ licai — connected inside multiplexed gateway
#          ✓ wenyu — connected inside multiplexed gateway
grep "feishu.*connected.*profile" ~/.hermes/logs/gateway.log
```

**⚠ WRONG forms (tried and failed this session — do not repeat):**
- `hermes --profile <name>` without `gateway run` → exits immediately: "Warning: Input is not a terminal (fd=0). Shutting down…" — confirmed failed for all 6 profiles (cutegirl, geekwife, libai, licai, siliconflow, wenyu) in this session (2026.08.24). Each exited within seconds.
- `hermes gateway run --profile <name>` (--profile after subcommand) → "error: unrecognized arguments: --profile"
- `hermes --profile <name> gateway` (no `run`) → gateway starts but immediately exits with code 1
- Shell `&`/nohup/setsid → rejected by terminal tool; must use terminal(background=true)

**Startup results (2026.08.24 confirmed — 6 profiles, multiplexed single-gateway):**
- `hermes gateway restart` (single gateway, all profiles multiplexed) ✓ — PID 3802
  - default: QQBot + Telegram ✓
  - licai: 飞书理财 ✓
  - wenyu: 飞书文娱 ✓
  - libai: 飞书 ✓
  - cutegirl: Feishu ✓
  - geekwife: Telegram ✓
  - siliconflow: Telegram ✓

**libai profile Feishu connectivity (clarified 2026.08.29):**
libai's `config.yaml` HAS Feishu `app_id`/`app_secret` — it was NOT missing credentials. The failure to start was purely due to the app_id collision with licai. The previous "no Feishu credentials in .env" note was misleading — the `.env` only needs the AI API key; Feishu credentials live in `config.yaml` under `platforms.feishu.extra`. Once licai (PID 23604) was killed, libai connected successfully on its first start (PID 12327). To run libai: kill the licai process first, then `hermes -p libai gateway run`.
```yaml
model:
  default: MiniMax-M2.7
  provider: minimax-cn
providers:
  minimax-cn:
    api_key: ${MINIMAX_CN_API_KEY}
    base_url: https://api.minimaxi.com/anthropic
```
Restart required after this change (gateway reads .env only at startup).

**Gateway restart: kill BOTH wrapper AND python child, not just python (2026.08.25):**
`terminal(background=true)` creates a two-level process tree — bash wrapper (parent) + python child. `kill -9 <python_pid>` only kills the child; the bash wrapper survives and holds the tty reference. Subsequent starts fail with "Another gateway instance already running". **Correct kill sequence:**
```bash
# Find both PIDs
ps aux | grep 'hermes gateway' | grep -v grep
# Two lines = bash wrapper + python child

# Kill python child directly
kill -9 <python_child_pid>
# Kill bash wrapper
kill -9 <bash_wrapper_pid>
sleep 2
hermes gateway 2>&1 &
```
Alternatively, `pkill -f "hermes gateway"` kills both in one shot.

**siliconflow Telegram reconnect (2026.08.21):** After initial start, siliconflow gateway crashed with `ModuleNotFoundError: No module named 'nemo_relay'`. Process exited cleanly (exit 0). Restarted successfully with same command — Telegram polling reconnected and bot responded to messages.

**飞书主bot（libai）需要独立app_id**: 当前与licai共用 `cli_aafa2c6a83b85bee`，无法同时跑。要跑主bot+理财bot需要两个不同app_id。

**Safe 3-bot Feishu combinations (pick one per group):**
- `default` (A) + `licai` (B) + `wenyu` (C) ✅ (wenyu confirmed connected 2026.08.15)
- `default` (A) + `libai` (B) + `cutegirl` (C) ✅
- `licai` (B) + `wenyu` (C) ✅ — two bots, different groups
- `default` (A) + `licai` (B) + `cutegirl` (C) ✅
- `default` (A) + `libai` (B) + `wenyu` (C) ✅
- `licai` (B) + `cutegirl` (C) ✅ + third slot from A

**Three distinct app_ids → up to 3 simultaneous Feishu bots.**
Pick exactly one profile from each app_id group (A, B, C). All three must be different groups.

**Safe 3-bot combinations:**
- `default` (A) + `libai` (B) + `wenyu` (C) ✅
- `default` (A) + `libai` (B) + `cutegirl` (C) ✅
| `libai` + `licai` ❌ (both Group B — "Another local Hermes gateway is already using this Feishu app_id" error)
- `cutegirl` + `wenyu` ❌ (both Group C — same error)

**Telegram + QQ come with `default` only** — Telegram bot token and QQ Bot App ID are configured ONLY in the default profile. Non-default profiles (libai, licai, cutegirl, wenyu) have Feishu only.

**Profiles on this system (as of 2026.08.15):**
- `default` (主bot) — 无飞书credentials，当前未跑
- `licai` (理财Bot) — app_id `cli_aafa2c6a83b85bee` ✓ 老公open_id: `ou_a023ae4173052b881d472190d32065e2`
- `libai` (主bot/理财分析报告) — app_id `cli_aafa2c6a83b85bee` ⚠️ 与licai冲突
- `cutegirl` (妹妹) — app_id `cli_aae7a3ad78b8dbe3` 但secret无效 ⚠️
- `wenyu` (文娱写作bot) — app_id `cli_aae7a3ad78b8dbe3` ✓ confirmed connected
- `geekwife` (极客老婆) — Telegram ✅
- `siliconflow` — Telegram ✅

**Telegram profiles on this system (2026.08.15):**
- `default` (主bot) — 未跑（无飞书credentials）
- `geekwife` (极客老婆) — Telegram token `8637317610:AAFMUvm6-KLLslBLWLV8lRSFbhZDhGsdzVw` ✅
- `siliconflow` — Telegram token `8363232963` ✅
- All other profiles (libai, licai, cutegirl, wenyu) have Feishu only — no Telegram.

**Standard multi-bot startup (canonical commands — 2026.08.18 verified):**
```bash
# Kill stale processes first (use pkill, not --replace when multiple bots running)
pkill -f "hermes" 2>/dev/null; sleep 2

# Start each bot with `--profile <name> gateway run`
# The --profile flag comes IMMEDIATELY after `hermes`, before the `gateway run` subcommand.
# Named profiles: `hermes --profile <name> gateway run`
# Default profile: `hermes gateway run` (no --profile flag)
#
# IMPORTANT: `hermes gateway run --profile <name>` (--profile after gateway run) is WRONG.
terminal(background=true, command="hermes gateway run", notify_on_complete=true)
terminal(background=true, command="hermes --profile geekwife gateway run", notify_on_complete=true)
terminal(background=true, command="hermes --profile siliconflow gateway run", notify_on_complete=true)
terminal(background=true, command="hermes --profile licai gateway run", notify_on_complete=true)
terminal(background=true, command="hermes --profile wenyu gateway run", notify_on_complete=true)
```

**Currently verified working (2026.08.15):** 4 bots running — libai (飞书主bot), wenyu (飞书文娱bot), geekwife (Telegram), siliconflow (Telegram). licai (理财bot) 和 cutegirl (妹妹) 被app_id冲突阻塞。

**Verify all running:**
```bash
hermes gateway list
# Output: ✓ default — PID NNNN
#         ✓ libai — PID NNNN
#         ✗ cutegirl — not running   ← means failed to start
```
Note: `hermes gateway list` reads a shared PID file and may show wrong profile names or stale ✗ for running bots — always verify with `ps aux | grep hermes gateway`.

**Verify all three are up:**
```bash
# All three python processes should appear
ps aux | grep 'hermes gateway' | grep -v grep
# Correct output (3 lines):
# ... hermes gateway run                  ← default
# ... HERMES_HOME=.../libai hermes gateway run  ← libai
# ... HERMES_HOME=.../wenyu hermes gateway run  ← wenyu
```

**"启动所有bot"** means: start default + all named profiles that don't conflict. Currently: default + cutegirl + geekwife + libai + licai + siliconflow + wenyu, subject to app_id collision constraints.

**All app_ids must be distinct** — no two running Hermes gateways may share the same Feishu app_id. If two gateways share an app_id, the last-connected one steals all WebSocket events from the first (both DM and group), making the first bot appear completely silent despite showing "connected" in logs. Always verify: `grep "app_id" ~/.hermes/config.yaml` and `grep "app_id" ~/.hermes/profiles/<name>/config.yaml` — all must differ.
> ⚠️ **Never set default profile's feishu app_id to libai's app_id (`cli_aafa2c6a83b85bee`)**, even temporarily. The Feishu WebSocket connection will be claimed by whichever process connected last, starving the other bot of ALL events (both DM and group). If default and libai share the same app_id, only one will respond — the other will be completely silent despite showing "connected" in logs. Default profile needs its OWN unique Feishu app (e.g. `cli_aae7a0320738dbeb`) if DM capability is required.

> ⚠️ **All app_ids must be distinct** — no two running Hermes gateways may share the same Feishu app_id. If two gateways share an app_id, the last-connected one steals all WebSocket events from the first (both DM and group), making the first bot appear completely silent. Always verify: `grep "app_id" ~/.hermes/config.yaml` and `grep "app_id" ~/.hermes/profiles/<name>/config.yaml` — all must differ.

> ⚠️ **Platform-level Feishu group limitation**: When two bots are in the same Feishu group, `@mention` events are delivered to **only the earliest-joined bot**. The later-added bot receives **no @mention events at all** — this is a Feishu platform restriction, not a config issue. Workaround: ensure only one bot per group, or accept that only the first-joined bot will respond.

> ⚠️ **Pairing files are per-HERMES_HOME, not shared**: `~/.hermes/platforms/pairing/feishu-approved.json` is the **default profile's** store. When a gateway runs with `HERMES_HOME=~/.hermes/profiles/libai`, it reads `~/.hermes/profiles/libai/platforms/pairing/feishu-approved.json` — a completely separate file. Editing the wrong one has no effect. Always check which profile's directory the target gateway is using before manually editing pairing JSON.



### 0. Enable multiplex_profiles (one-time, Android/Termux only)
```bash
hermes config set gateway.multiplex_profiles true
# Verify:
python3 -c "import yaml; d=yaml.safe_load(open('/data/data/com.termux/files/home/.hermes/config.yaml')); print(d.get('gateway', {}))"
# Should show: {'multiplex_profiles': true}
```

### 1. Create profile directory
```bash
mkdir -p ~/.hermes/profiles/<name>/skills ~/.hermes/profiles/<name>/logs
```

### 2. .env — credentials (MUST be profile-specific!)
⚠️ **DO NOT just copy `~/.hermes/.env`** — it contains the default profile's Feishu app_id/app_secret. Copying it to a new profile gives that profile the WRONG Feishu credentials, causing every message to fail with "提供商身份验证失败".

Create each profile's `.env` with:
- The shared API key (same for all profiles)
- THAT profile's own Feishu app_id and app_secret (from 飞书开放平台 → 凭证与基础信息)

```
# ~/.hermes/profiles/licai/.env
MINIMAX_CN_API_KEY=sk-cp-K9L_eq3zCw9gn1y4dA48fEjdlsvQiwzN21P8b9Te2sKwdXCsfLwQS3oR941l6WvSVGNmH2qSQZRH3_xImS3dRH3JSOGVBocYqwhd3fGx9tES60hqSXXopK4
FEISHU_APP_ID=cli_aafa2c6a83b85bee
FEISHU_APP_SECRET=<LARK_SECRET>
```

```
# ~/.hermes/profiles/wenyu/.env
MINIMAX_CN_API_KEY=sk-cp-K9L_eq3zCw9gn1y4dA48fEjdlsvQiwzN21P8b9Te2sKwdXCsfLwQS3oR941l6WvSVGNmH2qSQZRH3_xImS3dRH3JSOGVBocYqwhd3fGx9tES60hqSXXopK4
FEISHU_APP_ID=cli_aae7a3ad78b8dbe3
FEISHU_APP_SECRET=<LARK_SECRET>
```

Root cause of "提供商身份验证失败" this session (2026.08.24): licai and wenyu's `.env` files were cloned from default, containing default's app_id (`cli_aae7a0320738dbeb`) instead of their own. The Feishu WebSocket connected fine, but every AI model request was rejected because the app_id in the request didn't match the connected bot's identity.

### 3. config.yaml — minimum required fields
```bash
mkdir -p ~/.hermes/profiles/<name>/skills ~/.hermes/profiles/<name>/logs
```

### 2. config.yaml — minimum required fields
```yaml
_config_version: 33

# ⚠ MUST HAVE — or gateway defaults to anthropic and fails to connect
model:
  base_url: https://api.minimaxi.com/anthropic
  default: MiniMax-M2.7
  provider: minimax-cn

agent:
  system_prompt: |
    # Bot 性格设定
    ## 人设：...
    ## 说话风格：...

platforms:
  feishu:
    enabled: true
    extra:
      app_id: cli_aae7a3ad78b8dbe3
      app_secret: xxxxxxxxxxxxxxxx
      default_group_policy: allowlist
      allowed_group_users:
        - ou_open_id_here
      group_rules:
        oc_group_id_here:
          policy: allowlist
          allowlist:
            - ou_open_id_here
```

### 3. .env — credentials
```bash
FEISHU_APP_ID=cli_aae7a3ad78b8dbe3
FEISHU_APP_SECRET=xxxxxxxxxxxx
```
### 4. Start independent gateway (dual-gateway setup)

Each bot = one Hermes gateway process, started independently. The default profile (主bot) uses no `--profile` flag; all other profiles use `--profile <name>`.

**⚠️ Use `terminal(background=True)` in Hermes agent, NOT shell `&`/nohup — shell background wrappers are rejected.**

**The `--profile` flag internally sets HERMES_HOME to the profile directory** — do NOT add a manual `HERMES_HOME=` prefix. Using `HERMES_HOME=~/.hermes/profiles/libai hermes gateway run --profile libai` is redundant and may cause issues. Just use `--profile` alone.

**Key rule: never use `--replace` when multiple bots are already running.**

The `--replace` flag reads the SHARED `~/.hermes/gateway.pid` file and sends SIGTERM to whatever PID is stored there — it does NOT check which profile that PID belongs to. Using `--replace` on a second bot will kill the first bot's process directly. This is NOT a dispatcher conflict — it's a direct process kill.

```bash
# Kill any existing gateways first
pkill -f "hermes gateway" 2>/dev/null; sleep 2

# Start libai (non-default profile — use --profile flag, NOT HERMES_HOME=)
terminal(background=true,
  command="hermes gateway run --profile libai",
  notify_on_complete=true)

# Start default/主bot (uses ~/.hermes/ by default — no --profile flag)
terminal(background=true,
  command="hermes gateway run",
  notify_on_complete=true)
```

**Always verify after startup:**
```bash
# Two python processes = both alive
ps aux | grep 'hermes gateway' | grep -v grep

# Each PID's HERMES_HOME points to the correct profile dir
cat /proc/<pid>/environ | tr '\0' '\n' | grep HERMES_HOME
```

**Confirm Feishu WebSocket connected:**
```
grep "Lark.*INFO.*connected" ~/.hermes/profiles/<name>/logs/gateway.log
grep "Lark.*INFO.*connected" ~/.hermes/logs/gateway.log
```

### 5. Pair new users (per-profile pairing files)

**Pairing files are per-HERMES_HOME, not shared.** When a gateway runs with `HERMES_HOME=~/.hermes/profiles/libai`, it reads `~/.hermes/profiles/libai/platforms/pairing/feishu-approved.json` — NOT `~/.hermes/platforms/pairing/feishu-approved.json`. Always edit the correct file for the target profile.

```bash
# Default profile (主bot) pairing file:
~/.hermes/platforms/pairing/feishu-approved.json

# libai profile pairing file:
~/.hermes/profiles/libai/platforms/pairing/feishu-approved.json
```

If the code has expired, manually add the user's open_id to the correct file:
```json
{
  "ou_2fcb5a59369405d74cf386b349aff96c": {"user_name": "", "approved_at": 1785535998.02079},
  "ou_a023ae4173052b881d472190d32065e2": {"user_name": "", "approved_at": 1785535998.02079}
}
```
Restart the gateway after editing the pairing file.

### 6. Group @mention limitation: only one bot receives events

**Feishu platform restriction**: When multiple bots are in the same group, `@mention` events are delivered to **only the earliest-joined bot**. The later-added bot receives **zero @mention events** — this is a Feishu platform limitation, not a config issue. Workaround: use DM only, or accept that only the first-joined bot will respond to @mentions in shared groups.

### 7. Diagnostic: which bot received a group message?

If group @mention is not working, check which bot's logs show the inbound message:
```bash
# 主bot (default):
grep "inbound message.*feishu" ~/.hermes/logs/gateway.log | grep "chat=oc_4c9d07126349124f942e382f7501b189"

# 理财Bot (libai):
grep "inbound message.*feishu" ~/.hermes/profiles/libai/logs/gateway.log | grep "chat=oc_4c9d07126349124f942e382f7501b189"
```
The group ID for both bots is `oc_4c9d07126349124f942e382f7501b189`. If only one bot's logs show inbound messages, the other bot's Feishu app was joined to the group second and will never receive @mention events.

## References
- [Bot Startup Commands 2026.08.21](references/startup-commands-20260821.md) — confirmed correct terminal() commands, wrong forms, verify steps
- [Pairing & User Management](references/pairing-and-user-management.md) — manual JSON approval, finding open_ids, group allowlist config
- [Profile Architecture](references/profile-architecture.md) — current profile inventory, app_id collision map, log locations, startup commands

```

## Key Differences: Feishu vs QQ Group Access Control

| Feature | Feishu | QQ |
|---------|--------|----|
| Config location | `platforms.feishu.extra.group_rules` | `platforms.qqbot.extra.group_allow_from` |
| Per-group config | ✅ yes | ❌ no |
| Global fallback users | `allowed_group_users` | `group_allow_from` |
| Policy values | `allowlist` / `open` / `blacklist` / `disabled` | `allowlist` |
| Open ID format | `ou_xxxxxxxx` | group hash `8B…37` |

## Find a User's Open ID
From gateway.log:
```bash
grep "inbound message.*feishu" ~/.hermes/logs/gateway.log | grep "user=ou_"
```

## Starting a Third (or Nth) Bot — Same Pattern

Each additional bot gets its own Hermes profile directory and is started the same way with `--profile`:

```bash
pkill -f "hermes gateway" 2>/dev/null; sleep 2

# Start all bots — no --replace, no HERMES_HOME= prefix needed
terminal(background=true, command="hermes --profile licai gateway run")
terminal(background=true, command="hermes --profile wenyu gateway run")
terminal(background=true, command="hermes --profile siliconflow gateway run")
terminal(background=true, command="hermes --profile geekwife gateway run")
terminal(background=true, command="hermes gateway run")  # default — no --profile
```

The `--profile` flag handles all HERMES_HOME isolation internally. Multiple bots can run simultaneously without conflicts.

> ⚠️ **If you need `--replace` to restart one bot without touching the others**: use `pkill -f "hermes.*profile/<name>"` to target only that bot's process, then restart it with the same `HERMES_HOME=...` pattern.

## Pitfalls

- **Accidentally setting duplicate app_id when adding feishu credentials**: A profile may have `group_rules` and `allowed_group_users` configured but be missing `app_id`/`app_secret` — it can receive group events but NOT DM messages. When adding credentials to such a profile, you must use a *different* app_id from any bot already running. Using the same app_id as another running bot causes Feishu to route events to only one bot (the last connected), making both bots appear silent. Always verify: `grep "app_id" ~/.hermes/config.yaml` (default) and `grep "app_id" ~/.hermes/profiles/<name>/config.yaml` (other profiles) — all must be distinct. If you accidentally set a duplicate, the fix is: find the correct app_id for the profile's own bot (from 飞书开放平台 → 凭证与基础信息), set it via `hermes config set platforms.feishu.extra.app_id <correct_id>`, then restart.
- **Default profile has another bot's app_id** (critical — prevents both from running): The default profile's `~/.hermes/config.yaml` had `app_id: cli_aafa2c6a83b85bee` — the SAME app_id as libai. When both gateways start, Feishu routes ALL events to only one (last-connected wins), making the other appear completely silent despite showing "feishu connected" in logs. This happened 2026.08.03: libai was running fine, default appeared dead. Fix: find the default bot's own app_id from 飞书开放平台 → 凭证与基础信息 (it has a different `cli_aae7a0320738dbeb`), set it in `~/.hermes/config.yaml` under `platforms.feishu.extra.app_id`, and restart default. Always verify all app_ids are distinct: `grep "app_id" ~/.hermes/config.yaml` and `grep "app_id" ~/.hermes/profiles/*/config.yaml`.

- **Default profile missing feishu `app_id`/`app_secret`**: The default profile's `~/.hermes/config.yaml` often has `allowed_group_users` and `group_rules` in the `platforms.feishu` block but is missing `app_id` and `app_secret`. This causes DM to fail silently — the bot's gateway starts, Feishu WebSocket connects (group events work), but the bot cannot receive or send DM messages. The bot that *does* have credentials (e.g. libai) will work fine for DM, making it look like a profile or routing issue.

  **When adding DM credentials to the default profile, you MUST use a *different* app_id from any other running bot.** Using the same app_id as another running bot causes Feishu to route ALL events to only the last-connected gateway, silently starving the first bot of all events (both DM and group). This happened when `cli_aafa2c6a83b85bee` was set on both default and libai — only libai responded, and default appeared completely silent despite showing "feishu connected" in logs.

  The fix:
  ```bash
  # Get the CORRECT app_id from 飞书开放平台 → 凭证与基础信息
  # DO NOT reuse another bot's app_id — each Feishu app must be unique
  hermes config set platforms.feishu.extra.app_id cli_xxxxxxxxxxxx
  hermes config set platforms.feishu.extra.app_secret xxxxxxxxxxxxxx
  cd ~ && hermes gateway run --replace
  ```
  Verify: `grep "app_id\|app_secret" ~/.hermes/config.yaml` — both must be present in the `feishu.extra` block. All app_ids across profiles must be distinct — no two running gateways may share the same Feishu app.

  **Diagnostic when bot suddenly stops receiving messages after a config change**: `grep "Inbound dm\|inbound message" ~/.hermes/logs/agent.log | tail -5` — if no new entries after a known message was sent, the WebSocket connection is likely starved by another bot sharing the same app_id. Compare `grep "app_id" ~/.hermes/config.yaml` with `grep "app_id" ~/.hermes/profiles/<name>/config.yaml` for all profiles — all must differ.
- **Missing `.env` in secondary profiles → "提供商身份验证失败" (provider auth failed)**: In multiplexed mode, each profile reads its own `.env` for API credentials via `set_secret_scope`. If a profile directory lacks a `.env` file, the gateway logs "No usable credentials found for provider 'minimax-cn'. Set MINIMAX_CN_API_KEY." and every message to that bot fails.

  **Critical: the .env must contain the CORRECT Feishu credentials for that specific bot, NOT the default profile's credentials.** Copying `~/.hermes/.env` directly gives the wrong `FEISHU_APP_ID`/`FEISHU_APP_SECRET` — each bot has its own app_id. Symptom: bot connects to Feishu WebSocket successfully but every message returns "提供商身份验证失败" because the API key is right but the Feishu app_id doesn't match what the gateway is actually using.

  Fix: create each profile's `.env` with both the API key AND that bot's own Feishu credentials:
  ```
  MINIMAX_CN_API_KEY=sk-cp-...     # API key — same for all profiles
  FEISHU_APP_ID=cli_aafa2c6a83b85bee   # licai's own app_id
  FEISHU_APP_SECRET=BI0RpisjwTuw...     # licai's own secret
  ```
  This was the root cause of the licai and wenyu "没有模型" error this session (06.08.24) — their .env files were cloned from default, which has app_id `cli_aae7a0320738dbeb`, while they use different app_ids.
- **Same app ID collision**: Two gateways with same Feishu app ID → lock error `Another local Hermes gateway is already using this Feishu app_id (PID NNN)`. Each bot needs its own App. Diagnostic: `hermes gateway list` shows ✗ for the failed profile; `grep "app_id" ~/.hermes/profiles/<name>/config.yaml` confirms duplicates.
- **写其他 profile 的 memories/ 需要 `cross_profile=True`**: wenyu 的 memories/ 目录归 wenyu profile 所有，直接写会被 soft guard 拦截。必须 `write_file(..., cross_profile=True)` 才能写入。写入示例：
  ```python
  write_file(
    path="~/.hermes/profiles/wenyu/memories/群聊权限.md",
    content="# 群聊权限说明\n- 飞书群聊需要通过白名单验证才能加入\n- 权限打通后可以在群里正常聊天",
    cross_profile=True
  )
  ```
  同样，写入其他 profile 的 skills/、cron/ 等也需要 `cross_profile=True`。对 default profile 写文件不需要此参数。
- **Cross-profile writes**: Need `cross_profile=True` on `write_file` when editing another profile's files.
- **Group messages not arriving despite Bot joining group**: The bot can be added to a group and show "Bot added to chat" in logs, yet never receive any group messages. Two root causes to check in order:

  1. **Wrong open_id in group_rules**: A user can have *different* open_ids per bot (determined by which bot they paired with). Always use the open_id from *that specific bot's* DM session, not from another bot. Get it from: `grep "sender=user:ou_" profiles/<name>/logs/gateway.log | head -3`. If DM works but group doesn't, this is almost always the cause — the user's open_id for this bot is not in `group_rules[group_id].allowlist`.
  2. **Event subscription scope missing 群组**: The WebSocket connects fine (DM works), but group IM events are filtered upstream because the event subscription for `im.message.receive_v1` only covers 「单聊」 and not 「群组」. Fix: in 飞书开放平台 → select the app → 事件与回调 → 事件订阅 → find `im.message.receive_v1` → ensure the subscription scope includes 群组. This is separate from the permissions page — both must be correct. Quick diagnostic: `grep "Inbound group" profiles/<name>/logs/gateway.log` — if empty while the working main bot has entries, this is the issue. Also confirm app type is 「机器人」 in 基本信息 → 应用类型.
- **Gateway process exits with SIGKILL / exit 137 (OOM)**: On low-memory devices (Android especially), the kernel `lowmemorykiller` daemon may SIGKILL the gateway process. Pattern: `exited UNCLEANLY (no exit path ran — SIGKILL / OOM / VM death)` in lifecycle ledger, with `last_mem` showing high swap usage. Memory pressure is the root cause — check `cat /proc/meminfo`. Wait for memory to ease, then restart. This is a device resource issue, not a config issue.

- **Default profile (`~/.hermes/config.yaml`) also uses `cli_aafa2c6a83b85bee`** — the same app_id as libai. When libai is already running and default starts, Feishu routes ALL events to libai (first connected), leaving default completely silent despite showing "feishu connected" in logs. This is NOT a config error — default IS connected to Feishu WebSocket, but Feishu only delivers events to one consumer per app. Fix: stop libai, then start default with `hermes gateway run --replace`. The two bots need different app_ids to coexist.

  Diagnostic: `grep "app_id" ~/.hermes/config.yaml` (default) and `grep "app_id" ~/.hermes/profiles/libai/config.yaml` — if both show `cli_aafa2c6a83b85bee`, they cannot both run.

- **Group messages need @mention even when policy is `open`**: `require_mention` defaults to `true` in the Feishu adapter. This means the bot silently ignores group messages unless it is @mentioned, even when `default_group_policy: open` is set. Set `require_mention: false` in the `feishu.extra` config to have the bot respond to all group messages:

  ```yaml
  platforms:
    feishu:
      extra:
        require_mention: false
        default_group_policy: open
        group_rules:
          oc_group_id:
            policy: open
  ```

- **`default_group_policy` missing → group @mentions silently ignored**: If `default_group_policy` is absent from `feishu.extra`, the gateway may only process DMs correctly while group @mentions produce no response at all (no error in logs, but no reply either). DM works because DMs bypass group policy checks. Fix: always include `default_group_policy: open` (or `allowlist`) in `feishu.extra` when the bot is expected to respond in groups. This was the root cause of the licai bot appearing completely silent in groups despite being able to receive and process DMs.

  ```yaml
  platforms:
    feishu:
      extra:
        require_mention: false
        default_group_policy: open
        group_rules:
          oc_group_id:
            policy: open
  ```
- **New user white-list: update BOTH `allowed_group_users` AND `group_rules[group_id].allowlist`** AND `dm_policy`/`allowed_dm_users`: When adding a new user to a group with `policy: allowlist`, you must add their `ou_` open_id in **all three** places in config.yaml — `allowed_group_users` (global list), `allowed_dm_users` (global DM list), and `group_rules[oc_xxx].allowlist` (per-group list). Forgetting any of the three silently results in the user being able to DM (or not) depending on which field is missing. After editing config.yaml, restart the gateway — no `--replace` flag needed since it's a named profile. The licai profile uses this pattern:
  ```yaml
  allowed_group_users:
    - ou_2fcb5a59369405d74cf386b349aff96c   #老公
    - ou_a023ae4173052b881d472190d32065e2   #新用户
  allowed_dm_users:
    - ou_2fcb5a59369405d74cf386b349aff96c
    - ou_a023ae4173052b881d472190d32065e2
  dm_policy: allowlist
  group_rules:
    oc_4c9d07126349124f942e382f7501b189:
      allowlist:
        - ou_2fcb5a59369405d74cf386b349aff96c
        - ou_a023ae4173052b881d472190d32065e2
      policy: allowlist
  ```

- **Quick diagnostic when group messages don't arrive**: Compare inbound logs between working bot and new bot:
  - Working: `grep "Inbound group" ~/.hermes/logs/gateway.log`
  - New bot: `grep "Inbound group" profiles/<name>/logs/gateway.log`
  - If working has entries and new bot has zero → event subscription or require_mention issue (see above).
  - If both have zero entries → the bot was never added to the group, or group ID is wrong in config.

- **Quick status check when all bots appear silent**: Run this to get a full picture in one shot:
  ```bash
  for p in cutegirl libai licai wenyu; do
    echo "=== $p ==="
    HERMES_HOME=~/.hermes/profiles/$p hermes gateway status 2>&1 | grep -E "Gateway|app_id|feishu" | head -5
  done
  # Also check: ps aux | grep hermes
  # And check app_id collisions:
  for p in cutegirl libai licai wenyu; do grep "app_id" ~/.hermes/profiles/$p/config.yaml 2>/dev/null; done
  ```
  The `hermes gateway status` output tells you which profiles are up vs stale (lock file says running but process is gone). The app_id grep reveals collision pairs that prevent simultaneous running.

- **On Android/Termux, `hermes --profile X` without `gateway run` exits immediately with "Input is not a terminal"**: prompt_toolkit detects no controlling TTY on stdin and Hermes exits immediately. **Fix: ALWAYS use `hermes --profile X gateway run`** — the `gateway run` subcommand bypasses the TUI/prompt_toolkit path entirely and has no TTY requirement. `hermes --profile X` (without `gateway run`) is ONLY for interactive TUI mode and will always fail in a headless/background context. This caused all 4 background-spawned bots (siliconflow, libai, licai, wenyu) to exit with code 0 within seconds during this session's "start all bots" attempt — the skill's own documented form `hermes --profile <name>` was silently wrong.
  ```bash
  # Check if cutegirl is receiving ANY messages
  cat ~/.hermes/profiles/cutegirl/feishu_seen_message_ids.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Latest: {max(d[\"message_ids\"].values()) if d[\"message_ids\\\"] else None}')"
  # Compare with default bot's latest
  grep -o '\"om_[^\"]*\": [0-9.]*' ~/.hermes/logs/gateway.log | tail -1
  ```
  If cutegirl's latest timestamp is days old but the default bot's is recent, the cutegirl bot is not receiving messages at all — not a config issue. Common causes (in order of likelihood):
  1. **App Secret rotated/invalidated** — Feishu may have invalidated the old secret. Generate a new secret in 飞书开放平台 → 凭证与基础信息 → App Secret → 更新。然后 `patch` the `.env` file and restart the gateway.
  2. **WebSocket connected but dead (SSL blackout)** — the process is alive and Feishu shows "connected" in logs, but upstream Feishu stopped routing events. Diagnostic: if `feishu_seen_message_ids.json` shows a freeze time but the bot process is running, this is the cause. Fix: restart the gateway, or remove/re-add the bot to the group.
  3. **Wrong feishu app_id in .env** — double-check that `FEISHU_APP_ID` in the profile's `.env` matches the bot that was added to the group.

- **Group messages need @mention even when policy is `open`**

- **Different bots = different open_ids for the same user**: When a user @mentions a bot in a group, the raw message contains the bot's open_id. Two different bots (different app_ids) have **different open_ids** for the same user. The `[Mentioned: 飞书助手小老婆 (open_id=ou_811e0301974f771446c962ac347b62dc)]` in a group message is specific to that bot. A second bot added to the same group will have a different open_id. Always get the open_id from the bot's own DM session, not from another bot's logs.
- **Dispatcher lock causes `kanban dispatcher: another gateway already holds the dispatcher lock`**: When a second bot's gateway starts, it may win the dispatcher lock while the first (main) bot's gateway already holds it, causing the new bot to be silently blocked from dispatching messages. Both gateways can be running simultaneously with `hermes gateway run --replace` but only the one that won the lock processes messages. Workaround: restart the main bot's gateway first, then start the second bot's gateway. Or accept that only one gateway dispatches and the other acts as a pure relay.

- **CRITICAL: `--replace` kills the OTHER bot when startup order is reversed**: The `--replace` flag reads `~/.hermes/gateway.pid` and sends SIGTERM to whatever PID is stored there — it does NOT check which profile that PID belongs to. If cutegirl starts first (no `--replace`, writes its PID to `~/.hermes/gateway.pid`), then default starts with `--replace` → default reads cutegirl's PID from the file and kill -15 cutegirl directly. This is NOT a dispatcher conflict — it's a direct process kill. **Always clear the shared pid file before starting the second bot:**
  ```bash
  # Kill all gateway processes first
  pkill -f "hermes gateway"
  rm -f ~/.hermes/gateway.lock ~/.hermes/gateway.pid ~/.hermes/profiles/cutegirl/gateway.lock ~/.hermes/profiles/cutegirl/gateway.pid
  # Start cutegirl FIRST (no --replace)
  cd ~/.hermes/profiles/cutegirl && hermes gateway run &
  sleep 3
  # Start default SECOND (with --replace) — default will kill cutegirl's PID from the file!
  # FIX: either clear pid file again before default starts, OR start default first
  # Safer approach: always start default first, then cutegirl with --replace
  ```
  The safest startup order when both bots need to run: start **default first without `--replace`**, then start **cutegirl with `--replace`** (cutegirl kills default → restart default without `--replace` → start cutegirl with `--replace`). Or accept that only one bot will survive unless you use a process supervisor (systemd, Termux-specific `pkill` script, etc.) instead of Hermes built-in pid management.

- **Identity confusion via shared `~/.hermes/gateway.pid`**: Both profiles write to the same `~/.hermes/gateway.pid` file (not `~/.hermes/profiles/<name>/gateway.pid`). The last-started gateway always owns the file. `hermes gateway list` reads this single file and always shows whichever profile wrote it last — cutegirl can appear as "default" and vice versa. The lifecycle ledger (`gateway.lifecycle_ledger`) also logs the wrong profile name. This is cosmetic — the actual bot process is unaffected — but it means you cannot trust `hermes gateway list` or the ledger for identification. Always use `cat /proc/<pid>/environ | grep HERMES_HOME` to confirm which profile a running process belongs to.

- **Cascading SIGTERM when main bot subprocess kills 妹妹bot**: When 妹妹bot runs as a subprocess of 主bot's TUI session (e.g. launched via "启动妹妹" agent command), stopping or crashing 主bot's gateway sends SIGTERM to all its child processes — including 妹妹bot's gateway. This is why 妹妹bot disappears whenever 主bot restarts. **Fix**: Always run 妹妹bot as a truly independent gateway process (separate `terminal(background=true)` call from the main bot), not as a subprocess. After restarting 主bot, manually re-launch 妹妹bot's independent gateway. Better yet: run both as independent daemons from the start so neither depends on the other.

- **Background wrapper processes getting killed (exit -9 / SIGKILL) on Termux**: When using `terminal(background=true)` to start a gateway, the actual gateway process (python hermes gateway) has a bash wrapper parent (`bash -lic set +m; cd ... && hermes gateway`). On Termux, this wrapper process can be independently SIGKILL'd by the system (exit -9) during process cleanup, even while the child gateway process is still alive. This creates "ghost" wrapper processes that show in `ps aux` as bash with no child, and causes subsequent `hermes gateway run --replace` attempts to fail with "Another gateway instance is already running (PID N)" even when N is a stale wrapper. **Fix**: always run `rm -f gateway.lock gateway.pid auth.lock` in the same command before starting, or explicitly clear them before retrying.

- **Killing a gateway via its wrapper PID does NOT stop the actual gateway**: `terminal(background=true)` creates a two-level process tree:
  - Parent: bash wrapper (e.g. `bash -lic set +m; cd ~/.hermes/profiles/cutegirl && hermes gateway run 2>&1`)
  - Child: actual python gateway (e.g. `/usr/bin/python ... hermes gateway run`)

  `ps aux` shows both processes with different PIDs. `kill <wrapper_pid>` only terminates the bash shell — the python child survives and continues running. Subsequent `hermes gateway run --replace` then fails with "Another gateway instance is already running (PID N)". **Always identify and kill the actual python child PID**:
  ```bash
  # Find the python child (not the bash wrapper)
  ps --ppid <wrapper_pid>   # or: pgrep -P <wrapper_pid>
  # Kill the child directly
  kill -9 <python_child_pid>
  ```
  The python child is the one shown as `/usr/bin/python /data/data/com.termux/files/usr/bin/python ... hermes gateway run` — not the bash line. After killing the child, the wrapper will exit on its own. Then you can safely start a fresh gateway.

- **Verified independent dual-gateway startup sequence (Termux/Android)**: On Termux where multiple Hermes gateways must coexist:
  1. Clear stale lock files: `rm -f ~/.hermes/gateway.lock ~/.hermes/gateway.pid ~/.hermes/profiles/<name>/gateway.lock ~/.hermes/profiles/<name>/gateway.pid` (for each profile)
  2. Start **first bot** (no `--replace`): `terminal(background=true, command="hermes gateway run --profile <name>")`
  3. Start **second bot** (no `--replace` either): same command with different profile name
  4. `sleep 8` then `hermes gateway list` — both should show `✓`
  5. **Log locations**: default profile → `~/.hermes/logs/gateway.log`; named profiles → `~/.hermes/profiles/<name>/logs/gateway.log`. Use `tail -30 <correct_log_path>` to diagnose.
  6. If lock error: a ghost wrapper process is still alive — find the python child PID with `ps aux | grep "hermes gateway"`, `kill -9 <python_pid>` the actual gateway process (not the bash wrapper), then retry.
  7. **Always verify after any restart**: check `hermes gateway list` and confirm all profiles are running
  8. **Startup-order rule**: The first gateway started must NOT use `--replace` (it exits with "another gateway instance starting during our startup"). Only use `--replace` when restarting a single bot with no others running.

- **Switching a Feishu profile's model/provider requires full gateway restart**: When editing a profile's `config.yaml` to change model or provider (e.g. wenyu: Groq `llama-3.3-70b-versatile` → MiniMax `MiniMax-M2.7`), the `.env` file is only re-read at gateway startup. A running gateway reads `.env` once at launch — subsequent `.env` edits do NOT take effect until the gateway is fully killed and restarted (`kill -9 <pid>` then fresh `hermes gateway run`). "Restart" from inside the gateway may not reload secrets. Always do `kill -9` + fresh start.

  Also: the new provider must be declared in `config.yaml`:
  ```yaml
  model:
    default: MiniMax-M2.7
    provider: minimax-cn
  providers:
    minimax-cn:
      api_key: ${MINIMAX_CN_API_KEY}
      base_url: https://api.minimaxi.com/anthropic
  ```
  Without the `providers.minimax-cn` block, the profile will log `No usable credentials found for provider 'minimax-cn'. Set MINIMAX_CN_API_KEY.` even if `.env` has the key.

- **Diagnostic trap: terminal `grep` column truncation looks like key truncation**: When `grep` output is wide, the terminal truncates display columns, showing `sk-cp-...opK4` instead of the full key. This LOOKS like the key was truncated when written to disk — it was not. Use `od -c` or `python3 -c "open('...').read()"` to see actual on-disk content. The `.env` key was fully updated; the gateway simply wasn't restarted to pick it up.


- **lark_oapi `RuntimeError: Task attached to a different loop` during Feishu WebSocket recv** (2026.08.28): After a successful `connected to wss://msg-frontier.feishu.cn` log line, the receive loop crashes with `RuntimeError: Task ... got Future <Future pending> attached to a different loop`. This is a known asyncio bug in the `lark_oapi` SDK's `Client._receive_message_loop` — it creates tasks against the wrong event loop. The crash is non-fatal: the SDK immediately reconnects and a new `connected to wss://` log line appears. The bot continues working normally. No action needed — just don't panic at the scary-looking stack trace in the logs. If reconnection fails repeatedly (3+ times in quick succession), restart the gateway.

- **`WARNING gateway.run: Unauthorized user` — DM allowlist is `.env`, NOT config.yaml**: The Feishu adapter does NOT override `enforces_own_access_policy = True`. The gateway's `authz_mixin._check_user_access` runs and checks `extra.get("allow_from")` for DM — NOT `allowed_dm_users`. Therefore `dm_policy: allowlist` + `allowed_dm_users` in config.yaml has ZERO effect for Feishu DMs. Adding `allowed_from` to config.yaml also doesn't work because the Feishu plugin doesn't plumb that field through to the authz layer.

  **Fix**: Add `FEISHU_ALLOWED_USERS=<open_id>` to the profile's `.env` file:
  ```
  FEISHU_ALLOWED_USERS=ou_c696f8f4d082ba11770301e40ee40063
  ```
  This is the env var that `authz_mixin.py` actually checks for Feishu. After adding, `kill -9 <pid>` and restart gateway. The `Unauthorized user` warning will disappear.

- **`WARNING gateway.run: Unauthorized user` — bot connected but silently ignores DMs**: The bot shows "connected to wss://msg-frontier.feishu.cn" in logs, but a user sends a DM and gets no reply. The logs show `WARNING gateway.run: Unauthorized user: ou_xxx (None) on feishu`. **Root cause**: the user's open_id is missing from `FEISHU_ALLOWED_USERS` in `.env` (NOT config.yaml). The `feishu-approved.json` pairing store does NOT gate DMs. Fix: add open_id to `FEISHU_ALLOWED_USERS` in `.env`, then restart gateway.

- **`WARNING gateway.lifecycle_ledger: Previous gateway life ... exited UNCLEANLY (SIGKILL / OOM / VM death)`**: After a gateway crash/restart, this warning appears on the next start. It's informational — the previous instance was killed by the system (low memory, Termux suspension, etc.). The gateway recovered automatically. No action needed unless it happens repeatedly, in which case check `cat /proc/meminfo` for available memory.

- **SSL EOFError crash and silent group-event blackout**:

- **SSL EOFError crash and silent group-event blackout**: The Feishu WebSocket can drop with `receive message loop exit, err: no close frame received or sent` followed by SSL errors during reconnection. The gateway auto-discovers it, but if Telegram shows repeated `ConnectError` and reconnect attempts (10+), the proxy is down. Check proxy separately. This is system-specific — other deployments may not need it. Two distinct failure modes:
  - **Crash mode** (gateway process exits): restart the gateway.
  - **Blackout mode** (gateway stays alive, DM works, group events stop): the WebSocket reconnection appears to succeed (`connected to wss://msg-frontier.feishu.cn`) but group message events stop arriving. DM continues to work. Root cause is upstream — Feishu stops routing group events to the app despite the WebSocket appearing connected. Fix: (a) restart the gateway, (b) remove and re-add the bot to the group, or (c) re-publish the app in 飞书开放平台 (events subscription can silently lose its 群组 scope after an app update). Diagnostic: `grep "Inbound group" profiles/<name>/logs/gateway.log` — if empty while the bot is running and DM works, this is the blackout mode.

- **Cannot restart gateway from inside the running gateway process**: Calling `kill <pid>` on a gateway from a terminal where that same gateway's shell is the parent shell, then immediately launching a new gateway in the same terminal, fails with `Blocked: cannot restart or stop the gateway from inside the gateway process`. Workaround: use a *different* terminal/shell to kill and restart. Or use `hermes gateway restart --profile <name>` from a separate shell — it works even when the target gateway is the current process's parent.

## Related Skills
- **feishu-bitable** — 飞书多维表格读写脚本（`~/.hermes/scripts/feishu_bitable.py`）
- **feishu-wiki-document-read** — 读取老公发的飞书 wiki/docx 链接内容（REST API 读取，无法用 web_extract）
