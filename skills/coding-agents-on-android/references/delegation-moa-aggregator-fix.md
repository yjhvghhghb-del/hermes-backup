# MoA Aggregator Provider Fix (2026-08-24)

## Problem
`delegate_task` failed with:
```
RuntimeError: No LLM provider configured for task=moa_aggregator provider=openrouter. Run: hermes setup
```

**Root cause:** Hermes uses MoA (Mixture of Agents) internally for delegation. The MoA aggregator has a hardcoded default of `openrouter`/`deepseek/deepseek-v4-pro`. When `openrouter` is not configured (no `OPENROUTER_API_KEY`), delegation fails with the above error — even when `delegation.model`/`delegation.provider` are set correctly.

## Fix

Add a `moa` section to `~/.hermes/config.yaml` to override the aggregator's provider/model:

```yaml
moa:
  aggregator:
    provider: minimax-cn
    model: MiniMax-M2.7

delegation:
  model: MiniMax-M2.7
  provider: minimax-cn
```

### Important: MoA config uses FLAT structure

The `moa` top-level key uses legacy flat config format — `moa.aggregator` is correct, **NOT** `moa.default.aggregator`. Setting `moa.default.aggregator` creates the wrong nested structure and the fix silently does nothing.

Use `hermes config set moa.aggregator.provider minimax-cn` and `hermes config set moa.aggregator.model MiniMax-M2.7`. The `hermes config` tool will emit a warning that these are "not recognized config keys" — this warning is spurious; the keys are valid custom keys and MoA reads them correctly.

## Verification

After config change, restart the gateway (must be from a **separate shell**, not from inside the gateway process):

```bash
cd ~ && hermes gateway run --replace
```

Then check logs:
```bash
tail -f ~/.hermes/logs/agent.log | grep -i "delegate\|moa\|aggregator"
```

## Config Propagation

- `delegation.model` / `delegation.provider` → controls what model subagents inherit
- `moa.aggregator.provider` / `moa.aggregator.model` → controls the MoA aggregator (used internally by delegation's MoA routing)
- Both are needed for a fully self-contained delegation setup
