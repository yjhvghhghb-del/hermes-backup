---
name: telegram-bot-scripts
description: "Telegram bot scripts: stickers, streaming, proxy API calls."
trigger: "Build or run a Telegram bot script (sticker, streaming, proxy API) from Termux."
---

# Telegram Bot Scripts — Build & Run

## What This Is
A reusable pattern for writing Python scripts that interact with the Telegram Bot API from Termux. Covers streaming text output, sticker sending, and proxy auto-discovery.

## Architecture

```
Script → SOCKS5 Proxy → Telegram Bot API → User's Telegram chat
         ↑
    Auto-discovers from 8 candidate IPs/ports
```

## Proxy Auto-Discovery Pattern

```python
import socket, requests

PROXIES_LIST = [
    ("10.1.252.196", 7891),
    ("10.1.252.196", 7890),
    ("192.168.110.40", 7891),
    ("192.168.110.40", 7890),
    ("192.168.110.225", 7891),
    ("192.168.110.225", 7890),
    ("172.19.0.1", 7891),
    ("172.19.0.1", 7890),
]

PROXY = None
for host, port in PROXIES_LIST:
    sock = socket.socket()
    sock.settimeout(3)
    r = sock.connect_ex((host, port))
    sock.close()
    if r == 0:
        proxy_url = f"socks5h://{host}:{port}"
        PROXY = {"http": proxy_url, "https": proxy_url}
        print(f"[代理] 使用 {host}:{port}", file=sys.stderr)
        break
```

Then pass `proxies=PROXY` to every `requests.get/post` call.

## API Base URL
Always use `https://api.telegram.org/bot{TOKEN}` — do NOT use IP-based URLs like `149.154.166.110`. They may route differently and cause authentication failures.

## Streaming Text Output (editMessageText)
Telegram does not support SSE/websocket streaming from bots. The pattern:
1. Send initial placeholder message (e.g. "⏳ 思考中...")
2. Receive streaming tokens from upstream LLM API
3. Buffer tokens, edit the message every 0.3s via `editMessageText`
4. User sees text appearing progressively

```python
def send_streaming(chat_id, prompt):
    init = api_post("sendMessage", {"chat_id": chat_id, "text": "⏳ 思考中..."})
    msg_id = init["result"]["message_id"]
    accumulated = ""
    last_edit = time.time()
    edit_interval = 0.3
    min_chunk = 4

    for delta in stream_tokens(prompt):
        accumulated += delta
        if time.time() - last_edit > edit_interval and len(accumulated) >= min_chunk:
            api_post("editMessageText", {
                "chat_id": chat_id, "message_id": msg_id,
                "text": f"[老婆] {accumulated}⏳"
            })
            last_edit = time.time()

    api_post("editMessageText", {
        "chat_id": chat_id, "message_id": msg_id,
        "text": f"[老婆] {accumulated}"
    })
```

## Sticker Sending

**Two paths — prefer Gateway-native (2026.8.2+):**

### 1. Gateway-native (preferred, since 2026.8.2)
LLM calls `telegram_send_sticker` tool → `TelegramAdapter.send_sticker()` → `bot.send_sticker()` natively.

**Key constraint**: `sticker_id` must be a Telegram `file_id` (starts with `CAACAgIAA`), NOT a pack URL like `https://t.me/addstickers/...` and NOT a pack name alone.

**How to get a file_id programmatically** (requires bot token):
```python
# This works if you have the bot token directly
sticker_set = await bot.get_sticker_set('hermes_emo_a2_by_avaya_hermesbot')
file_id = sticker_set.stickers[0].file_id  # first sticker in pack
```

**Without bot token**: ask the user to send a sticker from the pack → the gateway captures `msg.sticker.file_id` → you can then reply with that file_id.

**⚠️ Stuck without a file_id?**
- Sticker pack URL (`https://t.me/addstickers/...`) cannot be used directly — it's not a file_id
- `getStickerSet` requires the bot token — if gateway is running without exposing token to env, you cannot call it from a standalone script
- Simplest solution: user sends ONE sticker from the pack → you extract the file_id from the received message → subsequent sends work
- `~/.hermes/sticker_file_ids.json` caches file_ids by emoji — older packs (😺🐶) are there; hermes_emo_a2 is not cached yet

Full architecture details: `references/sticker_gateway_integration.md`

### 2. Standalone script (legacy)
```bash
python3 ~/.hermes/scripts/send_sticker.py <chat_id> -p <pack_name> -n <index>
```
Cache: `~/.hermes/sticker_file_ids.json` — clear on `FILE_ID_INVALID`.

## Key Files
- `~/.hermes/scripts/send_sticker.py` — Sticker sender with auto-proxy
- `~/.hermes/scripts/telegram_stream.py` — Streaming text via editMessageText
- `~/.hermes/scripts/stream_minimax.py` — MiniMax API streaming test
- `~/.hermes/sticker_file_ids.json` — Cached file_ids
- `references/sticker_gateway_integration.md` — **Gateway-native sticker integration (2026.8.2+)**
- `references/proxy_config.md` — Known proxy IPs and auto-scan config

## Sticker Sending — Which Path to Use

**Rule of thumb (2026.8.3 confirmed):**
- `telegram_send_sticker` tool often does NOT appear in `hermes tools list` even when gateway is running
- **Always prefer `curl` directly** — it's faster, more reliable, and bypasses the tool registration issue entirely

### Primary: curl (always try this first)
```bash
curl -s "https://api.telegram.org/bot{BOT_TOKEN}/sendSticker?chat_id={USER_ID}&sticker={FILE_ID}"
```
If returns `{"ok":true,...}` → success. No tool registration needed.

### Gateway tool (fallback only)
```bash
hermes tools list | grep -i sticker
```
If `telegram_send_sticker` listed → gateway is healthy, use it. If not listed → use curl.

## Sticker Diagnostic Pattern
When user reports "表情没看到":

1. **curl is definitive** — test directly, don't check `hermes tools list` first
2. If curl returns `{"ok":true,...}` → API is fine, check if user received it (network/delivery issue)
3. If curl fails → wrong token, chat_id, file_id, or network/proxy issue
4. Restart gateway only if curl succeeds but gateway tool is needed for a workflow

## Quirks & Pitfalls
- Termux has NO direct outbound internet; all Telegram API calls must go through proxy
- Proxy IPs change frequently (auto-discovery handles this)
- MiniMax API: `Authorization: Bearer {key}` NOT `X-Api-Key` for streaming endpoints
- MiniMax streaming URL: `https://api.minimaxi.com/v1/text/chatcompletion_v2`
- `socks5h://` (with 'h') resolves DNS on proxy side — use this, not `socks5://`
- API responses may be empty on transient failures — always wrap `.json()` in try/except
- Hermes gateway long-polling works even when Termux terminal cannot reach Telegram directly
- **Sticker file_id requirement**: Telegram's `sendSticker` needs a `file_id`, not a pack name or URL. If user provides a pack name/URL, fetch `file_id` via `get_sticker_set()` first.
- **"表情没看到"**: Always curl-test the API first before debugging gateway tool — curl is definitive.
