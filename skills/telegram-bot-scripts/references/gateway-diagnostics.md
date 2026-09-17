# Gateway Diagnostics Reference

## Quick Status Checks

```bash
# Is the gateway running?
hermes gateway status

# All profiles and their gateway state
hermes gateway list

# Process check
ps aux | grep -E 'hermes|gateway' | grep -v grep

# Recent gateway log
tail -30 ~/.hermes/logs/gateway.log
```

## Platform Connection Status (from logs)

```bash
# Telegram
grep -E "Connected to Telegram|Telegram.*reconnect|polling restarted" ~/.hermes/logs/gateway.log | tail -5

# Feishu
grep -E "feishu.*connected|Connected in websocket mode" ~/.hermes/logs/gateway.log | tail -3

# QQ
grep -E "qqbot.*Connected|Ready.*session_id" ~/.hermes/logs/gateway.log | tail -3
```

## Startup / Restart Pattern

```bash
# Kill stale gateway
pkill -f "hermes gateway" 2>/dev/null; sleep 2

# Start fresh
terminal(background=true, command="hermes gateway run", notify_on_complete=true)

# Verify all 3 platforms connected
sleep 6 && tail -15 ~/.hermes/logs/gateway.log
```

## Default Profile Telegram Bot Startup

The default profile has Telegram configured via `~/.hermes/config.yaml` `platforms.telegram` block (token `8800919754`), NOT in a profile subdirectory. Start it with:

```bash
terminal(background=true, command="hermes gateway run --profile default", notify_on_complete=true)
# OR equivalently (no --profile flag for default):
terminal(background=true, command="hermes gateway run", notify_on_complete=true)
```

Verify: `hermes gateway list` should show `✓ default — PID NNNN`.

## Common Errors

- `invalid choice: 'run'` → used `hermes run --profile` instead of `hermes gateway run`
- `Another gateway instance is already running` → stale lock file; kill stale python process directly (not just the bash wrapper)
- Telegram repeatedly reconnecting → proxy `127.0.0.1:7890` may be down
