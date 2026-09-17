# Telegram 重复回复案例

## 案例1：siliconflow profile 重复接入（2026-08-19）

- **症状**：老公反映每条消息看到两条几乎相同的回复
- **根因**：siliconflow profile 的 `config.yaml` 里 `platforms.telegram.enabled: true`，和 default profile 使用同一个 bot token
- **修复**：
  1. `patch` siliconflow/config.yaml：`enabled: false`
  2. `kill <PID>` 杀掉该 profile 的进程
  3. 确认 default profile 仍正常运行

**配置当时状态**：
```yaml
# siliconflow/config.yaml
platforms:
  telegram:
    enabled: true   # ← 重复接入！
_config_version: 33
```

**验证无重复的命令**：
```bash
# 只剩 default 接 Telegram
grep "Sending response" ~/.hermes/logs/gateway.log
# 每条消息应该只有一行 Sending response
```

---

## 案例2：geekwife profile 重复接入（2026-08-19）

- **症状**：siliconflow 关掉后继续出现重复
- **根因**：geekwife profile 同样配置了 `telegram.enabled: true`
- **修复**：同上，`enabled: false` + 重启

---

## 核心原则

**一个 Telegram bot token 只允许一个 Hermes profile 接入。**

如果需要多个独立 bot，必须向 @BotFather 申请多个 token，在各自 profile 的 `.env` 里配置不同的 `TELEGRAM_BOT_TOKEN`。

调查 checklist：
```bash
# Step 1：扫描所有 profile 的 telegram 配置
for profile in ~/.hermes/profiles/*/; do
  name=$(basename $profile)
  tg=$(grep -A1 "^  telegram:" $profile/config.yaml 2>/dev/null | grep "enabled" | awk '{print $2}')
  echo "$name: telegram=$tg"
done

# Step 2：看实际在跑哪些 profile
ps aux | grep "hermes --profile" | grep -v grep

# Step 3：确认只有 default 接 Telegram
grep "Sending response" ~/.hermes/logs/gateway.log | grep "Telegram" | wc -l
# 每条消息应该只有一行 Sending response 到对应 chat_id
```
