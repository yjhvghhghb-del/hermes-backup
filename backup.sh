#!/bin/bash
# hermes-backup-daily.sh — 增量备份 knowledge/skills/memories 到 GitHub
# 用法: bash ~/hermes-backup/backup.sh
set -e
BACKUP_DATE=$(date +%Y%m%d)

cd ~

# 1. 从 live 目录打tar包，排除嵌套 .git
#    动态枚举 profiles（default 在 Termux 上不存在）
TAR_SRCS=".hermes/knowledge .hermes/skills .hermes/memories"
for profile_dir in .hermes/profiles/*/; do
  profile=$(basename "$profile_dir")
  for subdir in skills memories; do
    if [ -d "$profile_dir/$subdir" ]; then
      TAR_SRCS="$TAR_SRCS .hermes/profiles/$profile/$subdir"
    fi
  done
done
[ -d .hermes/hermes-agent/skills ] && TAR_SRCS="$TAR_SRCS .hermes/hermes-agent/skills"
[ -d .hermes/knowledge/skills ] && TAR_SRCS="$TAR_SRCS .hermes/knowledge/skills"

tar -czf hermes-backup-daily.tar.gz \
  --exclude='knowledge/我是老公/.git' \
  --exclude='knowledge/我是老公/.git/**' \
  --exclude='*/.git' \
  --exclude='*/.git/*' \
  $TAR_SRCS

# 2. 进入备份仓库
cd ~/hermes-backup

# 3. 清理嵌入式 .git 目录（避免 embedded repo warnings）
find work/.hermes -name ".git" -type d 2>/dev/null | while read d; do
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
