# 代理自動發現日誌（2026.8.1）

## Cron Job: Proxy Auto-Discovery
- job_id: `57a86162ad9f`
- 每 5 分鐘掃描一次

## 掃描結果（2026.08.01 06:11 UTC）
```
[AutoScan] Scanning 192.168.110.0/24 (256 hosts) for proxy ports...
[AutoScan] Found 0 hosts with open ports: {}
[AutoScan] Scanning 10.1.252.0/24 (256 hosts) for proxy ports...
[AutoScan] Found 1 hosts with open ports: {'10.1.252.196': [7890, 7891]}
[AutoScan] Testing 8 candidates...
[AutoScan]   10.1.252.196:7890: ❌ code=0 latency=8073.8ms
[AutoScan]   10.1.252.196:7891: ✅ code=200 latency=688.7ms
[AutoScan]   192.168.110.40:7891: ❌ code=0 latency=8064.1ms
[AutoScan]   192.168.110.40:7890: ❌ code=0 latency=8066.1ms
[AutoScan]   192.168.110.225:7891: ❌ code=0 latency=8066.1ms
[AutoScan]   192.168.110.225:7890: ❌ code=0 latency=8072.3ms
[AutoScan]   172.19.0.1:7891: ✅ code=200 latency=842.1ms
[AutoScan]   172.19.0.1:7890: ❌ code=0 latency=8075.2ms
[AutoScan] Best proxy: 10.1.252.196:7891
[AutoScan] Alive: ['10.1.252.196:7891', '172.19.0.1:7891']
```

## 結論
- `192.168.110.40` 段全部不通（code=0 表示 SOCKS 握手失敗）
- `10.1.252.196:7891` 最穩（688ms），但今天稍後已恢復
- `172.19.0.1:7891` 可用（842ms），備用
- 老公稍後確認 `192.168.110.40` 已恢復，目前腳本優先試 192.168.110.40

## 腳本代理順序（已更新）
1. `192.168.110.40:7891` ← 優先
2. `192.168.110.40:7890`
3. `172.19.0.1:7891`
4. `172.19.0.1:7890`
5. `10.1.252.196:7891`
6. `10.1.252.196:7890`
7. `192.168.110.225:7891`
8. `192.168.110.225:7890`
