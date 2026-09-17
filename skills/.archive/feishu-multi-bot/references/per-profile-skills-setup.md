# Per-Profile Skills Setup

Profile skills are **isolated** — a skill installed in `~/.hermes/skills/` (the default/global skills dir) is NOT visible to named profile gateways. Each profile has its own `~/.hermes/profiles/<name>/skills/` directory.

**Symptom**: `hermes skills list --profile <name>` shows nothing (or fewer skills than `hermes skills list` in the default profile).

## Giving a Feishu Profile Access to a Skill

Copy the skill directory into the profile's skills folder:

```bash
mkdir -p ~/.hermes/profiles/<name>/skills/<skill-name>
cp ~/.hermes/skills/<skill-name>/SKILL.md ~/.hermes/profiles/<name>/skills/<skill-name>/
```

**Example — give cutegirl and licai access to knowledge-qa:**
```bash
mkdir -p ~/.hermes/profiles/cutegirl/skills/knowledge-qa
mkdir -p ~/.hermes/profiles/licai/skills/knowledge-qa
cp ~/.hermes/skills/knowledge-qa/SKILL.md ~/.hermes/profiles/cutegirl/skills/knowledge-qa/
cp ~/.hermes/skills/knowledge-qa/SKILL.md ~/.hermes/profiles/licai/skills/knowledge-qa/
```

Verify: `hermes skills list --profile cutegirl | grep knowledge` should show `knowledge-qa`.

**Then restart the gateway** for the skill to take effect:
```bash
pkill -f "hermes gateway.*<name>"
hermes gateway run --profile <name> &
```

## Why Not Symlinks?

Symlinks may work but are fragile on Android/Termux (symlink across Termux internal storage and shared storage can break). Copy is reliable.

## Which Skills to Copy Per Profile?

- **knowledge-qa** — any Feishu bot expected to answer tech/数码 questions should have this
- **feishu-bitable** — bots that need to read/write 飞书多维表格
- **feishu-wiki-document-read** — bots that need to read 飞书 wiki/docx links
- **note-taking** (obsidian) — bots that manage notes

Skills with external credentials (API keys, tokens) in their env vars: those credentials come from the profile's own `.env`, not the global one. Make sure the profile's `.env` has the required keys.
