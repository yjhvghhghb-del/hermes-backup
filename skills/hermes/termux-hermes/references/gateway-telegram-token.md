# Gateway Telegram Bot Token Resolution

## Problem
Gateway log shows: `[Telegram] No bot token configured` on `cutegirl` profile, even though `TELEGRAM_BOT_TOKEN=8800919754:***` is set in `~/.hermes/.env` and `bot_token: 8800919754:***` is in `~/.hermes/config.yaml`.

## Root Cause
When the gateway starts, it reads `bot_token` from the **main** `~/.hermes/config.yaml`, NOT from `~/.hermes/profiles/cutegirl/config.yaml`. The main config's token `8800919754:***` is the "主bot" (main bot) and is the one that successfully connects.

The `cutegirl` profile has no `telegram:` section in its `config.yaml` at all — it inherits the main config's Telegram platform settings implicitly via the gateway's multiplex. The error log `[Telegram] No bot token configured (profile: cutegirl)` means that when the cutegirl profile tried to initialize its own Telegram platform adapter, it found no token configured in its profile config.

This is **normal and expected behavior** — the main bot works fine. The cutegirl profile's Telegram "failure" is a non-issue because cutegirl is primarily a Feishu-only profile and uses the main bot's Telegram connection for any Telegram needs.

## Key Facts
- Main gateway uses `~/.hermes/config.yaml` → bot_token `8800919754:***` → ✓ telegram connected
- Per-profile config files (e.g. `cutegirl`) are for that profile's **agent** settings, not platform tokens
- Platform tokens (Telegram, Feishu, QQBot) are read from the main config
- The gateway multiplexes all profiles through the same platform connections
