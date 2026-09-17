#!/usr/bin/env python3
"""MiniMax 流式文本對話腳本"""
import os, sys, json

api_key = open(os.path.expanduser("~/.hermes/.env")).read()
api_key = [l for l in api_key.split("\n") if l.startswith("MINIMAX_CN_API_KEY=")][0].split("=", 1)[1].strip()

import urllib.request

if len(sys.argv) < 2:
    print("用法: python3 stream_minimax.py <消息>")
    sys.exit(1)

message = " ".join(sys.argv[1:])

url = "https://api.minimaxi.com/v1/text/chatcompletion_v2"
data = json.dumps({
    "model": "MiniMax-Text-01",
    "messages": [{"role": "user", "content": message}],
    "stream": True
}).encode()

req = urllib.request.Request(url, data=data,
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    })

print(f"[用戶] {message}\n")
print("[老婆] ", end="", flush=True)

try:
    with urllib.request.urlopen(req, timeout=60) as r:
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
                    print(delta, end="", flush=True)
            except:
                pass
except Exception as e:
    print(f"\n錯誤: {e}")

print("\n")
