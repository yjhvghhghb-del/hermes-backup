---
name: github-code-search
description: "GitHub代码搜索与网络空间测绘联动打野"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Search, Reconnaissance, OSINT, API-Key-Hunting]
    related_skills: [github-repo-management, github-auth]
---

# GitHub Code Search & 打野 (Reconnaissance)

在GitHub上搜索代码、资源、API key，以及联动FOFA/Shodan/Censys/Hunter/Quake等网络空间测绘引擎进行"打野"。

## 核心场景

- 找免费API key资源
- 搜热门开源项目
- 挖掘泄露的凭证
- 批量资源发现

## 1. GitHub代码搜索

### API限制

| 接口 | 认证限速 | 未认证限速 |
|------|----------|------------|
| Search API | 30请求/分钟 | 10请求/分钟 |
| 普通API | 5000请求/小时 | 60请求/小时 |

**触发限速后的解决方案：**
- 等15分钟自动解封
- 用更强的token
- 加`time.sleep()`降低频率

### Python搜索脚本

```python
import requests
import time
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
PROXY = {"http": "http://172.19.0.1:7890", "https": "http://172.19.0.1:7890"}

def search_github(query: str, max_pages: int = 3):
    if not GITHUB_TOKEN:
        return []
    
    results = []
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    for page in range(1, max_pages + 1):
        url = f"https://api.github.com/search/code?q={__import__('urllib.parse', fromlist=['quote']).quote(query)}&per_page=30&page={page}"
        resp = requests.get(url, headers=headers, proxies=PROXY, timeout=15)
        if resp.status_code != 200:
            print(f"⚠️  {resp.status_code}")
            break
        data = resp.json()
        for item in data.get("items", []):
            results.append({
                "name": item.get("name", ""),
                "html_url": item.get("html_url", ""),
                "repository": item.get("repository", {}).get("full_name", ""),
                "path": item.get("path", ""),
            })
        time.sleep(1)  # 避免触发限速
    return results
```

### 推荐搜索关键词

```
free API key site:github.com
API key filetype:json github
free LLM API github
sk- OR api_key OR "api-key" filename:.env
free API key list open source
```

## 2. 网络空间测绘引擎

### FOFA (fofa.info) 🇺🇸

```python
import base64

def search_fofa(query: str):
    FOFA_EMAIL = os.getenv("FOFA_EMAIL", "")
    FOFA_KEY = os.getenv("FOFA_KEY", "")
    if not FOFA_EMAIL or not FOFA_KEY:
        return []
    
    qbase64 = base64.b64encode(query.encode()).decode()
    url = "https://fofa.info/api/v1/search/all"
    params = {"email": FOFA_EMAIL, "key": FOFA_KEY, "qbase64": qbase64, "size": 100}
    resp = requests.get(url, params=params, proxies=PROXY, timeout=15)
    # data = resp.json() → ["host", "port", "protocol"]
```

### Shodan

```python
def search_shodan(query: str):
    SHODAN_KEY = os.getenv("SHODAN_KEY", "")
    if not SHODAN_KEY:
        return []
    
    url = f"https://api.shodan.io/shodan/host/search?key={SHODAN_KEY}&query={quote(query)}&limit=100"
    resp = requests.get(url, proxies=PROXY, timeout=15)
    # data["matches"] → ["ip_str", "port", "product", "hostnames"]
```

### Censys

```python
def search_censys(query: str):
    CENSYS_API_ID = os.getenv("CENSYS_API_ID", "")
    CENSYS_API_SECRET = os.getenv("CENSYS_API_SECRET", "")
    if not CENSYS_API_ID or not CENSYS_API_SECRET:
        return []
    
    url = "https://search.censys.io/api/v1/search"
    params = {"q": query, "resource": "hosts", "per_page": 100}
    resp = requests.get(url, params=params, proxies=PROXY, timeout=15,
                       auth=(CENSYS_API_ID, CENSYS_API_SECRET))
    # data["results"] → ["ip", "protocols", "services"]
```

### Hunter.io

```python
def search_hunter(query: str):
    HUNTER_API_KEY = os.getenv("HUNTER_API_KEY", "")
    if not HUNTER_API_KEY:
        return []
    
    url = "https://hunter.qianxin.com/openapi/search"
    params = {"api-key": HUNTER_API_KEY, "search": query, "page": 1, "page_size": 100}
    resp = requests.get(url, params=params, proxies=PROXY, timeout=15)
    # data["data"]["arr"] → ["domain", "ip", "port", "web_title"]
```

### 360 Quake

```python
def search_quake(query: str):
    QUAKE_API_KEY = os.getenv("QUAKE_API_KEY", "")
    if not QUAKE_API_KEY:
        return []
    
    url = "https://quake.360.cn/api/v1/search"
    headers = {"X-QuakeAPIKey": QUAKE_API_KEY, "Content-Type": "application/json"}
    payload = {"query": query, "size": 100, "start": 0}
    resp = requests.post(url, json=payload, headers=headers, proxies=PROXY, timeout=15)
    # data["data"]["items"] → ["ip", "port", "protocol", "service"]
```

## 3. 完整打野脚本结构

```python
#!/usr/bin/env python3
"""GitHub打野脚本 - 批量搜索免费资源"""

SEARCH_QUERIES = [
    "free API key site:github.com",
    "API key filetype:json github",
    "free LLM API github",
    "free API key list open source",
]

OUTPUT_DIR = "/data/data/com.termux/files/home/ganking_results"

def main():
    for query in SEARCH_QUERIES:
        results = {
            "github": search_github(query),
            "fofa": search_fofa(query),
            "shodan": search_shodan(query),
            "censys": search_censys(query),
            "hunter": search_hunter(query),
            "quake": search_quake(query),
        }
        save_result("all", query, results)
        time.sleep(2)  # 查询间隔
```

## 4. 相关资源

- [mnfst/awesome-free-llm-apis](https://github.com/mnfst/awesome-free-llm-apis) — 免费LLM API列表 (6.3k stars)
- [zebbern/no-cost-ai](https://github.com/zebbern/no-cost-ai) — 80+免费AI服务 (2k stars)
- [public-api-lists/public-api-lists](https://github.com/public-api-lists/public-api-lists) — 免费公共API大合集

## 5. 打野脚本

完整脚本位于 `references/ganking-script.py`，直接运行：

```bash
python3 ~/.hermes/skills/github/github-code-search/references/ganking-script.py
```

## 环境变量速查

| 变量 | 说明 |
|------|------|
| `GITHUB_TOKEN` | GitHub PAT |
| `FOFA_EMAIL` + `FOFA_KEY` | FOFA |
| `SHODAN_KEY` | Shodan |
| `CENSYS_API_ID` + `CENSYS_API_SECRET` | Censys |
| `HUNTER_API_KEY` | Hunter.io |
| `QUAKE_API_KEY` | 360 Quake |
| `TAVILY_KEY` | Tavily AI搜索 |
