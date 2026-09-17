# 代理自動發現腳本（老公內網用）

實際代碼見：`~/.hermes/scripts/send_sticker.py` 和 `telegram_stream.py`

## 核心模式

```python
import socket, requests

PROXIES_LIST = [
    ("10.1.252.196", 7891),
    ("10.1.252.196", 7890),
    ("192.168.110.40", 7891),
    ("192.168.110.40", 7890),
    ("192.168.110.225", 7891),
    ("192.168.110.225", 7890),
    ("172.19.0.1", 7891),
    ("172.19.0.1", 7890),
]

PROXY = None
for host, port in PROXIES_LIST:
    try:
        sock = socket.socket()
        sock.settimeout(3)
        r = sock.connect_ex((host, port))
        sock.close()
        if r == 0:
            proxy_url = f"socks5h://{host}:{port}"
            PROXY = {"http": proxy_url, "https": proxy_url}
            print(f"[代理] 使用 {host}:{port}")
            break
    except Exception:
        pass

if PROXY is None:
    print("[代理] 警告：沒有檢測到可用代理！")
```

## 快速檢測命令

```bash
python3 -c "
import socket
ips = ['10.1.252.196', '192.168.110.40', '192.168.110.225', '172.19.0.1']
for ip in ips:
    for port in [7891, 7890]:
        sock = socket.socket()
        sock.settimeout(3)
        r = sock.connect_ex((ip, port))
        sock.close()
        print(f'{ip}:{port} -> code={r}')
"
```

## 老公當前狀態（2026.07.31）
- 主要可用：10.1.252.196:7891（code=0，正常）
- 備用：172.19.0.1:7891（code=200）
- 其餘 IP 暫時斷線
