# Hermes 免费模型配置参考

## Groq（老公已配置，2026-08-19）

**API Key 格式:** `gsk_xxxxx`（Groq 专属格式）

**config.yaml 配置位置:** `providers:` 区块（顶级，不是 `model:` 里面）

```yaml
providers:
  groq:
    api_key: gsk_xxxxx
    base_url: https://api.groq.com/openai/v1
    models:
      - id: llama-3.3-70b-versatile
      - id: mixtral-8x7b-32768
      - id: gemma-7b
```

**生效操作:**
```bash
hermes gateway restart
hermes model  # 选 groq
```

## 其他免费模型 Provider（未配置）

| Provider | Free tier | Sign up | Models |
|----------|-----------|---------|--------|
| Google Gemini | 1M tokens/月 | https://aistudio.google.com/apikey | gemini-2.5-pro, gemini-2.5-flash |
| OpenRouter | 27+ 模型 `:free` | https://openrouter.ai/keys | hermes-3-405b:free, llama-4-nema-tron:free |
| NVIDIA NIM | 注册送 credits | https://nvidianim.ai | Llama 4, Qwen, Mistral |
| Cerebras | 每天免费 | https://inference.cerebras.ai | llama-3.3-70b |
| Together AI | $5 免费 | https://api.together.xyz | Various open source |

## 安全限制

**不能直接编辑** `~/.hermes/config.yaml`：
- Hermes 安全策略阻止 agent 修改此文件
- 需手动编辑或用 `hermes config set` 命令
- 编辑后需 `hermes gateway restart` 生效
