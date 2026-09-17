# 飞书多 Bot 平台限制（2026-08-03 确认）

## 核心限制：群 @mention 只发给第一个加入群的 Bot

**平台级行为，飞书自身设计，无法绕过。**

- 同一群的 `@mention` 事件 → 只发给群里**最早添加**的 Bot
- 其他 Bot 收不到任何群 @mention 事件（WebSocket 连着也没用）
- 即使两个 Bot 都在群里，也只有一个能收到群消息

## 群消息路由表

| Bot 加入顺序 | 群 @mention | 群 DM（非 @） |
|-------------|------------|--------------|
| 主 Bot 先加 | 主 Bot 收到 | 主 Bot 收到 |
| 妹妹 Bot 后加 | **妹妹收不到** | **妹妹收不到** |
| 只有妹妹在群 | 妹妹收到 | 妹妹收到 |

## 解决方案

### 方案 1：删主 Bot，只留新 Bot（推荐）
- 从群里删掉主 Bot（第一个加入的）
- 新 Bot 成为群里唯一 Bot → 群消息全归新 Bot

### 方案 2：新 Bot 只做 DM
- 主 Bot 留群处理群消息
- 新 Bot 只做私聊用途（DM）

### 方案 3：新建独立 App（彻底分离）
- 为主 Bot 和新 Bot 各建独立飞书 App（不同 App ID）
- 两个 Bot 都加群 → 仍然只有先加的收到群 @mention
- 只有删掉主 Bot 才能让新 Bot 收群消息

## pairing 的正确理解

- 飞书 DM pairing 是用户跟 App ID 绑定的
- **换 Secret 不影响 pairing**（App ID 不变，pairing 记录还在）
- 但**新建 Bot**（新 App ID）需要重新 pairing

## 当前状态

- 理百 Bot（libai）用妹妹的旧 App ID → pairing 记录还在，不需要重新 approve
- 但理百 Bot DM 收不到消息 → 可能原因：飞书 App 事件订阅配置问题或 Bot 本身未正确接收消息（需进一步排查）
