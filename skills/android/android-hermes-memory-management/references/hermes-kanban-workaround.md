# Hermes 静态 HTML 看板

当 Termux 上 Hermes Web UI 无法使用时，可用静态 HTML 看板替代。

## 快速部署

**1. 创建看板 HTML**（已保存路径）：
```
/storage/emulated/0/Documents/Hermes看板.html
/storage/emulated/0/Documents/HermesOperit看板.html
```

**2. 在目标环境 serve：**
```bash
cd /storage/emulated/0/Documents
python -m http.server 8888
```

**3. 访问：**
- 本机浏览器：`http://127.0.0.1:8888`
- 外网穿透：用 ngrok `ngrok http 8888`

## 看板内容建议

- 平台连接状态（Telegram/飞书/QQ/Operit）
- 定时任务列表 + 下次执行时间
- Gateway 进程状态
- Bot Profile 列表
- 工具能力总览
- 存储/内存使用
- AI 全家桶状态

## 自定义看板

用 Python 脚本定时更新数据（进程数、内存、cron 任务状态），写入 HTML 后 serve。

## 限制

这是**静态展示**，不是真正的 Hermes 交互界面。
如需交互，用 OpenClaw（`openclaw dashboard`）或 Operit AI 完整环境。
