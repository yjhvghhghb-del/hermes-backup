# Proxy Auto-Discovery Config

## Known Proxy IPs (as of 2026-07-31)

| IP | Ports | Status |
|---|---|---|
| 10.1.252.196 | 7891, 7890 | ✅ Primary |
| 192.168.110.40 | 7891, 7890 | Backup |
| 192.168.110.225 | 7891, 7890 | Backup |
| 172.19.0.1 | 7891, 7890 | ✅ Discovered by auto-scan |

## Auto-Scan Cron Job
- Job ID: `57a86162ad9f`
- Scans: `192.168.110.0/24`, `10.1.252.0/24`
- Runs: every 5 minutes
- Best proxy selected by lowest latency

## User Preference
- Streaming: 4 chars minimum, 0.3s interval
- Streaming URL: `telegram_stream.py <chat_id> <message>`
- Sticker: `send_sticker.py <chat_id> -p <pack> -n <index>`
