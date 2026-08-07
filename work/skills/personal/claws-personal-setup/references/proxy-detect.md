# 代理自動檢測腳本

## 腳本位置
`~/.hermes/skills/personal/claws-personal-setup/scripts/proxy_detect.py`

## 檢測邏輯

啟動時按順序嘗試8個IP×2個端口（共16個組合），第一個成功連接的即使用：

```
10.1.252.196:7891 → 7890
192.168.110.40:7891 → 7890
192.168.110.225:7891 → 7890  ← 當前唯一可用（2026.8.2）
172.19.0.1:7891 → 7890
```

- Socket 連接超時 3 秒
- 全部失敗則回傳 `None`，調用方直連

## API

```python
from proxy_detect import detect_proxy, get_proxy_dict

# 回傳 (host, port) tuple 或 None
proxy = detect_proxy()  # e.g. ("192.168.110.225", 7891)

# 回傳 requests 可用的 dict 或 None
proxies = get_proxy_dict()
# e.g. {"http": "socks5h://192.168.110.225:7891", "https": "socks5h://192.168.110.225:7891"}
```

## 已接入腳本

| 腳本 | 調用方式 |
|------|----------|
| `telegram_stream.py` | `PROXY = get_proxy_dict() or {}` |
| `send_sticker.py` | `proxy = detect_proxy()` → 使用 `PROXY_HOST`/`PROXY_PORT` |

## 驗證命令

```bash
python3 ~/.hermes/skills/personal/claws-personal-setup/scripts/proxy_detect.py
```

輸出示例（當前）：
```
代理檢測中...
[proxy] ✗ 10.1.252.196:7891 (timed out)
[proxy] ✗ 10.1.252.196:7890 (timed out)
[proxy] ✗ 192.168.110.40:7891 (No route to host)
[proxy] ✗ 192.168.110.40:7890 (No route to host)
[proxy] ✓ 192.168.110.225:7891
結果: {'http': 'socks5h://192.168.110.225:7891', 'https': 'socks5h://192.168.110.225:7891'}
```

## IP 變動規律

老公說：「有些时段ip就会切换」。代理可用性會不定時變化，腳本每次運行都重新檢測，不需要重啟。
