# Vivien Chin — Portfolio

A single-page portfolio site for Vivien Chin, Senior Product Designer. The landing view
is a 90s desktop: a dithered desk, a menu bar, six icons, and windows you drag, stack
and close. Client Work and The Lab are Finder list views; every case study and side
project opens as its own window.

## Stack

Plain HTML + hand-written CSS + vanilla JS, all inline in one file. No build step, no
CDN, no framework, no npm dependencies. Everything lives in `index.html` (~2,080 lines).
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

Six icons, and the desk opens with three windows already up: **Vivien Chin** (hero),
**Client Work** and **The Lab**.

| Icon | Window | Holds |
| --- | --- | --- |
| Vivien Chin | hero | Intro, NN/g training, past clients |
| Client Work | list | 4 case studies |
| The Lab | list | 11 side projects — 5 featured, 6 under "Also built" |
| about me.txt | note | Bio, pull quote, portrait, client lists |
| Beyond work | list | Volunteering, sound healing, photography, aerial arts |
| Get in touch | — | Email, LinkedIn, résumé, currently exploring |

The Gallery (18 photographs) opens from Beyond work, item 03. `photography.html` is a
separate standalone page for the same photographs and links back here.

## Deep links

The URL scheme from the previous scrolling version still resolves, so old links keep
working: `#work`, `#about`, `#lab`, `#contact`, `#gallery`, `#beyond`, `#resume`, and
per-item slugs like `#work/in-car-payments` and `#lab/spliteasy`. Opening a case-study
link cold also opens the list window behind it.

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
