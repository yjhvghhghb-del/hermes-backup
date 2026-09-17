# GitHub Push Protection — Secret Scanning Blocks

## What happens

GitHub Enterprise/GHAS scans every commit **at push time**, before it is accepted. On private repos the error looks like:

```
remote: error: GH013: Repository rule violations found for refs/heads/main.
remote:
remote: - GITHUB PUSH PROTECTION
remote:   — Push cannot contain secrets
remote:
remote:   —— Lark Application Secret ———
remote:        locations:
remote:          - commit: <SHA>
remote:            path: work/memories/MEMORY.md:18
remote:          - commit: <SHA>
remote:            path: work/skills/productivity/feishu-wiki-document-read/SKILL.md:23
```

## Why naive approaches fail

- `git commit --amend` alone does NOT help if the secret is still in the working tree / tar
- Amending AFTER the first push attempt still contains the secret in the new commit
- The secret must be removed from the **work tree** BEFORE the amended commit is created

## Correct recovery sequence (lived this session)

1. **Identify all files** containing real secrets — GitHub tells you the paths and line numbers
2. **Sanitize the work-tree files in-place** with `sed -i` replacements:
   ```bash
   sed -i 's/REAL_SECRET_HERE/<PAT_REDACTED>/g' work/memories/MEMORY.md
   sed -i 's/REAL_SECRET_HERE/<FEISHU_SECRET_1>/g' work/skills/.../SKILL.md
   ```
3. **Stage the sanitized files only**, then amend:
   ```bash
   git add work/memories/MEMORY.md work/skills/.../SKILL.md
   git commit --amend --no-edit   # keeps original date, only swaps content
   ```
4. **Push again** — the sanitized commit is clean

## Why `--amend` is the right move

Creating a new commit (instead of amending) would add a second "dirty" commit to the history before the clean one, and GitHub would still block on the first one. `--amend` replaces the dirty commit atomically.

## Secret patterns that trigger detection

| Pattern | Example | Placeholder to use |
|---------|---------|-------------------|
| GitHub PAT | `<PAT_REDACTED>lhbD4q16FJCpzlTVCCNF0NgeF1` | `<PAT_REDACTED>` |
| Feishu/Lark App Secret (32 char) | `exampleLarkSecret32CharsHereXYZ123` | `<FEISHU_SECRET_REDACTED>` |
| Any 30+ char alphanumeric token | `exampleToken30CharsLongHereXYZ123` | `<TOKEN_REDACTED>` |
| Truncated secret with `...` | `<PAT_REDACTED>` | Still detected — replace fully |

## Prevention: pre-commit hook

Add a `.git/hooks/pre-commit` that runs secret scanning before any commit:

```bash
#!/bin/bash
# Scan staged files for known secret patterns before commit
for file in $(git diff --cached --name-only); do
  if grep -E 'ghp_[A-Za-z0-9]{36}' "$file" 2>/dev/null; then
    echo "ERROR: GitHub PAT pattern detected in $file"
    exit 1
  fi
done
```
