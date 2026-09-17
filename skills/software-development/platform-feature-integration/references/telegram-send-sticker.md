# Telegram send_sticker — worked example

Added in session 20260802 to fix "表情不能发了吗？".

## What was done

6 files modified, 1 new file created:

### `plugins/platforms/telegram/adapter.py`
- Added `send_sticker()` method (line ~7361)
- Added `_active_instance`, `get_active()`, `set_active()` classmethods (line ~645)
- Called `TelegramAdapter.set_active(self)` in `_mark_connected()`
- Called `TelegramAdapter.set_active(None)` in `_mark_disconnected()`

### `gateway/platforms/base.py`
- Added `send_sticker()` default stub (line ~3994) — returns `[sticker]` text fallback

### `tools/telegram_tools.py` (NEW)
- `send_sticker(sticker_id, chat_id, reply_to)` function
- Lazy imports `TelegramAdapter` from `plugins.platforms.telegram.adapter`
- Calls `adapter.send_sticker()` then wraps result

### `toolsets.py`
- Added `"telegram_send_sticker"` to `hermes-telegram` toolset
- Added `"module": "tools.telegram_tools"` to that block

### `acp_adapter/tools.py`
- Added `"telegram_send_sticker": "execute"` to `TOOL_KIND_MAP`
- Added `"telegram_send_sticker"` to `_POLISHED_TOOLS`

### `agent/prompt_builder.py`
- Added sticker hint to `PLATFORM_HINTS["telegram"]`

## Key discovery

`TelegramAdapter` had NO `get_active()` / `set_active()` singleton pattern.
The Yuanbao adapter has it; Telegram did not. Without it, the lazy import in
`telegram_tools.py` always returns `None` at runtime even when the gateway is
connected. Fixed by adding the classmethods + registration in `_mark_connected`.

## Sticker ID format

Telegram `send_sticker` accepts:
- `file_id` (starts with `CAACAgIAA`) — from a previously sent sticker
- Sticker set name (e.g. `EvilMunchianoMiniStickers`)
- Direct sticker URL (telegram.org supports this)

The LLM needs a real file_id to send. There is no built-in sticker search
tool for Telegram (unlike Yuanbao's `yb_search_sticker`).
