#!/usr/bin/env python3
"""Build assets/vivien-chin-resume.pdf from the résumé window in index.html.

The PDF reuses the page's own markup so the two cannot drift apart; only the
stylesheet differs. Re-run this after editing the résumé window.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
src = (ROOT / 'index.html').read_text(encoding='utf-8')

win = re.search(r'<section class="win"[^>]*\bdata-win="resume"[^>]*>.*?</section>', src, re.S)
assert win, 'résumé window not found'
body = re.search(r'<div class="win-body">(.*?)\n      </div>', win.group(0), re.S).group(1)

# the eyebrow and the download button belong to the page, not to the document
body = re.sub(r'\s*<p class="eyebrow">Résumé</p>', '', body)
body = re.sub(r'\s*<div class="doc-links">.*?</div>', '', body, flags=re.S)

# the contact block reads better as one line on paper than as a boxed grid
meta = re.search(r'<dl class="doc-meta">(.*?)</dl>', body, re.S)
pairs = re.findall(r'<dd>(.*?)</dd>', meta.group(1), re.S)
pairs = [re.sub(r'<[^>]+>', '', p).strip() for p in pairs]
body = body.replace(meta.group(0), '<p class="contact">' + ' &middot; '.join(pairs) + '</p>')

CSS = """
@page { size: A4; margin: 12mm 14mm 10mm; }
@font-face { font-family:'Spectral'; font-style:normal; font-weight:300; src:url('assets/fonts/spectral-300.woff2') format('woff2'); }
@font-face { font-family:'Spectral'; font-style:normal; font-weight:400; src:url('assets/fonts/spectral-400.woff2') format('woff2'); }
@font-face { font-family:'Satoshi'; font-style:normal; font-weight:400; src:url('assets/fonts/satoshi-400.woff2') format('woff2'); }
@font-face { font-family:'Satoshi'; font-style:normal; font-weight:500; src:url('assets/fonts/satoshi-500.woff2') format('woff2'); }
@font-face { font-family:'Satoshi'; font-style:normal; font-weight:700; src:url('assets/fonts/satoshi-700.woff2') format('woff2'); }

* { box-sizing: border-box; }
body {
  margin: 0; color: #1F1F1F; background: #fff;
  font-family: 'Satoshi', -apple-system, sans-serif;
  font-size: 9pt; line-height: 1.4; -webkit-print-color-adjust: exact;
}
h2 {
  margin: 0 0 2pt; font-family: 'Spectral', Georgia, serif; font-weight: 300;
  font-size: 22pt; line-height: 1.05; letter-spacing: -.01em;
}
.doc-client { margin: 0 0 2pt; font-size: 9.8pt; color: #444; }
.contact { margin: 0 0 10pt; font-size: 8.4pt; color: #5A5A5A; }
.contact a, a { color: #1F1F1F; text-decoration: none; }
h3 {
  margin: 10pt 0 5pt; padding-bottom: 2.5pt; border-bottom: .8pt solid #C9C5B9;
  font-size: 8.4pt; font-weight: 700; letter-spacing: .12em; text-transform: uppercase;
}
p { margin: 0 0 5pt; }
.doc-sub { margin: 7.5pt 0 1pt; font-weight: 700; font-size: 9.8pt; }
h3 + .doc-sub { margin-top: 2pt; }
.muted { margin: 0 0 4pt; font-size: 8.8pt; color: #5A5A5A; }
.doc-role { margin: 4.5pt 0 0; padding-left: 8pt; border-left: 1.2pt solid #DBD7CA; }
.doc-role-title { margin: 0 0 1pt; font-weight: 700; font-size: 9.2pt; }
.doc-role .muted { margin: 0 0 3pt; }
.doc-role .doc-list { margin-bottom: 0; }
.doc-list { margin: 0 0 5pt; padding-left: 11pt; }
.doc-list li { margin-bottom: 1.8pt; }
li, p, .doc-role, ul { break-inside: avoid; }
h3, .doc-sub, .doc-role-title { break-after: avoid; }
"""

html = ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
        '<title>Vivien Chin — Résumé</title><style>' + CSS + '</style></head><body>'
        + body + '</body></html>')

out_html = ROOT / '.resume-print.html'
out_html.write_text(html, encoding='utf-8')

pdf = ROOT / 'assets' / 'vivien-chin-resume.pdf'
chrome = next((c for c in ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                            shutil.which('google-chrome'), shutil.which('chromium')] if c and Path(c).exists()), None)
if not chrome:
    sys.exit('no Chrome/Chromium found to print the PDF')
res = subprocess.run([chrome, '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
                      '--virtual-time-budget=4000',
                      '--print-to-pdf=' + str(pdf), out_html.as_uri()],
                     capture_output=True, text=True, timeout=120)
out_html.unlink()
if not pdf.exists():
    sys.exit('chrome failed: ' + res.stderr[-600:])
print('wrote', pdf, pdf.stat().st_size // 1024, 'KB')
