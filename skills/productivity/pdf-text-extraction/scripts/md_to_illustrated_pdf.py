#!/usr/bin/env python3
"""Generate illustrated PDF from markdown — Termux/Android version.
Embeds local JPEG images into PDF so Telegram can display them inline.

Usage:
    python3 scripts/md_to_illustrated_pdf.py input.md output.pdf

Dependencies:
    pip install reportlab pillow
    Chinese font: /system/etc/custom/fonts/FZFengYaSongS-GB-Regular.ttf
"""
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Image, Spacer,
                                 PageBreak, HRFlowable)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import re, os, sys

FONT_PATH = '/system/etc/custom/fonts/FZFengYaSongS-GB-Regular.ttf'

def make_styles():
    pdfmetrics.registerFont(TTFont('Chinese', FONT_PATH))
    return {
        'normal': ParagraphStyle('N', fontName='Chinese', fontSize=10, leading=14,
                                spaceAfter=4, alignment=TA_JUSTIFY),
        'h1':     ParagraphStyle('H1', fontName='Chinese', fontSize=16, leading=20,
                                spaceAfter=8, spaceBefore=14, alignment=TA_CENTER),
        'h2':     ParagraphStyle('H2', fontName='Chinese', fontSize=13, leading=17,
                                spaceAfter=6, spaceBefore=10),
        'h3':     ParagraphStyle('H3', fontName='Chinese', fontSize=11, leading=14,
                                spaceAfter=4, spaceBefore=8),
        'bold':   ParagraphStyle('B', fontName='Chinese', fontSize=11, leading=15,
                                spaceAfter=4),
    }

def parse_md_to_story(md_text, styles):
    story = []
    for line in md_text.split('\n'):
        ls = line.strip()
        if not ls or ls.startswith('[←') or '<!--' in ls:
            continue
        if ls == '---':
            story.append(HRFlowable(width='100%', thickness=0.5, color=colors.lightgrey))
            story.append(Spacer(1, 6))
        elif ls.startswith('# ') or (ls.startswith('#') and len(ls) < 80):
            story.append(Paragraph(re.sub(r'^#+\s*', '', ls), styles['h1']))
            story.append(Spacer(1, 6))
        elif ls.startswith('## '):
            story.append(Paragraph(ls[3:], styles['h2']))
            story.append(Spacer(1, 4))
        elif ls.startswith('### '):
            story.append(Paragraph(ls[4:], styles['h3']))
            story.append(Spacer(1, 3))
        elif '.jpg' in ls and ls.startswith('!['):
            m = re.search(r'\(([^)]+\.jpg)\)', ls)
            if m and os.path.exists(m.group(1)):
                p = m.group(1)
                try:
                    from PIL import Image as PI
                    pi = PI.open(p)
                    iw, ih = pi.size
                    pi.close()
                    aspect = ih / iw if iw else 1
                    max_h = 10 * cm
                    w = min(8 * cm, 13 * cm)
                    h = min(w * aspect, max_h)
                    if aspect > 1:
                        w, h = h / aspect, h
                except:
                    w, h = 7 * cm, 7 * cm
                story.append(Spacer(1, 4))
                story.append(Image(p, width=w, height=h, hAlign='CENTER'))
                story.append(Spacer(1, 4))
        elif ls.startswith('**') and ls.endswith('**'):
            story.append(Paragraph(ls.strip('* '), styles['bold']))
        elif len(ls) > 1:
            def bold_repl(m):
                return '<b>' + m.group(1) + '</b>'
            story.append(Paragraph(re.sub(r'\*\*([^*]+)\*\*', bold_repl, ls),
                                   styles['normal']))
    return story

def main():
    if len(sys.argv) < 3:
        print("Usage: md_to_illustrated_pdf.py input.md output.pdf")
        sys.exit(1)
    md_path, out_path = sys.argv[1], sys.argv[2]

    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    styles = make_styles()
    story = parse_md_to_story(md_text, styles)

    # Portrait-ish A5+ size good for mobile reading
    doc = SimpleDocTemplate(out_path,
                           pagesize=(17 * cm, 22 * cm),
                           leftMargin=1.5 * cm, rightMargin=1.5 * cm,
                           topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    doc.build(story)
    size_kb = os.path.getsize(out_path) / 1024
    print(f'Created: {out_path} ({size_kb:.0f} KB, {len(story)} elements)')

if __name__ == '__main__':
    main()
