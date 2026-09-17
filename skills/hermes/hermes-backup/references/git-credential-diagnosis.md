# Git Credential Diagnosis for Termux/Terminal Cron Jobs

Run these commands to identify which GitHub authentication method (if any) is configured. **Must be diagnosed BEFORE attempting `git push`** — cron jobs run unattended and will fail silently at a password prompt.

## Quick Check (One-Liner)

```bash
gh auth status 2>&1 | head -3; echo "GH_TOKEN=$([ -n "$GITHUB_TOKEN" ] && echo set || echo unset)"; grep -q "github.com" ~/.netrc 2>/dev/null && echo "NETRC=ok" || echo "NETRC=missing"
```

## Per-Method Checks

### Method 1: `gh` CLI
```bash
gh auth status 2>&1 | head -3
```
- **200/authenticated** → `gh` is logged in; SSH or HTTPS push will work
- **Not logged in** → `gh auth login` needed, or fall back to token/env

### Method 2: `$GITHUB_TOKEN` environment variable
```bash
echo "GH_TOKEN_SET=$([ -n "$GITHUB_TOKEN" ] && echo yes || echo no)"
```
- **yes** → token is set; HTTPS push with `https://$GITHUB_TOKEN@github.com/...` remote URL will work
- **unset** → set `export GITHUB_TOKEN=ghp_...` in shell profile or cron env

### Method 3: `~/.netrc` machine login
```bash
grep -i "github.com" ~/.netrc 2>/dev/null && echo "NETRC_OK" || echo "NO_NETRC"
```
- **NETRC_OK** → credentials present; git uses them automatically for HTTPS
- **NO_NETRC** → no `.netrc` credential entry for github.com

### Method 4: Git credential helper
```bash
git config --global credential.helper 2>/dev/null || echo "NO_CREDS_HELPER"
```
- **store / osxkeychain / etc.** → helper is active; credentials sourced from disk keychain
- **empty/NO_CREDS_HELPER** → no helper; must use one of the above methods

### Method 5: Embedded token in remote URL
```bash
git -C ~/hermes-backup remote get-url origin | grep -o 'https://[^@]*@github.com'
```
- **empty** → no embedded token; push will prompt for password
- **shows URL with `@`** → token is embedded; push will succeed

## SSH Check (for `git@github.com:...` remote)

```bash
ssh -o ConnectTimeout=5 -T git@github.com 2>&1 | head -3
```

- **timed out** → **port 22 is blocked on Termux** — SSH remote will NEVER work; switch to HTTPS with embedded PAT immediately
- **Permission denied (publickey)** → SSH is reachable but key not configured; switch to HTTPS with embedded PAT
- **Hi username!** → SSH handshake succeeded; SSH remote is viable on this system

> ⚠️ **On Termux (2026-09-06 confirmed):** `ssh -o ConnectTimeout=5 -T git@github.com` times out every time. GitHub port 443 (HTTPS) works fine (`curl https://github.com` → 200). SSH (`git@github.com:` URLs) is broken and must be replaced with HTTPS remote + embedded `$GITHUB_TOKEN`.

## Expected Outputs by Auth Status

| Scenario | gh status | $GITHUB_TOKEN | .netrc | remote URL |
|----------|-----------|---------------|---------|------------|
| Fully configured (gh) | authenticated | unset | missing | git@github.com |
| Token in env | not logged in | set | missing | https://github.com |
| Token in .netrc | not logged in | unset | present | https://github.com |
| Token in URL | not logged in | unset | missing | https://TOKEN@github.com |
| **Nothing configured** | not logged in | unset | missing | https://github.com |

## If Nothing Is Configured — Fix

```bash
# Option A: GITHUB_TOKEN env var (simplest for cron)
export GITHUB_TOKEN="ghp_YOUR_TOKEN_HERE"
# Add to ~/.bashrc or profile to persist

# Option B: embed in git remote URL
git -C ~/hermes-backup remote set-url origin "https://$GITHUB_TOKEN@github.com/USER/hermes-backup.git"

# Option C: gh auth login (interactive, persistent)
gh auth login

# Option D: .netrc
echo "machine github.com login YOUR_USER password ghp_TOKEN" >> ~/.netrc
chmod 600 ~/.netrc
```

## Verification Before Push

Always run this before the push step in `backup.sh`:

```bash
# Pre-flight: verify at least one auth method is available
if ! gh auth status -h github.com >/dev/null 2>&1 && \
   [ -z "$GITHUB_TOKEN" ] && \
   ! grep -q "github.com" ~/.netrc 2>/dev/null; then
  echo "ERROR: No GitHub credentials found. Backup will fail. Fix before proceeding."
  exit 1
fi
```
