#!/usr/bin/env python3
"""自動檢測可用代理 - 並行快速檢測8個IP×2個端口"""
import socket
import concurrent.futures

PROXY_LIST = [
    ("10.1.252.196", 7891),
    ("10.1.252.196", 7890),
    ("192.168.110.40", 7891),
    ("192.168.110.40", 7890),
    ("192.168.110.225", 7891),
    ("192.168.110.225", 7890),
    ("172.19.0.1", 7891),
    ("172.19.0.1", 7890),
]

def _try_connect(args, timeout=1.5):
    host, port = args
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.close()
        return (host, port, True, None)
    except (socket.timeout, ConnectionRefusedError, OSError) as e:
        return (host, port, False, str(e))

def detect_proxy():
    """並行檢測，返回第一個可連接的 (host, port) 或 None"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(_try_connect, p): p for p in PROXY_LIST}
        # 按提交順序返回結果，誰先成功誰先返回
        for future in concurrent.futures.as_completed(futures, timeout=5):
            host, port, ok, err = future.result()
            if ok:
                print(f"[proxy] ✓ {host}:{port}", flush=True)
                # 取消所有其他任務
                executor.shutdown(wait=False, cancel_futures=True)
                return (host, port)
            else:
                print(f"[proxy] ✗ {host}:{port}", flush=True)
    print("[proxy] ⚠ 無可用代理（將直連）", flush=True)
    return None

def get_proxy_dict():
    """返回 requests 可用的 proxy dict"""
    result = detect_proxy()
    if result:
        host, port = result
        proxy_url = f"socks5h://{host}:{port}"
        return {"http": proxy_url, "https": proxy_url}
    return {}

# 模塊級緩存，import 時只檢測一次
_cached = None

def get_cached_proxy():
    global _cached
    if _cached is None:
        _cached = get_proxy_dict()
    return _cached

if __name__ == "__main__":
    print("代理檢測中（並行）...", flush=True)
    r = detect_proxy()
    if r:
        print(f"結果: {r}")
    else:
        print("無可用代理")
