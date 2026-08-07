---
name: hermes-backup
description: "Incremental backup of ~/.hermes to GitHub."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, termux, macos, windows]
metadata:
  hermes:
    tags: [backup, hermes, git, github, incremental, cron]
    related_skills: [github-auth, github-repo-management]
---

# Hermes Backup — Incremental Backup to GitHub

Backup `~/.hermes/knowledge`, `~/.hermes/skills`, `~/.hermes/memories` to a private GitHub repo. Fully incremental — only changed files are committed each run.

## Prerequisites

- GitHub PAT with `repo` scope (stored as `$GITHUB_TOKEN` or embedded in remote URL)
- Repo `hermes-backup` created under the user's GitHub account
- `git`, `tar` available

> **Termux proxy note**: On Android/Termux, GitHub is only reachable via proxy. See `references/termux-proxy-auth.md` for the verified proxy config (`172.19.0.1:7890`) and curl/git patterns that work.

## One-Time Setup

```bash
# 1. Create the backup repo via API
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"hermes-backup","private":true}' \
  https://api.github.com/user/repos

# 2. Clone it
git clone https://github.com/$GH_USER/hermes-backup.git ~/hermes-backup

# 3. Configure git identity
cd ~/hermes-backup
git config user.name "$GH_USER"
git config user.email "$GH_USER@users.noreply.github.com"
git remote set-url origin https://$GITHUB_TOKEN@github.com/$GH_USER/hermes-backup.git

# 4. Add .gitignore
echo -e ".git\n.gitignore\n*.lock" > .gitignore
git add .gitignore && git commit -m "Add .gitignore" && git push origin main
```

## Daily Backup Script

Save as `~/hermes-backup/backup.sh`:

```bash
#!/bin/bash
set -e
cd ~/hermes-backup
git fetch origin main

# Create tar from live hermes dirs
cd ~
tar -czf hermes-backup-daily.tar.gz .hermes/knowledge .hermes/skills .hermes/memories

# Extract into work/ (git works from work/ tree)
cd ~/hermes-backup
rm -rf work && mkdir -p work
tar -xzf ~/hermes-backup-daily.tar.gz -C work

# Remove embedded .git dirs (causes "adding embedded git repository" errors)
find work/.hermes/knowledge -name ".git" -type d -exec rm -rf {} + 2>/dev/null || true

# Stage and commit
git add -A
if ! git diff --cached --quiet; then
  git commit -m "Backup $(date '+%Y-%m-%d %H:%M')"
fi

git push origin main
echo "Backup done $(date)"
```

## ⚠️ Critical: GitHub Secret Scanning Blocks Pushes

GitHub push protection scans every commit **before** acceptance, even on public repos. Three categories blocked:

| Type | Example | Detection rule |
|------|---------|----------------|
| GitHub PATs | `GH_PAT_REDACTED` | `ghp_` + 36 alphanumeric |
| Lark/Feishu secrets | `nMXvHNQmE8o0obLOV3GXVff1qoj76NWu` | 32-char base58-like string |
| Other long tokens | `9w519nveoLWESPvXicJiEeqhb76w6rh3` | 30+ char alphanumeric |

**Pre-commit redaction (BEFORE tarring):**

```python
secrets = [
    ('ghp_FULL_TOKEN_HERE', '<PAT_REDACTED>'),
    ('nMXvHNQmE8o0obLOV3GXVff1qoj76NWu', '<LARK_SECRET_1>'),
    ('BI0RpisjwTuwI1o670OXRb2e7oxLM7dG', '<LARK_SECRET_2>'),
    ('MpxugHJ0FzlcbEPSmi6zZb57YiGzhmgl', '<LARK_SECRET_3>'),
]
for old, new in secrets:
    content = content.replace(old, new)
```

**Key rules:**
1. Redact BEFORE tarring — never after, as the secret is already in the tar.gz
2. `ghp_MR...geF1` (with `...` in middle) is STILL detected — use completely different placeholder strings like `<PAT_REDACTED>`
3. Always check: `MEMORY.md`, `USER.md`, any `SKILL.md` with credentials, `config.yaml` files

## ⚠️ Pitfall: Embedded `.git` Directories

`knowledge/` may contain nested git repos (e.g. `我是老公/.git`). Causes:
```
warning: adding embedded git repository: work/.hermes/knowledge/我是老公
```

**Fix**: Before staging:
```bash
find work/.hermes/knowledge -name ".git" -type d -exec rm -rf {} + 2>/dev/null || true
```

## Restoring from Backup

```bash
git clone https://github.com/$GH_USER/hermes-backup.git /tmp/restore
cd /tmp/restore
tar -xzf hermes-backup-daily.tar.gz -C ~
```

## Cron Setup

```bash
crontab -e
# Daily at 3 AM
0 3 * * * bash /data/data/com.termux/files/home/hermes-backup/backup.sh >> ~/hermes-backup/backup.log 2>&1
```
