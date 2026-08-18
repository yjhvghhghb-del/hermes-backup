#!/bin/bash
# hermes-backup-daily.sh — 增量备份 knowledge/skills/memories 到 GitHub
# 用法: bash ~/hermes-backup/backup.sh
set -e
BACKUP_DATE=$(date +%Y%m%d)

cd ~

# 1. 从 live 目录打tar包，排除嵌套 .git
tar -czf hermes-backup-daily.tar.gz \
  --exclude='knowledge/我是老公/.git' \
  --exclude='knowledge/我是老公/.git/**' \
  .hermes/knowledge \
  .hermes/skills \
  .hermes/memories

# 2. 进入备份仓库
cd ~/hermes-backup

# 3. 清理嵌入式 .git 目录（避免 embedded repo warnings）
find work/.hermes/knowledge -name ".git" -type d 2>/dev/null | while read d; do
  rm -rf "$d"
done

# 4. 复制新tar到work目录
cp ~/hermes-backup-daily.tar.gz work/

# 5. Stage 增量
git add -A

# 有变化才提交
if ! git diff --cached --quiet; then
  git commit -m "Backup $(date '+%Y-%m-%d %H:%M')"
fi

# Push
git push origin main
echo "Backup done $(date)"
