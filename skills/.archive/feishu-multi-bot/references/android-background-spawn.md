# Android/Termux Background Spawn Workaround (updated 2026.08.21)

## Problem
On Android/Termux, `hermes --profile <name>` exits immediately with:
```
Warning: Input is not a terminal (fd=0).
Shutting down… (finalizing session)
```
Root cause: prompt_toolkit detects no TTY on stdin and Hermes exits. This is NOT a config problem.

## Working Solution: `gateway run`

```bash
# Named profiles — --profile flag goes IMMEDIATELY after `hermes`
hermes --profile <name> gateway run

# Default profile (主bot / Telegram) — NO --profile flag
hermes gateway run
```

The `gateway run` subcommand bypasses the TUI prompt_toolkit path entirely — no TTY needed.

**⚠️ WRONG commands (avoid these):**
```bash
hermes serve --gateway              # ❌ "unrecognized arguments: --gateway"
hermes --profile <name> serve       # ❌ "unrecognized arguments: serve"
hermes --profile <name> gateway     # ❌ missing subcommand "run"
hermes --profile <name>            # ❌ exits immediately: "Input is not a terminal"
hermes gateway run --profile <name> # ❌ --profile goes after hermes, not after subcommand
```

**⚠️ Use terminal(background=true) in Hermes agent, NOT shell &/nohup** — shell background wrappers are rejected by the terminal tool.

**Key fact confirmed 2026.08.20:** The default profile (主bot/Telegram) uses `hermes gateway run` with NO `--profile` flag. All named profiles use `hermes --profile <name> gateway run`. Using `--profile default` is wrong for the default bot — it would look for a profile directory called "default" instead of using the main `~/.hermes/` directory.

## Verified Startup Log (2026.08.21)

| Profile | Command | Result |
|---------|---------|--------|
| default | `hermes gateway run` | ✓ PID 8221 |
| geekwife | `hermes --profile geekwife gateway run` | ✓ PID 5159 |
| licai | `hermes --profile licai gateway run` | ✓ PID 4947 |
| siliconflow | `hermes --profile siliconflow gateway run` | ✓ PID 5151 → PID 29965 (restarted after nemo_relay crash) |
| wenyu | `hermes --profile wenyu gateway run` | ✓ PID 5141 |
| cutegirl | `hermes --profile cutegirl gateway run` | ✗ blocked by wenyu (same app_id `cli_aae7a3ad78b8dbe3`) |
| libai | `hermes --profile libai gateway run` | ✗ blocked by licai (same app_id `cli_aafa2c6a83b85bee`) |

**nemo_relay crash and auto-recovery (2026.08.21):** siliconflow gateway's python child process crashed with `ModuleNotFoundError: No module named 'nemo_relay'` — process exited cleanly (exit code 0, "Goodbye! ⚕"). Restarted successfully with same command. Telegram polling re-established and bot responded to subsequent messages (`response ready ... time=9.9s`).

**Common errors from wrong commands (2026.08.21 repro):**
- `hermes --profile <name>` without `gateway run` → "Warning: Input is not a terminal (fd=0). Shutting down…"
- `hermes gateway run --profile <name>` (--profile after subcommand) → "error: unrecognized arguments: --profile"
- `hermes --profile <name> gateway` (no `run`) → exits with code 1 within seconds
- Shell `&`/nohup → "Foreground command uses shell-level background wrappers — use terminal(background=true)"

## App_id Collision Status (2026.08.21)

| Profile | app_id | Running? |
|---------|--------|----------|
| wenyu | `cli_aae7a3ad78b8dbe3` | ✓ (wins over cutegirl) |
| cutegirl | `cli_aae7a3ad78b8dbe3` | ✗ (blocked by wenyu) |
| licai | `cli_aafa2c6a83b85bee` | ✓ (wins over libai) |
| libai | `cli_aafa2c6a83b85bee` | ✗ (blocked by licai) |
| geekwife | (Telegram only) | ✓ |
| siliconflow | (Telegram only) | ✓ |
| default | (QQ/Telegram) | ✓ |

Only ONE per collision group can run at a time. Group A (`cli_aafa2c6a83b85bee`): licai wins. Group B (`cli_aae7a3ad78b8dbe3`): wenyu wins.

**Confirmed 2026.08.21:** 5 bots running simultaneously — default + geekwife + licai + siliconflow + wenyu.

## Deprecated Scripts
- `~/.hermes/scripts/run-profile.sh` — setsid approach, no longer works
- `~/.hermes/scripts/run-profile.py` — PTY approach, no longer works
Both replaced by `hermes --profile <name> gateway run`.
