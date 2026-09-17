# 2026-08-29 Bot 启动状态

## 运行中的 Bot

| Profile | 平台 | 启动命令 | 状态 |
|---------|------|----------|------|
| (无) default | Telegram主bot + 飞书 + QQ | `cd ~ && hermes gateway run --replace` | ✅ |
| wenyu | 飞书 | `hermes --profile wenyu gateway run` | ✅ |
| licai | 飞书 | `hermes --profile licai gateway run` | ✅ |
| libai | 飞书 | `hermes --profile libai gateway run` | ✅ |
| geekwife | Telegram | `hermes --profile geekwife gateway run --force` | ✅ |
| siliconflow | Telegram | `hermes --profile siliconflow gateway run` | ✅ |

## Token 状态

- 主bot Telegram: `8800919754:...` ✅ 有效（gateway.log 解密确认 connected）
- siliconflow Telegram: `8363232963:...` ✅ 有效（单独 profile 运行）
- geekwife Telegram: `8637317610:AAFMUvm6...` ✅ 有效（ffdrtfcgbot）
- 所有 profile MiniMax CN API Key: `sk-cp-K9L_eq3zCw9gn1y4dA48fEjdlsvQiwzN21P8b9Te2sKwdXCsfLwQS3oR941l6WvSVGNmH2qSQZRH3_xImS3dRH3JSOGVBocYqwhd3fGx9tES60hqSXXopK4` ✅ 有效

## .env 关键配置

### default ~/.hermes/.env
```
TELEGRAM_BOT_TOKEN=8800919754:...（从日志解密获取）
MINIMAX_CN_API_KEY=sk-cp-K9L_eq3zCw9gn1y4dA48fEjdlsvQiwzN21P8b9Te2sKwdXCsfLwQS3oR941l6WvSVGNmH2qSQZRH3_xImS3dRH3JSOGVBocYqwhd3fGx9tES60hqSXXopK4
```

### wenyu/.env
```
FEISHU_APP_ID=cli_aae7a3ad78b8dbe3
FEISHU_APP_SECRET=<LARK_SECRET>
FEISHU_ALLOWED_USERS=ou_c696f8f4d082ba11770301e40ee40063
MINIMAX_CN_API_KEY=sk-cp-K9L_eq3zCw9gn1y4dA48fEjdlsvQiwzN21P8b9Te2sKwdXCsfLwQS3oR941l6WvSVGNmH2qSQZRH3_xImS3dRH3JSOGVBocYqwhd3fGx9tES60hqSXXopK4
```

### licai/.env
```
FEISHU_APP_ID=cli_aafa2c6a83b85bee
FEISHU_APP_SECRET=<LARK_SECRET>
FEISHU_ALLOWED_USERS=ou_a023ae4173052b881d472190d32065e2
FEISHU_GROUP_ALLOWED_USERS=ou_a023ae4173052b881d472190d32065e2
MINIMAX_CN_API_KEY=sk-cp-K9L_eq3zCw9gn1y4dA48fEjdlsvQiwzN21P8b9Te2sKwdXCsfLwQS3oR941l6WvSVGNmH2qSQZRH3_xImS3dRH3JSOGVBocYqwhd3fGx9tES60hqSXXopK4
```

### geekwife/.env
```
TELEGRAM_BOT_TOKEN=8637317610:AAFMUvm6-KLLslBLWLV8lRSFbhZDhGsdzVw
TELEGRAM_PROXY=socks5://192.168.110.40:7891
MINIMAX_CN_API_KEY=sk-cp-K9L_eq3zCw9gn1y4dA48fEjdlsvQiwzN21P8b9Te2sKwdXCsfLwQS3oR941l6WvSVGNmH2qSQZRH3_xImS3dRH3JSOGVBocYqwhd3fGx9tES60hqSXXopK4
```

### siliconflow/.env
```
SILICONFLOW_API_KEY=sk-gbq...lngb
TELEGRAM_BOT_TOKEN=8363232963:...
REPLICATE_API_KEY=r8_8Hg...eKnI
TELEGRAM_ALLOWED_USERS=877708648
TELEGRAM_PROXY=socks5://192.168.110.40:7891
```
