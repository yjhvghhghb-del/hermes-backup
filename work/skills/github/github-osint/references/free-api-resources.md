# 免费API资源参考（2025-08实测）

## 高星资源列表仓库

| 仓库 | Stars | URL | 内容 |
|------|-------|-----|------|
| `public-api-lists/public-api-lists` | 35k+ | https://github.com/public-api-lists/public-api-lists | 免费公共API大合集 |
| `mnfst/awesome-free-llm-apis` | 6.3k | https://github.com/mnfst/awesome-free-llm-apis | 免费LLM API列表 |
| `zebbern/no-cost-ai` | 2k | https://github.com/zebbern/no-cost-ai | 80+免费AI服务 |
| `smew-tech/public-apis` | 25k+ | https://github.com/smew-tech/public-apis | 免费API汇总 |

## 免费LLM API（需注册拿key）

### Groq — 超快推理
- **注册**: https://console.groq.com/keys
- **Base URL**: `https://api.groq.com/openai/v1`
- **免费模型**: llama-3.3-70b-versatile, llama-3.1-8b-instant, qwen3.6-27b
- **限速**: 30 RPM, 1000 RPD
- **特点**: 推理速度极快，OpenAI SDK兼容

### Cloudflare Workers AI — 无需API Key
- **注册**: https://dash.cloudflare.com/profile/api-tokens
- **Base URL**: `https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run`
- **免费模型**: llama-3.3-70b, gemma-4-31b, deepseek-r1-distill-qwen-32b 等50+模型
- **限速**: 10,000神经元/天
- **特点**: 不需要信用卡，账户级API token

### GitHub Models — GitHub账号直接用
- **注册**: https://github.com/marketplace/models (GitHub账号)
- **Base URL**: `https://models.github.ai/inference`
- **免费模型**: gpt-4.1, gpt-4.1-mini, gpt-4o, o4-mini, Llama-4-Scout 等45+模型
- **限速**: 10-15 RPM, 50-150 RPD
- **特点**: OpenAI SDK兼容，GitHub Pro账号额度更多

### LLM7.io — 无需注册
- **注册**: 无需注册
- **Base URL**: `https://api.llm7.io/v1`
- **免费模型**: deepseek-r1-0528, deepseek-v3-0324, gpt-4o-mini, qwen2.5-coder-32b 等30+
- **限速**: 30 RPM (120 RPM with token)
- **特点**: 零门槛，直接用

### Cohere — 免费1000次/月
- **注册**: https://dashboard.cohere.com/api-keys
- **Base URL**: `https://api.cohere.com/v2`
- **免费模型**: Command A+, Command R+, Aya Expanse 32B 等
- **限速**: 20 RPM, 1000 API calls/月
- **特点**: 非商用免费，无需信用卡

### Google Gemini — 1M Context
- **注册**: https://aistudio.google.com/app/apikey
- **Base URL**: `https://generativelanguage.googleapis.com/v1beta`
- **免费模型**: Gemini 3.5 Flash, Gemini 2.5 Pro, Gemini 3.6 Flash
- **限速**: 15-30 RPM, 1500 RPD
- **注意**: EU/UK/瑞士不可用

### SiliconFlow — 国内可用
- **注册**: https://cloud.siliconflow.cn/account/ak
- **Base URL**: `https://api.siliconflow.cn/v1`
- **免费模型**: Qwen3-8B, DeepSeek-R1-Distill-Qwen-7B
- **限速**: 30 RPM, 60K TPM
- **特点**: 国内可直接访问，永久免费

## 免注册直接用（Web界面）

| 平台 | URL | 模型 | 限速 |
|------|-----|------|------|
| lmarena.ai | https://lmarena.ai | 40+模型 | 无限 |
| sharedchat.cn | https://sharedchat.cn | GPT-4o, o3, o4-mini | 无限 |
| sur.pollinations.ai | https://sur.pollinations.ai | 开源模型聚合 | 无限 |
| groq.com | https://groq.com | Llama系 | 30 RPM |

## 快速测试命令

```bash
# 测试Groq（需key）
curl -s https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY" | jq '.data[0].id'

# 测试LLM7.io（无需key）
curl -s https://api.llm7.io/v1/models | jq '.data[0].id'

# 测试GitHub Models（需GitHub token）
curl -s https://models.github.ai/inference \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4.1","messages":[{"role":"user","content":"hi"}]}'
```
