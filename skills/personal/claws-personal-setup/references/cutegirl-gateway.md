# Cutegirl Bot Gateway — 部署參考

## 基本資訊

- **Profile 目錄**：`~/.hermes/profiles/cutegirl/`
- **Gateway PID 檔**：`~/.hermes/profiles/cutegirl/gateway.pid`
- **日誌檔**：`~/.hermes/profiles/cutegirl/logs/gateway.log`
- **啟動命令**：
  ```python
  terminal(background=True, command="cd ~/.hermes/profiles/cutegirl && rm -f gateway.lock gateway.pid auth.lock && hermes gateway run --replace", notify_on_complete=True)
  ```
  - **`--replace` 是必須的**：即使在 profile 目錄內，Hermes 的 lock 機制是全局的，會檢測系統上所有 hermes gateway 进程
  - **每次啟動前都要刪 `gateway.lock` + `gateway.pid` + `auth.lock`**：OOM/SIGKILL 後這些檔案會殘留，導致 `Another gateway instance already running (PID N)`
  - 禁止用 shell `&` / `nohup` / `disown`，會被 Hermes 拒絕

## 啟動後預期日誌（成功模式）

```
[Lark] [2026-08-02 01:20:08,284] [INFO] connected to wss://msg-frontier.feishu.cn/ws/v2?...
2026-08-02 01:20:07,415 INFO gateway.run: Connecting to feishu...
2026-08-02 01:20:07,894 INFO hermes_plugins.feishu_platform.adapter: [Feishu] Connected in websocket mode (feishu)
2026-08-02 01:20:07,898 INFO gateway.run: ✓ feishu connected
2026-08-02 01:20:07,908 INFO gateway.run: Gateway running with 1 platform(s)
```

注意：只會顯示 **1 platform**（Feishu），因為 Cutegirl profile 沒有配置 QQ 和 Telegram。

## 進程結構（2026.8.2 實測）

```
 PID 31366  bash -lic "cd ~/.hermes/profiles/cutegirl && hermes gateway run --replace"
    └─ PID 31368  python ... hermes gateway run --replace  ← 實際 gateway 行程
```

查詢：
```bash
ps aux | grep -E 'hermes.*gateway' | grep -v grep
```

## 驗證啟動成功的快速命令

```bash
# 檢查進程是否活著
kill -0 <PID> 2>&1 && echo "alive" || echo "dead"

# 檢查日誌關鍵字（cutegirl 的 Lark 格式）
grep -E 'Lark.*INFO.*connected|Gateway running with 1 platform' ~/.hermes/profiles/cutegirl/logs/gateway.log

# ⚠️ 不要只 grep '✓' — Lark 的連線日誌是 [INFO] 不是 ✓
```

## Termux SIGKILL / 殘留 lock 的重啟行爲

如果 gateway 被 Android 低記憶體殺死（exit 137 / SIGKILL），或者 wrapper bash 進程被單獨殺掉（exit -9），症狀是：

```
# 症狀：ps aux 有 python 進程但日誌停在舊時間
# 原因：gateway.lock / gateway.pid / auth.lock 殘留，lock 機制衝突

# 解法：啟動命令中強制刪除 lock 檔
cd ~/.hermes/profiles/cutegirl && rm -f gateway.lock gateway.pid auth.lock && hermes gateway run --replace
```

### ⚠️ `hermes gateway list` 不等於 cutegirl 真实状态
`hermes gateway list` 只查看当前 profile，cutegirl 永远显示 `✗ not running`。

**真实状态看这里**：
1. `ps aux | grep hermes` — 有两个 python 进程 = 都在跑
2. `process(action='list')` — `status=running` 的 session 是活跃的
3. `process(action='log', session_id='<id>')` — 即時 stdout（飞书 Lark 连接日志在这里，不在 gateway.log 文件里）

### 殺掉並重啟的完整流程

```bash
# 1. 清理 lock/pid（Termux SIGKILL 後殘留 lock 是 ghost 進程的主要原因）
cd ~/.hermes/profiles/cutegirl && rm -f gateway.lock gateway.pid auth.lock

# 2. 啟動（第一個 gateway 不加 --replace）
terminal(background=True, command="cd ~/.hermes/profiles/cutegirl && hermes gateway run", notify_on_complete=False)

# 3. 啟動 default gateway（第二個 gateway 加 --replace）
terminal(background=True, command="cd ~ && hermes gateway run --replace", notify_on_complete=False)

# 4. 等 8 秒後檢查進程
sleep 8 && ps aux | grep 'hermes gateway' | grep -v grep

# 5. 確認 cutegirl 飛書連線（日誌在 process session，不在文件）
#    process(action='log', session_id='<proc_id>', limit=30)
#    成功關鍵字：Lark.*INFO.*connected to wss://msg-frontier.feishu.cn
```

## Default Profile Gateway 崩潰恢復（2026.8.19 實測）

**背景症狀**：Android low-memory killer 發送 SIGKILL → `lifecycle_ledger` 記錄 `exited UNCLEANLY (no exit path ran — SIGKILL / OOM / VM death)` → 下次重啟時日誌會警告。

**崩潰後發生的問題**：
- `hermes --profile default gateway run` → 回報「Another gateway instance is already running (PID N)」然後立刻退出（exit code 1），即使該 PID 已經死了
- 這是因為殘留的 lock/ledger 機制認為還活著

**正確恢復方式**（`restart` 會自動處理清理）：
```bash
hermes --profile default gateway restart
```

**千萬不要**：直接跑 `hermes --profile default gateway run`（會閃退）或殺掉舊 PID 再跑（多此一舉）。

**驗證成功**：
```bash
hermes --profile default gateway status
# 預期：✓ Gateway is running (PID: <new>)
```

**日誌確認**：
```bash
# 查看 lifecycle_ledger 警告是否消失（重啟後應不再出现 SIGKILL 警告）
hermes --profile default gateway restart 2>&1 | grep -i 'UNCLEAN\|lifecycle\|SIGKILL'
```

**其他 profile 的同類問題**：邏輯相同，先清理 lock/pid，再重啟。
