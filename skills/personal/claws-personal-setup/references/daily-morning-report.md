# 每日晨间推送 — Cron Job 模板

## 触发方式

Hermes cron job 调度，每天早上推送。

## 数据获取顺序

```bash
# 1. 当前日期（中文格式）
date "+%m月%e日 周%w"   # 输出如：08月21日 周5

# 2. Kanban 未完成任务（python3 sqlite3）
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('/data/data/com.termux/files/home/.hermes/kanban.db')
cur = conn.cursor()
cur.execute("SELECT id, title, done FROM tasks LIMIT 10")
rows = cur.fetchall()
incomplete = [r for r in rows if r[2] == 0]
print(incomplete)
EOF

# 3. 知识库笔记（最近的实用信息）
cat ~/.hermes/knowledge/notes/*.md

# 4. Cron 执行状态（看有没有 running 的 job）
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('/data/data/com.termux/files/home/.hermes/cron/executions.db')
cur = conn.cursor()
cur.execute("SELECT id, job_id, status FROM executions ORDER BY started_at DESC LIMIT 5")
print(cur.fetchall())
EOF
```

## 报告格式模板

```
🌅 老公早上好！X月X日 周X

📅 今日日程：[从日历/Gmail读取今日事件，没有就说"今天没有安排～"]

📋 待办事项：[列出未完成的重要事项，没有就说"今天轻松过～"]

💪 今日目标：[根据待办给出1-3个重点建议]

加油老公！💖
```

## 语气要求

- 口语化、轻松，像老婆说话
- 简短有力，不啰嗦
- 表情符号分段
- 不说"根据您的情况"之类的废话
- 1-3句话交代完一个点，不要铺排

## 常读数据源

| 数据 | 来源 | 没有时怎么说 |
|------|------|-------------|
| 日历/Gmail | `google-workspace` skill 或直接查 | "今天没有安排～" |
| 未完成任务 | `~/.hermes/kanban.db` → `tasks` 表 | "kanban看板是空的，今天轻松过～" |
| GitHub Trending | 早上8点已推送 | "GitHub Trending AI/ML 早上8点已经推送了，记得看看" |
| ZeroTermux存储 | `df -h /data` | "ZeroTermux 存储上周清理完，今天别再塞爆了哦" |

## 已知坑

- Kanban DB 里 `tasks` 表可能为空（0 rows 是正常的，不代表有问题）
- `sqlite3` 命令在 Termux 可能不存在，用 `python3 -c "import sqlite3; ..."` 代替
- Telegram 不稳定（DNS污染），报告通过飞书/QQ推送时不依赖 Telegram 状态
