---
name: gateway-architecture
description: One gateway, all profiles. Check logs not gateway list.
tags: [hermes, gateway, termux, multiplex]
---

# Hermes Gateway Architecture

## Core Model: Single Gateway, Multiple Platforms

On a single-node deployment (Termux, Linux server), there is **one gateway process** at port 9119. All messaging platforms (Feishu, Telegram, QQBot, etc.) connect through it regardless of how many profiles exist.

`multiplex_profiles: true` in `~/.hermes/config.yaml` is the default. When active:
- The single gateway handles ALL profiles simultaneously
- Each profile's `config.yaml` platforms section is loaded by the same gateway

## Profile Startup Sequence — CORRECTED (2026-09-14)

The key insight: when `multiplex_profiles: true`, the default gateway with `--replace` **absorbs** the platform connections of profile gateway subprocesses that are already running. The startup sequence must be:

### Step 1 — Kill everything, clean locks
```bash
killall hermes 2>/dev/null
sleep 2
rm -f ~/.hermes/gateway.lock ~/.hermes/gateway.pid
```

### Step 2 — Start profile gateway processes (distinct tokens first)
Each uses: `hermes profile use <name> && hermes gateway run`
```bash
# These have distinct Telegram tokens — must run separately
hermes profile use siliconflow && hermes gateway run  # background=true
hermes profile use geekwife && hermes gateway run     # background=true
# These have distinct Feishu app_ids
hermes profile use wenyu && hermes gateway run        # background=true
hermes profile use licai && hermes gateway run        # background=true
hermes profile use libai && hermes gateway run        # background=true
sleep 15  # let them init their platform connections
```

### Step 3 — Start main gateway with --replace
```bash
hermes profile use default && hermes gateway run --replace  # background=true
```
The `--replace` flag tells the new main gateway to take over platform connections from running profile gateways.

### Step 4 — Restart distinct-token profiles (they were killed by --replace)
```bash
hermes profile use siliconflow && hermes gateway run  # background=true
hermes profile use geekwife && hermes gateway run     # background=true
# wenyu/licai/libai are NOT restarted — their Feishu is handled by main gateway
```

### Step 5 — Verify
```bash
hermes profile use default && hermes gateway status
tail -30 ~/.hermes/logs/gateway.log | grep -E '✓|✗|connected|failed'
```

**CORRECTED COMMAND SYNTAX:**
- WRONG: `hermes profile run siliconflow` → `error: argument profile_action: invalid choice 'run'`
- WRONG: `hermes --profile siliconflow gateway run` → not recognized
- RIGHT: `hermes profile use siliconflow && hermes gateway run`

**What actually happens:** `hermes profile use X && hermes gateway run` starts a SEPARATE gateway process for that profile (not multiplexed). The `--replace` on the main gateway absorbs their platform connections as subprocesses, then kills the parent shell processes. The profile gateway Python processes survive as children of the main gateway.

**Conflicting Feishu app_ids:** wenyu/cutegirl share `cli_aae7a3ad78b8dbe3` and libai/licai share another. Only ONE Feishu websocket per app_id. The multiplexed main gateway handles this by running one WS per unique app_id and routing to all sharing profiles.

## Profile Startup — HYBRID MODEL (2026-09-03)

`multiplex_profiles: true` means the default gateway CAN serve multiple profiles, BUT some profiles still need **separate gateway processes** because they have distinct platform tokens that can't share one inbound connection. The rule:

**Multiplexed (run under default gateway):**
```bash
hermes gateway run
```
Profiles served by the multiplexer: `default`, `wenyu`, `libai`, `licai` (these have duplicate/shared tokens — the default gateway's single Feishu WS handles them all)

**Separate processes (required for distinct platform tokens):**
```bash
hermes --profile cutegirl gateway run &
hermes --profile geekwife gateway run &
hermes --profile siliconflow gateway run &
```

If you try to start a profile that the multiplexer already serves, you get:
```
✗ The default gateway is running as a profile multiplexer and already serves profile 'X'.
```
This is **not an error** — it means that profile is already live under the default gateway. `hermes gateway list` will show it as ✗ but it's actually running.

## Verifying Connections

`hermes gateway list` is **partially reliable** — interpret it correctly:

| Profile type | List shows | Reality |
|---|---|---|
| Separate process (cutegirl/geekwife/siliconflow) | ✓/✗ accurately | Trust this |
| Multiplexed (wenyu/libai/licai) under default | ✗ even when running | DON'T trust this |

**For multiplexed profiles, check the gateway log:**
```bash
tail ~/.hermes/logs/gateway.log | grep -E '✓|✗|connected|failed'
```
Look for lines like:
```
✓ feishu connected (profile: licai)
✓ feishu connected (profile: wenyu)
```

**Quick status command:**
```bash
hermes gateway status
```

## Profile Architecture Summary (2026-09-03)

**Startup rule:** default gateway (multiplexed) + separate processes for distinct platform tokens.

| Profile | Platform | Startup mode | Token conflict |
|---|---|---|---|
| default | Telegram, QQBot | default gateway (multiplex) | — |
| wenyu | Feishu | default gateway (multiplex) | shares app_id with cutegirl |
| libai | Feishu | default gateway (multiplex) | shares app_id with licai |
| licai | Feishu | default gateway (multiplex) | shares app_id with libai |
| cutegirl | Feishu | **separate process** | distinct token |
| geekwife | Telegram | **separate process** | distinct token |
| siliconflow | Telegram | **separate process** | distinct token |

Key insight: profiles with the SAME app_id/token (wenyu+cutegirl, libai+licai) cannot each have their own gateway process — only one Feishu WS connection per app_id. The multiplexed default gateway handles this by running one WS and routing to all sharing profiles. Profiles with distinct tokens must run separately.

## Telegram Reconnect Wedging (Android/Termux)

Symptom in gateway.log:
```
Telegram reconnect task wedged for XXXXs with no ladder progress
init deadline (30s) expired but the event loop has not processed the expiry
CRITICAL gateway.shutdown_watchdog: Gateway event loop missed 3 consecutive liveness probes
```

**Cause**: Telegram polling thread blocks the event loop on Android/Termux, preventing timeout mechanism from firing. The watchdog eventually kills the gateway.

**Fix**: `hermes gateway run --replace` to restart. This is a known Android Termux issue.

## Telegram Token Verification

When a Telegram bot returns 404/401, verify if it's the token or the proxy:
```bash
curl -s --max-time 5 "https://api.telegram.org/bot{TOKEN}/getMe"
# With proxy:
curl -s --max-time 5 --proxy "socks5h://127.0.0.1:7890" "https://api.telegram.org/bot{TOKEN}/getMe"
```

**Token status (2026-09-14):**
- 8800919754 (主bot): 401 Unauthorized via API call, BUT gateway log shows `✓ telegram connected` — token is valid, the API check fails due to proxy/mask issue. WORKING.
- siliconflow 8363232963: WORKING (used by main gateway multiplexer)
- geekwife 8637317610: WORKING (separate process)

If `curl getMe` returns 401 but logs show successful connection, trust the logs — the gateway may use a different proxy or the token display masking causes confusion.

## Common Errors

**Error**: `The default gateway is running as a profile multiplexer and already serves profile 'X'.`
**Cause**: Tried to start a per-profile gateway when multiplexer is active.
**Fix**: Don't. The single gateway already handles it.

**Error**: `asyncio RuntimeError: Task attached to a different loop` in Feishu WebSocket
**Cause**: Feishu SDK bug with multiple WS connections in same process
**Impact**: Usually harmless — the connection still establishes and works despite the error log
