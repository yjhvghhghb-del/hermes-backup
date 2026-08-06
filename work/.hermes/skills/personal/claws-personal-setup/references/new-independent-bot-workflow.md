# 新建独立飞书 Bot 的正确流程（2026-08-03 实测教训）

## 错误做法：用现有 App ID + 新 Secret → 替换原 Bot，不是新增

**教训**：用 `cli_aae7a3ad78b8dbe3`（妹妹的 App ID） + 新 Secret → 建「理百 Bot」→ 结果：理财 Bot 替换了妹妹 Bot，只剩一个 Bot 在跑。

**原因**：同一个 App ID 同时只能被一个 gateway 进程使用。新 Secret 替换了旧 Secret，但 App ID 没变，所以还是同一个 Bot。

## 正确做法：新建独立 Bot 需要全新 App ID

### 方案 A：新建飞书 App（真正独立）
1. 去飞书开放平台 → 创建企业自建应用
2. 拿新的 App ID + App Secret
3. 创建新 Hermes profile：`~/.hermes/profiles/<name>/`
4. 写 config.yaml + .env
5. `cd ~/.hermes/profiles/<name> && hermes gateway run`

### 方案 B：用现有 App ID（只替换，不新增）
- 只换 Secret，不换 App ID → 同一个 Bot，内容替换
- 适合：想换 Bot 性格/角色，但保留同一个飞书 App

## 多 Bot 共存的关键约束

| 场景 | App ID 关系 | 结果 |
|------|------------|------|
| 两个 profile 不同 App ID | 各用各的 | ✅ 和平共存 |
| 两个 profile 同 App ID | 后启动的抢前一个 | ❌ 先启动的被踢 |
| 同一 App ID 换 Secret | 同一个 App | 替换，非新增 |

## pid 文件互抢问题（无解，只能选一个顺序）

`~/.hermes/gateway.pid` 是所有 profile 共用的。两个 Bot 要同时跑，只能：
- Bot A 先抢 pid 文件（先启动）
- Bot B 后启动，必须用 `--replace` 抢 pid → **会把 Bot A kill 掉**

**唯一共存方案**：两个都不用 `--replace`，先启动的占 pid，后启动的检测到已有进程直接退出（不是同时跑）。

**真正不互抢的唯一办法**：每个 profile 用独立 pid 文件路径（需修改 hermes 源码或配置，当前不可行）。

## 当前状态（2026-08-03）
- 理财 Bot（libai profile）用妹妹的旧 App ID `cli_aae7a3ad78b8dbe3` + 新 Secret 在跑
- 妹妹 Bot 已下线（被替换）
- 主 Bot（default）未启动（gateway.pid 被理财占用）
