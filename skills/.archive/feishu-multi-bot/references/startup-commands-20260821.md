# Bot Startup Commands (2026.08.25 updated)

## Current approach: single multiplexed gateway (2026.08.25)

All profiles run inside ONE gateway process via `gateway.multiplex_profiles: true`. No need to start separate processes.

```bash
# Standard startup
pkill -f "hermes gateway" 2>/dev/null; sleep 2
hermes gateway 2>&1 &

# Verify all connected
sleep 20 && grep "feishu.*connected.*profile" ~/.hermes/logs/gateway.log
```

## Legacy multi-process approach (deprecated — for reference only)

The separate-process approach below is no longer needed and introduces app_id collision issues. Kept here for historical reference only.

| Command | Status |
|---------|--------|
| `hermes --profile cutegirl gateway run` | Deprecated — separate process |
| `hermes --profile geekwife gateway run` | Deprecated — separate process |
| `hermes --profile libai gateway run` | Deprecated — separate process |
| `hermes --profile licai gateway run` | Deprecated — separate process |
| `hermes --profile siliconflow gateway run` | Deprecated — separate process |
| `hermes --profile wenyu gateway run` | Deprecated — separate process |
| `hermes gateway run` | Deprecated — separate process |

## Verify connected

```bash
# All Feishu profiles — check log
grep "feishu.*connected.*profile" ~/.hermes/logs/gateway.log

# Quick status
ps aux | grep 'hermes gateway' | grep -v grep
```
