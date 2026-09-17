---
name: android-hermes-memory-management
description: Android Termux 内存不足时 Hermes gateway 被 SIGKILL 的诊断与恢复。
triggers:
  - exit code -9
  - OOM killer
  - gateway exited uncleanly
  - Android Hermes 被杀
---

# Android Hermes 内存管理

## 触发条件
在 Android Termux 环境下运行 Hermes 时遭遇 OOM killer (SIGKILL exit code -9)，gateway 反复被杀死。

## 识别信号
- `hermes --profile <name> status` 显示 `Gateway Service: stopped`
- `ps aux | grep hermes` 对应 profile 消失
- 后台进程 notification 显示 `exited (exit code -9)`
- 日志含 `Previous gateway life ... exited UNCLEANLY (no exit path ran — SIGKILL / OOM / VM death)`
- 系统内存：RAM available < 1GB，swap 已用 10G+，/data 分区 99% 满

## 诊断命令
```bash
# 检查各 profile gateway 状态
hermes --profile default gateway status

# 检查内存
free -k

# 检查存储
df -h /data

# 查看哪个 profile 还在跑
ps aux | grep 'hermes.*gateway' | grep -v grep
```

## 应急重启（multiplex 模式，2026-09-17 更新）

`gateway.multiplex_profiles: true` 默认开启，**所有 profile 的 bot 连接都由主 gateway 统一托管，不需要（也不能）单独启动各 profile 的 gateway 进程。**

```bash
# 杀掉所有旧进程
pkill -9 hermes; sleep 2

# 直接启动主 gateway
hermes gateway run
```

主 gateway 启动后飞书+Telegram 自动 multiplex 连接所有 profile。若已有实例在跑，用：
```bash
hermes gateway run --replace
```

**不要再分别启动独立 profile 的 gateway 进程**（`hermes --profile geekwife gateway run` 会报 double-bind 错误）。

## 根因
Android 系统内存紧张时 OOM killer 优先杀内存占用最高的进程。Hermes default profile 内存占用高于其他 profiles，所以被盯上。其他4个profile（geekwife/licai/siliconflow/wenyu）体量小，经常没事。

## 缓解方案
1. **临时**：主bot被kill后重启 — 这是主要工作流
2. **中级**：停掉不用的其他 profiles 释放内存
   ```bash
   # 停掉某个 profile
   hermes --profile <name> gateway stop
   ```
3. **长期**：清理 Android 存储空间（/data 99%满会影响swap效率），或减少同开 profile 数量

## 验证
重启后确认进程在跑：
```bash
sleep 5 && ps aux | grep 'hermes.*default' | grep -v grep
```

---

## 限制：Web UI / Dashboard / TUI 在 Termux 上不可用

**症状：**
- `hermes dashboard` → `npm install failed` / `Web UI npm install failed`
- `hermes --tui` → `npm install failed`
- `hermes desktop` / `hermes gui` → npm build 失败
- `hermes serve` → 能跑（headless 后端 API），但返回 `{"error":"Headless backend"}`

**根因：**
Termux 是 Tier 2 平台（官方"尽力而为"支持）。Web UI、TUI、Desktop App 都依赖 npm build 流程（`npm install --workspace web && npm run build -w web`），而 Termux 的 Node.js 环境不支持该构建流程。

**可用的界面方案：**

| 方案 | Termux 能用？ | 说明 |
|------|-------------|------|
| `hermes serve` | ✅ headless API | 不是 UI |
| Telegram Bot | ✅ | 主交互方式 |
| Operit AI 完整环境 | ✅ | Ubuntu 24 环境里 `hermes dashboard` 应能跑 |
| OpenClaw 内置 Web UI | ✅ | `npm install -g openclaw@latest` 后 `openclaw dashboard` → `http://127.0.0.1:18789` |
| 静态 HTML 看板 | ✅ | 写好 HTML 后 `python -m http.server <端口>` serve |

**Operit AI 换 Profile 后 Hermes 找不到的解决：**
```bash
source ~/.bashrc
# 或
exec bash
```

**核心结论：Termux 上的 Hermes 只有 CLI + Telegram Bot 界面。Web UI/Dashboard/TUI 需要完整 Linux 环境（Operit AI Ubuntu 24）或电脑。**

**静态看板替代方案：** 见 `references/hermes-kanban-workaround.md`
