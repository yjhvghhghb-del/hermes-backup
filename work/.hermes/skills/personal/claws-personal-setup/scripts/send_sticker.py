#!/usr/bin/env python3
"""發送 Telegram 貼圖 - 支持老公的 SOCKS5 代理

用法:
  # 列出貼圖包 (60張)
  python3 ~/.hermes/scripts/send_sticker.py 877708648 -l -p hermes_emo_a2_by_avaya_hermesbot

  # 發送第 N 張 (1-60)
  python3 ~/.hermes/scripts/send_sticker.py 877708648 -p hermes_emo_a2_by_avaya_hermesbot -n 7

  # 直接指定 file_id
  python3 ~/.hermes/scripts/send_sticker.py 877708648 -s "CAACAgUAAxUAA..."

依賴: pip install requests pysocks
"""
import sys, os, json, argparse, warnings
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from proxy_detect import detect_proxy

warnings.filterwarnings('ignore')

_proxy = detect_proxy()
PROXY_HOST = _proxy[0] if _proxy else None
PROXY_PORT = _proxy[1] if _proxy else None

ENV_FILE = os.path.expanduser("~/.hermes/.env")
TOKEN = None
with open(ENV_FILE) as f:
    for line in f:
        if line.startswith("TELEGRAM_BOT_TOKEN="):
            TOKEN = line.split("=", 1)[1].strip()
            break

PROXY = {
    'http': f'socks5h://{PROXY_HOST}:{PROXY_PORT}',
    'https': f'socks5h://{PROXY_HOST}:{PROXY_PORT}'
}

# Telegram fallback IP (當 DNS 解析失敗時使用)
API_BASE = "https://149.154.166.110/bot" + TOKEN

def api_get(method, params=None):
    r = requests.get(
        f"{API_BASE}/{method}",
        params=params or {},
        proxies=PROXY,
        headers={"Host": "api.telegram.org"},
        verify=False,
        timeout=10
    )
    return r.json()

def send_sticker(chat_id, file_id):
    return api_get("sendSticker", {"chat_id": chat_id, "sticker": file_id})

def get_sticker_set(name):
    return api_get("getStickerSet", {"name": name})

def send_sticker_idx(chat_id, pack_name, idx):
    result = get_sticker_set(pack_name)
    if not result.get("ok"):
        return result
    sticks = result["result"]["stickers"]
    if idx < 0 or idx >= len(sticks):
        return {"ok": False, "description": f"索引超出範圍 (1-{len(sticks)})"}
    file_id = sticks[idx]["file_id"]
    return send_sticker(chat_id, file_id)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="發送 Telegram 貼圖")
    parser.add_argument("chat_id", help="Telegram Chat ID")
    parser.add_argument("--sticker", "-s", help="Sticker file_id")
    parser.add_argument("--pack", "-p", help="Sticker pack 名稱")
    parser.add_argument("--list", "-l", action="store_true", help="列出貼圖包")
    parser.add_argument("--send", "-n", type=int, metavar="N", help="發送第 N 張貼圖")
    args = parser.parse_args()

    if args.list and args.pack:
        result = get_sticker_set(args.pack)
        if result.get("ok"):
            sticks = result["result"]["stickers"]
            print(f"貼圖包: {result['result']['name']} ({len(sticks)} 張)")
            cache = {s['file_id']: s.get('emoji','') for s in sticks}
            with open(os.path.expanduser("~/.hermes/sticker_file_ids.json"), 'w') as f:
                json.dump(cache, f, ensure_ascii=False)
            for i, s in enumerate(sticks):
                print(f"  {i+1:2d}. {s.get('emoji','?')} | {s['file_id'][:35]}...")
        else:
            print("錯誤:", result.get("description"))

    elif args.sticker:
        result = send_sticker(args.chat_id, args.sticker)
        if result.get("ok"):
            print("✓ 貼圖發送成功")
        else:
            print("錯誤:", result.get("description"))

    elif args.send is not None and args.pack:
        result = send_sticker_idx(args.chat_id, args.pack, args.send - 1)
        if result.get("ok"):
            print(f"✓ 第 {args.send} 張貼圖發送成功")
        else:
            print("錯誤:", result.get("description"))

    else:
        parser.print_help()
