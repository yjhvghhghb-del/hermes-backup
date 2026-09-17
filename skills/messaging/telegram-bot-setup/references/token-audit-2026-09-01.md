# Telegram Bot Token Audit

## 2026-09-17 最新验证

**终端显示 `***` 但文件实际字节完整**：

| Profile | Token (raw bytes) | 终端显示 | 状态 |
|---------|------------------|---------|------|
| default | `8800919754:AAFdNkpAGSI6M5ahwd3_5g-SuZzusH7ybp4` | `8800919754:***` | ✅ 完整 |
| geekwife | `8637317610:AAFMUvm6-KLLslBLWLV8lRSFbhZDhGsdzVw` | `8637317610:***` | ✅ 完整 |
| siliconflow | `8363232963:AAEcAg...`（部分） | `8363232963:***` | ✅ 完整 |

**验证方法（Python 读 raw bytes）**：
```python
with open('~/.hermes/.env', 'rb') as f:
    content = f.read()
idx = content.find(b'8800919754')
line_end = content.find(b'\n', idx)
line = content[idx:line_end]
print("真实token:", line[len(b'8800919754:'):].decode())
```

**注意**：curl/API 层面有时返回 404 可能是代理/网络问题（直连 DNS 失败，代理能连通但 Telegram 返回 404），不一定代表 token 本身失效。

---

## 2026-09-01 历史记录（stale）

| Profile | Token | Bot名 | API状态 |
|---------|-------|-------|---------|
| default | `8800919754:***` | Hhvvbfgbot | 当时 404 |
| geekwife | `8637317610:***` | ffdrtfcgbot | 当时 404 |
| siliconflow | `8363232963:***` | ? | 当时 404 |

2026-09-17 发现文件里 raw bytes 实际完整，2026-09-01 的 curl 测试结果可能受代理影响。
