---
name: coding-agents-on-android
description: "Run coding agents on Android/Termux."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [android, termux]
metadata:
  hermes:
    tags: [coding-agent, android, termux, platform-constraints, proot]
    related_skills: [claude-code, codex, opencode]
---

# Coding Agents on Android/Termux

## Core Problem

Android/Termux uses **bionic libc** — not glibc, not musl. Coding agent CLIs ship platform-specific native binaries linked against glibc or musl. These binaries fail with `required file not found` or `libc.so.6 => not found` errors on Android/Termux.

## Platform Detection Failures

| Binary | Linked against | Result |
|--------|----------------|--------|
| `codex-linux-arm64` | glibc | `ld-linux-aarch64.so.1 => not found` |
| `claude-code-linux-arm64` | glibc | `libc.so.6 => not found` |
| `claude-code-linux-arm64-musl` | musl | `libc.musl-aarch64.so.1 => not found` |
| `opencode-linux-arm64` | glibc | `libc.so.6 => not found` |
| `opencode-linux-arm64-musl` | musl | `libstdc++.so.6 => not found` |

npm reports `EBADPLATFORM: notsup` but `--force` installation succeeds — the binary simply can't execute.

## Verified Workaround: proot-distro

Run a full Linux container inside Termux:

```bash
pkg install proot-distro
proot-distro install ubuntu
proot-distro login ubuntu
# Inside Ubuntu, install the agent normally
```

The Ubuntu container has glibc and can run the standard Linux binaries.

## Verified Working: Claude Code + mytokk in proot-distro Ubuntu

Claude Code CLI runs successfully inside the Ubuntu container with the correct environment variables.

### Setup: Wrapper Script at `/usr/bin/claude`

Replace Termux's broken symlink with a wrapper that routes to the Ubuntu container with auth env vars pre-injected:

```bash
# Remove the broken Termux symlink first
rm /data/data/com.termux/files/usr/bin/claude

# Create wrapper at /usr/bin/claude
cat > /data/data/com.termux/files/usr/bin/claude << 'WRAPPER'
#!/data/data/com.termux/files/usr/bin/bash
export PATH='/data/data/com.termux/files/usr/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
export ANTHROPIC_BASE_URL='https://api.mytokk.com'
export ANTHROPIC_AUTH_TOKEN='sk-211ba2142f4704a7ae8e3b00fa9fb3786775504ff42535f284021ceb89a187a2'
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
export CLAUDE_CODE_ATTRIBUTION_HEADER=0
exec proot-distro login ubuntu -- /usr/bin/claude "$@"
WRAPPER
chmod +x /data/data/com.termux/files/usr/bin/claude
```

### Key Environment Variables (CRITICAL)

| Variable | Value | Notes |
|----------|-------|-------|
| `ANTHROPIC_BASE_URL` | `https://api.mytokk.com` | **No `/v1` suffix** — unlike other providers |
| `ANTHROPIC_AUTH_TOKEN` | `sk-211ba...` | Not `ANTHROPIC_API_KEY` |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | `1` | Reduces non-essential API calls |
| `CLAUDE_CODE_ATTRIBUTION_HEADER` | `0` | Disables attribution header |

### Verified Working CLI Usage

```bash
# Simple text task
claude -p 'say hello' --max-turns 1 --model claude-opus-4-8

# Coding task (write + run)
claude -p 'Write hello.py that prints Hello, run it' --max-turns 3 --model claude-opus-4-8 --allowedTools 'Read,Write,Bash'

# Auth verification
claude auth status --text
# Expected output:
#   Auth token: ANTHROPIC_AUTH_TOKEN
#   Anthropic base URL: https://api.mytokk.com
```

### Available Models on mytokk (via `claude -p --model` flag)

- `claude-opus-4-8` ✅ works
- `claude-opus-4-6` ✅ works
- `claude-sonnet-4-6` ✅ works
- `sonnet` / `haiku` → resolves to `claude-sonnet-5` / `claude-haiku-5` which may not exist — use full names

### mytokk API quirks

- **No `/v1` in `ANTHROPIC_BASE_URL`** — adding it causes 404 on model resolution
- **`claude auth status` may fail with "no access"** even when the key is valid — the key works via CLI but the auth check may not reflect actual model entitlement
- **curl directly to `/v1/messages` is blocked** — mytokk only accepts official Claude Code CLI traffic
- **mytokk has client fingerprint detection** — non-CLI requests to `/v1/chat/completions` or `/v1/messages` return http 200 with empty stream body (`EmptyStreamError` in Hermes logs). Only the official `claude` CLI can successfully make model calls through mytokk.

### proot-distro PATH Gotcha

When wrapping with `proot-distro login`, `$PATH` inside the container differs from Termux. The wrapper above hardcodes the container's PATH. Without this, `/usr/bin/claude` resolves correctly inside the container but may be unreachable during proot's exec.

## Verified Working: OpenCode in proot-distro Ubuntu

OpenCode installs and runs successfully inside the Ubuntu container via npm:

```bash
proot-distro login ubuntu
npm install -g opencode-ai          # v1.18.18 installed
opencode --version                  # confirm
```

**Two working provider configurations:**

### Option A — SiliconFlow (recommended, works out of the box)
```json
{
  "provider": {
    "siliconflow": {
      "options": {
        "baseURL": "https://api.siliconflow.cn/v1",
        "apiKey": "sk-gbqejbhbccufgsqgejnbstovckcllkluqtwjlnpumvmllngb"
      },
      "npm": "@ai-sdk/openai"
    }
  }
}
```
- Working models: `Qwen/Qwen3-14B` (general), `Qwen/Qwen3-Coder-30B-A3B-Instruct` (code)
- Run: `opencode run 'task' -m 'siliconflow/Qwen/Qwen3-14B' --dir /project`
- Note: Qwen3-Coder outputs code as text, does not invoke file-write tool calls

### Option B — mytokk (key has Claude entitlement issues)
```json
{
  "provider": {
    "anthropic": {
      "options": {
        "baseURL": "https://api.mytokk.com/v1sk-211ba2142f4704a7ae8e3b00fa9fb3786775504ff42535f284021ceb89a187a2",
        "apiKey": "sk-211ba2142f4704a7ae8e3b00fa9fb3786775504ff42535f284021ceb89a187a2"
      },
      "npm": "@ai-sdk/anthropic"
    }
  }
}
```
- Run: `opencode run 'task' -m 'anthropic/claude-opus-4-8' --dir /project`
- **Known issue**: API call succeeds (no error), but token counts come back as 0 — SDK may not parse the response correctly. Needs further investigation.
- **mytokk key status**: `claude auth status` returns ✅ oauth success, but all Claude model invocations return "may not have access" — account lacks Claude model entitlement. Check mytokk dashboard.

## mytokk Proxy — Client Detection

`api.mytokk.com` blocks non-official clients with:

```
"我们检测到您的客户端存在异常，请使用标准 Claude Code 客户端请求"
```

- `/v1/chat/completions` — blocked for curl/custom clients on Claude models
- `/v1/messages` (Anthropic native) — blocked the same way
- `/v1/models` — **not blocked**, returns model list fine with Bearer auth
- Key-as-URL-path format (`/v1sk-<key>/...`) works for listing models

## Checklist Before Starting a Coding Agent on Termux

- [ ] Android/Termux → use proot-distro (bionic incompatibility with glibc/musl)
- [ ] `proot-distro login ubuntu` → `npm install -g opencode-ai` (or `@anthropic-ai/claude-code`)
- [ ] Create config at `~/.config/opencode/opencode.json` inside the Ubuntu container
- [ ] If using SiliconFlow: `opencode run 'task' -m 'siliconflow/Qwen/Qwen3-14B' --dir /project`
- [ ] If using mytokk + Claude: model returns 0 tokens — likely SDK/response parsing issue; check key entitlements first
- [ ] mytokk: only official CLI works for Claude; custom clients are blocked
- [ ] **Permission issue**: if agent generates tool calls but they don't execute, add `~/.config/opencode/settings.json` with `{"permissions": {"allow": ["*"], "ask": []}}`

## Subagent / delegate_task Configuration (Critical)

When using `delegate_task` (Hermes's built-in subagent), two config sections are required:

| Config key | Purpose |
|---|---|
| `delegation.model` / `delegation.provider` | Model subagents inherit |
| `moa.aggregator.provider` / `moa.aggregator.model` | MoA aggregator (internal to delegation) |

**Both are required.** Without `moa.aggregator`, delegation fails with:
```
RuntimeError: No LLM provider configured for task=moa_aggregator provider=openrouter
```

⚠️ **MoA uses FLAT config structure** — `moa.aggregator` (not `moa.default.aggregator`).

See `references/delegation-moa-aggregator-fix.md` for full diagnosis and fix.

## Hermes → Claude Code Delegation (print mode)

When Hermes needs to hand off a coding task to Claude Code running in proot Ubuntu:

```bash
# Wrapper is at /usr/bin/claude (Termux native path, pre-injects auth env vars)
# Simple text task
/usr/bin/claude -p 'say hello' --max-turns 1 --model claude-opus-4-8

# Coding task (write + run) — use --allowedTools to whitelist capabilities
/usr/bin/claude -p 'Write hello.py that prints Hello, run it' --max-turns 3 --model claude-opus-4-8 --allowedTools 'Read,Write,Bash'
```

Key flags: `--max-turns N` prevents runaway loops, `--allowedTools` whitelists capabilities, `--verbose` shows all output including tool results.

> **Note**: `~/bin/claude` is NOT in PATH by default. The wrapper must be at `/usr/bin/claude` or you must call it with full path.
