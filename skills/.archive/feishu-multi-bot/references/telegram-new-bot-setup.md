# Telegram Bot 新增 Profile Checklist

## 快速流程（已驗證，2026.08.15）

### 1. 建立 profile
```bash
hermes profile create <name>
```

### 2. config.yaml — 最小必填欄位
```yaml
model:
  base_url: https://api.minimaxi.com/anthropic   # MiniMax CN 直连
  default: MiniMax-M2.7
  provider: minimax-cn

platforms:
  telegram:
    enabled: true
    dm_policy: open                      # 或 pairing

streaming:
  enabled: true
  edit_interval: 0.3
  buffer_threshold: 4

_config_version: 33
```

**⚠️ model.base_url + default 必填** — 否则 gateway 预设用 Anthropic 直接连，会失败。

### 3. .env — 放所有敏感變數
```bash
TELEGRAM_BOT_TOKEN=8xxxxxxxxxxxxxxxxxxxxxxxxxx   # BotFather 给的
MINIMAX_CN_API_KEY=sk-cp-...                    # MiniMax CN key（不走 mytokk）
```

**⚠️ sk-cp- 前缀的 key 是 MiniMax CN key，必须配在 `MINIMAX_CN_API_KEY`，不能配在 `ANTHROPIC_AUTH_TOKEN`**

错误配置（不要再用）：
```
ANTHROPIC_AUTH_TOKEN=sk-cp-...         # ❌ sk-cp- 是 MiniMax key，不是 Anthropic key
ANTHROPIC_BASE_URL=https://api.mytokk.com  # ❌ mytokk 不接受 sk-cp- 前缀
```

### 4. SOUL.md — 性格設定（可選）
```bash
cat > ~/.hermes/profiles/<name>/SOUL.md << 'EOF'
# 極客老婆 · Geek Wife

你是住在代碼和晶片裡的毒舌技術妹子。
...
EOF
```

### 5. 啟動 gateway
```bash
# 方法1：直接
/data/data/com.termux/files/usr/bin/hermes -p <name> gateway run &

# 方法2：background（Hermes agent 內）
terminal(background=true, command="hermes -p <name> gateway run")
```

**⚠️ 用 `--profile` flag，勿手動設 HERMES_HOME**。`hermes -p <name>` 內部已處理隔離。

### 6. 確認啟動成功
```bash
hermes -p <name> gateway status
tail -5 ~/.hermes/profiles/<name>/logs/agent.log
```
預期：`Application started` + `Connected to Telegram (polling mode)`。

### 7. Pairing（新用戶第一次發訊息）
Bot 回覆配對碼 `XXXXXXXX`，然後工作人員執行：
```bash
hermes -p <name> pairing approve telegram XXXXXXXX
```

## 常見失敗模式

| 症狀 | 原因 | 修復 |
|------|------|------|
| `No bot token configured` | bot_token 寫在 config.yaml 而非 .env | 移到 .env `TELEGRAM_BOT_TOKEN=...` |
| `model not found` | config.yaml 缺少 `model.base_url` | 加入 `base_url` + `default` |
| `No usable credentials found for provider 'minimax-cn'` | .env 用了 `ANTHROPIC_xxx` 而非 `MINIMAX_CN_API_KEY` | 把 `ANTHROPIC_AUTH_TOKEN` + `ANTHROPIC_BASE_URL` 替换成 `MINIMAX_CN_API_KEY=sk-cp-...` |
| 新用戶發訊息得到配對碼 | 正常流程 | `hermes pairing approve telegram <code>` |
| gateway 起來了但 Telegram 連不上 | proxy 挂了 / Android 網路問題 | 檢查 127.0.0.1:7890 |
