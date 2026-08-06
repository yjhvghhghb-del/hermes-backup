#!/bin/bash
# hermes-backup-daily.sh — 增量备份 knowledge/skills/memories 到 GitHub
# 用法: bash ~/hermes-backup/backup.sh
set -e
cd ~/hermes-backup

# 拉取最新
git fetch origin main

# 清理嵌入式 .git 目录（避免 embedded repo warnings）
find work/.hermes/knowledge -name ".git" -type d 2>/dev/null | while read d; do
  rm -rf "$d"
done

# Stage 增量
git add -A

# 有变化才提交
if ! git diff --cached --quiet; then
  git commit -m "Backup $(date '+%Y-%m-%d %H:%M')"
fi

# Push
git push origin main
echo "Backup done $(date)"
