#!/usr/bin/env python3
"""Give every window in index.html a real address of its own.

The desktop is one page whose windows are its pages, addressed by fragment:
#work/apex-ai. A fragment is not an address a search engine can list, and it is
not one analytics can tell apart either — so each window also gets a real page
at the matching path:

    #work/apex-ai   ->  /portfolio/work/apex-ai/
    #paint          ->  /portfolio/paint/
    #contact        ->  /portfolio/contact/

Each page carries that window's own title, description and preview card, the
same content, and a way back to the desktop. Nothing is written by hand: add a
window to index.html with a data-slug and re-run this, and its page appears with
the same structure.

    python3 scripts/build-pages.py

The window content is copied verbatim, and the stylesheet is lifted straight out
of index.html into assets/site.css, so the pages cannot drift from the desktop.
index.html itself keeps its inline styles and stays a single file.
"""
import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / 'index.html'
SITE = 'https://aibotvivi.github.io/portfolio/'

src = PAGE.read_text(encoding='utf-8')

# ---------------------------------------------------------------- stylesheet
style = re.search(r'<style>(.*?)</style>', src, re.S)
if not style:
    sys.exit('no <style> block in index.html')
(ROOT / 'assets').mkdir(exist_ok=True)
(ROOT / 'assets' / 'site.css').write_text(style.group(1).strip() + '\n', encoding='utf-8')

# the analytics tags, taken from the page so the two cannot drift apart
tags = re.findall(r'<!-- Google Tag Manager -->.*?<!-- End Google Tag Manager -->'
                  r'|<script async src="https://www\.googletagmanager\.com/gtag/js[^>]*></script>\s*<script>.*?</script>',
                  src, re.S)
if len(tags) != 2:
    sys.exit('expected the Tag Manager and gtag blocks in index.html, found %d' % len(tags))
gtm, gtag = tags
# the generated pages are ordinary pages: they want the automatic page view back
gtag = gtag.replace(", { send_page_view: false }", "")
gtag = re.sub(r'\n\s*/\* send_page_view is off.*?\*/', '', gtag, flags=re.S)
noscript = re.search(r'<!-- Google Tag Manager \(noscript\) -->.*?<!-- End Google Tag Manager \(noscript\) -->', src, re.S)
theme = re.search(r'<script>\n(/\* Theme is resolved before first paint.*?)</script>', src, re.S)
if not noscript or not theme:
    sys.exit('could not find the noscript iframe or the theme script')

# ---------------------------------------------------------------- windows
WINDOW = re.compile(r'<section class="win"[^>]*?data-win="([^"]+)"[^>]*?>(.*?)\n    </section>', re.S)
windows = {}
for m in WINDOW.finditer(src):
    tag = m.group(0)[:m.group(0).index('>') + 1]
    slug = re.search(r'data-slug="([^"]+)"', tag)
    label = re.search(r'aria-label="([^"]+)"', tag)
    body = re.search(r'<div class="win-body"[^>]*>(.*)\n      </div>', m.group(2), re.S)
    if not body:
        continue
    windows[m.group(1)] = {
        'slug': (slug.group(1) if slug else m.group(1)),
        'title': html.unescape(label.group(1)) if label else m.group(1),
        'body': body.group(1),
    }
windows.pop('hero', None)          # the hero window is the desk itself

by_id = {k: v['slug'] for k, v in windows.items()}


def text_of(markup):
    t = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', markup, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', html.unescape(t)).strip()


def summarise(body, title):
    for m in re.finditer(r'<p(?![^>]*class="eyebrow")[^>]*>(.*?)</p>', body, re.S):
        t = text_of(m.group(1))
        if len(t) > 40:
            return (t[:152].rsplit(' ', 1)[0] + '…') if len(t) > 155 else t
    return '%s — from the portfolio of Vivien Chin, Senior Product Designer in London.' % title


def rewrite(body, depth):
    """Point the window's own markup at real files from this page's depth."""
    up = '../' * depth
    body = re.sub(r'((?:src|href)=")(assets/)', lambda m: m.group(1) + up + m.group(2), body)
    body = re.sub(r'(href=")(photography\.html)', lambda m: m.group(1) + up + m.group(2), body)

    # a button that opens another window becomes a link to that window's page
    def as_link(m):
        target = by_id.get(m.group(2))
        if not target:
            return m.group(0)
        cls = re.search(r'class="([^"]*)"', m.group(1))
        return '<a %shref="%s%s/">%s</a>' % (
            'class="%s" ' % cls.group(1) if cls else '', up, target, m.group(3))
    body = re.sub(r'<button([^>]*?)data-open="([a-z-]+)"[^>]*>(.*?)</button>', as_link, body, flags=re.S)

    # the rest of the desktop's controls mean nothing on a page of plain text
    body = re.sub(r'<button[^>]*data-(?:close|back|theme)[^>]*>.*?</button>', '', body, flags=re.S)
    return body


# Two windows are named as desktop files, which reads as a filename in a search
# result rather than a page. The desktop keeps its labels; the pages get titles.
PAGE_TITLE = {'resume': 'Résumé', 'about': 'About'}


# Windows that are running programs, not documents. Their behaviour lives in
# index.html's script, so copying their markup here would publish dead buttons
# and a blank canvas. They get an address and a description, and send the reader
# to the desktop where the thing actually runs.
APPS = {
    'paint': 'A 90s Paint, rebuilt in the browser: brushes and an airbrush, emoji stamps, '
             'mirror drawing, a palette, and an image of your own to draw over.',
    'games': 'Seven small games. The Journey walks her career as a side-scrolling map of '
             'checkpoints; Catch the Sky is about the planets; and beside them sit Deadline '
             'Crossing, Scope Snake, Minesweeper, Rhythm Deck and Solitaire.',
    'screensaver': 'Five screen savers for the desktop — a starfield, Mystify, Pipes, '
                   'flying floppies and a scrolling marquee — with a live preview and a '
                   'wait of ten seconds, twenty, sixty, or off.',
    'travel-map': 'A pixel world map of everywhere she has been — thirty-one places, pinned '
                  'or shaded country by country, against the 195 countries in the world.',
}


def app_body(slug, title, up):
    return (
        '    <p class="eyebrow">On the desktop</p>\n'
        '    <h2>%s</h2>\n'
        '    <p class="lede">%s</p>\n'
        '    <div class="doc-links"><a class="btn btn-primary" href="%s#%s">Open %s →</a></div>\n'
        % (html.escape(title), html.escape(APPS[slug]), up, slug, html.escape(title))
    )


# The sign-up form is part of the Lab window's markup, so it lands on that
# window's page too — but a page carries no script, and a form with no handler
# submits natively and reloads. Lift the handler out of index.html for the pages
# that need it, so there is still only one copy of the logic.
def signup_script():
    """Just the sign-up. The end anchor used to be the next IIFE in the file,
    which quietly swallowed every game and the screen saver the moment they were
    written above it — 79 KB of dead code on a page with none of their markup.
    It ends where its own IIFE ends now."""
    marker = '  /* ------------------------------ lab sign-up ---'
    if marker not in src:
        sys.exit('could not find the sign-up block in index.html')
    start = src.index(marker)
    close = src.index('\n  }());', start)
    if close < 0:
        sys.exit('the sign-up IIFE has no closing brace where one was expected')
    body = src[start:close + len('\n  }());')]
    fn = re.search(r'  function track\(name, params\) \{.*?\n  \}\n', src, re.S)
    if not fn:
        sys.exit('could not find track() to carry over with the sign-up')
    return '<script>\n(function () {\n' + fn.group(0) + '\n' + body + '\n}());\n</script>'


PAGE_CSS = """
  body.page { background: var(--page); color: var(--ink); }
  .page-bar {
    position: sticky; top: 0; z-index: 20; display: flex; align-items: center; gap: 14px;
    padding: 0 16px; height: var(--menubar-h); border-bottom: 2px solid var(--ink);
    background: var(--surface-2);
    font-family: var(--font-chrome); font-size: 10px; letter-spacing: .1em; text-transform: uppercase;
  }
  .page-bar a { color: var(--ink); text-decoration: none; }
  .page-bar a:hover { text-decoration: underline; }
  .page-bar .sep { margin-left: auto; color: var(--body); }
  .page-wrap { max-width: 760px; margin: 0 auto; padding: 0 0 64px; }
  .page-wrap > .win-body { overflow: visible; padding: 34px 24px 8px; }
  .page-foot {
    max-width: 760px; margin: 0 auto; padding: 22px 24px 60px;
    border-top: 1px solid var(--hairline);
    font-family: var(--font-chrome); font-size: 10px; letter-spacing: .06em; color: var(--body);
  }
  .page-foot a { color: var(--ink); }
"""

TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{gtm}
<title>{title} — Vivien Chin</title>
<meta name="description" content="{desc}">
<meta name="author" content="Vivien Chin">
<link rel="canonical" href="{url}">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="{up}assets/img/favicon.png">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Vivien Chin">
<meta property="og:title" content="{title} — Vivien Chin">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://aibotvivi.github.io/portfolio/assets/img/og-card.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title} — Vivien Chin">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="https://aibotvivi.github.io/portfolio/assets/img/og-card.jpg">
{gtag}
<script>
{theme}</script>
<link rel="stylesheet" href="{up}assets/site.css">
<style>{page_css}</style>
</head>
<body class="page">
{noscript}
<header class="page-bar">
  <a href="{up}">← Vivien Chin</a>
  <span class="sep">{title}</span>
</header>
<main class="page-wrap">
  <div class="win-body">
{body}
  </div>
</main>
{signup}<footer class="page-foot">
  This page is also a window on the desktop —
  <a href="{up}#{slug}">open {title} there →</a>
</footer>
</body>
</html>
"""

written = []
for wid, w in sorted(windows.items(), key=lambda kv: kv[1]['slug']):
    slug = w['slug']
    depth = slug.count('/') + 1
    out = ROOT.joinpath(*slug.split('/')) / 'index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    up = '../' * depth
    title = PAGE_TITLE.get(slug, w['title'])
    body = app_body(slug, w['title'], up) if slug in APPS else rewrite(w['body'], depth)
    desc = APPS[slug] if slug in APPS else summarise(w['body'], w['title'])
    out.write_text(TEMPLATE.format(
        gtm=gtm, gtag=gtag, noscript=noscript.group(0), theme=theme.group(1),
        title=html.escape(title), desc=html.escape(desc, quote=True),
        url=SITE + slug + '/', up=up, slug=slug,
        page_css=PAGE_CSS, body=body,
        signup=signup_script() if 'data-signup' in body else '',
    ), encoding='utf-8')
    written.append((slug, len(text_of(w['body']).split())))

# ---------------------------------------------------------------- sitemap
urls = [(SITE, '1.0'), (SITE + 'photography.html', '0.4')]
urls += [(SITE + s + '/', '0.3' if s in APPS else '0.7') for s, _ in written]
(ROOT / 'sitemap.xml').write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + ''.join('  <url><loc>%s</loc><priority>%s</priority></url>\n' % u for u in urls)
    + '</urlset>\n', encoding='utf-8')

print('%d pages, %d urls in the sitemap' % (len(written), len(urls)))
for slug, words in written:
    print('  /%s/%s%d words' % (slug, ' ' * max(1, 26 - len(slug)), words))
