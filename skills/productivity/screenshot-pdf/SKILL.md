---
name: screenshot-pdf
description: 把多张截图合并成PDF，图片铺满页面只留少量白边（横向A4）。
trigger: 截图转PDF / 把图片做成PDF
---

# 截图转PDF技能

## 核心命令

### 横向A4 PDF（14张截图示例）
```python
python3 << 'PYEOF'
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from PIL import Image as PILImage
import os

img_dir = '/data/data/com.termux/files/home'
images = sorted([f for f in os.listdir(img_dir) if f.startswith('cover_img_') and f.endswith('.jpg')])

w, h = 29.7*cm, 21*cm  # A4横向
margin = 0.3*cm  # 白边大小，可调（3mm效果不错）

c = canvas.Canvas('/data/data/com.termux/files/home/screenshot_pages.pdf', pagesize=(w, h))

for i, img_name in enumerate(images):
    img_path = os.path.join(img_dir, img_name)
    pil_img = PILImage.open(img_path)
    img_w, img_h = pil_img.size
    
    scale = min((w - 2*margin) / img_w, (h - 2*margin) / img_h)
    draw_w = img_w * scale
    draw_h = img_h * scale
    x = (w - draw_w) / 2
    y = (h - draw_h) / 2
    
    c.drawImage(img_path, x, y, width=draw_w, height=draw_h)
    c.showPage()

c.save()
print(f"PDF完成: {os.path.getsize('/data/data/com.termux/files/home/screenshot_pages.pdf')/1024/1024:.1f} MB")
PYEOF
```

### 发到Telegram
```bash
TG_TOKEN="8800919754:AAFdNkpAGSI6M5ahwd3_5g-SuZzusH7ybp4"
curl -s -F "document=@/data/data/com.termux/files/home/screenshot_pages.pdf" \
  "https://api.telegram.org/bot$TG_TOKEN/sendDocument" \
  -F "chat_id=877708648" \
  -F "caption=📄 PDF说明" 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print('ok' if d.get('ok') else d)"
```

## 关键参数
- **页面尺寸**: A4横向 `29.7*cm x 21*cm`
- **白边**: `margin = 0.3*cm` (3mm) 效果最好
- **图片选择**: `f.startswith('cover_img_') and f.endswith('.jpg')` — 按实际文件名调整glob pattern
- **输出路径**: `/data/data/com.termux/files/home/screenshot_pages.pdf`
- **chat_id**: 877708648（老公的Telegram ID）
