#!/usr/bin/env python3
"""MiniMax H3 视频生成脚本（curl版）"""
import os, sys, time, json, subprocess

# --- 配置 ---
API_KEY = os.environ.get("MINIMAX_API_KEY", "")
PROXY = "http://172.19.0.1:7890"
BASE_URL = "https://api.minimax.io/v2"

MODEL = "MiniMax-H3"
RESOLUTION = "768P"   # 或 "2K"
DURATION = 5          # 4-15秒
RATIO = "16:9"

DEFAULT_PROMPT = "A lone astronaut stands on a Martian ridge, watching a dust storm roll in, cinematic lighting, 4K"

def runcurl(url, data, method="POST"):
    cmd = [
        "curl", "-s", "--proxy", PROXY,
        "-X", method,
        "-H", f"Authorization: Bearer {API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(data),
        url
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise Exception(f"curl failed: {r.stderr}")
    return json.loads(r.stdout)

def create_task(prompt: str, resolution=RESOLUTION, duration=DURATION, ratio=RATIO):
    payload = {
        "model": MODEL,
        "content": [{"type": "text", "text": prompt}],
        "resolution": resolution,
        "duration": duration,
        "ratio": ratio
    }
    data = runcurl(f"{BASE_URL}/video_generation", payload)
    if "error" in data:
        err = data["error"]
        raise Exception(f"{err.get('message','unknown')} (code {err.get('http_code')})")
    return data["task_id"]

def query_task(task_id: str):
    data = runcurl(f"{BASE_URL}/video_generation/retrieve?task_id={task_id}", None, "GET")
    return data["task"]

def wait_task(task_id: str, poll_interval=10, timeout=300):
    start = time.time()
    while True:
        task = query_task(task_id)
        status = task["status"]
        print(f"  [{time.strftime('%H:%M:%S')}] status={status}", flush=True)
        if status == "succeeded":
            return task
        if status in ("failed", "cancelled"):
            raise Exception(f"Task {status}: {task}")
        if time.time() - start > timeout:
            raise TimeoutError(f"Timeout after {timeout}s")
        time.sleep(poll_interval)

def download_video(url: str, output_path: str):
    cmd = ["curl", "-s", "--proxy", PROXY, "-L", "-o", output_path, url]
    r = subprocess.run(cmd, capture_output=True, timeout=300)
    if r.returncode != 0:
        raise Exception(f"download failed: {r.stderr}")
    print(f"  下载完成: {output_path} ({os.path.getsize(output_path)//1024}KB)", flush=True)

def main():
    if len(sys.argv) < 2:
        prompt = DEFAULT_PROMPT
    else:
        prompt = " ".join(sys.argv[1:])

    print(f"=== MiniMax H3 视频生成 ===")
    print(f"Prompt: {prompt}")
    print(f"分辨率: {RESOLUTION} | 时长: {DURATION}s | 比例: {RATIO}")

    print("创建任务...")
    task_id = create_task(prompt)
    print(f"task_id: {task_id}")

    print("等待生成（约1-3分钟）...")
    task = wait_task(task_id)

    output_dir = os.path.expanduser("~/video-gen")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"h3_{task_id}.mp4")

    print("下载视频...")
    download_video(task["content"]["url"], output_file)
    print(f"\n完成: {output_file}")

if __name__ == "__main__":
    main()
