# 飞书群@无响应 — pairing 快速修复

## 症状
gateway.log 有多个 `connected to wss`（飞书连接正常），但群里@bot完全无反应。

## 根因
用户（如老公）的 open_id 不在 profile 的 `feishu-approved.json` 名单中。

## 快速检查
```bash
OU_MAIN="ou_2fcb5a59369405d74cf386b349aff96c"
grep "$OU_MAIN" ~/.hermes/profiles/licai/platforms/pairing/feishu-approved.json
grep "$OU_MAIN" ~/.hermes/profiles/wenyu/platforms/pairing/feishu-approved.json
```

## 修复步骤

1. 老公的 open_id：`ou_2fcb5a59369405d74cf386b349aff96c`

2. 用 Python（绕过 /tmp 写文件权限问题）写入 approved 名单：
```python
import json

for profile, existing in [("licai", ["ou_a023ae4173052b881d472190d32065e2"]),
                          ("wenyu", [])]:
    data = {k: {"user_name": "", "approved_at": 1786401750.089151}
            for k in existing}
    data["ou_2fcb5a59369405d74cf386b349aff96c"] = {"user_name": "", "approved_at": 1786401750.089151}
    path = f"/data/data/com.termux/files/home/.hermes/profiles/{profile}/platforms/pairing/feishu-approved.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
```

3. 重启 gateway：
```python
import os, subprocess
# 找到并 kill 旧 gateway 进程
r = subprocess.run("ps aux | grep 'hermes gateway' | grep -v grep | awk '{print $2}'",
                  shell=True, capture_output=True, text=True)
for pid in r.stdout.strip().split():
    os.kill(int(pid), 9)
# 重启（Terminal 后台模式）
terminal(background=True, command="cd /data/data/com.termux/files/home && hermes gateway run --replace")
```

4. 验证：等10秒后 `grep 'connected to wss' ~/.hermes/gateway.log` 应有多个不同时间戳的连接。

## 相关 open_id（备忘）
- 老公主号：`ou_2fcb5a59369405d74cf386b349aff96c`
- licai 旧用户：`ou_a023ae4173052b881d472190d32065e2`
- wenyu 旧用户：`ou_c696f8f4d082ba11770301e40ee40063`
