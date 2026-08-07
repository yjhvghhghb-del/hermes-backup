# GitHub打野脚本

## 免费版脚本 `~/github_ganking_free.py`

纯免费，无需API key即可运行（GitHub token可选）。

```python
#!/usr/bin/env python3
"""
GitHub打野 - 纯免费版（免key）
用免费LLM API + 开源工具扫描
"""

import requests
import json
import time
import os
from datetime import datetime

PROXY = {"http": "http://172.19.0.1:7890", "https": "http://172.19.0.1:7890"}

# GitHub Token（可选，加了搜索结果更多）
GITHUB_TOKEN = "GH_PAT_REDACTED"

# 搜索关键词
SEARCH_QUERIES = [
    "free API key site:github.com",
    'sk- OR "api_key" filename:.env github',
    "free LLM API key openai github",
    "free API list open source github",
    "awesome free API key github",
]

OUTPUT_DIR = "/data/data/com.termux/files/home/ganking_results"
```

**功能：**
- GitHub代码搜索（需token否则限速403/401）
- 推荐工具扫描（ggshield/trufflehog/aipocket等）
- 免费LLM API资源发现

**运行：**
```bash
python3 ~/github_ganking_free.py
```

**结果输出：** `~/ganking_results/`

---

## 完整版脚本 `~/github_ganking.py`

支持 FOFA + Hunter + Quake + Shodan + Censys（需各平台API key）。

```python
# 环境变量配置
FOFA_EMAIL = os.getenv("FOFA_EMAIL", "")
FOFA_KEY = os.getenv("FOFA_KEY", "")
SHODAN_KEY = os.getenv("SHODAN_KEY", "")
CENSYS_API_ID = os.getenv("CENSYS_API_ID", "")
CENSYS_API_SECRET = os.getenv("CENSYS_API_SECRET", "")
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY", "")
QUAKE_API_KEY = os.getenv("QUAKE_API_KEY", "")
```

**功能：**
- 7个搜索引擎批量搜索
- 结果自动保存JSON
- 汇总报告生成

---

## GitHub API限速说明

| 认证状态 | Search API限制 |
|----------|----------------|
| 未认证 | 10次/分钟 |
| 已认证(token) | 30次/分钟 |

触发限速后会403/401，等15分钟或加token解决。

---

## 推荐搜索关键词

```
free API key site:github.com
sk- OR "api_key" filename:.env
free LLM API github
API key filetype:json
awesome free API key
```
