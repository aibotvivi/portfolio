# Vivien Chin — Portfolio

A single-page portfolio site for Vivien Chin, Senior Product Designer. The landing view
is a 90s desktop: a dithered desk, a working menu bar, ten icons, and windows you drag,
stack and close. Client Work and The Lab are Finder list views; every case study and side
project opens as its own window.

## Stack

Plain HTML + hand-written CSS + vanilla JS, all inline in one file. No build step, no
CDN, no framework, no npm dependencies. Everything lives in `index.html` (~7,000 lines).
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

Ten icons, and the desk opens with three windows already up: **Vivien Chin** (hero),
**Client Work** and **The Lab**.

| Icon | Window | Holds |
| --- | --- | --- |
| Vivien Chin | hero | Intro, portrait, NN/g training, past clients |
| Client Work | list | 4 case studies |
| The Lab | list | 11 side projects — 5 featured, 6 under "Also built"; blurred behind a password (`hello`) |
| Resume | — | Opens `assets/vivien-chin-resume.pdf` (rebuild with `scripts/make-resume-pdf.py`) |
| Pastime | photo cards | Travel with a pixel world map (rebuild its data with `scripts/build-travel-map.py`), photography, sound healing, aerial arts. The sound-healing card opens the Singing Bowls |
| Get in touch | — | Email, LinkedIn, résumé, currently exploring |
| Paint | canvas | A 90s Paint: tools, emoji stamps, mirror, import an image |
| Games | canvas | Seven games: The Journey, Catch the Sky, Deadline Crossing, Scope Snake, Minesweeper, Rhythm Deck, Solitaire |
| Screen Saver | canvas | Five savers with a live preview and a wait of 10s / 20s / 60s / off |
| Trash | file grid | Thirteen discarded files, each one openable. Tiles or list, remembered. **Empty Trash works** — and everything comes back five minutes later, apart from `.DS_Store`, which never leaves |

**Singing Bowls** (`#sound`) has no icon of its own: it opens from the Pastime card and
from Special ▸ Singing Bowls. Seven bowls, one per chakra, struck rather than looped —
four inharmonic partials each, detuned in pairs, synthesised in the browser. There is no
audio file anywhere in this site.

## Switching on, and off

The desk boots once per session — a grey screen, a smiling machine, the desk's
own icons loading as extensions, about a second and a quarter, any key skips it,
never under reduced motion (`sessionStorage` key `vc-booted`). Special ▸ **Shut
Down** shows the orange sentence on black; any key restarts. Special ▸
**Restart** replays the boot with a synthesised chime. A wrong address gets
`404.html`: white on blue, "the page has been thrown away", any key returns.

## The menu bar

Every title pulls down and everything under them does something a person could also
have done from an icon. **The logo** is the Apple menu: About This Desk, then the desk
accessories — Disk Drive (five floppies, one per section; insert one and its window mounts
with the slot animation, the bar tints, a `Drive A: ▸` crumb appears and a disk icon lands on
the desk; asking for a second disk raises "please insert the disk" with a Swap; eject closes
it; the last disk is remembered as `vc-disk`. Item counts and sizes are read from the real
windows. It is a second door, never the only one — the icons and menus keep working), Alarm Clock (with a stopwatch, and an alarm that rings the chime only while
the page is open and says so), Calculator, and Puzzle (the fifteen-puzzle, the portrait
cut into tiles, shuffled by legal moves so it is always solvable). **File** — résumé,
PDF, Print Résumé (a print stylesheet: monospace, tractor-feed holes, nothing else on
the page), contact, Close Window. **Edit** — copy email, copy link to this window, Paint.
**View** — dark mode, CRT (scanlines and a vignette, remembered as `vc-crt`), Clean up
the desk, gallery, travel map. **Special** — Empty Trash, Desktop Patterns (twelve 8×8
tiles drawn from bitmaps, remembered as `vc-pattern`), Singing Bowls, Screen Saver,
Games, Restart, Shut Down. Items grey out when they cannot fire, Escape closes a menu without touching the
window behind it, and the whole bar is hidden below 700px where the icons are the
interface. The brand mark is `assets/img/logo-chin-script.png` (RGBA, no background, so
one file works in both themes; `-lg` is the same mark at full size).

`about me.txt` still exists as a window (`#about`) but its icon is hidden, so it is
marked `data-unlisted` and generates no page — a window nobody can reach from the desk
should not be indexed either. The Gallery (18 photographs) opens from Pastime.
`photography.html` is a separate standalone page for the same photographs and links back
here.

## Pages

Almost every window also exists as a real page at the matching path — `#work/apex-ai` is served
at `/portfolio/work/apex-ai/` — with its own title, description and preview card, so a
case study can be found in a search or shared on its own. Windows that are running
programs rather than documents (Paint, Games, Screen Saver, Trash, Singing Bowls, the
travel map) get an address and a description that sends the reader back to the desk;
windows marked `data-unlisted` get no page at all. They are generated:

```bash
python3 scripts/build-pages.py   # 18 pages + sitemap.xml, from the windows themselves
```

Never edit a generated page by hand. Change the window in `index.html` and re-run.

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

## Changing the GitHub username

The Pages host is `<username>.github.io`, and that username is written into the canonical
link, four social card tags, the JSON-LD `url` and `image`, the sitemap line in
`robots.txt`, the `SITE` constant in `scripts/build-pages.py`, the Daily News link that
points at another repo on the same account, and three github.com source links in The Lab.

Rename the account on GitHub first, then run:

```bash
python3 scripts/rename-github-user.py aibotvivi NEWNAME --dry-run   # see the damage
python3 scripts/rename-github-user.py aibotvivi NEWNAME             # do it
```

It rewrites the sources, re-runs `build-pages.py` so every generated page and the sitemap
follow, then greps for anything it missed. Add `--remotes` and it also repoints the origin
URL of every clone under `$HOME` that still names the old account (26 of them). What it
cannot do is printed at the end: the account rename itself, renaming the root redirect repo
to match, the Analytics data-stream URL, a fresh Search Console property, the repo's own
homepage field, and the link on your LinkedIn profile.

**The old address stops working.** `aibotvivi.github.io` is derived from the username, so
once you no longer hold the name that host is not yours — there is nothing to redirect
from, and four other Pages sites on the account (`daily-news-live`, `spliteasy`,
`maria-site` and the root redirect) move with it. GitHub does redirect the `github.com`
repository paths, but that redirect lapses if anyone claims the freed username. Do this
before sharing the link widely, not after.

## Analytics

Google Tag Manager (container `GTM-5FTTLHDT`) is installed on both pages: the script
high in `<head>`, the `<noscript>` iframe immediately after `<body>`. The container is
empty until tags are configured in the GTM console, so on its own it collects nothing.

Google Analytics 4 is live alongside it. The tag is Google's standard snippet near the top of
`<head>` in **both** `index.html` and `photography.html`, with the Measurement ID written
out in the script URL and the `config` call — change it everywhere, or a page goes
uncounted. Delete both script tags to turn analytics off. Because each window is a page
here, an
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
