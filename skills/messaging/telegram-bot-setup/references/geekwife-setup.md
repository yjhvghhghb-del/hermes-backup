# geekwife Profile 配置记录

## 基本信息
- Profile 名：geekwife
- Bot Token：`8637317610:AAFMUvm6-KLLslBLWLV8lRSFbhZDhGsdzVw`
- Bot 性格：毒舌极客老婆
- 用途：编程助手

## config.yaml
```yaml
model:
  base_url: https://api.minimaxi.com/anthropic
  default: MiniMax-M2.7
  provider: minimax-cn

platforms:
  telegram:
    enabled: true
    dm_policy: open

streaming:
  enabled: true
  edit_interval: 0.3
  buffer_threshold: 4

_config_version: 33
```

## ⚠️ .env 配置关键规则（2026.08.24 实测）

**gateway 读取的是全局 `~/.hermes/.env`，不是 profile 下的 `.env`！**

profile 目录下的 `.env` 只在 profile 子 agent 启动时读取，gateway multiplexer 进程读全局 `.env`。所以：
- 改 profile `.env` → 无需重启 gateway（子 agent 下次启动生效）
- 改全局 `~/.hermes/.env` → 必须 `kill <PID>` + `hermes gateway` 重启

### 正确配置

**全局 `~/.hermes/.env`**（2026.08.24 23:00 确认当前值）：
```
MINIMAX_CN_API_KEY=sk-cp-K9L_eq3zCw9gn1y4dA48fEjdlsvQiwzN21P8b9Te2sKwdXCsfLwQS3oR941l6WvSVGNmH2qSQZRH3_xImS3dRH3JSOGVBocYqwhd3fGx9tES60hqSXXopK4
```

**profile `~/.hermes/profiles/geekwife/.env`**：
```
TELEGRAM_BOT_TOKEN=8637317610:AAFMUvm6-KLLslBLWLV8lRSFbhZDhGsdzVw
MINIMAX_CN_API_KEY=sk-cp-K9L_eq3zCw9gn1y4dA48fEjdlsvQiwzN21P8b9Te2sKwdXCsfLwQS3oR941l6WvSVGNmH2qSQZRH3_xImS3dRH3JSOGVBocYqwhd3fGx9tES60hqSXXopK4
```

### 错误配置（2026.08.24 故障根因）
```
ANTHROPIC_AUTH_TOKEN=sk-cp-K9L_...    # ❌ sk-cp- 是 MiniMax key，不是 Anthropic key
ANTHROPIC_BASE_URL=https://api.mytokk.com  # ❌ mytokk 不接受 sk-cp- 前缀
```
后果：日志 `No usable credentials found for provider 'minimax-cn'`，bot 回复 "model provider failed after retries"

### 调试命令
```bash
# 1. 查看 gateway 进程实际读到的环境变量
cat /proc/<gateway_pid>/environ | tr '\0' '\n' | grep MINIMAX

# 2. 确认 .env 文件实际内容（grep 截断显示...，用 od -c 看原始字符）
grep MINIMAX ~/.hermes/.env | od -c

# 3. 验证 key 是否有效（走 172.19.0.1:7890 代理）
curl -s --max-time 10 -x http://172.19.0.1:7890 \
  https://api.minimaxi.com/anthropic/v1/models \
  -H "x-api-key: sk-cp-K9L_eq3zCw9gn1y4dA48fEjdlsvQiwzN21P8b9Te2sKwdXCsfLwQS3oR941l6WvSVGNmH2qSQZRH3_xImS3dRH3JSOGVBocYqwhd3fGx9tES60hqSXXopK4"
# 返回 {"data":[{"id":"MiniMax-M3"...}]} = key 有效
```

## SOUL.md 性格设定（节选）
- 毒舌但有爱
- 傲娇本娇
- 技术流满嘴代码梗
- 像"这代码写得跟猪一样"的亲密吐槽风格

## .env 完整配置
```
TELEGRAM_BOT_TOKEN=8637317610:AAFMUvm6-KLLslBLWLV8lRSFbhZDhGsdzVw
MINIMAX_CN_API_KEY=sk-cp-K9L_eq3zCw9gn1y4dA48fEjdlsvQiwzN21P8b9Te2sKwdXCsfLwQS3oR941l6WvSVGNmH2qSQZRH3_xImS3dRH3JSOGVBocYqwhd3fGx9tES60hqSXXopK4
TELEGRAM_PROXY=socks5://10.1.252.196:7891
```

## 配对记录
- 老公 Telegram ID：877708648
- 配对码：9DGC9MJZ
- 审批命令：`hermes -p geekwife pairing approve telegram 9DGC9MJZ`
