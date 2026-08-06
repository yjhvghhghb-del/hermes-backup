老公的MiniMax API认证方式：ANTHROPIC_API_KEY在api.mytokk.com有效（minimaxi.com用X-Api-Key失败）；代理用172.19.0.1:7890；模型用claude-haiku-4-5-20251001(claude-haiku系列)，不能用MiniMax-M2.7
§
老公用內網代理（翻譯/MiniMax）：首選 172.19.0.1:7890（返404=能通），備用 192.168.110.225:7891；認證用 api.mytokk.com + ANTHROPIC_API_KEY
§
老公喜歡的流式速度：每0.3秒累積4個字才編輯發送
§
【語音】tts 預設值舊了（DEFAULT_MINIMAX_VOICE_ID="English_expressive_narrator"）；config.yaml 加 tts.minimax（model: speech-2.8-hd, voice_id: female-tianmei）後重啟
§
本地知識庫：~/.hermes/knowledge/facts/ · notes/ · skills/（持續更新）；老公公共知識庫：/storage/emulated/0/我是老公/老公知識庫.txt
§
老公Telegram bot token: 8800919754:AAFdNkpAGSI6M5ahwd3_5g-SuZzusH7ybp4；发文件用sendDocument；hermes_emo_a2 贴纸 file_id 存 ~/.hermes/hermes_emo_a2.json
§
飞书多bot并发限制：同一 app_id 的多个 Hermes 实例不能同时跑（共用同一个 WebSocket 连接会冲突）。新加飞书 bot 需确保 app_id 与现有bot都不同
§
飞书群 oc_4c9d07126349124f942e382f7501b189 白名单策略，仅老公 ou_2fcb5a59369405d74cf386b349aff96c 可发言；新用户Unauthorized需手动加到 platforms/pairing/feishu-approved.json 后重启
§
【飛書三Bot配置】同时运行三个独立profile，各自不同app_id：
• 主bot (default) — app_id: cli_aae7a0320738dbeb, secret: <LARK_SECRET_1>，白名單：ou_2fcb5a59369405d74cf386b349aff96c，群 oc_4c9d07126349124f942e382f7501b189
• 理财Bot (libai) — app_id: cli_aafa2c6a83b85bee, secret: <LARK_SECRET_2>，白名單：ou_2fcb5a59369405d74cf386b349aff96c，群 oc_4c9d07126349124f942e382f7501b189
• 文娱写作bot (wenyu) — app_id: cli_aae7a3ad78b8dbe3, secret: <LARK_SECRET_3>，白名單：ou_2fcb5a59369405d74cf386b349aff96c，群 oc_4c9d07126349124f942e382f7501b189
新用户配对：HERMES_HOME=~/.hermes/profiles/<profile> hermes pairing approve feishu <配對碼>
§
• 理财 bot (libai profile): app_id=cli_aafa2c6a83b85bee，群白名单 oc_4c9d07126349124f942e382f7501b189；同群多 bot 时飞书 @事件只推给其中一个（嗨妹小老婆抢走了），建议理财bot单独建群
• 理财 bot 技能规划：网络搜索+Python代码+飞书文档+飞书多维表格（已有 feishu-bitable/feishu-wiki-document-read skill）+ 缺财经数据API
§
沟通风格：极简直接型——"好的"、"A"、"1 2"、"没事"、"不错"。说方向我就干，不喜欢被追问。
§
GitHub PAT (yjhvghhghb-del): <PAT_REDACTED>，代理 172.19.0.1:7890
