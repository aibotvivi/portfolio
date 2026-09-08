# Vivien Chin — Portfolio

A single-page portfolio site for Vivien Chin, Senior Product Designer. The landing view
is a 90s desktop: a dithered desk, a menu bar, eight icons, and windows you drag, stack
and close. Client Work and The Lab are Finder list views; every case study and side
project opens as its own window.

## Stack

Plain HTML + hand-written CSS + vanilla JS, all inline in one file. No build step, no
CDN, no framework, no npm dependencies. Everything lives in `index.html` (~4,300 lines).
Fonts and images are self-hosted under `assets/`.

## Running it

Either works identically:

```bash
open index.html
```

or

```bash
python3 -m http.server 8090
# then open http://localhost:8090/
```

## What is on the desk

Eight icons, and the desk opens with three windows already up: **Vivien Chin** (hero),
**Client Work** and **The Lab**.

| Icon | Window | Holds |
| --- | --- | --- |
| Vivien Chin | hero | Intro, portrait, NN/g training, past clients |
| Client Work | list | 4 case studies |
| The Lab | list | 11 side projects — 5 featured, 6 under "Also built"; blurred behind a password (`hello`) |
| Resume | — | Opens `assets/vivien-chin-resume.pdf` (rebuild with `scripts/make-resume-pdf.py`) |
| Pastime | photo cards | Aerial arts, sound healing, photography and travel |
| Paint | canvas | A 90s Paint: tools, emoji stamps, mirror, import an image |
| Games | canvas | The Journey (her career as checkpoints) and Catch the Sky (planets) |
| Get in touch | — | Email, LinkedIn, résumé, currently exploring |

`about me.txt` still exists as a window (`#about`) but its icon is hidden for now. The
Gallery (18 photographs) opens from Pastime. `photography.html` is a separate standalone
page for the same photographs and links back here.

## Deep links

The URL scheme from the previous scrolling version still resolves, so old links keep
working: `#work`, `#about`, `#lab`, `#contact`, `#gallery`, `#beyond`, `#resume`, and
per-item slugs like `#work/in-car-payments` and `#lab/spliteasy`. Opening a case-study
link cold also opens the list window behind it. Opening a window pushes a history entry,
so the browser's Back button closes it rather than leaving the site.

## Search and sharing

`<head>` carries the title, description, canonical URL, Open Graph / Twitter tags and a
JSON-LD `Person` block; `assets/img/og-card.jpg` is the link preview. `robots.txt` and
`sitemap.xml` are at the root. Getting indexed still needs the URL submitted in Google
Search Console and linked from LinkedIn.

## Analytics

Google Analytics 4 is live. The Measurement ID sits in `window.GA_ID` near the top of
`<head>` in **both** `index.html` and `photography.html` — change it in both, or one page
goes uncounted. Blank it back to `G-XXXXXXXXXX` to turn analytics off entirely: nothing
loads and no cookie is set. Because each window is a page here, an
opening is reported as its own `page_view` (`#work/in-car-payments` and the like), so the
report shows which case studies people actually read.

Note that analytics cookies require consent under UK PECR and GDPR, and the site has no
consent banner yet.

## Local addresses in The Lab

Seven Lab write-ups mention an address like `localhost:8787` for an app that only runs
on the author's machine. **These ship as plain text, not links** — a localhost address
is not something a visitor can follow.

When the page is itself served from somewhere that *can* reach those ports — the
author's machine, the LAN, the tailnet, or `file://` — `localAddresses()` upgrades each
one into a real link, pointed at whatever host the page was loaded from rather than at
the literal word `localhost`. So the links work from a phone over Tailscale, and stay
inert on a public host such as GitHub Pages. The page never health-checks those
servers, so a link that does not load simply means that app is not running.

## Editing content

- **Design tokens** (colour, type, the desk, accents) — the `:root { ... }` block at the
  top of the `<style>` element, with dark values in `:root[data-theme="dark"]`.
- **Copy and structure** — each window is a `<section class="win" data-win="id">` inside
  `.desk-inner`. Adding one means adding the section plus a `[data-open="id"]` control.
- **Window behaviour** — the single `<script>` block at the end of the file.

There is no build step: edit `index.html` directly and refresh the browser.
