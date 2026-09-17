---
name: chinese-pdf
description: "Chinese PDF generation with reportlab and system CJK fonts."
version: 1.0.0
platforms: [android, linux]
---

# Chinese PDF Generation (Android/Termux)

## Trigger
User wants a Chinese-language PDF, needs to combine images into a PDF, or wants a document sent via Telegram.

## CJK Font Registration

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
FONT = '/system/etc/custom/fonts/FZFengYaSongS-GB-Regular.ttf'
pdfmetrics.registerFont(TTFont('Chinese', FONT))
```

Font paths on Android: `/system/etc/custom/fonts/FZFengYaSongS-GB-Regular.ttf`, `/system/etc/custom/fonts/FZKaiTi-GB-Regular.ttf`.

## PDF Generation

```python
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.units import cm
import re, os

normal = ParagraphStyle('N', fontName='Chinese', fontSize=10, leading=14, spaceAfter=4)
h1 = ParagraphStyle('H1', fontName='Chinese', fontSize=16, leading=20, spaceAfter=8)

def md_to_story(md_text, img_dir):
    story = []
    for line in md_text.split('\n'):
        ls = line.strip()
        if not ls or ls.startswith('[←') or '<!--' in ls:
            continue
        if ls.startswith('# '):
            story.append(Paragraph(re.sub(r'^#+\s*', '', ls), h1))
        elif ls.startswith('## '):
            story.append(Paragraph(ls[3:], h2))
        elif '.jpg' in ls and ls.startswith('!['):
            m = re.search(r'\(([^)]+\.jpg)\)', ls)
            if m and os.path.exists(m.group(1)):
                p = m.group(1)
                from PIL import Image as PI
                pi = PI.open(p)
                iw, ih = pi.size
                pi.close()
                aspect = ih / iw if iw else 1
                w = min(8*cm, 13*cm)
                h = min(w * aspect, 10*cm)
                story.append(Spacer(1, 4))
                story.append(Image(p, width=w, height=h, hAlign='CENTER'))
                story.append(Spacer(1, 4))
        elif len(ls) > 1:
            story.append(Paragraph(re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', ls), normal))
    return story

doc = SimpleDocTemplate(out, pagesize=(17*cm, 22*cm),
                        leftMargin=1.5*cm, rightMargin=1.5*cm,
                        topMargin=1.5*cm, bottomMargin=1.5*cm)
doc.build(md_to_story(open('doc.md').read(), '/path/to/images'))
```

## Screenshots to PDF (Legacy — Small Images with Margins)

> ⚠️ **Wrong approach for Telegram**. Images appear tiny. Use the "Multi-Page PDF" section above instead for full-screen swipeable output.

```python
# DEPRECATED — only use for thumbnails or proof-of-concept
story = []
for fname in sorted(os.listdir(img_dir)):
    if not fname.endswith('.jpg'): continue
    path = os.path.join(img_dir, fname)
    ...
    story.append(Spacer(1, 0.5*cm))
    story.append(Image(path, width=img_w, height=img_h, hAlign='CENTER'))
    story.append(Spacer(1, 0.5*cm))
```

## Telegram Delivery

```bash
curl -s -F "document=@output.pdf" \
  "https://api.telegram.org/bot$TG_TOKEN/sendDocument" \
  -F "chat_id=<id>" -F "caption=Description"
```

## Screenshots to Multi-Page PDF (One Per Page, Swipeable)

For Telegram/phone viewing — each screenshot becomes one full-page PDF:

```python
from reportlab.platypus import SimpleDocTemplate, Image as RLImage
from reportlab.lib.units import cm
from PIL import Image as PILImage
import os

img_dir = '/path/to/screenshots'
out_path = '/path/to/output.pdf'

imgs = ['shot1.jpg', 'shot2.jpg', ...]

# LANDSCAPE A4 so wide screenshots fill the screen for left/right swipe
PAGE_W = 29.7 * cm   # landscape width
PAGE_H = 21 * cm     # landscape height

story = []
for fname in imgs:
    path = os.path.join(img_dir, fname)
    pi = PILImage.open(path)
    w, h = pi.size
    pi.close()
    aspect = h / w
    img_w = float(PAGE_W)
    img_h = img_w * aspect
    if img_h > float(PAGE_H):
        img_h = float(PAGE_H)
        img_w = img_h / aspect
    story.append(RLImage(path, width=img_w, height=img_h, hAlign='CENTER'))

doc = SimpleDocTemplate(out_path,
    pagesize=(float(PAGE_W), float(PAGE_H)),
    leftMargin=0.0, rightMargin=0.0,
    topMargin=0.0, bottomMargin=0.0)
doc.build(story)
```

**Key decision**: If source screenshots are landscape (1280×576 = 2.22:1), use landscape A4 pages so images fill the screen. If portrait, use portrait A4.

## Telegram Delivery

```bash
curl -s -F "document=@output.pdf" \
  "https://api.telegram.org/bot$TG_TOKEN/sendDocument" \
  -F "chat_id=<id>" -F "caption=Description"
```

## Pitfalls

1. **CJK renders as blank squares**: font file lacks glyphs — Try another system font path.
2. **Image aspect wrong**: always compute `aspect = ih / iw` before sizing; guard `if iw else 1`.
3. **Python lstrip syntax error**: `lstrip('# ")` is invalid — use `lstrip('# \\u201c')` or string splitting.
4. **Telegram broken image links**: embed images in PDF directly instead of sending markdown with local paths.
5. **`vAlign='MIDDLE'` rejected**: ReportLab `Image` only supports `hAlign`, not `vAlign`. Remove it.
6. **PDF says "0 pages" but story has items**: usually means `doc.build(story)` silently failed — check with pypdf: `len(pypdf.PdfReader(path).pages)`.
7. **Landscape vs portrait**: screenshot PDFs for phone viewing should match source aspect ratio. Wide screenshots → landscape A4 pages for correct left/right swipe. Portrait screenshots → portrait A4.
8. **`/tmp` permission denied on Android**: use `/data/data/com.termux/files/home/` for temporary rotated images instead of `/tmp`.
