# OneBot v11 / NapCat 新建适配器 — 完整记录

**会话背景：** 用户想把 NapCat（基于 NTQQ 协议的 Bot 方案）配合 Hermes 使用真人 QQ 号作为 Bot。Hermes 内置的 `qqbot` 是官方 QQ 机器人 API（走 `api.sgroup.qq.com`），与 NapCat 的 OneBot WebSocket 完全不同，需要新建适配器。

---

## 创建的文件

### 1. `gateway/platforms/onebot.py`（新建适配器）

关键实现要点：

**继承与注册：**
```python
from gateway.config import Platform, PlatformConfig
from gateway.platforms.base import (
    BasePlatformAdapter, MessageEvent, MessageType, SendResult,
)

class OneBotAdapter(BasePlatformAdapter):
    platform = Platform.ONEBOT   # 或者用 platform.value == "onebot" 做动态匹配
```

**必须实现的抽象方法：**
- `async def connect(is_reconnect) -> bool`
- `async def disconnect() -> None`
- `async def send(chat_id, content, reply_to, metadata) -> SendResult`
- `async def get_profile(user_id, chat_id) -> Optional[Dict]`
- `async def health_check() -> bool`

**消息派发的正确方式（重要！）：**
```python
# 错误方式 —— 不存在 _dispatch 方法
# self._dispatch(event)

# 正确方式 —— 继承自 BasePlatformAdapter.handle_message()
await self.handle_message(event)
```
`BasePlatformAdapter.handle_message()` 会自动处理 session key、排队、active session guard 等所有逻辑，适配器只需构建好 `MessageEvent` 然后调用即可。

**构造 SessionSource 的正确方式：**
```python
source = self.build_source(
    chat_id=str(data.get("group_id") or data.get("user_id") or ""),
    chat_type="group" if is_group else "dm",
    user_id=str(data.get("user_id", "")),
    user_name=data.get("sender", {}).get("nickname", "") or None,
)
```

**构造 MessageEvent：**
```python
event = MessageEvent(
    text=text,
    message_type=MessageType.TEXT,
    source=source,
    raw_message=data,
    message_id=str(data.get("message_id", "")),
)
await self.handle_message(event)
```

**aiohttp 可用检查（标准模式）：**
```python
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    aiohttp = None
```

---

### 2. `gateway/run.py` — 注册新适配器

在 `_create_adapter()` 方法的 `return None` 之前加入：

```python
elif platform.value == "onebot":
    from gateway.platforms.onebot import OneBotAdapter
    return OneBotAdapter(config)
```

位置大约在 `elif platform == Platform.YUANBAO:` 的 `return None` 之后。

**不要**在 `run.py` 里重复检查 `AIOHTTP_AVAILABLE`，因为 `OneBotAdapter.__init__` 会在连接时自己处理。

---

### 3. `config.yaml` — 平台配置示例

```yaml
platforms:
  onebot:
    enabled: true
    extra:
      ws_url: "ws://127.0.0.1:3000"    # NapCat WebSocket 地址
      access_token: ""                   # NapCat 访问令牌（可选）
      ignore_self: true                 # 忽略自己发的消息
      group_policy: allowlist            # open | allowlist | disabled
      group_allow_from:
        - "群号1"
        - "群号2"
      dm_policy: open                  # open | disabled
      allow_from: []                   # 允许的 user_id 白名单
```

---

## NapCat 端部署（Termux）

```bash
# 安装一键脚本
curl -o napcat.termux.sh https://nclatest.znin.net/NapNeko/NapCat-Installer/main/script/install.termux.sh && bash napcat.termux.sh

# 首次启动并扫码登录
./napcat

# 后续直接启动
./napcat
```

NapCat 启动后在 WebUI（`http://localhost:3000`）开启 **正向 WebSocket**，Hermes 即可通过 `ws://127.0.0.1:3000` 接收 QQ 消息。

---

## 常见陷阱

1. **不要自己实现 dispatcher** — `BasePlatformAdapter.handle_message()` 已经处理了所有 session 路由逻辑，直接调用即可。

2. **不要在 `run.py` 做 `AIOHTTP_AVAILABLE` 检查** — 适配器在 `connect()` 里自己处理，冒昧阻断会导致网关无法启动。

3. **`config.yaml` 里 `platform` 的名字** — 用 `platform.value == "onebot"` 做字符串匹配，因为 `Platform` 枚举里没有预定义 `ONEBOT`，是用 `_missing_()` 动态创建的。

4. **NapCat 需要配合框架使用** — 单独跑 NapCat 只提供协议层，还需要一个 Bot 框架（如 AstrBot、Koishi、NoneBot）来执行业务逻辑，或者自己实现 OneBot API 调用。

---

## 相关文件路径

```
~/.hermes/hermes-agent/gateway/platforms/onebot.py   ← 新建
~/.hermes/hermes-agent/gateway/run.py                 ← 修改
~/.hermes/config.yaml                                ← 手动配置
```
