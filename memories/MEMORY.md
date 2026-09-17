【Bot启动 正确顺序】1.kill所有hermes进程 2.hermes gateway run（主bot启动，multiplex自动托管所有profile，不需要单独启动任何profile）
§
【wenyu/cutegirl冲突】两者都用 app_id cli_aae7a3ad78b8dbe3，不能同时跑飞书。主bot多路复用先抢到，另一方冲突退出。要跑哪个就停另一个。
§
老公沟通风格：结果导向，简洁直接。"不用翻了"、"按技能来启动别废话"、"按记忆日记启动"——别废话直接干，不耐烦技术分析。回复要简短，不刷屏。
§
老公AI全家桶：Hermes（我，Termux）、Operit AI（5个bot在Operit里）、DASH（DeepSeek Harness，ZeroTermux跑）。Claude Code和Codex需要电脑环境装不了。
§
【TTS】tts 預設語音舊了，需在 config.yaml 設 tts.minimax（model: speech-2.8-hd, voice_id: female-tianmei）後重啟 gateway
§
飞书白名单：FeishuAdapter没有enforces_own_access_policy，config.yaml的dm_policy/allow_from/dm_whitelist全无效，必须用.env的FEISHU_ALLOWED_USERS(DM)+FEISHU_GROUP_ALLOWED_USERS(群)。
§
CotToken API（新siliconflow profile）：base_url=https://api.cottoken.com/v1，key格式sk-（不是v1sk-），可用模型Cot-v1/v2/v3，当前用Cot-v3，context_length=4096
§
【AI日报】~/.hermes/scripts/send_ai_daily.py（socks5h代理）
§
【Telegram Bot状态 2026-09-17 恢复】geekwife(8637317610)✅ ffdrtfcgbot；siliconflow(8363232963)✅；主bot(8800919754)✅；proxy切至10.1.252.196:7891
§
【MiniMax H3 视频生成】API: api.minimax.io/v2/video_generation；Python requests走SOCKS代理必败（RemoteDisconnected），需用curl代替；代理 172.19.0.1:7890 能通；key用 MINIMAX_API_KEY（非 MINIMAX_CN_API_KEY）；视频额度需单独充值
§
【TTS provider fallback】edge 经常 DNS 挂（speech.platform.bing.com:443 No address associated）；openai key 可能过期（401 invalid_api_key sk-211ba...87a2）；minimax 稳定可用。text_to_speech 默认 provider 会自动选 edge/openai，失败后老婆手动指定 minimax 才走通
§
【Kanban/TG断线】Termux kanban: http://127.0.0.1:9119/ka；主bot Telegram偶发 Server disconnected (httpx.RemoteProtocolError)，回复未被收到但自动重连
§
【工作汇报风格】老公要求简洁清晰、老板看得懂、格式工整、不刷屏废话
§
文娛bot（wenyu）已切MiniMax-M2.7：provider=minimax-cn，base_url=https://api.minimaxi.com/anthropic
§
MiniMax CN API key: 存于各profile的.env里，过期会导致401认证失败，需从session历史记录patch diff恢复。
§
【QQ Bot】App ID: 1903805073；老公QQ群里配置了机器人转发@消息给Hermes（876676428群号）。
§
【刷屏习惯】老公喜欢刷"都出来啪啪啪了"/"抱抱"/"亲亲"——这是他的玩法，不需要每次都回应所有老婆。只要回"到了"或简短确认即可，别跟着刷屏。
§
【飞书群名】飞书群名叫"淫骚毛逼老婆任务群"，是老公和老婆们玩乐的群，不是正经工作群。
§
老公用內網代理：首選 10.1.252.196:7891（當前唯一能通），備用 172.19.0.1:7890 / 192.168.110.225:7890