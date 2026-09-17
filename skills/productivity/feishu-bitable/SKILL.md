---
name: feishu-bitable
description: 操作飞书多维表格（Bitable）读写记录
tags: [feishu, bitable, 多维表格]
---

# 飞书多维表格（Bitable）操作

## 触发条件
老公需要在飞书多维表格里读写数据时使用。

## 脚本位置
`~/.hermes/scripts/feishu_bitable.py`

## 环境变量
```bash
FEISHU_APP_ID=cli_xxxxxxxx
FEISHU_APP_SECRET=xxxxxxxx
```
可用老公 Bot 的飞书应用（`cli_4c9d07126349124f942e382f7501b189`）或萌妹 Bot 的应用。

## 使用方法

**列出数据表：**
```bash
python3 ~/.hermes/scripts/feishu_bitable.py list <app_token>
```

**读取表内容：**
```bash
python3 ~/.hermes/scripts/feishu_bitable.py read <app_token> <table_id>
```

**插入记录：**
```bash
python3 ~/.hermes/scripts/feishu_bitable.py insert <app_token> <table_id> '<fields_json>'
# 示例
python3 ~/.hermes/scripts/feishu_bitable.py insert bascnxxxxx tblxxxxx '{"name": "测试", "age": 18}'
```

**更新记录：**
```bash
python3 ~/.hermes/scripts/feishu_bitable.py update <app_token> <table_id> <record_id> '<fields_json>'
```

**删除记录：**
```bash
python3 ~/.hermes/scripts/feishu_bitable.py delete <app_token> <table_id> <record_id>
```

## 注意事项
- `app_token` 是多维表格 URL 中的 `bascnxxxxx` 部分
- `table_id` 是数据表的 ID（不是名字），用 `list` 命令先查出来
- 字段值必须是 JSON 对象格式的字符串
- 需要先在飞书开放平台给应用开通 `bitable:app` 权限
