# 2026-09-01 Bot 启动状态

## 当前运行中的 Bot

| Profile | 平台 | 代理 | 状态 |
|---------|------|------|------|
| (无) default | Telegram主bot + multiplex | 127.0.0.1:7890 | ✅ 主bot在跑，multiplex托管cutegirl/siliconflow/wenyu/libai |
| licai | 飞书 | - | ✅ 单独启动 |
| libai | 无平台 | - | ✅ 单独启动（纯cron） |
| cutegirl | 飞书 | - | ✅ 已由主bot multiplex 托管 |

## 关键教训

### 多路复用模式（gateway.multiplex_profiles: true）

**主 gateway 启动后会自动加载所有 profiles**，不需要对每个 profile 单独执行 `hermes --profile X gateway run`。

**错误做法**：在主 gateway 已运行的情况下，对被 multiplex 的 profile 单独启动 → 报错 "already serves profile"

**正确做法**：
1. 先 `ps aux | grep "hermes gateway run --replace" | grep -v grep` 确认主 gateway 是否在跑
2. 只有需要独立平台且没有被 multiplex 的 profile 才单独启动（licai）

### 飞书 app_id 冲突

- cutegirl/libai/licai/wenyu 共用 `cli_aae7a3ad78b8dbe3`
- 主 gateway multiplex 已包含 cutegirl，所以 wenyu 即使单独启动也会冲突退出
- **老公态度：不管冲突，直接全启动，冲突的自动退出**

### Telegram Bot Token 状态（2026-09-01）

| Bot | Token前缀 | API验证 | 状态 |
|-----|----------|---------|------|
| 主bot | 8800919754:AAFRd7... | 401 Unauthorized | ❌ token无效（secret错了） |
| geekwife | 8637317610:AAFMU... | 404 Not Found | ❌ bot被删 |
| siliconflow | 8363232963:AAEcAg... | 404 Not Found | ❌ bot被删 |

geekwife 在 19:40 还成功回复了「在吗？」，之后重连就 404——bot在那之后被删除或token被撤销。

## .env 关键配置

### geekwife/.env（当前配置）
```
TELEGRAM_BOT_TOKEN=8637317610:AAFMUvm6-KLLslBLWLV8lRSFbhZDhGsdzVw
TELEGRAM_PROXY=socks5h://10.1.252.196:7891
```

### cutegirl/.env
```
FEISHU_APP_ID=cli_aae7a3ad78b8dbe3
FEISHU_APP_SECRET=<LARK_SECRET>
FEISHU_ALLOWED_USERS=ou_c696f8f4d082ba11770301e40ee40063
```
