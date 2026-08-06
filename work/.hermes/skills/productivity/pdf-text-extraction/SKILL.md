---
name: pdf-text-extraction
description: Extract PDF text & images when pymupdf unavailable.
---

# PDF Text & Image Extraction (Termux/Android)

Handles PDFs where `pymupdf` cannot be installed (Termux — SWIG unavailable via pip).

## Install
```
pip install pdfminer.six pypdf pillow
```

## Text: pdfminer.six

```python
from pdfminer.high_level import extract_text
text = extract_text('document.pdf')
```

## Images: pypdf XObject + raw byte search for inline JPEGs

Standard libraries miss inline image streams in illustrated PDFs (occult books, etc.).

### Raw byte search

```python
import re, os

with open('document.pdf', 'rb') as f:
    data = f.read()

# JPEG: SOI=0xFFD8, EOI=0xFFD9; stream boundary is CRLF
pattern = b'stream\r\n\xFF\xD8'
for i, m in enumerate(re.finditer(pattern, data)):
    start = m.start() + len(b'stream\r\n')
    end = data.find(b'\xFF\xD9', start)
    if end > start:
        with open(f'output/img_{i:03d}.jpg', 'wb') as f:
            f.write(data[start:end+2])
```

### Map images to page numbers via file size comparison

```python
from pypdf import PdfReader
import os

img_dir = 'output_images'
our = {f: os.path.getsize(os.path.join(img_dir, f))
       for f in os.listdir(img_dir) if f.endswith('.jpg')}

size_map = {}
for pg in range(len(PdfReader('doc.pdf').pages)):
    page = PdfReader('doc.pdf').pages[pg]
    for name, obj in page.get('/Resources', {}).get('/XObject', {}).items():
        if obj.get('/Subtype') == '/Image' and obj.get('/Filter') == '/DCTDecode':
            try:
                sz = len(obj.get_data())
                size_map.setdefault(sz, []).append((pg+1, name))
            except: pass

page_to_file = {}
for fname, fsize in our.items():
    matches = size_map.get(fsize, [])
    if len(matches) == 1:
        page_to_file[matches[0][0]] = fname
```

## MiniMax API via proxy

Translation endpoint: `https://api.mytokk.com/v1/chat/completions`
Model: `claude-haiku-4-5-20251001` (confirmed working; key: `ANTHROPIC_API_KEY` env)
Proxy: `http://172.19.0.1:7890` (confirmed accessible)

```python
import httpx
transport = httpx.HTTPTransport(proxy='http://172.19.0.1:7890')
with httpx.Client(transport=transport, timeout=60.0) as client:
    resp = client.post('https://api.mytokk.com/v1/chat/completions',
        json={'model': 'claude-haiku-4-5-20251001', 'max_tokens': 4000,
              'messages': [{'role': 'user', 'content': f'Translate to Chinese:\n{text}'}]},
        headers={'Authorization': f'Bearer {API_KEY}'})
```

## Notes

- pymupdf always fails on Termux (SWIG unavailable) — do not retry
- Stream boundary in modern PDFs: `stream\r\n` (CRLF), not `stream\n`
- File size matching is the only way to map extracted images to page numbers when LTImage returns nothing
- httpx.Client with HTTPTransport(proxy=...) is the correct API call pattern

## Generate PDF with Embedded Images (reportlab)

When Markdown images are local paths, Telegram can't render them. Convert to PDF with embedded images.

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import re, os

# Find Chinese font on Android/Termux
font_path = '/system/etc/custom/fonts/FZFengYaSongS-GB-Regular.ttf'
pdfmetrics.registerFont(TTFont('Chinese', font_path))

styles
normal = ParagraphStyle('N', fontName='Chinese', fontSize=10, leading=14, spaceAfter=4, alignment=TA_JUSTIFY)
h1 = ParagraphStyle('H1', fontName='Chinese', fontSize=16, leading=20, spaceAfter=8, spaceBefore=14, alignment=TA_CENTER)
bold = ParagraphStyle('B', fontName='Chinese', fontSize=11, leading=15, spaceAfter=4)

story = []
for line in md_text.split('\n'):
    ls = line.strip()
    if not ls or ls.startswith('[←') or '<!--' in ls: continue
    if ls == '---': story.append(HRFlowable(...))
    elif ls.startswith('# '): story.append(Paragraph(re.sub(r'^#+\s*', '', ls), h1))
    elif ls.startswith('## '): story.append(Paragraph(ls[3:], h2))
    elif '.jpg' in ls and ls.startswith('!['):
        m = re.search(r'\(([^)]+\.jpg)\)', ls)
        if m and os.path.exists(m.group(1)):
            # Embed with proper aspect ratio
            story.append(Image(m.group(1), width=7*cm, height=7*cm, hAlign='CENTER'))
    elif ls.startswith('**') and ls.endswith('**'):
        story.append(Paragraph(ls.strip('* '), bold))
    elif len(ls) > 1:
        story.append(Paragraph(re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', ls), normal))

doc = SimpleDocTemplate(out_path, pagesize=(17*cm, 22*cm),
                         leftMargin=1.5*cm, rightMargin=1.5*cm,
                         topMargin=1.5*cm, bottomMargin=1.5*cm)
doc.build(story)
```
