# Gateway Startup Log Reference

## Normal startup sequence
```
2026-08-24 05:58:46,758 INFO gateway.run: Starting Hermes Gateway...
2026-08-24 05:58:46,762 INFO gateway.run: Session storage: ...
2026-08-24 05:58:46,864 INFO gateway.run: Connecting to qqbot...
2026-08-24 05:58:47,751 INFO gateway.run: ✓ qqbot connected
2026-08-24 05:58:47,753 INFO gateway.run: Connecting to feishu...
2026-08-24 05:58:48,269 INFO hermes_plugins.feishu_platform.adapter: [Feishu] Connected in websocket mode (feishu)
2026-08-24 05:58:48,275 INFO gateway.run: ✓ feishu connected
2026-08-24 05:58:48,292 INFO gateway.run: Connecting to telegram...
2026-08-24 05:58:48,303 WARNING hermes_plugins.telegram_platform.adapter: [Telegram] Discovering Telegram API fallback IPs via DNS-over-HTTPS…
2026-08-24 05:59:09,229 INFO hermes_plugins.telegram_platform.adapter: [Telegram] Connected to Telegram (polling mode)
2026-08-24 05:59:09,598 INFO gateway.run: ✓ telegram connected
2026-08-24 05:59:09,613 INFO gateway.run: Gateway running with 3 platform(s)
2026-08-24 05:59:10,729 INFO gateway.run: Press Ctrl+C to stop
```

## Platform names in log
- QQBot: `gateway.platforms.qqbot.adapter`
- Feishu: `hermes_plugins.feishu_platform.adapter`
- Telegram: `hermes_plugins.telegram_platform.adapter`

## Known stale-state issue
If gateway was killed ungracefully (SIGKILL/OOM), next start shows:
```
WARNING gateway.lifecycle_ledger: Previous gateway life (pid=X, ...) exited UNCLEANLY
```
The gateway still starts normally — this is just informational.

## Telegram reconnection pattern
Telegram may show repeated warnings before connecting:
```
Connecting to Telegram (attempt 1/8)…
Connect attempt 1/8 failed: httpx.ConnectError
```
Normal resolution: it eventually connects after ~3 attempts. If stuck at attempt 8/8, check proxy/network.
