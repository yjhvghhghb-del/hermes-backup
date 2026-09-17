---
name: minimax-video-generation
description: "MiniMax H3 视频生成：API、脚本、代理配置。当用户要生成AI视频或问MiniMax有什么视频模型时用。"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [android, linux]
tags: [minimax, video, AI-video, H3, API]
---

# MiniMax H3 视频生成

## 能力概览

MiniMax 视频生成模型：
- **Video-01** — 720p/25fps，最长6秒，文生视频+图生视频
- **T2V-01-Director / I2V-01-Director** — 支持镜头控制，电影感运镜
- **MiniMax H3**（当前主力）— 768P/2K，4-15秒，多模态统一模型

## API 端点

```
POST https://api.minimax.io/v2/video_generation
```

注意：是 `/v2/` 不是 `/v1/`。视频生成 API 和文字模型 API 是分开的。

## 关键区别：文字API vs 视频API

| | 文字模型 | 视频生成 |
|---|---|---|
| API 域名 | `api.minimaxi.com` | `api.minimax.io` |
| Key 环境变量 | `MINIMAX_CN_API_KEY` | 需单独的视频API key（网页领取免费额度后获得） |
| 代理 | 同一代理 | 同一代理（`172.19.0.1:7890`） |

**`MINIMAX_CN_API_KEY` 是文字模型key，不能用于视频API。** 视频API需要单独的视频额度，升级套餐后从 `platform.minimax.io` 获取视频专用的key。

## 代理配置

可用代理（2026-08）：
| 代理地址 | 状态 |
|----------|------|
| `http://172.19.0.1:7890` | ✅ 通（返回404=能通） |
| `http://192.168.110.225:7891` | ❌ 不通 |
| `http://127.0.0.1:7890` | ✅ 通（本地clash） |

## 脚本

```bash
python3 ~/.hermes/scripts/minimax_video.py "提示词"
```

环境变量：`MINIMAX_API_KEY`（视频API key，需视频额度）

参数：`-resolution 768P`（或`2K`）、`-duration 4-15`、`-ratio 16:9`

## 工作流程

1. 创建任务 → 拿 `task_id`
2. 轮询状态（10秒间隔，约1-3分钟完成）
3. 拿到视频URL后下载

## 已知问题

- **401 = key无权限**，不是网络问题。常见原因：key没有视频API权限，或视频额度未开通
- 网络代理：Python requests 库走 `172.19.0.1:7890` 有连接问题（但 curl 正常），脚本已改用 curl subprocess 调用
