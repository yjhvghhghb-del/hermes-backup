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
Each bot = one Hermes profile with its own config.yaml + .env + gateway process.
Feishu App IDs are locked — two gateways cannot share the same `cli_xxxxxxxx` app ID.

**Feishu app_id collision map — CRITICAL (as of 2026.08.06):**
Three simultaneous Feishu bots are possible when picking from three distinct app_ids. The maximum is 3 because there are only 3 distinct app_ids total.

| Profile | app_id | feishu_secret | Distinct app_id group |
|---------|--------|---------------|----------------------|
| `default` (主bot) | `cli_aae7a0320738dbeb` | `nMXvHNQmE8o0obLOV3GXVff1qoj76NWu` | Group A |
| `libai` (理财Bot) | `cli_aafa2c6a83b85bee` | `BI0RpisjwTuwI1o670OXRb2e7oxLM7dG` | Group B |
| `licai` | `cli_aafa2c6a83b85bee` | `BI0RpisjwTuwI1o670OXRb2e7oxLM7dG` | Group B — COLLIDES with libai |
| `cutegirl` (妹妹) | `cli_aae7a3ad78b8dbe3` | `9w519nveoLWESPvXicJiEeqhb76w6rh3` | Group C — COLLIDES with wenyu |
| `wenyu` (文娱写作bot) | `cli_aae7a3ad78b8dbe3` | `MpxugHJ0FzlcbEPSmi6zZb57YiGzhmgl` | Group C — COLLIDES with cutegirl |

**Three distinct app_ids → up to 3 simultaneous Feishu bots.**
Pick exactly one profile from each app_id group (A, B, C). All three must be different groups.

**Safe 3-bot combinations:**
- `default` (A) + `libai` (B) + `wenyu` (C) ✅
- `default` (A) + `libai` (B) + `cutegirl` (C) ✅
- `libai` + `licai` ❌ (both Group B)
- `cutegirl` + `wenyu` ❌ (both Group C)

**Telegram + QQ come with `default` only** — Telegram bot token and QQ Bot App ID are configured ONLY in the default profile. Non-default profiles (libai, licai, cutegirl, wenyu) have Feishu only.

**Profiles on this system (as of 2026.08.06):**
- `default` (主bot) — app_id `cli_aae7a0320738dbeb`, feishu_secret `nMXvHNQmE8o0obLOV3GXVff1qoj76NWu` ✅
  - **Also has Telegram (`8800919754:AAFdNkpAGSI6M5ahwd3_5g-SuZzusH7ybp4`) and QQ (App ID `1905311551`)**
- `libai` (理财Bot) — app_id `cli_aafa2c6a83b85bee`, feishu_secret `BI0RpisjwTuwI1o670OXRb2e7oxLM7dG` ✅
- `licai` — app_id `cli_aafa2c6a83b85bee` ⚠️ COLLIDES with libai (same app_id)
- `cutegirl` (妹妹) — app_id `cli_aae7a3ad78b8dbe3`, feishu_secret `9w519nveoLWESPvXicJiEeqhb76w6rh3` ⚠️ COLLIDES with wenyu (same app_id)
- `wenyu` (文娱写作bot, 活泼性格) — app_id `cli_aae7a3ad78b8dbe3`, feishu_secret `MpxugHJ0FzlcbEPSmi6zZb57YiGzhmgl` ⚠️ COLLIDES with cutegirl (same app_id)

**Telegram and QQ are ONLY in the default profile.** Non-default profiles (libai, licai, cutegirl, wenyu) have NO Telegram or QQ config — they only have Feishu. If the user asks to "start all bots", the Telegram and QQ bots only come up with the default profile.

**Currently running (as of 2026.08.06):**
- `default` (PID dynamic) — 主bot (feishu `cli_aae7a0320738dbeb`) + Telegram + QQ; start: `hermes gateway run --replace`
- `libai` (PID dynamic) — 理财Bot (feishu `cli_aafa2c6a83b85bee`); start: `HERMES_HOME=~/.hermes/profiles/libai hermes gateway run`
- `wenyu` (PID dynamic) — 文娱写作bot (feishu `cli_aae7a3ad78b8dbe3`); start: `HERMES_HOME=~/.hermes/profiles/wenyu hermes gateway run`
All three can run simultaneously (distinct app_ids) ✅

**All app_ids must be distinct** — no two running Hermes gateways may share the same Feishu app_id. If two gateways share an app_id, the last-connected one steals all WebSocket events from the first (both DM and group), making the first bot appear completely silent despite showing "connected" in logs. Always verify: `grep "app_id" ~/.hermes/config.yaml` and `grep "app_id" ~/.hermes/profiles/<name>/config.yaml` — all must differ.
> ⚠️ **Never set default profile's feishu app_id to libai's app_id (`cli_aafa2c6a83b85bee`)**, even temporarily. The Feishu WebSocket connection will be claimed by whichever process connected last, starving the other bot of ALL events (both DM and group). If default and libai share the same app_id, only one will respond — the other will be completely silent despite showing "connected" in logs. Default profile needs its OWN unique Feishu app (e.g. `cli_aae7a0320738dbeb`) if DM capability is required.

> ⚠️ **All app_ids must be distinct** — no two running Hermes gateways may share the same Feishu app_id. If two gateways share an app_id, the last-connected one steals all WebSocket events from the first (both DM and group), making the first bot appear completely silent. Always verify: `grep "app_id" ~/.hermes/config.yaml` and `grep "app_id" ~/.hermes/profiles/<name>/config.yaml` — all must differ.

> ⚠️ **Platform-level Feishu group limitation**: When two bots are in the same Feishu group, `@mention` events are delivered to **only the earliest-joined bot**. The later-added bot receives **no @mention events at all** — this is a Feishu platform restriction, not a config issue. Workaround: ensure only one bot per group, or accept that only the first-joined bot will respond.

> ⚠️ **Pairing files are per-HERMES_HOME, not shared**: `~/.hermes/platforms/pairing/feishu-approved.json` is the **default profile's** store. When a gateway runs with `HERMES_HOME=~/.hermes/profiles/libai`, it reads `~/.hermes/profiles/libai/platforms/pairing/feishu-approved.json` — a completely separate file. Editing the wrong one has no effect. Always check which profile's directory the target gateway is using before manually editing pairing JSON.

## Setup Steps

### 1. Create profile directory
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
When running two Feishu bots simultaneously, BOTH must be started as truly independent gateway processes — NOT as a subprocess of the main bot's agent. If cutegirl runs as a subprocess (e.g. via "启动妹妹" agent command), a main bot restart kills it.

⚠ **CRITICAL: Always use `HERMES_HOME=` env var — `cd` into the profile dir is NOT sufficient.**
The gateway resolves its lock file path via `_get_gateway_lock_path()` which calls `_get_process_hermes_home()`. That function reads the `HERMES_HOME` environment variable, **not** the shell's current working directory. So `cd ~/.hermes/profiles/libai && hermes gateway run` still writes lock files to `~/.hermes/` (the default HERMES_HOME), causing conflicts with other gateways. Always use the explicit env var form:

```bash
# ✅ Correct — each gateway gets its own lock files
HERMES_HOME=~/.hermes/profiles/libai hermes gateway run
HERMES_HOME=~/.hermes/profiles/cutegirl hermes gateway run

# ❌ Wrong — lock files collide at ~/.hermes/ despite the cd
cd ~/.hermes/profiles/libai && hermes gateway run
```

⚠ Use `terminal(background=True)` in Hermes agent, NOT shell `&`/nohup — shell background wrappers are rejected.

**Neither gateway uses `--replace`** when started with the `HERMES_HOME=` pattern — they each have their own lock files and never conflict. `--replace` is only needed when restarting a single bot in place (no other bots running).
### 4. Start independent gateway (dual-gateway setup)

Each bot = one Hermes gateway process, started independently. The default profile (主bot) uses no `HERMES_HOME` override; all other profiles MUST use `HERMES_HOME=` env var.

**⚠️ Use `terminal(background=True)` in Hermes agent, NOT shell `&`/nohup — shell background wrappers are rejected.**

**Key rule: never use `--replace` when multiple bots are already running, and never use `cd` instead of `HERMES_HOME=` for non-default profiles.**

The `--replace` flag reads the SHARED `~/.hermes/gateway.pid` file and sends SIGTERM to whatever PID is stored there — it does NOT check which profile that PID belongs to. Using `--replace` on a second bot will kill the first bot's process directly. This is NOT a dispatcher conflict — it's a direct process kill.

The `HERMES_HOME=` approach eliminates lock-file collisions entirely: each profile directory gets its own lock files, so multiple bots can run simultaneously without `--replace`.

```bash
# Kill any existing gateways first
pkill -f "hermes gateway" 2>/dev/null; sleep 2

# Start libai (non-default profile — MUST use HERMES_HOME=)
terminal(background=true,
  command="HERMES_HOME=~/.hermes/profiles/libai hermes gateway run",
  notify_on_complete=true)

# Start default/主bot (uses ~/.hermes/ by default — no HERMES_HOME override needed)
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
- [Pairing & User Management](references/pairing-and-user-management.md) — manual JSON approval, finding open_ids, group allowlist config
- [Wenyu profile config template](references/wenyu-config.yaml) — 文娱写作bot SOUL + config.yaml 模板，建新 bot 时可直接复制修改

## References
```yaml
_config_version: 33
model:
  base_url: https://api.minimaxi.com/anthropic
  default: MiniMax-M2.7
  provider: minimax-cn

agent:
  system_prompt: |
    # Bot 性格设定
    ...

platforms:
  feishu:
    enabled: true
    extra:
      app_id: cli_aae7a3ad78b8dbe3
      app_secret: xxxxxxxxxxxxxxxx
      require_mention: false
      default_group_policy: open
      group_rules:
        oc_group_id_here:
          policy: open
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

Each additional bot gets its own HERMES_HOME profile directory and is started the same way:

```bash
pkill -f "hermes gateway" 2>/dev/null; sleep 2

# Start all bots — no --replace, no conflicts
HERMES_HOME=~/.hermes/profiles/libai hermes gateway run &
HERMES_HOME=~/.hermes/profiles/cutegirl hermes gateway run &
HERMES_HOME=~/.hermes/profiles/<newbot> hermes gateway run &
```

Each profile directory has its own lock files. The gateways don't interfere with each other.

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
- **Missing model config**: Profile config without `model:` block → gateway uses Anthropic as default → all messages fail with "Connection error". Always include `model:` block in new profiles.
- **Same app ID**: Two gateways with same Feishu app ID → lock error `Another local Hermes gateway is already using this Feishu app_id`. Each bot needs its own App.
- **Heredoc blocked**: `cat > file << EOF` heredoc is blocked. Use `write_file` tool instead.
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

- **`feishu_seen_message_ids.json` as a message-receipt diagnostic**: Located at `~/.hermes/profiles/<name>/feishu_seen_message_ids.json`, this file tracks every message ID the Feishu WebSocket has received and deduplicated. If the bot was receiving messages but suddenly stopped, the timestamps in this file freeze at the last received message. Compare the timestamps between the working bot and the new bot:
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
  1. Clear stale lock files in both profiles: `rm -f ~/.hermes/gateway.lock ~/.hermes/gateway.pid ~/.hermes/profiles/cutegirl/gateway.lock ~/.hermes/profiles/cutegirl/gateway.pid`
  2. Start **cutegirl first** (no `--replace`): `cd ~/.hermes/profiles/cutegirl && hermes gateway run` (use `terminal(background=true)`)
  3. Start **default second** (with `--replace`): `cd ~ && hermes gateway run --replace` (use `terminal(background=true)`)
  4. `sleep 8` then `hermes gateway list` — both should show `✓`
  5. Verify env: `cat /proc/<pid>/environ | tr '\0' '\n' | grep HERMES_HOME` — must show the correct profile dir path for each process
  6. Confirm WebSocket: `grep "connected to wss://msg-frontier.feishu.cn" profiles/<name>/logs/gateway.log`
  7. If lock error: a ghost wrapper process is still alive — `kill <stale_pid>` and retry
  8. **Always verify after any restart**: check `hermes gateway list` and confirm both profiles are running
  9. **Startup-order rule**: The first gateway started must NOT use `--replace` (it exits with "another gateway instance starting during our startup"). Only the second gateway needs `--replace` to override the lock conflict check.
  10. **Licai profile** (`~/.hermes/profiles/licai/`) uses `hermes gateway run` without `HERMES_HOME=` prefix — the profile directory structure already provides isolation. Startup: `cd ~/.hermes/profiles/licai && hermes gateway run` (background=true).

- **SSL EOFError crash and silent group-event blackout**: The Feishu WebSocket can drop with `receive message loop exit, err: no close frame received or sent` followed by SSL errors during reconnection. Two distinct failure modes:
  - **Crash mode** (gateway process exits): restart the gateway.
  - **Blackout mode** (gateway stays alive, DM works, group events stop): the WebSocket reconnection appears to succeed (`connected to wss://msg-frontier.feishu.cn`) but group message events stop arriving. DM continues to work. Root cause is upstream — Feishu stops routing group events to the app despite the WebSocket appearing connected. Fix: (a) restart the gateway, (b) remove and re-add the bot to the group, or (c) re-publish the app in 飞书开放平台 (events subscription can silently lose its 群组 scope after an app update). Diagnostic: `grep "Inbound group" profiles/<name>/logs/gateway.log` — if empty while the bot is running and DM works, this is the blackout mode.

- **Cannot restart gateway from inside the running gateway process**: Calling `kill <pid>` on a gateway from a terminal where that same gateway's shell is the parent shell, then immediately launching a new gateway in the same terminal, fails with `Blocked: cannot restart or stop the gateway from inside the gateway process`. Workaround: use a *different* terminal/shell to kill and restart. Or use `hermes gateway restart --profile <name>` from a separate shell — it works even when the target gateway is the current process's parent.

## Related Skills
- **feishu-bitable** — 飞书多维表格读写脚本（`~/.hermes/scripts/feishu_bitable.py`）
- **feishu-wiki-document-read** — 读取老公发的飞书 wiki/docx 链接内容（REST API 读取，无法用 web_extract）
