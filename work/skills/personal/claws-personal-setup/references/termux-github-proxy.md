# Termux/Android GitHub Proxy

Termux on Android cannot resolve `github.com` via DNS. GitHub traffic must go through the SOCKS5 proxy. SSH and HTTPS API use different proxy mechanisms.

## Quick Setup

```bash
# 1. Install netcat (provides nc)
apt install netcat-openbsd -y

# 2. Test SSH through proxy
ssh -o StrictHostKeyChecking=no \
    -o ProxyCommand="nc -X connect -x 172.19.0.1:7890 %h %p" \
    git@github.com
# Expected: "Hi <username>! You've successfully authenticated..."

# 3. Persist SSH proxy for git globally
git config --global core.gitProxy "ssh -o ProxyCommand='nc -X connect -x 172.19.0.1:7890 %h %p'"

# 4. Persist HTTPS proxy for API calls
git config --global https.proxy http://172.19.0.1:7890
git config --global http.proxy http://172.19.0.1:7890
```

## Why Two Different Configs?

| Traffic | Method | Config |
|---------|--------|--------|
| SSH git push/pull | SOCKS5 via netcat | `core.gitProxy` or `GIT_SSH_COMMAND` |
| HTTPS API (curl, gh) | HTTP proxy env var | `https.proxy` git config or `$https_proxy` env |

## Verification

```bash
# SSH auth works?
ssh -o StrictHostKeyChecking=no \
    -o ProxyCommand="nc -X connect -x 172.19.0.1:7890 %h %p" \
    git@github.com

# git push works?
git push -u origin main

# API works?
export https_proxy=http://172.19.0.1:7890
curl -s https://api.github.com/users/yjhvghhghb-del/repos
```

## Key Gotcha

- `git push` works but `curl https://api.github.com/...` returns 404 → need `https_proxy` env var, SSH proxy doesn't cover HTTPS API
- Install `netcat-openbsd` first — without it, SSH proxy command fails with "nc: cannot execute"
