---
name: feishu-bot-setup
description: 飞书多Bot配置、排错、启动（feishu-multi-bot + feishu-licai-bot 合并版）
category: messaging
---

# 飞书 Bot 配置与排错

## 启动命令

### 判断运行模式

先查主 gateway 是否已在跑：

```bash
ps aux | grep "hermes gateway run" | grep -v grep
```

如果输出中有 PID，且 config 里 `gateway.multiplex_profiles: true`（**默认值，已开启**），**所有 profiles 都已由主 gateway 托管，不需要单独启动任何 profile**。

### 正确启动方式（2024+ 版本）

**没有 `hermes start` 命令**（踩坑实录）。正确的完整启动流程：

```bash
# 1. 杀掉所有旧进程
pkill -9 hermes; sleep 2

# 2. 直接启动主bot（前台阻塞，用独立 session 跑）
hermes gateway run
```

`hermes gateway run` 是 foreground 命令。在 Termux 里需要开一个**独立 session** 跑它——不要在本 session 用 `&` 或 `nohup`，terminal tool 的 `background=true` 也会随 session 退出被 SIGTERM 掉。

**`hermes gateway run --replace` 废弃**：新版已不需要 `--replace` flag，直接用 `hermes gateway run`。

### multiplex_profiles 默认开启

`gateway.multiplex_profiles: true`（默认）时，主 gateway 自动托管所有 profiles 的消息路由。**不能**用 `hermes --profile xxx gateway run` 单独启动任何已 multiplex 的 profile，否则报错：

> "The default gateway is running as a profile multiplexer and already serves profile 'xxx'"

如果某个 profile 需要强制独立运行，可以加 `--force`，但不推荐。

## 权限架构（关键）

### Feishu Adapter 不自己执行白名单

**Feishu 跟 Telegram 不同** — `FeishuAdapter` 没有实现 `enforces_own_access_policy`，所以：
- config.yaml 里的 `dm_policy`、`allow_from`、`dm_whitelist` 等字段**对飞书 DM 无效**
- 必须通过 **环境变量** 控制白名单：`FEISHU_ALLOWED_USERS`

### 正确的飞书白名单配置

在 profile 的 `.env` 文件里设置：

```bash
FEISHU_APP_ID=cli_xxxxxxxx
FEISHU_APP_SECRET=xxxxxxxx
FEISHU_ALLOWED_USERS=ou_xxxxxxxxxx   # DM 白名单
FEISHU_GROUP_ALLOWED_USERS=ou_xxxxxxxxxx  # 群聊白名单（群消息需要）
```

config.yaml 里的 `group_rules` 只在飞书 adapter 自己执行 allowlist 时生效，但 adapter 没有这个能力，所以群聊也必须靠 `FEISHU_GROUP_ALLOWED_USERS`。

### config.yaml 里的 allow_from 为何无效

authz_mixin.py 的 gateway 级检查会查 `extra.get("allow_from")`，但这只在 `enforces_own_access_policy` 返回 True 时才会被 gateway 信任。FeishuAdapter 没有实现这个方法，所以即使在 config.yaml 里配了 `allow_from`，gateway 也不会采纳。**唯一有效方案：.env 里的 `FEISHU_ALLOWED_USERS`。**

### 群聊无响应常见原因

1. **用户不在 `FEISHU_GROUP_ALLOWED_USERS` 里** — 最常见！DM 有回复但群聊没反应，基本都是这个原因。必须在 profile 的 `.env` 里单独配置：
   ```bash
   FEISHU_ALLOWED_USERS=ou_xxxxxxxxxx       # DM 白名单
   FEISHU_GROUP_ALLOWED_USERS=ou_xxxxxxxxxx  # 群聊白名单（分开配置）
   ```
   config.yaml 的 `group_rules`/`group_whitelist` 对飞书群聊无效，因为 FeishuAdapter 没有实现 `enforces_own_access_policy`。
2. config.yaml 的 `group_whitelist` 没有包含对应群 ID（wenyu 的 `group_whitelist: ['oc_457ae34d4ae483c1ff40716be1c165cb']`）
3. `require_mention: false` 没设（需要 @bot 才触发）
4. 飞书 WS 连接不稳定，日志里出现 `lifecycle_ledger: Previous gateway life exited UNCLEANLY` — bot 被系统 SIGKILL，OOM 导致，需要等几秒后重查进程

### 飞书 app_id 冲突（同一 app_id 多 profile 互斥）

飞书 websocket 模式下，同一 app_id 同时只能有一个 gateway 实例连接。多个 profile 共用同一个 app_id 时，后启动的会直接退出：

```
Another local Hermes gateway is already using this Feishu app_id (PID XXXX).
```

**wenyu 的实际行为（2026-09-01 实测）**：
- wenyu 在 `multiplex_profiles: true` 下**不会**被主gateway多路复用——它会尝试独立连接飞书，然后跟 cutegirl 抢 `cli_aae7a3ad78b8dbe3`，抢不过就退出（报错 "PID XXXX already using this Feishu app_id"）
- 主gateway自己连的是 `cli_aae7a0320738dbeb`，跟cutegirl/wenyu的 `cli_aae7a3ad78b8dbe3` **不冲突**
- 所以：主gateway + cutegirl 能同时跑；wenyu 要跑就得停掉cutegirl
- 两者互斥，不能同时存在

如需同时运行，需要分配不同的飞书 app_id 给 wenyu。

## Telegram Bot（中国大陆）

需要代理，在 `.env` 里设置：

```bash
TELEGRAM_BOT_TOKEN=xxxxxxxxxx:xxxxxx
TELEGRAM_PROXY=socks5://192.168.110.40:7891
```

**格式必须是 `socks5://`，不是 `http://`**（Clash 默认是 SOCKS5）。

### 代理 IP 当前状态（2026-09-01）

- `127.0.0.1:7890` — 主bot Telegram（http代理，Telegram DoH fallback）
- `10.1.252.196:7891` — geekwife/siliconflow Telegram（socks5h代理）✅ 当前有效
- `192.168.110.40:7891` — **已失效**（siliconflow 连不上就是这个原因）

如果 Telegram 连不上，先检查代理是否还能连通：
```bash
curl -x socks5://10.1.252.196:7891 --connect-timeout 5 -s https://api.telegram.org/bot<TOKEN>/getMe
```

### Telegram Token 失效排查

Token 无效（401/404）时 curl 验证：
```bash
curl -s "https://api.telegram.org/bot<TOKEN>/getMe"
```
- 401 = token 无效/被吊销
- 404 = token 不存在
- 出现 401 后不要再尝试启动，bot 已经被封

主 bot token 存于 `~/.hermes/.env` 的 `TELEGRAM_BOT_TOKEN`，不是 profile .env。

## .env 文件规范

- 同一变量**不要写多行**，后写的会追加在后，以最后一行生效，但重复 key 会导致解析异常（某些字段只读第一行）
- 追加配置时先 `cat` 查看是否已有该 key，避免重复
- token 写到 `config.yaml` 里的 `${VAR}` 形式会被 `.env` 覆盖
- 不要在 `.env` 里追加内容后不重启就以为生效

## 排错顺序

1. `ps aux | grep hermes | grep python` — 看进程在不在
2. `tail -20 ~/.hermes/profiles/<name>/logs/gateway.log` — 看日志
3. `grep -i "unauthorized\|denied\|error\|failed" logs/gateway.log` — 找拒绝原因
4. 如果是 "Unauthorized user" — 白名单没配或没生效，重查 .env
5. 如果是 Telegram connect failed — 查代理是否可达，token 是否有效

## 主 Bot（非 profile 模式）启动

主 bot 用根目录配置，**不在 profile 里**：

```bash
cd ~ && hermes gateway run --replace
```

- token 在 `~/.hermes/.env` 的 `TELEGRAM_BOT_TOKEN`（被 `***` 遮住，从 `~/.hermes/logs/gateway.log` 解密日志可查实际值）
- config 在 `~/.hermes/config.yaml` 的 `platforms.telegram` 节
- 用 `hermes --profile xxx gateway run` 启动的是子 bot，不是主 bot

## Telegram 多路复用（同一 token 多个 profile）

主 bot 和 siliconflow 都用同一套 Telegram token 时，siliconflow 启动会报错：
> "only one gateway can hold the Telegram token"，需要通过主 bot 的多路复用机制管理，不能单独 profile 启动。

## 已知有效配置参考

详见 `references/active-profiles-2026-09-01.md`，包含各 profile 的 .env 实际配置和 token 状态。
