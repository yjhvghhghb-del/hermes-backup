---
name: siliconflow-telegram-agent
description: 用SiliconFlow免费模型创建Telegram Bot。触发：需要新建telegram bot或用免费模型。
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, android (termux)]
---

# SiliconFlow + Telegram Agent 部署

## 背景
- SiliconFlow 有永久免费额度（Qwen2.5-72B等）
- Hermes Agent 需要64K+ context的模型
- Qwen2.5-72B-Instruct 131K context，免费可用

## 创建Profile

```bash
mkdir -p ~/.hermes/profiles/siliconflow
```

## config.yaml

```yaml
model:
  base_url: https://api.siliconflow.cn/v1
  default: Qwen/Qwen2.5-72B-Instruct
  provider: custom
  api_key: YOUR_SILICONFLOW_KEY
  context_length: 131072
  max_tokens: 8192
streaming:
  enabled: true
  edit_interval: 0.3
  buffer_threshold: 4
platforms:
  telegram:
    enabled: true
_config_version: 33
```

## .env

```bash
SILICONFLOW_API_KEY=YOUR_KEY
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN
```

## 启动Gateway

```bash
HERMES_HOME=~/.hermes/profiles/siliconflow hermes gateway
```

## 配对

1. 给bot发消息，获取配对码
2. 执行配对：
```bash
HERMES_HOME=~/.hermes/profiles/siliconflow hermes pairing approve telegram 配对码
```

## 验证

```bash
HERMES_HOME=~/.hermes/profiles/siliconflow hermes chat -q "你好"
```

## 踩坑记录

- Qwen2.5-7B 只有32K context，Hermes要求64K+，会报错
- 必须用 Qwen2.5-72B-Instruct 或其他64K+模型
- Termux不支持后台gateway，需要手动跑或用其他方式
- 模型名必须完全匹配：`Qwen/Qwen2.5-72B-Instruct`
