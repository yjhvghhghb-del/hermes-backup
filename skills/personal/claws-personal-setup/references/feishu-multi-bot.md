# 飞书 Bot 接入与多 Bot 部署

## 已接入的飞书 Bot（截至 2026-08-01）

### Bot 1：主 Bot（default profile）
- 配置文件：`~/.hermes/config.yaml` → `platforms.feishu`
- 主 gateway 进程：PID 13434（`hermes gateway`）

### Bot 2：理财 Bot（libai profile）✅ 已部署（2026.8.3 替换 cutegirl）
- Profile 路径：`~/.hermes/profiles/libai/`
- App ID: `cli_aae7a3ad78b8dbe3`
- App Secret: `YgaaFW19cOS2yA5ZYuGV4gj2mQkydJ8E`（2026.8.3 新 secret）
- Bot 性格：专业金融数据分析（`agent.system_prompt` 注入）
- 老公 open_id: `ou_2fcb5a59369405d74cf386b349aff96c`
- 已加入群: `oc_4c9d07126349124f942e382f7501b189`
- 启动命令：`cd ~/.hermes/profiles/libai && hermes gateway run`
  - ⚠️ 必须 cd 进 profile 目录，不能用 HERMES_HOME 环境变量

## 飞书 Bot 接入步骤（全新 App）

1. 去 [飞书开放平台](https://open.feishu.cn/) 建 App → 拿 App ID + App Secret
2. 创建独立 profile：`~/.hermes/profiles/<name>/`
3. 写 `config.yaml`（必须包含 model + platform + agent.system_prompt）
4. 写 `.env`（FEISHU_APP_ID + FEISHU_APP_SECRET）
5. **cd 进 profile 目录启动**：`cd ~/.hermes/profiles/<name> && hermes gateway run --replace`
   - ⚠️ **不能用 `HERMES_HOME=...` 环境变量**，Termux bash login shell 会重置 HERMES_HOME，仍使用 default profile 配置
   - 必须先 `cd` 进 profile 目录
   - 必须加 `--replace`
6. Bot 加进飞书群（从飞书群设置中添加机器人）
7. 用户 DM 机器人 → 收到 pairing code
8. approve：`hermes pairing approve feishu <CODE>`
9. 群内发消息测试

## 飞书群组配置格式（已验证有效）

```yaml
platforms:
  feishu:
    enabled: true
    extra:
      app_id: cli_xxx
      app_secret: xxx
      default_group_policy: allowlist
      allowed_group_users:
        - ou_xxxxxxxxxxxxxxxx
      group_rules:
        oc_xxxxxxxxxxxxxxxx:
          policy: allowlist
          allowlist:
            - ou_xxxxxxxxxxxxxxxx
```

## 独立 profile 的 config.yaml 最小模板

```yaml
_config_version: 33
model:
  base_url: https://api.minimaxi.com/anthropic
  default: MiniMax-M2.7
  provider: minimax-cn

agent:
  system_prompt: |
    # Bot 性格设定

platforms:
  feishu:
    enabled: true
    extra:
      app_id: cli_xxx
      app_secret: xxx
      default_group_policy: allowlist
      allowed_group_users:
        - ou_xxxxxxxxxxxxxxxx
      group_rules:
        oc_xxxxxxxxxxxxxxxx:
          policy: allowlist
          allowlist:
            - ou_xxxxxxxxxxxxxxxx
```

## 已知坑

### 1. pairing 码验证（DM 首次）
新 Bot 加进组织后，用户 DM 机器人，Bot 回复 pairing code。
→ approve：`hermes pairing approve feishu <CODE>`

### 2. Bot 不会自动出现在群里
飞书机器人需要手动从群设置中添加，不能靠配置自动加入。

### 3. 一个 app_id 只能被一个 gateway 实例使用
报错：`Another local Hermes gateway is already using this Feishu app_id`
→ 解决方案：独立 profile + 独立进程

### 4. nemo_relay 模块缺失
日志里出现 `ModuleNotFoundError: No module named 'nemo_relay'` 不影响 Bot 运行（DM pairing 机制相关）。

### 5. 独立 profile 必须包含 model: 配置
若 `config.yaml` 缺少 `model:` 区块，Bot 会用默认的 Anthropic（Timeout）。必须在独立 profile 的 config.yaml 里显式写：
```yaml
model:
  base_url: https://api.minimaxi.com/anthropic
  default: MiniMax-M2.7
  provider: minimax-cn
```

### 6. 启动独立 gateway 必须用 --replace
直接 `hermes gateway` 会报 `Another gateway instance is already running (PID xxx)` 并卡住。用 `hermes gateway run --replace` 才会自动终止旧进程。

### 7. 飞书 WebSocket 连接超时
独立 profile 启动时飞书 websocket 可能 30s 超时，多试几次重连后会成功。建议等 2 分钟让重连完成再测试。

### 9. 同一个用户在不同 Bot 下的 open_id 不同（关键！）
飞书 pairing 机制下，同一个用户跟不同 Bot 配对后会得到不同的 open_id。
- 主 Bot（default profile）里，老公是 `ou_2fcb5a59369405d74cf386b349aff96c`
- 萌妹 Bot（cutegirl profile）里，老公是 `ou_c696f8f4d082ba11770301e40ee40063`

**症状**：DM 正常回复，但群消息完全没反应，日志里没有 `Inbound group message received`。

**原因**：新 Bot 的 `group_rules` 里配的是老公在主 Bot 下的 open_id，不是新 Bot 下的。

**解决方法**：从新 Bot 的 gateway.log 里找正确的 open_id：
```bash
grep "sender=user:ou_" ~/.hermes/profiles/cutegirl/logs/gateway.log | head -3
```
然后把这个 open_id 加进 `allowed_group_users` 和对应群的 `group_rules[group_id].allowlist`。

**调试信号**：对比两个 Bot 的日志
```bash
# 主 Bot 有群消息
grep "Inbound group" ~/.hermes/logs/gateway.log
# cutegirl 没有群消息
grep "Inbound group" ~/.hermes/profiles/cutegirl/logs/gateway.log
```
如果主 Bot 有、cutegirl 没有，基本就是 open_id 配错了。

### 10. 飞书群事件只路由给第一个加入的 Bot（平台级限制）
**症状**：Bot 已成功加入群（gateway.log 有 `Bot added to chat`），open_id 正确，DM 也正常，但**所有群消息在日志里完全看不到**（没有 `Inbound group message received`）。

**根因**：飞书平台限制 — 同一群的 `@mention` 事件**只路由给群里第一个添加的 Bot**，其他 Bot 根本收不到群事件。这是 Feishu 平台行为，不是配置问题。

**关键区分（2026.8.3 实测）**：
- **群 @mention 事件**：只发给第一个加入的 Bot，受平台限制
- **私聊 DM**：完全独立通道，不受群限制，cutegirl DM 正常工作
- 今天实测：cutegirl 收到私聊"在吗"→ 13.6秒后回复72字 ✅
- cutegirl 日志里有 `Inbound dm message received` 但**完全没有** `Inbound group message received` → 群限制，DM 正常

**验证方法**：
```bash
# 对比两个 Bot 的群消息计数
grep "Inbound group message" ~/.hermes/logs/gateway.log | wc -l   # 主 Bot：应有记录
grep "Inbound group message" ~/.hermes/profiles/cutegirl/logs/gateway.log | wc -l  # cutegirl：应为 0

# 验证 cutegirl DM 是否正常（关键信号）
grep "Inbound dm message" ~/.hermes/logs/gateway.log | tail -3  # 有记录说明 cutegirl DM 正常
```

**解法**：
1. **推荐**：把主 Bot 从群里移除，只保留 cutegirl Bot → 群事件就会全发给 cutegirl
2. **折衷**：主 Bot 留群，cutegirl Bot 只做 DM 用途（群里 @ 哪个 Bot 就哪个回）
3. **不可行**：没有办法让同一个群的同一消息同时发给两个 Bot

### 11. 群事件路由正常但 Bot 就是不响应：重启 gateway
**症状**：Bot 已加群、权限已开、open_id 正确，但日志里群消息始终为 0。

**排查**：主 Bot 日志有 `Inbound group message received`，cutegirl 日志没有。Bot 加群确认日志正常（`Bot added to chat`），DM 完全正常。飞书应用权限已包含所有群消息权限。

**根因**：飞书 WebSocket 长连接建立时序问题 — 权限/订阅/加群都OK，但连接没有正确刷新群事件订阅。

**解法**：重启 cutegirl gateway 后群消息立即生效 ✅

### 13. 群 @ 机器人默认需要 @（require_mention 默认为 true）
飞书 adapter 默认 `require_mention: true`，群里**必须 @ 机器人才会响应**。如果希望 Bot 监听群里所有消息（不需要 @），在 `platforms.feishu.extra` 里加：
```yaml
require_mention: false
```
注意：关闭后 Bot 会响应群里所有消息（受 `default_group_policy` / `group_rules` 约束）。

### 14. gateway 重启后日志文件不更新的问题（关键！）
**症状**：重启 cutegirl gateway 后，`~/.hermes/profiles/cutegirl/logs/gateway.log` 仍然是旧内容（停在最后一次写入的时间点），`tail -f` 看不到新输出，`wc -l` 显示旧行数，但 `process(action='poll')` 显示进程正在运行。

**根因**：日志文件被旧进程持有（file descriptor），新进程写到了 stdout/stderr 或新文件。旧的 `gateway.log` 不会自动追踪新进程。

**排查方法**：
```bash
# 旧的 log 文件（不更新）—— 不要看这个
tail ~/.hermes/profiles/cutegirl/logs/gateway.log

# 正确：看进程实时输出（poll 或 log action）
process(action='log', session_id='proc_xxx', limit=30)

# 或者用 kill -0 确认进程是否活着
kill -0 <PID> 2>&1 && echo "alive" || echo "dead"
```

**实战教训（2026.8.2）**：
- cutegirl gateway 被 OOM kill 后重启，`wc -l` 始终是 71 行（旧内容）
- 但 `process(action='poll')` 显示进程 running，且输出 `[Lark] connected to wss://...`（实时输出在 stdout，不在 log 文件）
- 等了几分钟后日志文件才更新

### 15. gateway.lock / gateway.pid 残留导致 "Another gateway instance already running"
**症状**：执行 `hermes gateway` 报错 `Another gateway instance is already running (PID xxx)`，但该 PID 进程已死。

**根因**：unclean exit（SIGKILL/OOM）后，`gateway.lock` 和 `gateway.pid` 没有被清理。

**解法**：
```bash
cd ~/.hermes/profiles/cutegirl
rm -f gateway.lock gateway.pid
hermes gateway stop 2>&1   # 先停掉残留引用
# 然后再启动
terminal(background=True, command="cd ~/.hermes/profiles/cutegirl && hermes gateway")
```

**实战教训（2026.8.2）**：先用 `hermes gateway stop`（会自动清理 lock/pid），再启动新进程。

### 16. cutegirl Bot 在群里的实际行为（2026.8.2 实测）
- **主 Bot 在群里**：cutegirl Bot 收不到任何群消息
- **只有 cutegirl 在群里**：cutegirl Bot 可以正常收到并回复群消息 ✅
- **结论**：如果两个 Bot 都在群里，群消息只会发给主 Bot，cutegirl 完全收不到（飞书平台级限制）
- ⚠️ **但如果 cutegirl gateway 用错误方式启动**（HERMES_HOME=xxx 而非 cd 进目录），它会实际运行 default profile 的配置，导致 DM 也不响应，看起来像"平台限制"但其实是启动方式错误。验证方法：`cat /proc/<pid>/environ | grep HERMES_HOME` 确认指向的是 cutegirl 目录

### 16b. `--replace` 会误杀对方 profile 的进程（2026.8.3 新发现）
**症状**：主 Bot 启动时加 `--replace`，结果把 cutegirl 进程杀掉了；或者反过来。

**根因**：两个 profile 共用同一个 `~/.hermes/gateway.pid` 文件（不是各自独立的）。`--replace` 读取该文件得到对方 Bot 的 PID，然后发送 SIGTERM。

**解法**：永远不要用 `--replace` 来"安全重启"。正确做法：
1. 手动 `kill -9 <PID>` 杀掉要停止的进程（从 `gateway.pid` 读取 PID，根据 `hermes_home` 字段判断是谁的）
2. `rm -f ~/.hermes/gateway.lock ~/.hermes/gateway.pid`
3. 再启动新进程（第一个启动的不加 `--replace`，后续加 `--replace`）
或者始终按「先启 cutegirl → 后启 default（加 --replace）」的顺序操作。

### 17. 部署检查清单（快速验证）
```bash
# 1. 群消息有没有到 gateway（最关键）
grep "Inbound group" ~/.hermes/profiles/<profile>/logs/gateway.log

# 2. 没有群消息但 DM 正常 → 基本是飞书应用事件订阅问题
#    （不是 Hermes 配置问题）

# 3. 有群消息但 Bot 不回复 → 检查 open_id 是否正确、group_rules 是否配置

# 4. 权限、订阅、加群都OK但仍无 → 重启 gateway
```
