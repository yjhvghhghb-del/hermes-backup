---
name: delegation-best-practices
description: "Add delegation.model and provider to config.yaml."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [android, linux, macos, windows]
metadata:
  hermes:
    tags: [delegation, subagent, model-config]
    homepage: https://hermes-agent.nousresearch.com/docs/
---

# Delegation Best Practices

`delegate_task` spawns subagents with isolated context + terminal sessions. Key config requirements:

## Always Required: `delegation.model` + `delegation.provider`

Without explicit delegation config in `config.yaml`, subagents inherit NO model and fail to run:

```yaml
delegation:
  model: MiniMax-M2.7        # must match your main model or a compatible one
  provider: minimax-cn       # must match your main provider
```

**Location:** `~/.hermes/config.yaml` (not `.env` — credentials go there, not model settings).

## Optional Tuning Knobs

| Key | Default | Description |
|-----|---------|-------------|
| `delegation.max_concurrent_children` | 3 | Parallel subagent cap |
| `delegation.max_iterations` | 50 | Hard loop cap per subagent |
| `delegation.max_spawn_depth` | 1 | Nesting depth (1 = leaf-only) |

## Common Failure Mode

**Symptom:** "no model configured" or subagent immediately fails.

**Root cause:** `delegation.model` / `delegation.provider` absent from config.

**Fix:** Add the `delegation.*` block above and restart the gateway.

## References

- `references/delegation-config.md` — session-specific config details, error transcripts, reproduction steps
