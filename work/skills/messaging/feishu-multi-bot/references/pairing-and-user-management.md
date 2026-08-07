# Feishu Pairing & User Management

## ⚠️ CRITICAL: Pairing Files Are Per-HERMES_HOME

The approved-user store is **profile-scoped**, not global. The file path is:
```
~/.hermes/profiles/<name>/platforms/pairing/feishu-approved.json
```
When a gateway runs with `HERMES_HOME=~/.hermes/profiles/libai`, it reads `~/.hermes/profiles/libai/platforms/pairing/feishu-approved.json` — **not** `~/.hermes/platforms/pairing/feishu-approved.json`.

Manually editing the wrong file has ZERO effect. Always verify the target gateway's HERMES_HOME before editing:
```bash
ps aux | grep 'hermes gateway' | grep -v grep
cat /proc/<pid>/environ | tr '\0' '\n' | grep HERMES_HOME
```

## Approving a Pending Pairing Code

```bash
hermes pairing approve feishu <CODE>
```

Pairing codes expire after a few minutes. If expired, the user must send another message to the bot to generate a fresh code.

## Manual Approval via JSON (When Code Expires)

The approved-user store is a JSON file. You can directly edit it to add users without a pairing code:

```
~/.hermes/platforms/pairing/feishu-approved.json
~/.hermes/profiles/<name>/platforms/pairing/feishu-approved.json
```

Format:
```json
{
  "ou_2fcb5a59369405d74cf386b349aff96c": {
    "user_name": "",
    "approved_at": 1785535998.02079
  },
  "ou_a023ae4173052b881d472190d32065e2": {
    "user_name": "",
    "approved_at": 1785535998.02079
  }
}
```

The `approved_at` value is Unix timestamp — any recent value works.

**Where to find a user's open_id**:
- From gateway logs: `grep "Unauthorized user.*ou_" ~/.hermes/logs/gateway.log`
- From the pairing ledger: the open_id appears in the "Unauthorized user" warning when an unapproved user sends a message

## List Approved Users

```bash
hermes pairing list
```

## Adding a User to Group Allowlist

For group access, the user's open_id must also be in `group_rules[group_id].allowlist` in config.yaml. Being in `feishu-approved.json` grants DM access; group access additionally requires the open_id be listed per-group.

```yaml
platforms:
  feishu:
    extra:
      allowed_group_users:
        - ou_2fcb5a59369405d74cf386b349aff96c
      group_rules:
        oc_group_id_here:
          policy: open  # or: allowlist
          allowlist:
            - ou_2fcb5a59369405d74cf386b349aff96c
```
