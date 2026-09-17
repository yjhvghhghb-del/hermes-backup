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
- **Credential verification (REQUIRED before first run):**
  ```bash
  # Verify PAT works before attempting any git operations
  curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: token $GITHUB_TOKEN" \
    https://api.github.com/user
  # Expected: 200. If 401/403/404 → credentials invalid or expired, fix before proceeding
  ```

> **Termux proxy note**: On Android/Termux, GitHub is only reachable via proxy. See `references/termux-proxy-auth.md` for the verified proxy config (`172.19.0.1:7890`) and curl/git patterns that work.
>
> **Incremental tar snapshot**: Use `--listed-incremental` with an **absolute path** for the snapshot file — `~` does NOT expand inside `--listed-incremental=<path>`. Use `/data/data/com.termux/files/home/hermes-backup/snapshot.list` on Termux. Create the file with `touch` before the first run.

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

## Actual Directory Structure on This System (Termux/Termux Herald)

**Do NOT assume `profiles/default/` exists — it does not.** The real structure is:

```
~/.hermes/
├── knowledge/               ← top-level knowledge (includes knowledge/skills/)
├── memories/                ← top-level memories (NOT under profiles/)
├── skills/                  ← top-level skills (NOT under profiles/)
├── hermes-agent/skills/     ← hermes-agent built-in skills
├── knowledge/skills/        ← knowledge-domain skills
└── profiles/
    ├── wenyu/{skills,memories}
    ├── siliconflow/{skills,memories}
    ├── licai/{skills,memories}
    ├── libai/{skills,memories}
    ├── cutegirl/{skills,memories}
    └── geekwife/{skills,memories}
```

**Note**: `profiles/default/` does NOT exist on Termux. Always enumerate actual profiles with `find ~/.hermes/profiles -maxdepth 1 -type d`. Current profiles: `cutegirl`, `geekwife`, `libai`, `licai`, `siliconflow`, `wenyu`.

## ⚠️ Failure Mode: Repo Does Not Exist (404)

When `git push` fails and API check returns 404:
```bash
curl -s --proxy http://172.19.0.1:7890 \
  https://api.github.com/repos/ClawTwice/hermes-backup
# → {"message": "Not Found"}
```
**Cause**: Repo was never created, or was deleted.
**Fix**: Create it via API (requires valid PAT with `repo` scope), then use HTTPS push:
```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"hermes-backup","private":true}' \
  https://api.github.com/user/repos
# 401 → token invalid/expired; 422 → name taken; 201 → created

# Switch remote to HTTPS with embedded token (SSH push fails on Termux)
cd ~/hermes-backup-git
git remote set-url origin "https://$GITHUB_TOKEN@github.com/ClawTwice/hermes-backup.git"
git push origin main --force  # first push sets upstream
```

## ⚠️ New Failure Mode: Missing GitHub Credentials Entirely

If `git push` fails with:
```
fatal: could not read Password for 'https://github.com': No such device or address
```
This means **no GitHub credential is configured at all** — not `gh auth`, no `$GITHUB_TOKEN`, no `~/.netrc`, no `credential.helper`. The remote URL may show `https://@github.com/...` (empty token placeholder).

**Diagnosis commands:**
```bash
# Check if gh is logged in
gh auth status 2>&1 | head -3

# Check for token env var
echo "GH_TOKEN_SET=$([ -n "$GITHUB_TOKEN" ] && echo yes || echo no)"

# Check .netrc for github credentials
grep -i github ~/.netrc 2>/dev/null && echo "NETRC_OK" || echo "NO_NETRC"

# Check git credential helper
git config --global credential.helper 2>/dev/null || echo "NO_CREDS_HELPER"

# Check remote URL for embedded token
git -C ~/hermes-backup-git remote get-url origin
```

**If credentials are missing — fix before proceeding:**
```bash
# Option A: set GITHUB_TOKEN env var (persistent: add to ~/.bashrc or profile)
export GITHUB_TOKEN="ghp_YOUR_TOKEN_HERE"

# Option B: embed in git remote URL (works, but token visible in process list / config)
git -C ~/hermes-backup-git remote set-url origin "https://$GITHUB_TOKEN@github.com/ClawRunner/hermes-backup.git"

# Option C: use gh auth login (interactive, persistent)
gh auth login
```

> **Always verify credentials before a push** — run the diagnosis commands above. If credentials are missing, the push will fail silently at the password prompt with no user present to type. Cron jobs run unattended; credentials MUST be pre-configured.

## Authentication on Termux (IMPORTANT)

### ⚠️ SSH (git@github.com:) is BROKEN on Termux — port 22 blocked

- `ssh -o ConnectTimeout=5 -T git@github.com` → **timed out** (port 22 unreachable)
- `curl https://github.com` → **200** (HTTPS port 443 works fine)
- **SSH remote URLs (`git@github.com:...`) will ALWAYS timeout on Termux**

**Required fix: switch to HTTPS with embedded PAT**

```bash
cd ~/hermes-backup-git
# Embed PAT directly in the HTTPS URL (no password prompt)
git remote set-url origin "https://$GITHUB_TOKEN@github.com/ClawTwice/hermes-backup.git"
git push origin main
```

If `$GITHUB_TOKEN` is not set, set it first:
```bash
export GITHUB_TOKEN="ghp_YOUR_TOKEN_HERE"
# Make persistent:
echo 'export GITHUB_TOKEN="ghp_YOUR_TOKEN_HERE"' >> ~/.bashrc
```

**Without both HTTPS remote + `$GITHUB_TOKEN` set, every push will fail.**

**✅ Working proxy pattern (2026-09-01):**
- `http.proxy http://172.19.0.1:7890` → git push WORKS
- `socks5://` proxy → git push SILENTLY HANGS (no error, just times out)
- `curl --proxy http://172.19.0.1:7890 https://github.com` → works
- `curl --proxy socks5h://172.19.0.1:7890 https://github.com` → times out (HTTP:000)

**⚠️ The `socks5://` scheme silently kills git push.** Even with `http.proxy socks5://172.19.0.1:7890` configured, `git push` hangs at the TCP level with no error message. Always use `http://` for the proxy scheme on Termux.

**Fix a stuck `socks5` proxy config — check BOTH repo-level and global:**
```bash
# 1. Check repo-level .git/config FIRST (this overrides global!)
git -C ~/hermes-backup-git cat .git/config

# 2. If repo-level socks5 proxy found, unset it at repo level
git -C ~/hermes-backup-git config --unset http.proxy
git -C ~/hermes-backup-git config --unset https.proxy

# 3. Then set correct proxy at global level
git config --global http.proxy http://172.19.0.1:7890
git config --global https.proxy http://172.19.0.1:7890
```

> ⚠️ **Repo-level `.git/config` silently overrides `~/.gitconfig`.** If the repo has `socks5h://` in its `.git/config`, unsetting only the global will not help — the repo-level entry takes precedence and git push will still hang silently. Always check `git cat .git/config` (not just `git config --list`) to see the actual effective config.

**`nc` SOCKS proxycommand does NOT work on Termux** (`nc -X connect` returns "unsupported proxy protocol"). Do not use `GIT_SSH_COMMAND` with nc on Termux.

**When GitHub is unreachable**: Local commit still succeeds; push retries on next run.

> **Fallback options**: Gitee mirror, Tencent COS upload via curl, or VPN tunnel. See `references/termux-proxy-auth.md` for alternatives.

**When to use SSH vs HTTPS — CONFIRMED 2026-09-07:**
- `git@github.com:owner/repo.git` (SSH remote) → **COMPLETELY BROKEN on Termux** — port 22 is blocked. `ssh git@github.com` times out at banner exchange. Do NOT attempt; it will always fail.
- `https://github.com/owner/repo.git` (HTTPS remote) → **ONLY working option on Termux**. MUST embed `$GITHUB_TOKEN` in the URL (e.g., `https://$GITHUB_TOKEN@github.com/...`) OR set `$GITHUB_TOKEN` as an env var. Without one of these, push fails with "could not read Username for 'https://github.com': No such device or address".

> ⚠️ **GitHub unreachable via proxy (2026-08-27 to 2026-08-28)**: On 老公's Termux Herald, even `nc` SOCKS proxy (`172.19.0.1:7890`) cannot reach GitHub — `curl --proxy socks5h://172.19.0.1:7890 https://api.github.com` returns `HTTP:000` (connection refused/failed), and both HTTPS git push and `GIT_SSH_COMMAND` push both timeout (~120s). GitHub may be blocked at the proxy level, or the proxy chain is down. When this happens:
> - **Local commit still succeeds** — backup is preserved locally in the git repo
> - **Do NOT re-tar** — the commit is already good; push retries automatically on next run
> - **Fallback options**: Gitee mirror, Tencent COS via curl, or VPN tunnel
```bash
#!/bin/bash
set -e
BACKUP_DATE=$(date +%Y%m%d)

# ── PRE-FLIGHT: verify GitHub credentials before any git work ──────────────
# Cron runs unattended — push will fail silently at password prompt with no
# user present. Must diagnose NOW, not after tar+cp+commit.
if ! gh auth status -h github.com >/dev/null 2>&1 && \
   [ -z "$GITHUB_TOKEN" ] && \
   ! grep -q "github.com" ~/.netrc 2>/dev/null; then
  echo "ERROR: No GitHub credentials found. Run: gh auth login or set \$GITHUB_TOKEN"
  TOKEN=$(grep TELEGRAM_BOT_TOKEN ~/.hermes/.env | cut -d= -f2 | tr -d ' ')
  curl -s "https://api.telegram.org/bot${TOKEN}/sendMessage" \
    -d "chat_id=877708648" \
    -d "text=❌ 备份失败：未配置 GitHub 认证凭据" 2>/dev/null || true
  exit 1
fi

# ── STEP 1: tar from live $HOME ────────────────────────────────────────────
# MUST cd ~ first, NOT ~/hermes-backup. See critical pitfall below.
cd ~

# Discover actual skills/memories/knowledge dirs dynamically
# 'default' does NOT exist on Termux — enumerate what's real
TAR_SRCS=".hermes/knowledge .hermes/memories .hermes/skills"
for profile_dir in .hermes/profiles/*/; do
  profile=$(basename "$profile_dir")
  for subdir in skills memories; do
    if [ -d "$profile_dir/$subdir" ]; then
      TAR_SRCS="$TAR_SRCS .hermes/profiles/$profile/$subdir"
    fi
  done
done
# Also include hermes-agent built-in skills
[ -d .hermes/hermes-agent/skills ] && TAR_SRCS="$TAR_SRCS .hermes/hermes-agent/skills"
[ -d .hermes/knowledge/skills ] && TAR_SRCS="$TAR_SRCS .hermes/knowledge/skills"

tar -czf hermes-backup-daily.tar.gz \
  --exclude='knowledge/我是老公/.git' \
  --exclude='knowledge/我是老公/.git/**' \
  $TAR_SRCS

# ── STEP 2: copy into git working tree BEFORE git commands ─────────────────
cp ~/hermes-backup-daily.tar.gz ~/hermes-backup/work/

# ── STEP 3: git operations in the repo dir ─────────────────────────────────
cd ~/hermes-backup
git add hermes-backup-daily.tar.gz
if ! git diff --cached --quiet; then
  git commit -m "backup $BACKUP_DATE"
fi

# ── STEP 4: push (git push is currently blocked by proxy on this system) ───
# GIT_SSH_COMMAND with nc proxycommand does NOT work on Termux (nc -X connect
# returns "unsupported proxy protocol"). Push will fail until GitHub is reachable.
# The local commit is preserved; push retries automatically on next cron run.
git push origin main 2>/dev/null || echo "Push pending (GitHub unreachable)"
```

> **Pre-flight credential check is mandatory** — without it, `git push` hangs at a password prompt with no user to respond. The check above covers all four auth methods (`gh`, `$GITHUB_TOKEN`, `.netrc`, embedded URL). See `references/git-credential-diagnosis.md` for full diagnosis commands and expected outputs.

## ⚠️ Pre-flight Guard — MUST Run Before Tarring

Every backup invocation (cron, manual, or subagent) MUST run this guard FIRST:

```bash
# === PRE-FLIGHT: credentials check ===
if ! gh auth status -h github.com >/dev/null 2>&1 && \
   [ -z "$GITHUB_TOKEN" ] && \
   ! grep -q "github.com" ~/.netrc 2>/dev/null && \
   ! git -C ~/hermes-backup remote get-url origin | grep -q '@'; then
  echo "ERROR: No GitHub credentials. git push will fail."
  # Notify and abort
  python3 -c "
import requests
with open('$HOME/.hermes/.env') as f:
    for line in f:
        if 'TELEGRAM_BOT_TOKEN' in line:
            token = line.split('=',1)[1].strip()
            break
requests.post(f'https://api.telegram.org/bot{token}/sendMessage',
    json={'chat_id': '877708648', 'text': '❌ 备份失败：未配置 GitHub 认证凭据'},
    proxies={'https': 'socks5h://10.1.252.196:7891'}, timeout=15)
"
  exit 1
fi
# === END PRE-FLIGHT ===
```

**Why this matters**: cron runs without a terminal. If credentials are missing, `git push` stalls at a password prompt indefinitely and the job never completes. The guard above is in `~/hermes-backup/backup.sh` — always use that script, never run raw `git add/commit/push` from `~`.

> **⚠️ Hidden-file naming**: `tar` output must NOT be named with a leading dot (`.hermes-backup-daily.tar.gz`). `git add` silently ignores dot-prefixed files in working trees — `git add .` and `git add -A` both skip them. Use `hermes-backup-daily.tar.gz` as the filename. See `references/termux-proxy-auth.md` for the full failure symptom and fix.

> **⚠️ CRITICAL PITFALL — Always re-tar from live `$HOME` directories!**
>
> The deployed `backup.sh` on 2026-08-08 was MISSING the re-tar step. Its
> sequence was: `cd ~/hermes-backup` → clean .git → `git add -A` → push.
> This committed the SAME tar from the previous run every time — never capturing
> new changes. The script looked structurally correct but silently did nothing.
>
> **Every run MUST:**
> 1. `cd ~` (not `~/hermes-backup`)
> 2. `tar -czf hermes-backup-daily.tar.gz` from live `.hermes/` dirs
> 3. `cp ~/hermes-backup-daily.tar.gz work/`
> 4. `cd ~/hermes-backup` — THEN git commands
>
> **Verification checklist after any edit to backup.sh:**
> ```bash
> bash -x ~/hermes-backup/backup.sh 2>&1 | grep -E 'tar|cp|commit|push'
> # Must see ALL four: tar -czf ..., cp ..., git commit ..., git push ...
> # If you only see git commit/push → re-tar is missing → script is broken
> ```

**Incremental mechanism**: each run overwrites `work/hermes-backup-daily.tar.gz` — git stores only the binary delta between tar versions. The actual tar is ~15 MB; git delta is typically small.

## ⚠️ Critical: GitHub Secret Scanning Blocks Pushes

GitHub push protection scans every commit **before** acceptance, even on public repos. Three categories blocked:

| Type | Example | Detection rule |
|------|---------|----------------|
| GitHub PATs | `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` | `ghp_` + 36 alphanumeric |
| Lark/Feishu secrets | `<LARK_SECRET_EXAMPLE>` | 32-char base58-like string |
| Other long tokens | `9w519nveoLWESPvXicJiEeqhb76w6rh3` | 30+ char alphanumeric |

**Pre-commit redaction (BEFORE tarring) — REQUIRED every run:**

```python
secrets = [
    ('ghp_FULL_TOKEN_HERE', '<PAT_REDACTED>'),
    ('<LARK_SECRET_EXAMPLE>', '<LARK_SECRET_1>'),
    ('<LARK_SECRET_EXAMPLE>', '<LARK_SECRET_2>'),
    ('<LARK_SECRET_EXAMPLE>', '<LARK_SECRET_3>'),
]
for old, new in secrets:
    content = content.replace(old, new)
```

**Key rules:**
1. Redact BEFORE tarring — secrets are embedded in the tar and detectable even if you later amend the commit
2. Truncated tokens like `<PAT_REDACTED>...geF1` (with `...` in middle) are STILL matched — use completely different placeholder strings like `<PAT_REDACTED>`
3. After sanitizing, amend the commit: `git commit --amend --no-edit` then push

**Files to sanitize before tarring:** `MEMORY.md`, `USER.md`, any `SKILL.md` with credentials, `config.yaml` files, `wenyu-config.yaml` style profile files.

> See `references/push-protection-secret-scanning.md` for the complete recovery sequence (live-tested), all detected secret patterns, and a pre-commit hook to prevent future blocks.

## ⚠️ Pitfall: Embedded `.git` Directories

`knowledge/` may contain nested git repos (e.g. `我是老公/.git`). Causes:
```
warning: adding embedded git repository: work/.hermes/knowledge/我是老公
```

**Fix**: Before staging:
```bash
find work/.hermes/knowledge -name ".git" -type d -exec rm -rf {} + 2>/dev/null || true
> See `references/termux-proxy-auth.md` for the full failure symptom and fix.

## ⚠️ Pitfall: GitHub Unreachable — DNS + Proxy Timeout Chain

When Termux has no direct internet and GitHub DNS fails:
```
ssh: Could not resolve hostname github.com: No address associated with hostname
fatal: Could not read from remote repository
```
Or push simply **hangs and times out** (180s) even with `http.proxy` set.

**Diagnosis:**
```bash
# Test DNS resolution via proxy
curl -s --proxy socks5://172.19.0.1:7890 \
  https://api.github.com/zen 2>&1 | head -3

# Test git push with verbose to see where it hangs
GIT_CURL_VERBOSE=1 GIT_TRACE=1 git push origin main 2>&1 | grep -i 'connect|proxy|dns'
```

**If DNS fails**: The proxy itself (`172.19.0.1:7890`) may not be routing DNS, or the proxy chain is down. Try the fallback proxy `192.168.110.225:7891`.

**If push times out on HTTPS**: `http.proxy` may not apply to all git HTTP operations. The `nc` SOCKS approach is more reliable:
```bash
# SSH-style push via SOCKS proxy — more reliable than http.proxy on Termux
GIT_SSH_COMMAND="ssh -o ProxyCommand='nc -X connect -x 172.19.0.1:7890 %h %p'" \
  git push origin main
```
Note: SSH push only works when the remote URL is `git@github.com:...` (SSH), not `https://github.com/...` (HTTPS). If the remote is HTTPS, either convert it to SSH or use `curl` with the proxy for HTTPS git operations.

> ⚠️ **GitHub may be temporarily unreachable via proxy**: When `http.proxy` is misconfigured as `socks5://`, `git push` silently hangs. The local commit is always preserved — push retries automatically on next run. See proxy fix above.

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

- `references/session-2026-09-03.md` — real error trace: repo-level socks5 proxy override silently killed git push; fixed by reading `.git/config` directly
- `references/session-2026-09-04.md` — all GitHub credentials missing (no PAT, no gh auth); all Telegram bot tokens 404; repo `ClawTwice/hermes-backup` doesn't exist; precise "could not read Username for 'https://github.com'" error documented
- `references/session-2026-09-05.md` — repo actually doesn't exist (404); SSH push times out on Termux; only HTTPS with embedded PAT works; working dir is `~/hermes-backup-git` (not `~/hermes-backup`)
- `references/session-2026-09-06.md` — SSH remote (`git@github.com:`) times out because Termux blocks port 22; HTTPS needs embedded PAT (`$GITHUB_TOKEN` env var OR PAT in URL); no other auth configured; local commit succeeds but push always fails until credentials set
- `references/session-2026-09-07.md` — Confirmed: SSH remote completely broken on Termux (port 22 blocked, banner timeout); HTTPS remote with no embedded token fails with "could not read Username"; only HTTPS+$GITHUB_TOKEN works; local commit succeeded, push pending
- `references/session-2026-09-10.md` — Cron backup ran; tar succeeded (80 MB); git init + push failed — repo `yujn/termux-hermes-backup` may not exist or credentials missing; all 3 Telegram bot tokens are 401/404 (bots deleted); notification cannot be sent; backup preserved locally
- `references/session-2026-09-11.md` — Backup succeeded (21 MB tar, push to main worked); all 3 bot tokens return 401 (revoked, not deleted); notification silently fails

## Telegram Notification

**`curl` with `socks5h://` proxy returns 401 Unauthorized** — even with the correct bot token, `curl -x socks5h://...` silently fails authentication.

**Python `requests` with `socks5h://` works correctly.** Always use Python for Telegram notifications from cron jobs:

```python
import requests, os

with open(os.path.expanduser('~/.hermes/.env')) as f:
    for line in f:
        if 'TELEGRAM_BOT_TOKEN' in line:
            TOKEN = line.split('=')[1].strip()
            break

proxies = {'https': 'socks5h://10.1.252.196:7891'}
msg = '📦 Hermes 备份完成\n• 已 push origin main ✅'
r = requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage',
    json={'chat_id': '877708648', 'text': msg}, proxies=proxies, timeout=15)
```

Read token from `~/.hermes/.env` dynamically — never hardcode the token string.

## See Also

- `references/termux-proxy-auth.md` — proxy config for GitHub API/git on Termux
- `references/push-protection-secret-scanning.md` — GitHub secret scanning blocks & recovery
- `references/git-credential-diagnosis.md` — diagnosis commands for all 5 GitHub auth methods
- `references/session-2026-09-12.md` — curl 401 vs Python requests success, working proxy `10.1.252.196:7891`
- `references/session-2026-09-16.md` — no GitHub credentials (7th consecutive session); SSH dead on Termux; only HTTPS+$GITHUB_TOKEN works; local commit always succeeds, push always fails pending credentials
