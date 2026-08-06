# 腳本筆記

## send_sticker.py
- 用途：發送 Telegram 貼圖
- 用法：`python3 send_sticker.py <chat_id> -p <pack> -n <index>`
- 自動檢測代理，無需手動指定

## telegram_stream.py
- 用途：MiniMax 流式輸出 → Telegram editMessageText
- 用法：`python3 telegram_stream.py <chat_id> <消息>`
- 四字輸出，每0.3秒編輯一次

## stream_minimax.py
- 用途：MiniMax API 流式文本測試
- 用法：`python3 stream_minimax.py <消息>`

## TTS 修復記錄
- 問題：預設聲音是英文男聲
- 原因：tts_tool.py DEFAULT_MINIMAX_VOICE_ID 覆蓋了用戶設置
- 解決：config.yaml 加 tts.minimax.model=speech-2.8-hd, voice_id=female-tianmei
