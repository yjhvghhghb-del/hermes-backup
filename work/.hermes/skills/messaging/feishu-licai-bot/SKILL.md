---
name: feishu-licai-bot
description: 理财Bot (licai/libai profile) 启动、排错、SSL断开修复、群里无响应诊断。
tags: [feishu, licai, libai, 理财]
---

# 飞书理财Bot

## 基本信息
- **Profile**: `~/.hermes/profiles/libai/`（之前误名为 licai，实际目录是 libai）
- **App ID**: `cli_aafa2c6a83b85bee`
- **App Secret**: `<LARK_SECRET_2>`
- **Gateway**: `HERMES_HOME=~/.hermes/profiles/libai hermes gateway run`
- **日志**: `~/.hermes/profiles/libai/logs/gateway.log`

## 启动/重启
```bash
# 杀旧进程（找 libai 的 python gateway 进程）
ps aux | grep "hermes gateway" | grep -v grep
kill <PID>  # libai 的进程 PID

# 重启
HERMES_HOME=~/.hermes/profiles/libai hermes gateway run
```

## 已知问题

### SSL EOFError 导致 WebSocket 断开
`errors.log` 大量 `Lark: receive message loop exit` + `SSLEOFError`。Bot 进程可能还活着但群消息停了。
```bash
tail -10 ~/.hermes/profiles/libai/logs/errors.log
grep "Inbound group" ~/.hermes/profiles/libai/logs/gateway.log
```

### 群里 @ 不响应——两种可能
**可能1: `require_mention: true`（默认）导致静默忽略**
飞书 adapter 默认 `require_mention: true`，即使 `default_group_policy: open` 也只响应被 @ 的消息。在 config 里加：
```yaml
platforms:
  feishu:
    extra:
      require_mention: false  # 不需要 @ 就能回复群消息
      default_group_policy: open
```

**可能2: 飞书平台限制——同群多 bot @事件只推给最早加入的**
当两个 bot（理财bot + 嗨妹小老婆）在同一个群时，**@mention 事件只推给最早加入群的 bot**，后加的 bot 永远收不到任何 @事件。这是飞书平台级限制，非配置问题。
诊断：
```bash
# 看 libai 是否有收到群消息（不应该有，因为被嗨妹抢了）
grep "Inbound group" ~/.hermes/profiles/libai/logs/gateway.log

# 看嗨妹小老婆的（应该有）
grep "Inbound group" ~/.hermes/logs/gateway.log
```
如果 libai 的 log 里群消息为空 → 确认是这个平台限制。

**解决方案**：把理财bot 和 嗨妹小老婆 放在不同群；或者接受只有嗨妹小老婆能响应 @，理财bot 只能 DM。

### app_id 冲突
此 bot 的 app_id (`cli_aafa2c6a83b85bee`) 不能与任何其他 running gateway 共享。检查：
```bash
grep "app_id" ~/.hermes/config.yaml
grep "app_id" ~/.hermes/profiles/libai/config.yaml
grep "app_id" ~/.hermes/profiles/wenyu/config.yaml  # 如果 wenyu 在跑
```
所有 app_id 必须各不相同。
