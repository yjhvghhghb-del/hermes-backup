#!/bin/bash
set -e
cd ~/hermes-backup

# Remove embedded .git directories (they cause "adding embedded git repository" warnings)
find work -name ".git" -type d 2>/dev/null | while read d; do
  echo "Removing embedded git repo: $d"
  rm -rf "$d"
done

# Remove work dir from index if still there
git rm --cached -rf work >/dev/null 2>&1 || true

# Remove work dir physically
rm -rf work

# Move .hermes from old backup
if [ -d ~/hermes-backup-old/.hermes ]; then
  cp -r ~/hermes-backup-old/.hermes ~/hermes-backup/
  rm -rf ~/hermes-backup-old
  echo "Restored .hermes from old backup"
fi

# Stage changes
git add -A

# Commit only if there are changes
if ! git diff --cached --quiet; then
  git commit -m "Backup $(date '+%Y-%m-%d %H:%M')"
  echo "Committed"
else
  echo "No changes to commit"
fi

# Push
git push origin main
echo "Pushed"
