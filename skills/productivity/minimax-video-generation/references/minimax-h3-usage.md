# MiniMax H3 视频生成参考

## API 文档

- 官方文档：https://platform.minimax.io/docs/guides/video-generation
- 创建任务：POST `/v2/video_generation`
- 查询状态：GET `/v2/video_generation/retrieve?task_id=xxx`
- 取消/删除：DELETE `/v2/video_generation/delete?task_id=xxx`

## 输入输出规格

| 项目 | 规格 |
|------|------|
| 输出分辨率 | 768P / 2K |
| 输出时长 | 4-15秒，整数值 |
| 比例 | 21:9, 16:9, 4:3, 1:1, 3:4, adaptive |
| 输入图片 | 0-9张，JPG/JPEG/PNG/WEBP/HEIC/HEIF，最大30MB/张 |
| 输入视频 | ≤3段，每段2-15秒，总时长≤15秒，最大50MB/段 |
| 音频 | ≤3段，每段2-15秒，最大15MB/段 |
| 提示词上限 | 7000字符 |

## 三种生成模式

1. **Text-to-Video** —纯文本提示词生成
2. **Image-to-Video** — 图生视频（首帧/尾帧）
3. **Reference Generation** — 参考生成（参照角色/动作/风格/声音/剪辑节奏）

## 已知问题

- `MINIMAX_CN_API_KEY`（`api.minimaxi.com` 的key）**不能用于视频API**，视频API需要单独的视频额度
- **视频API是 `/v2/video_generation`**，不是 `/v1/`
- **需要开通视频额度**（升级套餐或网页端领取免费额度）才能调用成功
- **401错误 = key无权限**，不是网络问题
- Python requests 库走 `172.19.0.1:7890` 有连接问题，脚本改用 curl subprocess 调用

## 计费（2026-08）

MiniMax H3 属于 Pay-as-you-go 视频生成，按生成秒数计费。具体价格查官方定价页。
