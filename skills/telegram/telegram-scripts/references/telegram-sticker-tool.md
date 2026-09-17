# Telegram Sticker Tool — Implementation Record (2026.8.2)

## 背景
老公想让我主动发 Telegram 贴纸，但原有代码只有 `yb_send_sticker`（元宝平台），Telegram 适配器没有 `send_sticker` 方法。

## 修复内容

### 1. `TelegramAdapter.send_sticker`（adapter.py）
位置：`.hermes/hermes-agent/plugins/platforms/telegram/adapter.py`
新增 `send_sticker` 方法，调用 `bot.send_sticker(sticker=sticker_id)`。

### 2. `BasePlatformAdapter.send_sticker`（base.py）
位置：`.hermes/hermes-agent/gateway/platforms/base.py`
加默认实现（fallback 发送 "[sticker]" 文本），防止其他平台报 not implemented。

### 3. `TelegramAdapter.get_active / set_active`
TelegramAdapter 注册了类方法 `get_active()` / `set_active()`，在 `_mark_connected` 时注册自己，`_mark_disconnected` 时清空。这样 `telegram_tools.py` 可以通过 `TelegramAdapter.get_active()` 拿到当前活跃的 bot 实例。

### 4. `tools/telegram_tools.py`（新建）
位置：`.hermes/hermes-agent/tools/telegram_tools.py`
实现 `send_sticker` 工具函数（`telegram_send_sticker`），通过 adapter 直接发送。

### 5. `toolsets.py` 注册
`hermes-telegram` toolset 加入 `telegram_send_sticker`，指定 `module: tools.telegram_tools`。

### 6. `acp_adapter/tools.py` 注册
- `_POLISHED_TOOLS` 加入 `"telegram_send_sticker"`
- `TOOL_KIND_MAP` 加入 `"telegram_send_sticker": "execute"`

### 7. `prompt_builder.py` Telegram 平台提示
加入贴纸用法说明。

## Gateway 重启注意
**必须重启 gateway 才能加载新的 toolset**：
```bash
# default profile
cd ~ && hermes gateway run --replace

# cutegirl profile
cd ~/.hermes/profiles/cutegirl && hermes gateway run --replace
```

重启后 LLM 可以直接调用 `telegram_send_sticker` 工具发贴纸。

## Bot Token
老公的 Hermes Telegram Bot：`8800919754:AAFdNkpAGSI6M5ahwd3_5g-SuZzusH7ybp4`

## 老公的 hermes_emo_a2 贴纸包
- Pack: `hermes_emo_a2_by_avaya_hermesbot`
- 60 张，file_id → emoji 映射存于 `~/.hermes/hermes_emo_a2.json`
- 通过 `bot.get_sticker_set('hermes_emo_a2_by_avaya_hermesbot')` 可重新获取全部 file_id

## 调试方法
查看 gateway 日志：
```bash
tail -f ~/.hermes/logs/gateway.log | grep -i sticker
```

查看 telegram 适配器是否注册：
```python
from plugins.platforms.telegram.adapter import TelegramAdapter
print(TelegramAdapter.get_active())  # None = 未连接
```
