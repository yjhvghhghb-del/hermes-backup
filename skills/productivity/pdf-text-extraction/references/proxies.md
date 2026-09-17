# 老公的代理服务器（内网）

按优先级顺序尝试：

| 地址 | 端口 | 用途 |
|------|------|------|
| 172.19.0.1 | 7890 | 首选（返回404说明能通） |
| 192.168.110.225 | 7891 | 最终备用 |

## curl 用法
```bash
curl -x http://172.19.0.1:7890 https://api.minimaxi.com/...
```

## Python httpx 用法
```python
import httpx
transport = httpx.HTTPTransport(proxy='http://172.19.0.1:7890')
with httpx.Client(transport=transport, timeout=60.0) as client:
    resp = client.post(url, json=payload, headers={'Authorization': f'Bearer {API_KEY}'})
```

## MiniMax API 端点（已验证）
- **推荐** `https://api.mytokk.com/v1/chat/completions` — `ANTHROPIC_API_KEY` + Bearer token，模型 `claude-haiku-4-5-20251001`（确认可用）
- `https://api.minimaxi.com/anthropic/v1/messages` — 需要 X-Api-Key header（未验证成功）
- `api.minimaxi.com` 需要 HTTP 代理直连（不走代理会 401）
