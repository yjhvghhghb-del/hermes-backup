# Termux + GitHub Proxy Authentication

Termux on Android cannot reach GitHub directly — requires proxy.

## Proxy Configuration Used

- **Proxy**: `172.19.0.1:7890` (Claw's LAN proxy, returns 404 = reachable)
- **Fallback proxy**: `192.168.110.225:7891`
- **GitHub PAT**: `GH_PAT_REDACTED`
- **GitHub user**: `yjhvghhghb-del`

## API Token Extraction for curl

Since `gh` CLI is not reliably available on Termux, all GitHub API calls use curl with the PAT:

```bash
curl --proxy http://172.19.0.1:7890 \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user/repos
```

For embedding in git remote URL:
```bash
git remote set-url origin https://$GITHUB_TOKEN@github.com/$USER/hermes-backup.git
```

## Verified Approach: git clone https://github.com/... works

The git protocol handles proxies automatically when `http.proxy` is set, or by using `--proxy` flag:
```bash
git -c http.proxy=http://172.19.0.1:7890 clone https://github.com/owner/repo.git
```

Or set globally:
```bash
git config --global http.proxy http://172.19.0.1:7890
git config --global https.proxy http://172.19.0.1:7890
```

## Alternative: GitHub API via api.mytokk.com

The MiniMax API relay at `api.mytokk.com` also proxies GitHub API requests. Use `ANTHROPIC_API_KEY` (which is the MiniMax key) for auth. Pattern:
```bash
curl -s --proxy http://172.19.0.1:7890 \
  -H "Authorization: Bearer $ANTHROPIC_API_KEY" \
  https://api.github.com/user
```
(Note: this specific endpoint may not work for all GitHub API calls — the api.mytokk.com route was primarily verified for MiniMax models)
