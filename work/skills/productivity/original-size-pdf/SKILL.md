---
name: original-size-pdf
description: 把图片按原尺寸做成PDF，左右翻页显示，适合图片/艺术作品集。
trigger: 原尺寸PDF / 图片做成左右翻页PDF / 裸体图片PDF
---

# 原尺寸图片PDF技能

图片按原始尺寸放每页，PDF阅读器默认就是左右翻页模式。

## 核心命令

```python
python3 << 'PYEOF'
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from PIL import Image as PILImage
import os

img_dir = '/data/data/com.termux/files/home'
images = sorted([f for f in os.listdir(img_dir) if f.startswith('cover_img_') and f.endswith('.jpg')])

# A4竖向 or 横向，看图片尺寸决定
w, h = 29.7*cm, 21*cm  # A4横向

c = canvas.Canvas('/data/data/com.termux/files/home/screenshot_pages.pdf', pagesize=(w, h))

for i, img_name in enumerate(images):
    img_path = os.path.join(img_dir, img_name)
    pil_img = PILImage.open(img_path)
    orig_w, orig_h = pil_img.size
    
    # 300 DPI 转换成 cm（大多数屏幕截图是96 DPI，按原尺寸显示）
    # 原尺寸：直接用像素作为磅值（1 point = 1 pixel at 72 DPI）
    # 或者换算成厘米：1 inch = 2.54cm, 96 pixels/inch
    dpi = 96  # 屏幕截图默认DPI
    img_w_cm = orig_w / dpi * 2.54 * cm
    img_h_cm = orig_h / dpi * 2.54 * cm
    
    # 居中
    x = (w - img_w_cm) / 2
    y = (h - img_h_cm) / 2
    
    c.drawImage(img_path, x, y, width=img_w_cm, height=img_h_cm)
    c.showPage()

c.save()
print(f"PDF完成: {os.path.getsize('/data/data/com.termux/files/home/screenshot_pages.pdf')/1024/1024:.1f} MB, {len(images)}页")
PYEOF
```

### 发到Telegram
```bash
TG_TOKEN="8800919754:AAFdNkpAGSI6M5ahwd3_5g-SuZzusH7ybp4"
curl -s -F "document=@/data/data/com.termux/files/home/screenshot_pages.pdf" \
  "https://api.telegram.org/bot$TG_TOKEN/sendDocument" \
  -F "chat_id=877708648" \
  -F "caption=📄 原尺寸图片PDF，左右翻页~" 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print('ok' if d.get('ok') else d)"
```

## 关键参数
- **图片DPI**: `dpi = 96`（屏幕截图默认），原尺寸按96 DPI计算
- **页面尺寸**: A4横向 `29.7*cm x 21*cm`
- **居中**: 图片在页面居中显示
- **左右翻页**: PDF阅读器（如Acrobatreader）用「 facing pages 」模式就是左右翻
- **图片选择**: `f.startswith('cover_img_')` — 按实际文件名调整
- **chat_id**: 877708648（老公的Telegram ID）
