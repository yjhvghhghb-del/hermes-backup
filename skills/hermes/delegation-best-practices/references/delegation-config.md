# Delegation Config — Session Notes

## Error Encountered (2026-08-02)

**Symptom reported:** "写代码Agent没模型配的" (coding agent has no model configured)

**Root cause:** `config.yaml` had no `delegation.*` block. The `delegation` toolset was enabled in `platform_toolsets` and `known_builtin_toolsets`, but no `delegation.model` / `delegation.provider` was specified anywhere. Without this block, subagents have no model to run and fail immediately.

**Affected config:** `~/.hermes/config.yaml` (default profile)

## Fix Applied

Added to `~/.hermes/config.yaml`:

```yaml
delegation:
  model: MiniMax-M2.7
  provider: minimax-cn
```

The values match the main `model.default` and `model.provider` already configured in the same file.

## Verification

After adding, restart the gateway:
```bash
cd ~ && hermes gateway run --replace
```

Subagent model can be overridden per-call via `delegate_task(..., model="...", provider="...")`.
