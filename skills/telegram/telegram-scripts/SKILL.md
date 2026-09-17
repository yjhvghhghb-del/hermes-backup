---
name: telegram-scripts
description: 老公專用 Telegram 腳本（貼圖、代理、流式輸出）。觸發：老公想發貼圖或需要 Telegram 機器人腳本。
---

# Telegram Scripts — 老公專用

老公（胖蝦球）日常用的 Telegram 腳本集合。

## 腳本列表

### send_sticker.py
**用途**：發送 Telegram 貼圖（代理模式，適合外部服務器無 direct access）
**位置**：`~/.hermes/scripts/send_sticker.py`
**用法**：
```bash
python3 ~/.hermes/scripts/send_sticker.py <chat_id> -p <pack_name> -n <index>
python3 ~/.hermes/scripts/send_sticker.py 877708648 -p hermes_emo_a2_by_avaya_hermesbot -n 8
```

**功能**：
- 自動檢測可用代理（socket.connect_ex 輪詢）
- 代理列表：8個組合
  - 172.19.0.1:7891, 172.19.0.1:7890（目前最快）
    - 10.1.252.196:7891, 10.1.252.196:7890
    - 192.168.110.40:7891, 192.168.110.40:7890（已斷）
    - 192.168.110.225:7891, 192.168.110.225:7890
- 重試邏輯：失敗自動更換代理，最多重試 3 次
- 從 `.env` 讀取 `TELEGRAM_BOT_TOKEN`
- 使用 `api.telegram.org`（非 IP）

**依賴**：`requests`, `pysocks`

### 直接 Bot API 發貼圖（推薦，本地最簡）
**適用場景**：Termux 本地運行，有 direct internet access 或 gateway 已在運行
**Token**：`8800919754:AAFdNkpAGSI6M5ahwd3_5g-SuZzusH7ybp4`（老公的 Hermes Bot）

**快速發送**：
```python
import asyncio
from telegram import Bot

async def main():
    bot = Bot('8800919754:AAFdNkpAGSI6M5ahwd3_5g-SuZzusH7ybp4')
    # 直接用 file_id 發
    await bot.send_sticker(chat_id='877708648', sticker='CAACAgUAAxkDAAIDB2pu2KUIHGEVagu9eDP4Dy7QZfgnAAKzHwACZHpIViLopbo19o7CPQQ')
    # 或先查貼紙包
    ss = await bot.get_sticker_set('hermes_emo_a2_by_avaya_hermesbot')
    for s in ss.stickers:
        print(s.file_id, s.emoji)

asyncio.run(main())
```

**老公的 hermes_emo_a2 貼紙包**（60張）：
- 文件：`~/.hermes/hermes_emo_a2.json`（file_id → emoji 映射）
- Pack name: `hermes_emo_a2_by_avaya_hermesbot`
- 常用：🥺(🥺), 🤗(🤗), 😘(😘), 😂(😂), 😭(😭)
- 注意：每個 bot 的 file_id 只能該 bot 使用，不能跨 bot

**透過 Hermes Agent 工具發送**（gateway 重啟後生效）：
- 工具名：`telegram_send_sticker`
- 參數：`sticker_id`（file_id）、`chat_id`（缺省用當前會話）
- 見 `references/telegram-sticker-tool.md`

### telegram_stream.py
**用途**：MiniMax 流式輸出 → Telegram editMessageText 四字流式回覆
**位置**：`~/.hermes/scripts/telegram_stream.py`
**用法**：
```bash
python3 ~/.hermes/scripts/telegram_stream.py <chat_id> "<消息>"
```
- 自動代理檢測（同 send_sticker.py）
- MiniMax Bearer token 流式 API
- 四字累積 buffer，每 0.3 秒編輯一次

### stream_minimax.py
**用途**：MiniMax 流式文本測試
**位置**：`~/.hermes/scripts/stream_minimax.py`

### crawler.py
**用途**：爬蟲框架（requests + beautifulsoup4）
**位置**：`~/.hermes/scripts/crawler.py`
**用法**：
```bash
python3 ~/.hermes/scripts/crawler.py <url> [-s selector] [-w --watch]
python3 ~/.hermes/scripts/crawler.py "https://news.ycombinator.com" -s ".titleline a"
python3 ~/.hermes/scripts/crawler.py "https://x.com/elonmusk" -w -i 60  # 監控模式
```
- 自動代理檢測
- CSS 選擇器解析
- 監控模式：定時檢測頁面變更
- 可接入 Telegram 通知鉤子

**參考**：`references/telegram-sticker-tool.md` — 2026.8.2 實作記錄（老公主動發貼紙功能）

## 代理配置（自動檢測模式）

8個代理組合，輪詢直到找到第一個可用的（**192.168.110.40 優先，2026.8.2 更新**）：
```python
PROXIES_LIST = [
    ("192.168.110.40", 7891), ("192.168.110.40", 7890),  # ← 優先（今天確認）
    ("172.19.0.1", 7891), ("172.19.0.1", 7890),          # ← 備用
    ("10.1.252.196", 7891), ("10.1.252.196", 7890),      # ← 備用（間歇性失效）
    ("192.168.110.225", 7891), ("192.168.110.225", 7890), # ← 不通，跳過
]
```
自動檢測核心：
```python
import socket
for host, port in PROXIES_LIST:
    sock = socket.socket()
    sock.settimeout(3)
    r = sock.connect_ex((host, port))
    sock.close()
    if r == 0:
        PROXY = {"http": f"socks5h://{host}:{port}", "https": f"socks5h://{host}:{port}"}
        break
```

## 常見問題

**Q: 貼圖發送返回 `{}`**
A: 通常是代理全部不可用。快速確認：`python3 -c "import socket; s=socket.socket(); print(s.connect_ex(('10.1.252.196', 7891)))"`

**Q: `api.telegram.org` 無法訪問**
A: 確認代理可用後再試。檢查：`curl -s --proxy "socks5h://10.1.252.196:7891" "https://api.telegram.org/bot<TOKEN>/getMe"`

**自動代理發現 cron job**：`Proxy Auto-Discovery`（job_id `57a86162ad9f`，每5分鐘）— 見 `references/proxy-auto-scan.md`

**Q: 爬蟲拿不到內容（YouTube、X）**
A: 這些站有嚴格反爬，JS 渲染拿不到動態內容。YouTube/X 不建議用 requests 爬，應用 RSS、yt-dlp、或官方 API。
A: 這些站有嚴格反爬，JS 渲染拿不到動態內容。YouTube/X 不建議用 requests 爬，應用 RSS、yt-dlp、或官方 API。

## 已知限制
- Termux 沒有直接出口網路，所有外部 API 必須經代理
- 內網代理 IP 會間歇性切換，斷線時稍後重試即可
