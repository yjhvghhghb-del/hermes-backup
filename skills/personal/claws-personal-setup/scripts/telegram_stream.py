#!/usr/bin/env python3
"""Telegram 流式文本機器人 - 直接透過 Bot API 流式回覆（四字慢速）"""
import os, sys, json, time
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from proxy_detect import get_proxy_dict

TOKEN = open(os.path.expanduser("~/.hermes/.env")).read()
TOKEN = [l for l in TOKEN.split("\n") if l.startswith("TELEGRAM_BOT_TOKEN=")][0].split("=", 1)[1].strip()

PROXY = get_cached_proxy()
if not PROXY:
    print("[proxy] ⚠ 無代理，直連")

API_KEY = [l for l in open(os.path.expanduser("~/.hermes/.env")).read().split("\n") 
           if l.startswith("MINIMAX_CN_API_KEY=")][0].split("=", 1)[1].strip()

BASE_URL = f"https://149.154.166.110/bot{TOKEN}"

def api_get(method, params=None):
    r = requests.get(f"{BASE_URL}/{method}", params=params or {},
        proxies=PROXY, headers={"Host": "api.telegram.org"}, verify=False, timeout=10)
    return r.json()

def api_post(method, data):
    r = requests.post(f"{BASE_URL}/{method}", json=data,
        proxies=PROXY, headers={"Host": "api.telegram.org"}, verify=False, timeout=10)
    return r.json()

def stream_chat(prompt):
    """MiniMax 流式 API"""
    import urllib.request
    url = "https://api.minimaxi.com/v1/text/chatcompletion_v2"
    data = json.dumps({
        "model": "MiniMax-Text-01",
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    })
    return urllib.request.urlopen(req, timeout=60)

def send_streaming(chat_id, prompt):
    # 1. 發送初始空消息
    init = api_post("sendMessage", {
        "chat_id": chat_id,
        "text": "⏳ 思考中..."
    })
    if not init.get("ok"):
        print("發送失敗:", init)
        return
    
    message_id = init["result"]["message_id"]
    accumulated = ""
    buffer = ""
    last_edit = time.time()
    edit_interval = 0.3  # 每 0.3 秒編輯一次
    min_chunk = 4         # 至少累積4個字才發送（老公要求四字輸出）
    
    print(f"[用戶] {prompt}")
    print(f"[老婆] ", end="", flush=True)
    
    try:
        with stream_chat(prompt) as r:
            for line in r:
                line = line.decode().strip()
                if not line or not line.startswith("data:"):
                    continue
                payload = line[5:].strip()
                if payload == "[DONE]":
                    break
                try:
                    obj = json.loads(payload)
                    delta = obj.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if delta:
                        buffer += delta
                        accumulated += delta
                        print(delta, end="", flush=True)
                        
                        # 定期編輯消息（累積至少4個字才發送）
                        if time.time() - last_edit > edit_interval and len(buffer) >= min_chunk:
                            api_post("editMessageText", {
                                "chat_id": chat_id,
                                "message_id": message_id,
                                "text": f"[老婆] {accumulated}⏳"
                            })
                            buffer = ""
                            last_edit = time.time()
                except:
                    pass
        
        # 完成後替換最終內容
        final_text = f"[老婆] {accumulated}"
        api_post("editMessageText", {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": final_text
        })
        print("\n完成!")
        
    except Exception as e:
        print(f"\n錯誤: {e}")
        api_post("editMessageText", {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": f"[老婆] {accumulated}\n\n⚠️ 錯誤: {e}"
        })

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 telegram_stream.py <chat_id> <消息>")
        sys.exit(1)
    chat_id = sys.argv[1]
    prompt = " ".join(sys.argv[2:])
    send_streaming(chat_id, prompt)
