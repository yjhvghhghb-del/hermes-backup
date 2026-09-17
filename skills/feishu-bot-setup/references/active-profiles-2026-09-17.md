# 2026-09-17 Bot 启动状态（实测）

## 当前运行中的 Bot

| Profile | 平台 | Token | 状态 |
|---------|------|-------|------|
| default | Telegram主bot + Feishu | 8800919754 | ✅ 主gateway已启动(PID 24938)，飞书已连接 |
| geekwife | Telegram | 8637317610 | ✅ token有效 |
| siliconflow | Telegram | 8363232963 | ✅ token有效 |

## 关键发现（2026-09-17 实测）

### 正确的启动命令

```bash
# 杀掉所有旧进程
pkill -9 hermes; sleep 2

# 直接启动主gateway
hermes gateway run
```

**没有 `hermes start` 命令**（踩坑30分钟）。
**没有 `hermes serve` 命令**（`serve` 不是有效子命令）。
**`hermes --profile xxx gateway run` 会报错** 因为 multiplex 已托管。

### multiplex_profiles: true 默认开启

主 gateway 自动托管所有 profiles，不需要单独启动任何 profile 的 gateway 进程。运行 `hermes --profile siliconflow gateway run` 会报错：

> "The default gateway is running as a profile multiplexer and already serves profile 'siliconflow'"

### 主 bot token 在 default profile 的 .env 里

```
TELEGRAM_BOT_TOKEN=8800919754:***  ← 主bot
TELEGRAM_HOME_CHANNEL=877708648
```

### 独立 profiles 的 token 在各自 .env 里

```
# siliconflow/.env
TELEGRAM_BOT_TOKEN=8363232963:***

# geekwife/.env
TELEGRAM_BOT_TOKEN=8637317610:***

# 两者都用同一代理
TELEGRAM_PROXY=socks5://10.1.252.196:7891
```

## 验证命令

```bash
# 看进程
ps aux | grep "hermes gateway run" | grep -v grep

# 看状态
hermes gateway status

# 看日志
tail -30 ~/.hermes/logs/gateway.log | grep -E '✓|✗|connected|failed'
```

## gateway status 输出示例（正常）

```
✓ Gateway is running (PID: 24938)
  (Running manually, not as a system service)
```
