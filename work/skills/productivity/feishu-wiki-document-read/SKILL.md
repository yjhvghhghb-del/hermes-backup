---
name: feishu-wiki-document-read
description: Read Feishu wiki/docx links via REST API.
tags: [feishu, wiki, document, feishu-open-platform]
---

# 飞书 Wiki / 云文档 读取

## 触发条件
老公发来飞书 wiki 链接（`https://my.feishu.cn/wiki/xxx`）或文档链接（`https://my.feishu.cn/docx/xxx`），需要读取内容时使用。

## 限制（重要）
- `feishu_doc_read` 工具**只能在飞书评论上下文中使用**，直接调用会返回 `Feishu client not available (not in a Feishu comment context)`。
- `web_extract` 无法访问飞书内部文档（返回 `Failed to fetch url`）。
- 必须用**飞书开放平台 REST API** 读取。

## 完整流程（Python + urllib）

### Step 1：获取 tenant_access_token
```python
import urllib.request, json
app_id = "cli_aae7a0320738dbeb"
app_secret = "FEISHU_SECRET_REDACTED"
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=json.dumps({"app_id": app_id, "app_secret": app_secret}).encode(),
    headers={"Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req, timeout=10) as r:
    tenant_token = json.loads(r.read())["tenant_access_token"]
```

### Step 2：Wiki token → 真实文档 token
```python
wiki_token = "LuRMwMOYviKhVHkaTq7cpdx3nEN"  # 从URL中提取
req = urllib.request.Request(
    f"https://open.feishu.cn/open-apis/wiki/v2/spaces/get_node?token={wiki_token}",
    headers={"Authorization": "Bearer " + tenant_token})
with urllib.request.urlopen(req, timeout=10) as r:
    node = json.loads(r.read())["data"]["node"]
obj_token = node["obj_token"]   # 如 "MygOd1BzFoz0lpxRNsTctU87nGh"
obj_type = node["obj_type"]     # 如 "docx"
title = node["title"]
```

### Step 3：读取文档 blocks（分页）
```python
def get_blocks(doc_token, token, page_size=500):
    blocks, page_token = [], None
    while True:
        url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/blocks?page_size={page_size}"
        if page_token: url += "&page_token=" + page_token
        req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token})
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
        blocks.extend(d["data"]["items"])
        if not d["data"]["has_more"]: break
        page_token = d["data"].get("page_token", "")
    return blocks
```

### Step 4：解析文字内容
```python
block_type_names = {1:"document",2:"text",3:"image",4:"heading2",5:"heading3",
    6:"heading4",7:"bullet",8:"ordered",9:"code",10:"quote",11:"divider",
    12:"table",16:"callout",20:"table cell"}

def extract_text(block):
    bt = block.get("block_type", 0)
    if bt == 2:
        return "".join(el.get("text_run",{}).get("content","")
                      for el in block.get("text",{}).get("elements",[]))
    for key in ["heading2","heading3","heading4"]:
        if key in block:
            return "".join(el.get("text_run",{}).get("content","")
                          for el in block[key].get("elements",[]))
    return ""

for block in blocks:
    text = extract_text(block).strip()
    if text:
        print(f"[{block_type_names.get(block.get('block_type',0), '?')}] {text}")
```

### Step 5：只提取标题（heading blocks）
```python
for block in blocks:
    bt = block.get("block_type", 0)
    if bt == 4:
        text = "".join(el["text_run"].get("content","") for el in block.get("heading2",{}).get("elements",[]) if "text_run" in el)
    elif bt == 5:
        text = "".join(el["text_run"].get("content","") for el in block.get("heading3",{}).get("elements",[]) if "text_run" in el)
    elif bt == 6:
        text = "".join(el["text_run"].get("content","") for el in block.get("heading4",{}).get("elements",[]) if "text_run" in el)
    else:
        continue
    if text.strip():
        print(f"H{bt}: {text.strip()}")
```

## 需要的飞书权限
- `wiki:wiki:readonly` — 查看知识库
- `docx:document:readonly` — 查看云文档

## 关键点
1. **Wiki URL token ≠ 文档 token** — 必须通过 `wiki/v2/spaces/get_node` 转换
2. 文档内容以 block 为单位，block type 决定解析方式
3. text block 内容在 `block["text"]["elements"]` 数组，每个 element 可能是 `text_run`、`mention_doc` 等
4. 需要分页读取（`page_size=500`，`has_more` 判断是否继续）
5. 不能用 `feishu_doc_read` 工具，必须自己调 REST API
