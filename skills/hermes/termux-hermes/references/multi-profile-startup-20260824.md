# Multi-Profile Startup — 2026.08.24 Confirmed

## What Actually Happened

6 profiles started with `terminal(background=true, command="hermes --profile X serve")`. Each returned within seconds (process stays alive, not exit). All 6 profiles became accessible on the same 9119 port.

**Discovery:** `hermes --profile X serve` does NOT bind its own HTTP port. It registers with the already-running gateway at 9119. All profiles share one port.

## Key Behaviors Confirmed

- `hermes --profile X serve` → process stays alive (not "exits immediately")
- Same 9119 port shared by all profiles — no `--isolated`, no `--port` needed
- Health endpoint per profile: `curl "http://127.0.0.1:9119/api/health?profile=geekwife"`
- All 6 returned `{"ok":true,"version":"0.19.1","auth_required":false}`

## Canonical Startup Sequence

```bash
# All 6 in parallel — each is a separate background terminal() call
terminal(background=true, command="hermes --profile cutegirl serve")
terminal(background=true, command="hermes --profile geekwife serve")
terminal(background=true, command="hermes --profile libai serve")
terminal(background=true, command="hermes --profile licai serve")
terminal(background=true, command="hermes --profile siliconflow serve")
terminal(background=true, command="hermes --profile wenyu serve")
```

## Verification

```bash
# All profiles healthy
for p in cutegirl geekwife libai licai siliconflow wenyu; do
  echo "=== $p ==="; curl -s "http://127.0.0.1:9119/api/health?profile=$p"
done

# Process count: main gateway + 6 profile processes = 7+ python processes
ps aux | grep hermes | grep -v grep | wc -l
```

## What Does NOT Work

- `nohup ... &` or shell `&` in foreground terminal → SIGKILL on Termux
- `hermes --profile X` (without `serve` or `gateway run`) → exits immediately: "Input is not a terminal (fd=0)"
- `hermes --profile X gateway run` (with explicit `gateway run`) → works but unnecessary; `serve` is sufficient

## Profile Status (2026.08.24)

| Profile | Platform | Health |
|---------|----------|--------|
| cutegirl | 飞书 | ✅ ok |
| geekwife | Telegram | ✅ ok |
| libai | 飞书 | ✅ ok |
| licai | 飞书 | ✅ ok |
| siliconflow | Telegram | ✅ ok |
| wenyu | 飞书 | ✅ ok |
