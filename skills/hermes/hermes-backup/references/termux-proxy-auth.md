# Termux + GitHub Proxy Authentication

Termux on Android cannot reach GitHub directly — requires proxy.

## Proxy Configuration Used

- **Proxy**: `172.19.0.1:7890` (Claw's LAN proxy, returns 404 = reachable)
- **Fallback proxy**: `192.168.110.225:7891`
- **GitHub user**: `yjhvghhghb-del`
- **GitHub PAT**: stored in `~/.gitconfig` or `$GITHUB_TOKEN` env var — never hardcode in skill files

## API Token Extraction for curl

Since `gh` CLI is not available on Termux, all GitHub API calls use curl with the PAT:

```bash
curl --proxy http://172.19.0.1:7890 \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user/repos
```

For embedding in git remote URL:
```bash
git remote set-url origin https://$GITHUB_TOKEN@github.com/$USER/hermes-backup.git
```

## git clone / push via HTTPS through proxy

Set globally:
```bash
git config --global http.proxy http://172.19.0.1:7890
git config --global https.proxy http://172.19.0.1:7890
```

Or per-command:
```bash
git -c http.proxy=http://172.19.0.1:7890 clone https://github.com/owner/repo.git
```

## SSH through proxy (WORKS on Termux with nc proxycommand)

SSH via `git@github.com` works on Termux when routed through SOCKS proxy using `GIT_SSH_COMMAND` with `nc` — this was live-tested 2026-08-21.

> ⚠️ **GitHub may be unreachable via proxy (2026-08-27)**: On 老公's Termux Herald environment, both `nc` SOCKS push and HTTPS git push timeout (~120s) even through `172.19.0.1:7890`. Local commit still succeeds. Push retries on next cron run automatically. Fallback: Gitee mirror, Tencent COS, or VPN.

## ⚠️ Hidden files in git working tree (critical git add failure)

When the backup tar is named `.hermes-backup-daily.tar.gz` (starts with `.`), `git add hermes-backup-daily.tar.gz` silently does nothing. Git reports the file as "untracked" but refuses to stage it.

**Symptom** — after `cp ~/.hermes-backup-daily.tar.gz .`:
```
On branch main
Untracked files:
    .hermes-backup-daily.tar.gz
(use "git add <file>..." to include in what will be committed)
nothing added to commit
```

**Root cause**: `git add <name>` matches the filesystem name. When the file is named `.hermes-backup-daily.tar.gz` (dot-prefixed), git's path matching treats it as a hidden file that must be explicitly named — `git add .` and `git add -A` ignore dotfiles in the working tree.

**Fix**: Rename before staging, or use explicit dot-prefix path:
```bash
mv .hermes-backup-daily.tar.gz hermes-backup-daily.tar.gz
git add hermes-backup-daily.tar.gz
# OR use explicit path
git add .hermes-backup-daily.tar.gz
```

**Prevention**: Name the backup tar without a leading dot, e.g. `hermes-backup-daily.tar.gz` not `.hermes-backup-daily.tar.gz`.

> **Important**: `api.mytokk.com` is a MiniMax model relay, NOT a GitHub proxy. Do NOT use it for GitHub API calls.
