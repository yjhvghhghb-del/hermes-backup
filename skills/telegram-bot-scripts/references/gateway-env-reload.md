# Gateway .env Reload — When API Keys Change

## Core Rule
**Hermes reads `.env` once at startup and never again for the lifetime of that process.** Any change to `.env` (API key rotation, token refresh, etc.) requires a full gateway restart — config hot-reload does NOT apply to secrets.

## How to Force a Clean Restart

### Step 1: Kill the running gateway
```bash
# Find all hermes gateway processes
ps aux | grep 'hermes gateway' | grep -v grep

# Kill the WRAPPER bash process (PID from ps aux first column)
# The wrapper is what shows up in ps aux — killing it also terminates the child python process
kill -9 <WRAPPER_PID>

# Alternative: kill by name (catches all variants)
pkill -f "hermes gateway" 2>/dev/null

# Verify it's dead
ps aux | grep 'hermes gateway' | grep -v grep
```

### Step 2: Start fresh with `--replace`
```bash
hermes gateway run --replace
```

The `--replace` flag tells the new gateway process to replace any stale one that didn't die cleanly.

**Why `hermes gateway run --replace` and not `hermes gateway`?**
- Plain `hermes gateway` refuses with: "Another gateway instance is already running"
- `hermes gateway run --replace` atomically replaces the old process

### Step 3: Verify the new process read the updated .env
```bash
# Wait 15s for startup, then check
sleep 15 && ps aux | grep 'hermes gateway' | grep -v grep

# Verify MINIMAX key is in the new process env
cat /proc/<NEW_PID>/environ | tr '\0' '\n' | grep MINIMAX_CN_API_KEY
```

## Common Trap: Multiple Stale Background Processes

When restarting repeatedly, multiple `bash -lic` wrapper processes accumulate:
```
u0_a767  12458  0.0  0.0 10834948 4228 ?  Ss  1970  0:00 bash -lic ... hermes gateway
u0_a767  16425  0.0  0.0 10834948 4228 ?  Ss  1970  0:00 bash -lic ... hermes gateway
u0_a767  21341  9.3  2.5 11888000 400512 ? Sl  1970  0:16 python ... hermes gateway run --replace
```

Only the **latest** (21341) is the real gateway. Kill ALL stale wrappers before starting fresh.

## The `.env` Key Display Artifact

Terminal commands like `grep`, `cat`, `strings` may display key values with `...` in the middle:
```
MINIMAX_CN_API_KEY=sk-cp-...opK4
```

This is a **terminal column-width truncation**, NOT what the file actually contains. The full key is in the file — use `od -c` or Python binary read to confirm:
```bash
grep MINIMAX ~/.hermes/.env | od -c
```
or
```python
with open('~/.hermes/.env', 'rb') as f:
    raw = f.read()
idx = raw.find(b'MINIMAX_CN_API_KEY=')
print(raw[idx:idx+200])  # shows full bytes
```

## Profile .env vs Global .env — Which One Wins?

Each Hermes profile has its own `.hermes/profiles/<name>/.env`. The gateway reads ALL profile `.env` files at startup and merges them.

**Priority order** (highest to lowest):
1. Profile-specific `.env` (`~/.hermes/profiles/<profile>/.env`)
2. Global `.env` (`~/.hermes/.env`)

If a key appears in both, the profile-level value takes precedence.

**For the MINIMAX_CN_API_KEY used by `minimax-cn` provider**: Check which profile(s) need it. If the global `.env` has it but a profile doesn't, the profile inherits it from global. If a profile has its own copy, that overrides.

## Verified Restart Log
```
# Before restart — old key (sk-211...87a2) was INVALID
2026-08-24 11:02:25,678 WARNING Primary provider auth failed: No usable credentials found for provider 'minimax-cn'

# After restart with updated .env — no auth errors
2026-08-24 11:17:36,077 INFO gateway.run: inbound message: platform=telegram user=胖蝦球 msg='在吗'
2026-08-24 11:17:48,160 INFO gateway.run: response ready: platform=telegram chat=877708648 time=12.1s
```
