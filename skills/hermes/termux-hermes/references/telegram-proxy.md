# Telegram on Termux — Proxy Required

## Problem
Telegram直连在Termux网络环境里会ConnectError（httpx.ConnectError），需要走代理。

## Fix
主bot的`.env`（`~/.hermes/.env`）加一行：
```
TELEGRAM_PROXY=socks5h://10.1.252.196:7891
```
（注意是`socks5h`不是`socks5`，`h`表示DNS由远端解析）

## 验证
加完proxy后gateway restart（或重新启动），观察日志：
```
tail -30 ~/.hermes/logs/gateway.log | grep -i telegram
```
看到 `Connecting to Telegram (attempt N/8)...` 而不是 `No bot token configured` 就是读到了。
