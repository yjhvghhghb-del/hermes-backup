# MoA / delegate_task 故障排查

## 症状

`delegate_task` 失败，错误：
```
RuntimeError: No LLM provider configured for task=moa_aggregator provider=openrouter. Run: hermes setup
```

即使已在 `config.yaml` 正确配置了 `delegation.model` + `delegation.provider`，子 Agent 仍然失败。

## 根因：Session Metadata 里的 Model Override

某些旧 session 的 metadata 里硬编码了 MoA 配置（`provider=moa`, `base_url=moa://local`, `model=default`），导致**每次恢复都强制走 MoA 模式**，绕过了 config.yaml 的 delegation 配置。

Session metadata 里的 `model_override` 优先于 config.yaml。

## 排查步骤

```bash
# 1. 查看哪些 session 有 model_override
grep -l "model_override" ~/.hermes/sessions/sessions.json

# 2. 查看具体内容（以 20260731_023330_ca8ff308 为例）
grep -A20 '"20260731_023330_ca8ff308"' ~/.hermes/sessions/sessions.json | grep -E "model_override|provider|base_url"

# 3. 确认是 MoA override
# 看到 "provider": "moa", "base_url": "moa://local" 就是中招了
```

## 修复：删除/重置问题 Session

```bash
# 查看 session 列表
hermes sessions list

# 删除问题 session（会要求确认）
hermes sessions delete <SESSION_ID>

# 或者用管道自动确认
echo "y" | hermes sessions delete <SESSION_ID>
```

## 配置参考：正确的 delegation + MoA 配置

```yaml
# config.yaml

# delegate_task 子 Agent 使用的模型
delegation:
  model: MiniMax-M2.7
  provider: minimax-cn

# MoA 聚合器（如果用到 MoA 模式）
moa:
  aggregator:
    provider: minimax-cn
    model: MiniMax-M2.7
```

⚠️ `moa.aggregator` 结构：直接放在 `moa` 下面，不是 `moa.default.aggregator`。

## 多个 Hermes 进程冲突

重启用 `hermes gateway run --replace` 时，旧的 Hermes 进程可能没有真正退出（SIGTERM 没杀死），导致新旧进程同时跑在新 gateway 上。

```bash
# 检查所有 hermes 进程
ps aux | grep hermes | grep -v grep

# 强制杀掉旧进程
kill -9 <PID>

# 确认只剩一个
ps aux | grep hermes | grep -v grep
```

## 验证 delegate_task 正常工作

1. 删掉问题 session 后，发一条新消息开启干净 session
2. 尝试 `delegate_task(goal="say hello")` 
3. 检查日志：`~/.hermes/logs/agent.log` 里的 `provider=minimax-cn` 表示正常
