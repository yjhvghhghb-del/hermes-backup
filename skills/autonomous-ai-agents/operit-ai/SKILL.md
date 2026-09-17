---
name: operit-ai
description: Android AI agent with Ubuntu environment and UI automation.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [android]
metadata:
  hermes:
    tags: [android, ai-agent, mobile, operit]
    related_skills: [hermes-agent, autonomous-ai-agents]
---

# Operit AI

Android 上功能完备的 AI Agent 平台，与安卓系统深度集成。

## 核心能力

- **内置 Ubuntu 24 环境** — 手机上跑 Linux 命令行
- **多模型支持** — 云端（OpenAI/Claude）或本地 GGUF/Ollama
- **40+ 内置工具** — 文件管理、HTTP、系统控制、UI 自动化
- **UI 自动化** — 语音驱动 + 屏幕点击/滑动/表单填写
- **记忆系统** — 持久化上下文
- **MCP 插件扩展** — 可接入 MCP 生态
- **Skill 生态** — 可安装复用技能包
- **内置 Hermes Agent** — Operit 里也可以跑 Hermes，支持接多 Bot

## 与 Hermes 对比

| | Hermes (Termux) | Operit AI |
|--|-----------------|-----------|
| 平台 | Termux/Linux | Android App |
| 系统集成 | 弱（终端为主）| 强（安卓深度控制）|
| UI 自动化 | ❌ | ✅ |
| Ubuntu 环境 | ❌ | ✅ |
| Telegram | ✅ 原生 | 需配置 |
| 多 Bot | ✅ 可配 | ✅ 可配 |
| 模型 | MiniMax/可配置 | 自选 |

## 安装

- APK 下载：https://github.com/AAswordman/Operit/releases
- 要求：Android 8.0+ (API 26)，ARM64，4GB+ 内存

## 已知限制

- OpenCode、Prime Agent 等编程 Agent 不支持 Android/Termux 环境（平台检查：os: darwin,linux,win32）

## GitHub

https://github.com/AAswordman/Operit
