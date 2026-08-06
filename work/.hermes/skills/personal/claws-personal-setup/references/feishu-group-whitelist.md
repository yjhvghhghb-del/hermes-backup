# Feishu 群组白名单配置参考

## 核心概念

Feishu 平台有两层用户过滤：
1. **platform level** — `allowed_group_users`：全局生效，所有群都认
2. **per-group level** — `group_rules`：指定群单独配，覆盖全局

## config.yaml 结构

```yaml
platforms:
  feishu:
    enabled: true
    extra:
      # 全局允许的用户（所有群都认）
      allowed_group_users:
        - ou_xxxxxxxxxxxxxxxxxxxx
        - ou_yyyyyyyyyyyyyyyyyyyy

      # per-group 规则（覆盖全局）
      group_rules:
        oc_群ID1:
          policy: allowlist          # allowlist | blacklist | open | admin_only | disabled
          allowlist:
            - ou_xxxxxxxxxxxxxxxxxxxx
        oc_群ID2:
          policy: open               # open = 群里所有人都能触发
```

## policy 类型

| policy | 行为 |
|--------|------|
| `allowlist` | 只允许 `allowlist` 里的 open_id 触发 |
| `blacklist` | 允许所有人除了黑名单 |
| `open` | 群里所有人都能触发（但仍需在 `allowed_group_users` 全局列表里） |
| `admin_only` | 只有 bot 管理员能触发 |
| `disabled` | 完全禁用该群 |

## 查找自己的 open_id

在 gateway.log 里搜 `Inbound dm message received` 或 `inbound message`，里面有 `sender=user:ou_xxxxxxxx` 就是发送者的 open_id。

## 独立 Bot + 独立 profile 示例

> ⚠️ **新 profile 必须加 `model:` 配置块**，否则 gateway 默认 Anthropic 会导致所有消息失败！

```bash
# 建 profile 目录（用 bash mkdir，heredoc 被工具安全系统拦截）
mkdir -p ~/.hermes/profiles/cutegirl/skills ~/.hermes/profiles/cutegirl/logs

# 用 write_file 工具写入 config.yaml 和 .env
# 必须包含 model: 块（否则默认 Anthropic 无法连接）

# 启动独立 gateway
HERMES_HOME=~/.hermes/profiles/cutegirl hermes gateway > ~/.hermes/profiles/cutegirl/logs/gateway.log 2>&1 &
```

### 最精简 config.yaml 模板
```yaml
_config_version: 33

model:                          # ⚠️ 必须有！
  base_url: https://api.minimaxi.com/anthropic
  default: MiniMax-M2.7
  provider: minimax-cn

agent:
  system_prompt: |
    # 性格设定...

platforms:
  feishu:
    enabled: true
    extra:
      app_id: cli_xxxxxxxxxxxxxxxx
      app_secret: xxxxxxxxxxxxxxxx
      default_group_policy: allowlist
      allowed_group_users:
        - ou_你的open_id
      group_rules:
        oc_目标群ID:
          policy: allowlist
          allowlist:
            - ou_你的open_id
```

### 跨 profile 文件写入
编辑其他 profile 的文件时，需要 `write_file` 加 `cross_profile=True` 参数。

## 常见故障：Bot 运行正常但群消息完全无响应

**症状**：Bot 进程在跑，飞书 WebSocket 也连上了（`Connected in websocket mode`），但群里 @ 它完全没反应，日志里没有 `Inbound group message received`。

**排查步骤**：
```bash
# 1. 确认 Bot 进程在跑
ps aux | grep hermes | grep -v grep

# 2. 确认飞书已连接
grep -E "Feishu.*connected|Lark.*connected" ~/.hermes/logs/gateway.log

# 3. 确认 Bot 有收到群消息（关键诊断）
grep "Inbound group message" ~/.hermes/logs/gateway.log   # 主 Bot
grep "Inbound group message" ~/.hermes/profiles/cutegirl/logs/gateway.log  # cutegirl

# 4. 如果主 Bot 有群消息进入，但 cutegirl 没有 → 很可能是白名单问题（见下）
```

**根因**：独立 profile 的 `allowed_group_users` 和 `group_rules` 配置了空列表或 `policy: open`，但没有把老公的 open_id 加进 `allowlist`。飞书平台虽然把消息送到了 Bot，但 Hermes 的白名单过滤器静默丢弃了消息（不回复也不报错）。

**日志里的静默丢弃信号**：
- 有 `Received raw message` / `Inbound dm message` → DM 正常
- 完全无 `Inbound group message received` → 群消息被白名单过滤了
- 没有 ERROR / WARNING → Hermes 层面没有报错

**修复方法**：在独立 profile 的 `config.yaml` 里加入老公的 open_id：
```yaml
platforms:
  feishu:
    extra:
      allowed_group_users:
        - ou_2fcb5a59369405d74cf386b349aff96c
      group_rules:
        oc_4c9d07126349124f942e382f7501b189:
          policy: allowlist        # 不是 open，必须是 allowlist
          allowlist:
            - ou_2fcb5a59369405d74cf386b349aff96c
```

配置变更后 gateway **自动热重载生效**，无需重启进程。

**关键区别**：
- `policy: open` = 群里所有人都能触发（但仍需在 `allowed_group_users` 全局列表里）
- `policy: allowlist` = 只有 `allowlist` 里的 open_id 能触发
- 两者都必须有用户的 open_id 在 `allowed_group_users` 全局列表中

## 注意事项

- `group_rules` 的 key 是群的 `chat_id`（格式 `oc_xxxxxxxx`），不是群名
- 新 Bot 连接可能超时 30s 然后自动重连连上，不需要重启
- profile 里的 `.env` 会自动被 `build_profile_secret_scope` 加载，不需要手动 source
- 飞书群事件是否实际送到 Bot，完全取决于白名单配置，与 Bot 是否"已连接"是两个独立层面
