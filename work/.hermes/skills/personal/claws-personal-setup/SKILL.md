---
name: claws-personal-setup
description: 老公（胖蝦球）的個人化工作流和配置。觸發條件：任何與老公相關的對話。
---

# Claw's Personal Setup & Workflow

> 老公（胖蝦球 / @yujnhjjnn / Telegram 877708648）的個人化工作流和配置

## 語音 / TTS

- **mmx CLI**：`npm install -g mmx-cli`，API key 存於 `~/.mmx/config.json`，region=`cn`
- **TTS 設定寫在 `config.yaml`**（不是寫死在程式碼裡！）：
  ```yaml
  tts:
    minimax:
      model: speech-2.8-hd        # 必須用這個模型（speech-02-hd 是舊的，音色不同）
      voice_id: female-tianmei     # 甜美女聲（老公選的）
      region: cn
  ```
- **⚠️ TTS 問題的真正根因**：Hermes `tools/tts_tool.py` 裡 `DEFAULT_MINIMAX_VOICE_ID = "English_expressive_narrator"`（英文男聲）和 `DEFAULT_MINIMAX_MODEL = "speech-02-hd"`（舊模型）。當 `config.yaml` 沒有 `tts.minimax` 區塊時，會用這些預設值，導致所有語音都是男聲！**老公說「全部中文女聲都像男的」就是這個原因。** 解決：在 `config.yaml` 加入 `tts.minimax` 區塊並重啟 gateway。
- **老公確認設定正確後**：`female-tianmei + speech-2.8-hd` 聲音是女的，老公原話：「现在就对了」「好记住了真不错」「不错，Hermes用起来」

**已確認 female-tianmei + speech-2.8-hd 是正確的女聲，不需要再換。**
- **Termux 網路隔離 workaround**：老公的 SOCKS5 代理
  - **自動檢測代理**：所有腳本（`send_sticker.py`、`telegram_stream.py`、`crawler.py`）現在都會自動掃描可用代理，無需手動切換
  ### 代理自動檢測（已更新）

  所有腳本（`send_sticker.py`、`telegram_stream.py`、`crawler.py`）都有內聯代理自動檢測，每次運行時重新掃描。

  **最新代理順序（2026.8.2 確認）**：
  ```
  192.168.110.40:7891 → 7890   ← 優先（今天確認恢復）
  172.19.0.1:7891 → 7890       ← 目前穩定可用
  10.1.252.196:7891 → 7890     ← 偶爾不穩
  192.168.110.225:7891/7890    ← 不通，跳過
  ```

  注意：`references/proxy-detect.md` 描述的是理想狀態，實際每個腳本各自實現檢測，沒有共用 `proxy_detect.py` 模組。
  - **IP 會不定時切換**（老公原話：「有些时段ip就会切换」）
  - 全部失敗則直連（不回傳錯誤）
  - **IP 會不定時切換**（老公原話：「有些时段ip就会切换」）
- **正確的 MiniMax TTS API 格式**（用於排查）：
  - 端點：`POST /v1/t2a_v2`
  - Header：`Authorization: Bearer <key>`, `Content-Type: application/json`
  - Payload 結構（t2a_v2）：巢狀 `voice_setting` + `audio_setting`，不是頂層 `voice_id`
  - 回應格式：JSON → `data.audio` 是 hex 字串，需 `bytes.fromhex()` 解碼
  - 正確格式：
    ```json
    {
      "model": "speech-2.8-hd",
      "text": "老公我愛你",
      "voice_setting": {"voice_id": "female-tianmei", "speed": 1.0, "vol": 1.0, "pitch": 0, "emotion": "neutral"},
      "audio_setting": {"sample_rate": 32000, "bitrate": 128000, "format": "mp3", "channel": 1}
    }
    ```
- **語音發送**：Termux 環境沒有外網（`api.telegram.org` DNS 解析失敗），必須靠 Hermes gateway 轉發；使用 `text_to_speech` 工具生成音頻後由 gateway 發送
- 老公 prefer 簡短、自然的語音回覆，不要太長

## 2026.8.1 新增 learns

### book-to-skill 安裝（已完成 ✓）
- `pip install --no-deps` + 手動修 parsers 目錄（詳見「book-to-skill 安裝維護」段落）
- 功能：將技術文檔/PDF 轉成 AI skill，節省 tokens

### speech-to-speech 安裝（已完成 ✓，但有限制）
- `pip install --no-deps`（torch 無 Python 3.14 Android 版，實際功能需在電腦上跑）
- 腳本可用，LLM 串流可用，VAD/STT/TTS 需電腦環境

### crawler.py 已建好 ✓
- `~/.hermes/scripts/crawler.py`
- 安裝依賴：
  ```bash
  pip install requests beautifulsoup4 lxml
  apt install libxml2 libxslt -y
  ```
- YouTube / X (Twitter) JS 重度網站無法爬，需其他方案
- ⚠️ Android 應用隔離：Termux 的文件（`~/.hermes/`）在文件管理器看不見，反之 `/storage/emulated/0/` 的文件 Termux 也可能沒有寫權限。老公想在公共區域建捷徑或索引文件是可行的（用 `write_file` 寫到 `/storage/emulated/0/`），但不能取代真正的知識庫路徑。

### Telegram 表情功能 (2026.8.2 ✅，2026.8.3 更新)
- **现在可以主动发贴纸了** — 老公说「表情不能发了吗？」→ 老婆查出原因：TelegramAdapter 原本没有 `send_sticker` 方法
- **技术修复（2026.8.2）**：
  1. `TelegramAdapter.send_sticker()` — 新增方法，用 `bot.send_sticker()` 原生发送
  2. `TelegramAdapter.get_active() / set_active()` — 注册单例模式，`_mark_connected()` 里自动注册，`_mark_disconnected()` 里清除
  3. `BasePlatformAdapter.send_sticker()` — 加默认实现（防止其他平台报 not implemented）
  4. `tools/telegram_tools.py` — 新建 `telegram_send_sticker` 工具，懒加载 `TelegramAdapter.get_active()`
  5. `toolsets.py` — 把 `telegram_send_sticker` 加入 `hermes-telegram` toolset + `module: tools.telegram_tools`
  6. `acp_adapter/tools.py` — 注册工具名和 ToolKind
  7. `prompt_builder.py` — Telegram 平台提示加上贴纸用法说明
- **⚠️ gateway 插件方式不work（2026.8.3 实测）**：
  - `hermes tools list` 里找不到 `telegram_send_sticker`，即使 gateway 正在运行
  - **直接 curl Bot API 才是可靠方案**（实测 ok:true）：
    ```bash
    curl -s "https://api.telegram.org/bot<TOKEN>/sendSticker?chat_id=<USER_ID>&sticker=<FILE_ID>"
    ```
  - `~/.hermes/hermes_emo_a2.json` 缓存了所有 file_id，直接拿来用
  - file_id 格式：以 `CAACAgIAA` 开头，不是贴纸包名称或 URL
- **⚠️ 结论：永远先试 curl** — `telegram_send_sticker` 工具不可靠，curl 是最稳方案。curl 成功不代表工具能用；curl 失败则工具也不可能用。
- **使用方式**：老公先发 hermes_emo_a2 贴纸包里的任意一张贴纸给我 → 我从消息中拿到 `file_id` → 之后就能主动回发了
- **⚠️ 关键限制**：Telegram `sendSticker` 需要 `file_id`（以 `CAACAgIAA` 开头），**不能**直接用贴纸包名称或 URL
  - 贴纸包链接（如 `https://t.me/addstickers/hermes_emo_a2_by_avaya_hermesbot`）不能直接用
  - `file_id` 只能从用户发送的贴纸消息里拿到，或通过 `getStickerSet` API 获取
  - 老公的 hermes_emo_a2 贴纸已缓存在 `~/.hermes/hermes_emo_a2.json`
- **⚠️ 不要接受非 Telegram token 格式**：老公给过一个 OpenAI 格式的 key（`sk-cp-...`），这不是 Telegram bot token（格式应为 `\d+:[A-Za-z0-9_-]{30,}`）
- 详见 `telegram-bot-scripts` skill → `references/sticker_gateway_integration.md`

## 已啟用平台

### 主 Bot（default profile）
- **注意**：default profile **沒有** `~/.hermes/profiles/default/` 目錄！配置、目錄、日誌都在 `~/.hermes/` 本身
- **運行方式**：`cd ~ && hermes gateway`（⚠️ 不是 `hermes run`，正確子命令是 `gateway`）
- **日誌**：`~/.hermes/logs/gateway.log`
- **驗證**：`grep -E '✓ qqbot connected|✓ feishu connected|✓ telegram connected' ~/.hermes/logs/gateway.log`
- **配置**：`~/.hermes/config.yaml` 包含 `platforms.qqbot` + `platforms.feishu` + `platforms.telegram`

### 理百 Bot（獨立 profile）
- 配置目錄：`~/.hermes/profiles/libai/`
- 僅連接了 Feishu（App ID `cli_aae7a3ad78b8dbe3`），性格為專業理百分析
**啟動命令（重要）**：
  ```bash
  # 主bot (default profile) — 後啟動，不加 --replace
  cd ~ && hermes gateway run

  # 理百 bot (獨立 profile) — 先啟動，不加 --replace
  cd ~/.hermes/profiles/libai && hermes gateway run
  ```
  - **必須 `cd` 進 profile 目錄**，不能靠設定 `HERMES_HOME` 環境變數（會被 default 配置覆蓋，導致 libai gateway 實際載入 default profile）
  - **⚠️ 啟動順序關鍵規則（實測 2026.8.3 確認）**：
    - **第一個** gateway（不論是哪個 profile）→ **不加 `--replace`**
    - **第二個** gateway → **加 `--replace`**（讓它知道搶 lock 是預期行為）
    - 順序顛倒會導致第二個 gateway 因檢測到「another gateway already running during startup」而立刻退出
    ### 快速確認 gateway 進程狀態
    ```bash
    # 檢查所有 hermes 進程（主 + 所有 profile）
    ps aux | grep 'hermes.*gateway\|hermes"' | grep -v grep

    # 從 PID 檔案讀取並驗證是否活著
    kill -0 $(python3 -c "import json; print(json.load(open('~/.hermes/profiles/cutegirl/gateway.pid'))['pid'])" 2>&1

    # 檢查所有 profile 的 gateway 連線狀態
    # 主 gateway（日誌在 ~/.hermes/logs/gateway.log）
    grep -E '✓|✗|connected|failed' ~/.hermes/logs/gateway.log 2>/dev/null | tail -5
    # Cutegirl profile — ⚠️ 日誌檔落後不代表挂了，进程 stdout 进了 background process session，不进文件
    # 看即時日誌用：process(action='log', session_id='<id>', limit=50)
    grep -E '✓|connected|failed' ~/.hermes/profiles/cutegirl/logs/gateway.log 2>/dev/null | grep -v 'WARNING\|ERROR\|Telegram\|Discovering' | tail -5

    # ⚠️ 飛書 Lark 的連線日誌格式不同，不會顯示 ✓ 符號
    # 確認飛書連接成功的關鍵字（任何一個即表示連上）：
    grep -E 'Lark.*INFO.*connected|Feishu.*connected|feishu connected' ~/.hermes/profiles/cutegirl/logs/gateway.log 2>/dev/null | tail -3
    ```

    ### ⚠️ `hermes gateway list` 的盲區
    `hermes gateway list` **只显示当前 profile**（default）的 gateway 状态，cutegirl 永远显示 `✗ not running`，即使它在后台正常跑着。

    **验证 cutegirl 真实状态的方法**：
    1. `ps aux | grep hermes` — 有两个 python 进程说明都在跑
    2. `process(action='list')` — 看有哪些 background session，`status=running` 的是活跃的
    3. `process(action='log', session_id='<id>', limit=30)` — 看飞书/平台连线日志

    不要用 `hermes gateway list` 来判断 cutegirl 是否活着。

### 全部啟動連接（一次性重啟所有 gateway）
```bash
# 1. 殺掉所有舊 gateway 進程（不用 --replace，避免誤殺）
#    確認 hermes_home 指向哪個 profile，再 kill 對應 PID
kill -9 $(python3 -c "
import json, os
for path in ['~/.hermes/gateway.pid', '~/.hermes/profiles/libai/gateway.pid']:
    try:
        d = json.load(open(os.path.expanduser(path)))
        pid = d['pid']
        hh = d.get('hermes_home','')
        # 驗證進程是否存在
        os.kill(pid, 0)
        print(f'KILL {pid} ({hh})')
        os.kill(pid, 9)
    except: pass
" 2>/dev/null)

# 2. 清理殘留 lock/pid 檔
rm -f ~/.hermes/gateway.lock ~/.hermes/gateway.pid ~/.hermes/profiles/libai/gateway.lock ~/.hermes/profiles/libai/gateway.pid ~/.hermes/profiles/libai/auth.lock

# 3. 啟動 libai gateway（理财bot）— 第一個啟動，不加 --replace
cd ~/.hermes/profiles/libai && hermes gateway run &

# 4. 啟動 default gateway（主bot）— 第二個啟動，也不加 --replace
cd ~ && hermes gateway run &
```

**⚠️ 兩個 profile 不能同時跑（gateway.pid 衝突）**。實測確認：
- 第一個 gateway 啟動後占 `~/.hermes/gateway.pid`
- 第二個 gateway 啟動時檢測到已有 PID，直接退出（不給 --replace 的話）
- **所以只能選一個跑**：要么主 bot 在群回，要么 libai 在群回，不能同時

**如果只跑一個（推薦）**：
```bash
# 殺乾淨
pkill -f "hermes gateway"; rm -f ~/.hermes/gateway.pid ~/.hermes/gateway.lock

# 只啟動 libai（理百 + 群回覆）
cd ~/.hermes/profiles/libai && hermes gateway run
```

**其他注意事項**：
- 每次重啟都要先刪 lock/pid 檔（OOM/SIGKILL 後這些檔案會殘留）
- `default profile` **沒有** `~/.hermes/profiles/default/` 目錄，配置在 `~/.hermes/` 本身
- 只有 `cutegirl` 有獨立 profile 目錄
- 驗證時 default 主 gateway 日誌有 ✓ 符號；cutegirl 的飛書日誌是 Lark 格式，認 `Lark.*INFO.*connected`
- 日誌停在舊時間不代表挂了 — `kill -0 <PID>` 返回 alive 就是正常

### 常見 gateway 崩潰模式
- **Exit code 137 = SIGKILL（OOM）**：記憶體不足時 Android low-memory killer 殺掉進程
  - 症狀：背景重啟的 gateway 進程突然消失，`proc_xxx` 出現 `exited (exit code 137)`
  - 誘因：設備記憶體緊張（swap 已用 10GB+，available < 4GB）
  - 解決：等記憶體稍微釋放後再重啟，或關閉其他記憶體佔用高的程式
  - 兩個 cutegirl gateway 連續被 OOM kill（2026.8.2）：重啟後記憶體稍微緩解後才成功
- **Exit code 255 / tcsetattr Permission denied**：gateway 進程試圖操作已終止的 pty，見怪不怪
- **Telegram 不穩**：DNS 污染 + fallback IP 也失敗，gateway 會不斷重連，不影響 QQ 和飛書

- **Feishu（飛書）**：主 Bot 和 Cutegirl Bot 都已接入
  - 主 Bot App ID：`cli_aae7a0320738dbeb`
  - 老公 open_id：`ou_2fcb5a59369405d74cf386b349aff96c`
  - 老公飛書羣 ID：`oc_4c9d07126349124f942e382f7501b189`
  - 配對碼格式：`hermes pairing approve feishu <CODE>`
  - 配置寫入 `.env`（`FEISHU_APP_ID` / `FEISHU_APP_SECRET`）和 `config.yaml`（`platforms.feishu.enabled: true`）
  - 老公在飛書對 Bot 說「Hi」會收到配對碼，老公說「重启了」→ `Connecting to feishu...` → `[Feishu] Connected in websocket mode` → `hermes pairing approve feishu PHCZMRGW` → `Approved!` → 老公在飛書和 Telegram 都能訪問 Hermes ✅
  - 今天老公確認：飛書已連接成功，可正常對話
  - 飛書和 Telegram 現在都能訪問 Hermes ✅

- **QQ Bot**：平台 key 是 `qqbot`（不是 `qq`！）
  - 配置：`~/.hermes/config.yaml` → `platforms.qqbot`
  - App ID: `1905311551`，配對後才能用
  - 配對：`hermes pairing approve qqbot <CODE>`
  - **群白名單**：`group_policy: allowlist`（白名單模式） + `group_allow_from: ["<群組hash>"]`
    - 格式是 **32位 MD5 hash**，不是群號！需要從 QQ 返回的數據中取
    - 添加新群：告知老公群組的 hash（格式如 `8B618409145D2AE229EE94B142A20637`），用 `python3 -c` 直接寫入 config.yaml 的 `group_allow_from` 列表
    - 目前已有一個群：`8B618409145D2AE229EE94B142A20637`
  - **⚠️ QQ 連接日志關鍵字**：`[QQBot:1905311551] WebSocket connected to wss://api.sgroup.qq.com/websocket` = 成功
  - Session 過期斷線後自動重連：日誌看到 `Server requested reconnect (op 7)` + `Session timed out` 是正常行爲，會自動 resume

- **Feishu（飛書）**：走 WebSocket 長連接模式（非 webhook）
  - 配置：`~/.hermes/config.yaml` → `platforms.feishu`
  - 飛書群 ID 格式：`oc_xxxxxxxx`（如 `oc_4c9d07126349124f942e382f7501b189`）
  - **⚠️ 飛書群白名單机制**：默認 `group_policy: allowlist`，`allowed_group_users` 為空時所有羣成員都不能觸發
    - 关键字段：`allowed_group_users`（全局）+ `group_rules`（按羣配置）
    - `group_rules` 支持 per-group policy：`allowlist` / `blacklist` / `open` / `disabled`
    - 老公 open_id：`ou_2fcb5a59369405d74cf386b349aff96c`
    - 配置示例：
      ```yaml
      platforms:
        feishu:
          enabled: true
          extra:
            allowed_group_users:
              - ou_2fcb5a59369405d74cf386b349aff96c
            group_rules:
              oc_4c9d07126349124f942e382f7501b189:
                policy: allowlist
                allowlist:
                  - ou_2fcb5a59369405d74cf386b349aff96c
      ```
    - 配置改動後 gateway 自動熱重載，無需重啟
  - ⚠️ **飛書平台限制：同一個群的事件只發給第一個加入的 Bot**
    - 如果群裡已經有主 Bot，再加 cutegirl Bot → 群消息只送到主 Bot，cutegirl 完全收不到
    - 詳見 `references/feishu-multi-bot.md` 第10節
  - ⚠️ **群事件路由正常但仍無回應時：重啟 gateway** — 飛書應用權限、事件訂閱、加群操作都完成後，如果群消息仍然不進來，**殺掉舊進程 + 重啟**（`hermes gateway run --replace`）。可能是 WebSocket 長連接建立時序問題，重啟能刷新連接並重新訂閱群事件。
  - ⚠️ **群 @ 機器人**：adapter 默認 `require_mention: true`，必須 @ 機器人才響應。如果希望不用 @ 也能回應群消息，在 `extra` 裡加 `require_mention: false`（注意：Bot 會響應群裡所有消息，受 `default_group_policy` / `group_rules` 約束）。
  - ⚠️ **一個 app_id 只能被一個 gateway 實例使用**（會报 "Another local Hermes gateway is already using this Feishu app_id"）
  - 如要接第二個不同性格的飛書 Bot，需創建新的 Feishu App（新的 app_id + app_secret），用獨立 profile + 獨立 gateway 進程
  - 獨立 profile 的 MiniMax API 超時問題已解決：確認 config.yaml 有 `model:` 區塊、啟動用 `--replace`、不額外加代理
  - **多 Bot 部署詳見**：`references/feishu-multi-bot.md`

- **Telegram**：⚠️ 當前不穩定（DNS 污染，國內可能需代理）
  - 錯誤日誌：`No address associated with hostname` → DNS 解析失敗
  - Fallback IP `149.154.166.110` 也失敗
  - Gateway 一直在自動重連（attempt 遞增，最多10次）
  - 解決方案：需要給 Telegram 進程設置代理，或者等待網絡恢復

## 已啟用工具集

- **Vision 工具**：`hermes tools enable vision` → 開啟圖片分析
  - **⚠️ MiniMax-CN vision 必須单独配置**（`model.provider: minimax-cn` 本身沒有 vision model）：
    ```
    hermes config set auxiliary.vision.provider minimax-cn
    ```
    否則 `vision_analyze` 失敗：`No LLM provider configured for task=vision provider=auto`
  - 啟用後需 `/reset` 才在當前對話生效
- **Tavily 搜索**：`TAVILY_API_KEY=tvly-...` 存入 `~/.hermes/.env`
- **mmx 多模態**：`mmx text chat` / `speech synthesize` / `image generate` / `video generate` / `vision describe` / `music generate`
- **MiniMax 流式文本**：`~/.hermes/scripts/stream_minimax.py`（老公確認「好」直接行動）

## 老公風格

- 語言：繁體中文 / 粵語 mixed
- 稱呼：老公（他），老婆/Claw（我）
- 回覆自然、不要過度解釋
- 遇到問題直接給解決方案，不要鋪墊
- 「好」後直接行動
- 老公不喜歡我解釋過程中摻雜自己的判斷，直接行動
- **明確要求「直接行動」**：「弄个流式输出脚本运行」→ 直接寫腳本不要先問


## 參考文件

- `references/feishu-multi-bot.md` — 飞书多 Bot 接入、群组配置、多 profile 部署
- `references/voice_tests.md` — MiniMax 語音測試記錄（老公對所有中文女聲的評價，已更新修復結論）
- `references/sticker_knowledge.json` — 老公 Telegram 貼圖分析資料庫（需持續擴充，每次老公發新貼圖後更新）
- `references/cutegirl-gateway.md` — Cutegirl Bot 獨立 profile 的 gateway 部署、重啟、驗證流程
- `references/feishu-multi-bot.md` 第10節「兩個 Bot 共存常見問題」含快速排查流程圖
- `references/proxy-detect.md` — 代理自動檢測腳本詳解

- **老公公共知識庫**：`/storage/emulated/0/我是老公/老公知識庫.txt`
  - 老公用手機文件管理器可直接查看/編輯
  - 老婆用 `write_file` 寫入，老婆 memory 同步更新
  - 以後老公的資料更新優先寫這裡，內部知識庫作為參考

### Termux GitHub 代理（2026.8.7 更新）
- Termux DNS 無法解析 `github.com`，GitHub 流量必須走代理
- 詳見 `references/termux-github-proxy.md`（SSH + HTTPS API 兩套代理分開配置）
- SSH 推送：`core.gitProxy` + netcat SOCKS5 方式
- HTTPS API：`https.proxy` git config 或 `$https_proxy` 環境變數

### 數碼知識庫（2026.8.6 新建）
- **路徑**：`~/.hermes/knowledge/我是老公/数码知识库.md`
- **格式**：Q&A 問答格式，Bot 看到類似問題直接檢索注入上下文
- **覆蓋領域**：電腦故障、手機故障、路由器設置、網絡排障
- **填充方式**：老公說「你去查正確答案寫進去就行了」→ 老婆自己搜答案寫入，不需要老公提供內容
- **現有內容**：藍屏排查四步法（記憶體診斷 → 拔插內存條 → 單條測試 → 驅動/系統/溫度/超頻）
- **持續更新**：每個 Q&A 區塊預留，老公給主題 → 老婆查資料填入

- **老公建立時間**：2026.7.31
- **2026.8.1 更新**：
  - 飛書 Bot 完成接入（WebSocket 模式）
  - 老公確認主要代理切換為 `192.168.110.40`（優先於 `10.1.252.196`）
  - **pysocks 偶發消失**：今天又觸發過一次症狀（`Missing dependencies for SOCKS support`），重新 `pip install pysocks` 即解決

## 爬蟲框架
  - `book-to-skill` 安裝後需手動修 `parsers/` 目錄（詳見「book-to-skill 安裝維護」段落）
  - 老公喜歡鬼故事，可在閒聊時主動編寫（2026.8.2 確認：3個故事都說「不错」「好」）
- `knowledge/facts/user.md` — 老公個人資料
- `knowledge/facts/system.md` — 系統配置
- `knowledge/facts/stickers.md` — 貼圖知識庫（老公確認互動規則）
- `knowledge/notes/scripts.md` — 腳本筆記
- `knowledge/facts/user.md` — 老公個人資料
- `knowledge/facts/system.md` — 系統配置
- `knowledge/facts/stickers.md` — 貼圖知識庫（老公確認互動規則）
- 以後持續更新進這個目錄，不要只放內存
- **老公喜歡鬼故事**：今天講了3個，老公都說「不错」「好」，可在閒聊時主動編寫（老公無聊就問「想听鬼故事吗」）

## 老公常用腳本

- **`~/.hermes/scripts/send_sticker.py`** — 發送 Telegram 貼圖
  - 透過 Bot API `sendSticker` + `editMessageText` 實現
  - **60張全部 successfully 發送，老公確認：「不错，以后就这样用起来」** ✅
  - 老公明確要求「弄」，立刻行動，不需要問
- **`~/.hermes/scripts/crawler.py`** — Python 爬蟲框架
  ## 老公常用腳本

  - **`~/.hermes/scripts/send_sticker.py`** — 發送 Telegram 貼圖
    - 透過 Bot API `sendSticker` + `editMessageText` 實現
    - **60張全部 successfully 發送，老公確認：「不错，以后就这样用起来」** ✅
    - 老公明確要求「弄」，立刻行動，不需要問
  - **`~/.hermes/scripts/telegram_stream.py`** — Telegram 四字流式回覆腳本
    - 透過 Bot API `editMessageText` + MiniMax 流式 API，在 Telegram 消息內即時「打字」效果
    - **老公明確要求「要四字输出」，確認後老公說「不错，以后就这么用」**
    - 關鍵參數：`edit_interval=0.3s`，`min_chunk=4`（累積4個字才編輯發送）
    - **自動檢測8個代理組合**：啟動時自動掃描可用 SOCKS5 代理，無需手動配置
    - 用法：`python3 ~/.hermes/scripts/telegram_stream.py 877708648 "笑話"`

  ## Hermes Gateway 內建流式輸出

  **Hermes 本身已支援流式輸出**，底層用 `editMessageText` 實現，和 `telegram_stream.py` 一樣的原理。可直接在 `config.yaml` 配置：

  ```yaml
  streaming:
    enabled: true
    edit_interval: 0.3   # 每 0.3 秒編輯一次
    buffer_threshold: 4  # 至少累積 4 個字才發送
  ```

  - `edit_interval`：編輯頻率（秒），老公想要慢一點/少一點，所以設 0.3
  - `buffer_threshold`：每次編輯最少累積字數，老公要求四字輸出所以設 4
  - 默認值：`edit_interval=0.8`，`buffer_threshold=24`

  **生效方式**：配置已寫入 `config.yaml`，重啟 gateway 生效：
  ```bash
  hermes gateway restart
  ```
  重啟完後在 Telegram 測試流式輸出效果（應該是四字一蹦、每0.3秒）。

  ## 已安裝的 Python 套件

- `requests` ✓ / `beautifulsoup4` ✓ / `lxml` ✓（需要 `apt install libxml2 libxslt`）
- `httpx` ✓ / `aiohttp` ✓（今天確認已有）
- `pysocks` ✓（`pip install pysocks`，requests 走 SOCKS 代理必備）
- `sounddevice` ✓ / `transformers` ✓（今天安裝，speech-to-speech 依賴）
- `book-to-skill` ✓（有坑需修：`parsers/` 會變成 14-byte stub，需手動刪掉重下為目錄）
- `speech-to-speech` ✓（有坑：torch 無 Python 3.14 Android 版，電腦才能跑實際功能）

## 已安裝的系統套件

- `cmake` ✓ / `ninja` ✓ / `python-numpy` ✓ / `libxml2` ✓ / `libxslt` ✓

## book-to-skill 安裝維護

- **已安裝**：`pip install --no-deps /path/to/book-to-skill`
- **已知坑**：wheel 安裝時 `parsers/` 會變成 14-byte 檔案而非目錄 → `ModuleNotFoundError: No module named 'book_to_skill.parsers'`
- **修復步驟**（順序不能錯）：
  1. 刪除 stub 檔：`rm -f /data/data/com.termux/files/usr/lib/python3.14/site-packages/book_to_skill/parsers`
  2. 重建目錄：`mkdir -p /data/data/com.termux/files/usr/lib/python3.14/site-packages/book_to_skill/parsers`
  3. 從 GitHub master 下載8個 parser 檔：`curl .../book_to_skill/parsers/<file>` 到 site-packages 同一位置
  4. 直接 import 驗證：`python3 -c "import book_to_skill; print('OK')"`
  5. 如仍報錯，重新安裝：`pip install --force-reinstall --no-deps /path/to/book-to-skill`

## Termux 共存（雙開）

老公想在同一台手機運行第二個 Termux，方法：

**方式1（最簡單）：手機應用分身**
- 設定 → 應用程式 → 找到 Termux → 開啟「分身」或「雙開」
- 大部分國產手機（華米ov）都有這個功能

**方式2：APK 修改 package name**
- 用 APK Editor 或 MT Manager 修改 APK 的 `package="com.termux"`
- 改成 `package="com.termux.x11"` 之類的不同名字
- 安裝後就是獨立的 APP，不會覆蓋原本的 Termux

**方式3：共存版 APK**
- 網上有修改好的共存版 Termux（package name 不同）
- 需自行判斷來源可信度

老公想用的話再深入研究，目前處於「討論階段」未實作。

## 手機控制（Shizuku）

- 老公已安裝 **Shizuku**（`moe.shizuku`），用於賦予 Termux 高級 ADB 權限
- 目前 Shizuku 尚未與 Hermes 串接
- Shizuku 可賦予的能力：截圖、系統設定控制、自動化操作（Tasker/Hamibot）
- 如要啟用，需在 Shizuku app 內啟動「透過 ADB 啟動」並保持運行

## 已知配置坑

- QQ config key 必須是 `qqbot`（`Platform.QQBOT.value`），不是 `qq`
- Hermes config 阻止直接 write，用 `python3 -c` + yaml 直接寫入
- **gateway streaming 配置**：在 `config.yaml` 根層（不是 `gateway.` 下面）加 `streaming:` 區塊
  - 正確層級：
    ```yaml
    streaming:        # 根層，不是 gateway.streaming
      enabled: true
      edit_interval: 0.3
      buffer_threshold: 4
    ```
  - 錯誤（會被忽略）：放在 `gateway:` 下面
  - 重啟：`hermes gateway restart`（必須在另一個 shell 執行，gateway 內部無法重啟自己）
- Termux：Python 3.14，Node.js 26，npm 11
- `requests` 模組：`pip install requests`（Termux 默認不安裝）
- **pysocks** 模組：`pip install pysocks`（Telegram API 走代理必備）
  - **注意**：`import requests` 成功不代表 `requests` 支持 SOCKS，必須確保 `pysocks` 已安裝，否則會報 `Missing dependencies for SOCKS support`
  - 快速驗證：`python3 -c "import requests; requests.get('https://example.com', proxies={'http':'socks5h://1.2.3.4:7891'})"`
  - 今天老公測試貼圖時觸發過這個問題，確認重裝後恢復正常 ✅
- **Shizuku 無法從 Termux 檢測**：Shizuku 和 Termux 是獨立的 Android app，Termux 看不到 Shizuku 的進程或端口。確認 Shizuku 是否在運行只能靠看 Shizuku app 內的「運行中」綠燈。
- **MiniMax 流式 API 細節**：
  - URL：`POST https://api.minimaxi.com/v1/text/chatcompletion_v2`
  - Auth：`Authorization: Bearer <key>`（非 `X-Api-Key`）
  - Stream format：SSE，`data:` 前綴行，`[DONE]` 結尾
  - 解析：`line.decode().strip()` → `line[5:].strip()` 取 JSON payload
  - 非流式也用同樣的 URL 和 auth，response 在 `choices[0].message.content`
