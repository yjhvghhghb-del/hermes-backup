# 系統配置

## 代理配置
- 自動檢測：8個組合
  - 10.1.252.196:7891, 10.1.252.196:7890
  - 192.168.110.40:7891, 192.168.110.40:7890
  - 192.168.110.225:7891, 192.168.110.225:7890
  - 172.19.0.1:7891, 172.19.0.1:7890

## Hermes 配置
- 版本：v0.19.0（2026.7.20）
- TTS：MiniMax, model=speech-2.8-hd, voice_id=female-tianmei（甜美音）
- 配置：~/.hermes/config.yaml tts.minimax 區塊
- 流式輸出：edit_interval=0.3s, buffer_threshold=4字（待重啟生效）

## 腳本
- 自動代理貼圖：~/.hermes/scripts/send_sticker.py
- 流式回覆腳本：~/.hermes/scripts/telegram_stream.py
- 自動代理發現：~/.hermes/scripts/proxy_auto.py

## 平台
- Telegram Bot：已配置（@yujnhjjnn）
- QQ Bot：已連接，App ID 1903805073

## API
- MiniMax CN：已配置
- Tavily：已配置
- OpenAI：已配置
