---
name: platform-feature-integration
description: Add a capability to a Hermes platform adapter.
---

# Platform Feature Integration

Add a new capability (e.g. `send_sticker`) to an existing Hermes messaging platform adapter.

## When to use

You need to extend a platform adapter (Telegram, Discord, Feishu, etc.) with a new
send/list/query method that the LLM can call as a tool, and/or that needs to appear in
the platform's prompt hints.

## Checklist — all 6 steps required

### Step 1 — Adapter method

In `plugins/platforms/<platform>/adapter.py` (or `gateway/platforms/<platform>.py`):

```python
async def send_sticker(
    self,
    chat_id: str,
    sticker_id: Optional[str] = None,
    reply_to: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> SendResult:
    """Send a <platform> sticker by file_id or URL."""
    if not self._bot:
        return SendResult(success=False, error="Not connected")
    try:
        # ... call self._bot.send_sticker(...) or equivalent
        return SendResult(success=True, message_id=str(msg.message_id))
    except Exception as e:
        logger.warning("[%s] Failed to send sticker: %s", self.name, e)
        return SendResult(success=False, error=str(e))
```

Also check whether the adapter has `get_active()` / `set_active()` class methods.
If missing, add them (see Step 2).

### Step 2 — Active adapter singleton (if missing)

If the platform adapter has no `get_active()` classmethod, add one:

```python
_active_instance: Optional["TelegramAdapter"] = None

@classmethod
def get_active(cls) -> Optional["TelegramAdapter"]:
    """Return the currently active adapter, or None."""
    return cls._active_instance

@classmethod
def set_active(cls, adapter: Optional["TelegramAdapter"]) -> None:
    """Register (or clear) the active adapter instance."""
    cls._active_instance = adapter
```

Then register on connect/disconnect:

```python
def _mark_connected(self) -> None:
    MyAdapter.set_active(self)   # <— add this
    super()._mark_connected()

def _mark_disconnected(self) -> None:
    MyAdapter.set_active(None)  # <— add this
    super()._mark_disconnected()
```

### Step 3 — Base class fallback stub

In `gateway/platforms/base.py`, add a default implementation so non-overriding
platforms degrade gracefully:

```python
async def send_sticker(
    self,
    chat_id: str,
    sticker_id: Optional[str] = None,
    reply_to: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> SendResult:
    return await self.send(chat_id=chat_id, content="[sticker]",
                           reply_to=reply_to, metadata=metadata)
```

### Step 4 — Tool function

Create `tools/<platform>_tools.py` with the LLM-callable function:

```python
async def send_sticker(sticker_id: str = "", chat_id: str = "", reply_to: str = "") -> dict:
    """Send a <platform> sticker."""
    from gateway.session_context import get_session_env
    target = (chat_id or "").strip() or get_session_env("HERMES_SESSION_CHAT_ID", "")
    if not target:
        return {"success": False, "error": "chat_id required"}
    adapter = _get_active_adapter()  # lazy import of platform adapter
    if adapter is None:
        return {"success": False, "error": "Adapter not connected"}
    try:
        result = await adapter.send_sticker(chat_id=target, sticker_id=sticker_id.strip(),
                                            reply_to=reply_to or None)
    except Exception as exc:
        return {"success": False, "error": str(exc)}
    return {"success": getattr(result, "success", False),
            "message_id": getattr(result, "message_id", None)}
```

### Step 5 — Toolset and ACP registration

In `toolsets.py`, add the tool to the platform's toolset block:

```python
"<platform>": {
    "tools": _HERMES_CORE_TOOLS + ["<platform>_send_sticker"],
    "module": "tools.<platform>_tools",   # <-- required when non-core tool added
    "includes": []
},
```

In `acp_adapter/tools.py`:
```python
# In TOOL_KIND_MAP:
"<platform>_send_sticker": "execute",

# In _POLISHED_TOOLS:
"<platform>_send_sticker",
```

### Step 6 — Platform prompt hint

In `agent/prompt_builder.py`, in the `PLATFORM_HINTS["<platform>"]` block, add
usage guidance so the LLM knows when and how to call the tool.

## Pitfalls

- **Forgetting `module` in toolsets.py** — the tool won't be importable and the
  toolset will silently skip it.
- **Adapter class name** — check the actual class name (e.g. `TelegramAdapter`
  not `TelegramBotAdapter`) before importing in the tool function.
- **Lazy imports** — always lazy-import the adapter inside the function, not at
  module top-level, so the gateway starts even if the optional dependency is missing.
- **Missing `get_active` registration** — without it, `_get_active_adapter()` in
  the tool always returns `None` at runtime (even if the adapter is connected).
  The registration must happen in `_mark_connected`, not just in `__init__`.

## Verification

1. Syntax check all modified files: `python3 -c "import ast; ast.parse(open(f).read())"`
2. Import the new tool: `from tools.<platform>_tools import send_sticker`
3. Gateway must be restarted for changes to take effect
4. Test: send a message that triggers the new tool on the target platform
