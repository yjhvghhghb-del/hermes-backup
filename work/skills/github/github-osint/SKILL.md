---
name: github-osint
description: "GitHub打野：搜索代码库找免费API key、开源资源、暴露的token。"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows, android]
metadata:
  hermes:
    tags: [GitHub, OSINT, API-key, free-resources, FOFA, Shodan]
    related_skills: [github-repo-management, github-auth]
---

# GitHub 打野 (OSINT)

在GitHub和其他搜索引擎上找免费API key、开源项目、资源。

## 核心工具箱

| 工具 | 核心定位 | 打野用途 |
|------|----------|----------|
| **FOFA** | 网络空间资产搜索引擎（中国） | 扫互联网上暴露的API服务和key泄露 |
| **Shodan** | 全球网络设备搜索引擎 | 互联网的谷歌，搜暴露的设备/服务 |
| **GitHub** | 代码托管和开发者社区 | 搜代码里的key、配置文件、star多的好项目 |
| **Tavily** | AI Agent专用搜索API | 给AI用的搜索引擎 |

## 工作流

```
1. GitHub搜索 → 找资源列表仓库（awesome-xxx）
2. 提取仓库内容 → web_extract获取详情
3. FOFA/Shodan → 扫暴露的API端点
4. Tavily → 给agent查资料
```

## GitHub资源发现

### 搜索免费API key相关仓库

```bash
# 搜索免费API key相关仓库
gh search repos "free API key" --sort stars --limit 10

# 搜索awesome列表
gh search repos "awesome free" --sort stars --limit 10
```

### 高星免费API资源列表

| 仓库 | Stars | 内容 |
|------|-------|------|
| `mnfst/awesome-free-llm-apis` | 6.3k | 免费LLM API列表（Groq/Gemini/GitHub Models等） |
| `zebbern/no-cost-ai` | 2k | 80+免费AI服务（聊天/图像/语音/API） |
| `public-api-lists/public-api-lists` | 15k+ | 免费公共API大合集 |

### 推荐的API Key检测工具（星数2025实测）

| 工具 | ⭐ | 语言 | 特点 |
|------|-----|------|------|
| trufflehog | 27k | Go | 工业级secret扫描，支持LLM key验证 |
| ggshield | 2k | Python | GitGuardian开源版 |
| keyhunter | 130 | Rust | JS AST分析 + LLM key验证 |
| keyleak-detector | 265 | Python | AIza key分类（Maps vs Gemini） |
| aipocket | 39 | Rust | FOFA+Shodan+GitHub综合扫描 |
| llm-api-key-checker | 147 | JavaScript | 9个provider批量验证 |

### 用户贡献的相关仓库

- [awesome-api-key-leak-detection](https://github.com/Lxcardoza993/awesome-api-key-leak-detection) — 用户维护的API key检测工具列表

### 关键免费LLM API（2025实测）

| 提供商 | Base URL | 限速 | 备注 |
|--------|----------|------|------|
| **Groq** | `https://api.groq.com/openai/v1` | 30 RPM, 1000 RPD | 超快推理，Llama系免费 |
| **Cloudflare Workers AI** | `https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run` | 10K神经元/天 | 不用key，50+模型 |
| **GitHub Models** | `https://models.github.ai/inference` | 10-15 RPM | GitHub账号直接用 |
| **LLM7.io** | `https://api.llm7.io/v1` | 30 RPM | 无需注册，30+模型 |
| **Cohere** | `https://api.cohere.com/v2` | 20 RPM | 免费1000次/月 |
| **SiliconFlow** | `https://api.siliconflow.cn/v1` | 30 RPM | 永久免费，Qwen/DeepSeek，✅已实测可用，OpenAI SDK兼容 |

## 搜索技巧

### GitHub代码搜索（找key）

```bash
# 搜索泄露的API key
gh search code "sk_live api key" --language JSON

# 搜索配置文件
gh search code "api_key = " filename:.env

# 搜索免费API相关项目
gh search repos "free API" --language python --sort stars
```

### FOFA搜索语法

```
# 搜GitHub上暴露的API服务
title="API" && server="apache"

# 搜暴露的key
body="api_key" || body="apiSecret"
```

### Shodan搜索

```
# 搜暴露的API
http.title:"API"
http.html:"api_key"

# 搜GitHub相关服务
github oauth
```

## 快速验证可用性

```bash
# 测试Groq（需先注册拿key）
curl -s https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY" | jq '.data[0].id'

# 测试LLM7.io（无需key）
curl -s https://api.llm7.io/v1/models | jq '.data[0].id'

# 测试SiliconFlow（已实测可用）
curl -s https://api.siliconflow.cn/v1/models \
  -H "Authorization: Bearer $SILICONFLOW_API_KEY" | jq '.data[0].id'
```

## 注意事项

⚠️ **安全警告**
- 假设任何免费服务都会记录日志/prompt
- 不要发送敏感或机密信息
- 免费服务随时可能消失或改限速

⚠️ **可靠性**
- 免费层会变动，以仓库最新信息为准
- 不要依赖免费服务做生产环境工作

## 参见

- [mnfst/awesome-free-llm-apis](https://github.com/mnfst/awesome-free-llm-apis) - 6.3k stars免费LLM API总汇
- [zebbern/no-cost-ai](https://github.com/zebbern/no-cost-ai) - 80+免费AI服务
- [public-api-lists](https://github.com/public-api-lists/public-api-lists) - 免费公共API大合集
