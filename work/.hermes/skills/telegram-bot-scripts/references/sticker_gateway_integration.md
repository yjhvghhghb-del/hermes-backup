# Telegram Sticker — Gateway Integration vs curl (2026.8.3 Updated)

## Two Paths

### 1. curl (RELIABLE — always try this first)
```bash
curl -s "https://api.telegram.org/bot{BOT_TOKEN}/sendSticker?chat_id={USER_ID}&sticker={FILE_ID}"
```
Returns `{"ok":true,"result":{...}}` → success.

This is the **primary and most reliable path**. Does not depend on gateway tool registration.

### 2. Gateway-native tool (unreliable as of 2026.8.3)
```
LLM → telegram_send_sticker tool
    → TelegramAdapter.send_sticker()
        → bot.send_sticker()   ← native Telegram API
```

**⚠️ `telegram_send_sticker` often does NOT appear in `hermes tools list`** even when the gateway is running perfectly. The tool was registered in code, but the Hermes tool discovery system doesn't always pick it up. Always use curl as the primary path.

## Architecture (gateway tool path — for reference)

| File | Change |
|------|--------|
| `plugins/platforms/telegram/adapter.py` | + `send_sticker()` method; + `get_active()`/`set_active()` class methods; `_mark_connected()`/`_mark_disconnected()` register adapter |
| `gateway/platforms/base.py` | + `send_sticker()` stub (fallback to text "[sticker]") |
| `tools/telegram_tools.py` | **NEW** — `telegram_send_sticker(chat_id, sticker_id, reply_to)` |
| `toolsets.py` | `hermes-telegram` toolset: added `telegram_send_sticker`, `module: tools.telegram_tools` |
| `acp_adapter/tools.py` | Registered `telegram_send_sticker` in `_POLISHED_TOOLS` + `TOOL_KIND_MAP` |
| `agent/prompt_builder.py` | Telegram platform hint: added sticker usage docs |

## Getting a file_id

Telegram requires a `file_id` to send a sticker (not a pack URL). Two ways:

1. **User sends a sticker first** → gateway receives it, `msg.sticker.file_id` is available in `_handle_sticker()`
2. **Programmatically fetch pack info**:
   ```python
   # Via gateway adapter (best — uses active session proxy)
   adapter = TelegramAdapter.get_active()
   sticker_set = await adapter._bot.get_sticker_set('hermes_emo_a2_by_avaya_hermesbot')
   file_id = sticker_set.stickers[0].file_id
   
   # Via standalone script (old way — needs bot_token)
   python3 ~/.hermes/scripts/send_sticker.py <chat_id> -p hermes_emo_a2_by_avaya_hermesbot -n 0
   ```

**⚠️ Stuck without a file_id — common scenario:**
1. Gateway is running (PID 3948) but `TELEGRAM_BOT_TOKEN` is NOT in environment variables
2. `TelegramAdapter.get_active()` returns `None` when gateway was started without exposing token to env
3. `bot.get_sticker_set()` cannot be called without the token accessible to the calling process
4. `web_extract` cannot fetch `t.me/addstickers/...` (Telegram blocks scrapers)

**Resolution**: user sends ONE sticker from the pack → gateway receives it → `msg.sticker.file_id` is captured → all subsequent sends work.

**Don't try to use**:
- `https://t.me/addstickers/...` as a sticker_id (it's a URL, not a file_id)
- OpenAI-format keys (`sk-cp-...`) as bot tokens (Telegram token format is `\d+:[A-Za-z0-9_-]{30,}`)

## Key Implementation Detail (gateway tool path)

`TelegramAdapter.get_active()` / `set_active()` must be registered manually — unlike `YuanbaoAdapter`, `TelegramAdapter` had no singleton pattern. Added:
- `_active_instance` class variable
- `get_active()` / `set_active()` classmethods
- `set_active(self)` called in `_mark_connected()` and `_mark_disconnected()`

This lets `tools/telegram_tools.py` get the live adapter via lazy import without circular dependencies.
