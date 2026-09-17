# Hermes Backup — Telegram Notification

After each backup run, send a short report to 老公 via Telegram.

## Sending a Backup Report

```bash
TOKEN=$(grep TELEGRAM_BOT_TOKEN ~/.hermes/.env | cut -d= -f2 | tr -d ' ')
CHAT_ID=877708648
curl -s "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  -d "chat_id=${CHAT_ID}&text=✅ Hermes每日备份完成（$(date +%Y%m%d））&disable_notification=true"
```

Always extract bot token from `~/.hermes/.env` — never hardcode it.

## Token Validity Check (REQUIRED before sending)

```bash
TOKEN=$(grep TELEGRAM_BOT_TOKEN ~/.hermes/.env | cut -d= -f2 | tr -d ' ')
STATUS=$(curl -s "https://api.telegram.org/bot${TOKEN}/getMe" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ok',False))")
if [ "$STATUS" != "True" ]; then
  echo "Telegram bot token invalid (bot deleted or token revoked)"
  # Try fallback tokens if configured
  for FALLBACK_TOKEN in 8363232963 8637317610; do
    FALLBACK_STATUS=$(curl -s "https://api.telegram.org/bot${FALLBACK_TOKEN}/getMe" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ok',False))" 2>/dev/null)
    [ "$FALLBACK_STATUS" = "True" ] && TOKEN="$FALLBACK_TOKEN" && break
  done
fi
```

If all tokens are dead (all return `{"ok":false,"error_code":404}`), the notification silently fails — the backup still ran fine, just can't reach 老公.

**Known dead tokens (2026-09-11, confirmed all 3 returning 401 Unauthorized):**
- `8800919754` → 401 (primary, from `TELEGRAM_BOT_TOKEN` in `~/.hermes/.env`)
- `8363232963` → 401 (siliconflow profile)
- `8637317610` → 401 (geekwife profile)

**Error codes observed:**
- `401 Unauthorized` — bot token revoked or invalidated (current state, all 3 bots)
- `404 Not Found` — bot was deleted via @BotFather (`getMe` returns `{"ok": false, "error_code": 404}`)
- `403 Forbidden` — bot blocked by user

All Telegram bots are returning 401. Notification cannot be sent until a new bot token is obtained from @BotFather.

**Fix**: Get a new bot token from @BotFather and update `TELEGRAM_BOT_TOKEN` in `~/.hermes/.env`. Run `curl "https://api.telegram.org/bot<TOKEN>/getMe"` to verify before relying on it.

## Message Format Tips

- Keep it short — one screenshot-friendly block
- Use emoji as status indicators: ✅ success, ⚠️ warning, ❌ error
- Include file size (`du -h`) so老公 can verify backup is non-empty
- If push succeeds, replace the ⚠️ line with "✅ GitHub 推送成功"

## Cron Integration

The cron job calls this script; add Telegram send as the final step of `backup.sh`:

```bash
# Inside backup.sh, after git push:
TOKEN=$(grep TELEGRAM_BOT_TOKEN ~/.hermes/.env | cut -d= -f2 | tr -d ' ')
curl -s "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  -d "chat_id=877708648" \
  -d "text=📦 备份侠报告 $(date +%H:%M)

✅ 备份完成: $(du -h ~/hermes-backup-daily.tar.gz | cut -f1)

✅ GitHub 推送成功" \
  || echo "Telegram通知失败"
```

> ⚠️ Never hardcode a bot token in scripts. Always extract from `~/.hermes/.env`.
