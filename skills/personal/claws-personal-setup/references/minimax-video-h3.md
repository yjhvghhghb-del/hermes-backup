# MiniMax H3 视频生成 API

## 模型能力
- **模型名**: `MiniMax-H3`
- **API 端点**: `POST https://api.minimax.io/v2/video_generation`
- **查询端点**: `GET https://api.minimax.io/v2/video_generation/retrieve?task_id=<id>`
- **输出**: 768P / 2K，时长 4-15 秒，比例 21:9 / 16:9 / 4:3 / 1:1 / 3:4 / adaptive
- **模式**: 文生视频、图生视频（首尾帧）、参考生成
- **注意**: 需要 Pay-as-you-go API，视频额度独立于聊天额度

## 代理
- `172.19.0.1:7890` ✅ 能通 api.minimax.io（返 401 = key 验不过但代理通）
- `127.0.0.1:7890` ✅ 也能通
- `192.168.110.225:7891` ❌ 不通
- `10.1.252.196:7891` ❌ 不通

## Python requests + SOCKS 代理坑
`requests` 库走 SOCKS 代理调用 `api.minimax.io` 会报 `RemoteDisconnected: Remote end closed connection without response`。
**解法：用 curl subprocess 代替 requests**（curl 没问题）。

## API Key
- 环境变量: `MINIMAX_API_KEY`（不是 `MINIMAX_CN_API_KEY`）
- `MINIMAX_CN_API_KEY=sk-cp-...` 是聊天用的，视频 API 可能需要独立的 key/额度
- 测试命令:
  ```bash
  curl -s --proxy "http://172.19.0.1:7890" \
    -X POST "https://api.minimax.io/v2/video_generation" \
    -H "Authorization: Bearer $MINIMAX_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"model":"MiniMax-H3","content":[{"type":"text","text":"test"}],"resolution":"768P","duration":5,"ratio":"16:9"}'
  ```

## 三步流程
1. `POST /v2/video_generation` → 返回 `task_id`
2. 轮询 `GET /v2/video_generation/retrieve?task_id=<id>` 直到 `status==succeeded`
3. 从返回的 `content.url` 下载视频

## 脚本
- `scripts/minimax_video.py` — curl 版视频生成脚本
