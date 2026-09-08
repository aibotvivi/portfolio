# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-page portfolio site for Vivien Chin, Senior Product Designer. The landing view
is a 90s desktop rather than a scrolling page: a dithered desk, a menu bar, nine icons
(one hidden), and windows that drag, stack and close. Client Work and The Lab are Finder
list views, each case study or side project opens as its own window, and Paint and Games
are small toys of their own.

It reproduces the content of her Framer site (Work, About Me) and adds The Lab — her
own side projects — plus contact, résumé, Pastime (photo cards), Paint and Games.

## Stack and constraints

Plain HTML + hand-written CSS + vanilla JS, all in **one file**: `index.html` (~4,300
lines). No build step, no bundler, no npm dependencies, no framework, **no CDN assets** —
fonts and images are self-hosted under `assets/`. Edit `index.html` directly and refresh
the browser; there is nothing to compile.

The no-CDN rule is load-bearing, not incidental: it is why window chrome uses the system
mono stack via `--font-chrome` instead of Silkscreen (a Google Fonts face). A commented
`@font-face` sits at the top of the `<style>` block — drop a self-hosted woff2 into
`assets/fonts/` and uncomment it, and nothing else needs to change.

## Running it

```bash
open index.html
```
or
```bash
python3 -m http.server 8090
# then open http://localhost:8090/
```

There is no lint, build, or test command configured for this repo. Verify by driving the
real page — window open/close/drag, hash deep links, the mobile layout, console errors,
and that every referenced asset resolves. Write a throwaway script for this rather than
expecting an existing one.

## The window contract

Everything on the desk follows one set of attributes. Honour these and new windows work
without touching the script:

| Attribute | Meaning |
| --- | --- |
| `[data-desktop]` | the desk; windows are positioned inside its `.desk-inner` |
| `[data-win="id"]` | a window; the `hidden` attribute means closed |
| `[data-bar]` | title bar — drag handle, and raises its window on press |
| `[data-close]` | the top-left box; closes its window |
| `[data-open="id"]` | anything that opens a window (icon, list row, button) |
| `[data-back]` | the mobile `← Desktop` bar |
| `[data-modal]` | on the phone, this window fills the screen, one at a time |
| `[data-cascade]` | no fixed corner; cascades near the centre when opened |
| `[data-slug]` | the URL fragment this window answers to |
| `[data-x]` / `[data-y]` | opening corner in px, for non-cascading windows |
| `[data-cat]` | `work` / `lab` / `beyond` / `gallery` — colours the title bar |
| `[data-local-port]` / `[data-local-host]` | a local address that may be upgraded to a link |

## Structure of `index.html`

- `<head>`: pre-paint theme script (reads `localStorage['vc-theme']`), `@font-face`
  declarations (Spectral, Satoshi, self-hosted `.woff2`), then all CSS — design tokens
  in `:root` with dark overrides in `:root[data-theme="dark"]`.
- `.desk[data-desktop]` → `.menubar` (wordmark, decorative menu titles, clock, theme
  toggle) + `.desk-inner`, which is the positioning context for every window.
- Inside `.desk-inner`, in order: the hero window, `.icons`, then the remaining 24
  windows. Order matters only on mobile, where the hero and icons stack as a home screen.
- 25 windows total: 10 top-level (hero, work, lab, about, beyond, gallery, contact,
  resume, paint, games) and 15 long-form (4 case studies, 11 Lab write-ups). The
  `about` icon is `hidden` for now; its window still answers to `#about`.
- Single `<script>` IIFE at the end: theme, clock, the window stack
  (`raise`/`place`/`initialPlace`/`openWin`/`closeWin`), routing
  (`slugOf`/`setHash`/`writeHash`/`clearHash`/`applyHash`), dragging, delegated click and
  Escape wiring, `countUp` for stats, `localAddresses`, `setupLock` (the Lab password
  curtain), `setupPaint`, the two games (`setupQuest`, `setupRain`) behind
  `gameSwitcher`, and `landing`.

## Non-obvious behaviors worth knowing before editing

- **Windows carry `hidden` in the markup.** `landing()` is the only thing that decides
  what is on the desk at load. Removing `hidden` from a section makes it open on every
  visit, including on the phone.
- **Landing geometry is fractions of the desk, not pixels.** `LANDING` and `ICON_COL` in
  the script size and place the three opening windows relative to `.desk-inner`. The
  design mock's absolute pixels were authored against a ~1180px desk and collapsed into a
  single overlapping pile on a real 863px viewport — do not put fixed px back.
- **`.row` and `.rows-head` use `minmax(0,1fr)`, never `1fr`.** A bare `1fr` refuses to
  shrink below its content, so a long row name forced the whole window to scroll
  sideways.
- **Row layout is a container query on `.win-body`, not a media query.** A window is
  sized independently of the viewport, so rows have to answer to their own window's
  width. The `(max-width: 900px)` media query is the phone layout and a fallback, not
  the mechanism; `isMobile()` in the script shares that breakpoint, so change both.
- **`place()` writes an inline `max-height`** so a window always stays fully on the desk
  and its body scrolls instead. That is why the mobile block needs
  `max-height: none !important` — a stylesheet `!important` is what beats an inline
  style, and without it windows stay short on the phone.
- **`.win-title` is a `<span>`, and the window is named by `aria-label` on the
  `<section>`.** It is chrome, not document structure; as a heading it put a second `h1`
  above the hero's real one and inverted the heading order in every other window.
- **Watch specificity when a class styles an element the base rules also match.**
  This has bitten three times: `.win-body a` silently repainted `.btn-primary`
  black-on-black, `.win-body p` stripped the margins off eleven classed paragraph
  styles, and `.beyond li` turned the nested `.b-tags` pills into three-column
  grids. A rule like `.win-body p` is 0-1-1 and beats a plain `.rows-group` at
  0-1-0. The fixes in place are `:where(.win-body) p` to drop the base rule to
  element specificity, `:not(.btn)` to exclude, and `>` to stop a descendant
  selector reaching further than intended — prefer those over adding specificity
  on the other side.
- **The `--on-*` tokens encode contrast, not taste.** 10px chrome labels must clear
  4.5:1 against their own bar, which is why coral and yellow take ink text while teal and
  blue take white. Do not swap them to "even out" the palette.
- **Icons sit at `z-index: 5`, below windows**, so windows cover them as they would on a
  real desktop. The menu bar is at 9000 and stays on top.
- **Local addresses ship as plain text and are upgraded at runtime.** `localAddresses()`
  turns them into real links only when `location.hostname` can actually reach those
  ports (loopback, RFC1918, `file:`, or the Tailscale CGNAT range 100.64–100.127), and
  points them at the loaded host rather than the literal word `localhost` so they work
  over the tailnet. Adding a link straight into the markup undoes this.
- **Opening a window pushes a history entry; Back closes it.** `setHash(slug, push)`
  pushes only for windows a person opened (`openWin` with a trigger); `landing()` and
  deep links replace. The `hashchange` handler closes the window the previous entry
  named and applies the new one, so Back on the phone steps out of a case study, then
  out of the list, then leaves. Closing with the box or `← Desktop` replaces, not pops.
- **The Lab password (`setupLock`, word `hello`) is a curtain, not security.** The
  blurred content is in the HTML for anyone who views source, and for search engines.
- **Deep links from the previous scrolling version still resolve** — `#work`, `#about`,
  `#lab`, `#contact`, plus per-item slugs like `#work/in-car-payments`. Changing a
  `data-slug` breaks a URL that may already be shared.
- **The phone's scroller is `.desk-inner`, not the document**, so
  `history.scrollRestoration` does not govern it — a browser restores an
  element's offset after first layout, and fonts and lazy images settle later
  still. That is why the page kept opening scrolled past the menu bar and only a
  reload looked right. `pinTop(ms)` holds the top across that settling period on
  a rAF loop and releases on the first `wheel`/`touchstart`/`pointerdown`/
  `keydown`, so it never fights a person who meant to scroll. One reset at parse
  time is not enough; do not reduce it back to that.
- **Focus calls into windows use `{ preventScroll: true }`** — omitting this reintroduces
  an unwanted scroll on open.
- **`logo-chin.png` has a hand-added `tRNS` transparency chunk** (it is a palette PNG
  that did not ship with one) so `filter: invert()` works across themes. If you
  regenerate this asset it needs the same treatment or it renders as a solid box.
- **Finance Hub screenshots under `assets/img/cs/` are deliberately blurred** at numeric
  figures, since that app shows real personal financial data — preserve this if
  recapturing them.
- **The résumé PDF is generated, not hand-edited.** After changing the résumé window run
  `python3 scripts/make-resume-pdf.py` (headless Chrome, one A4 page) so
  `assets/vivien-chin-resume.pdf` matches the page.
- **SEO lives in `<head>` and must be kept in step.** `<title>`, the description, canonical,
  Open Graph / Twitter tags and the JSON-LD `Person` block all carry the same name, title
  and URL; `assets/img/og-card.jpg` (1200×630) is the shared social preview. `robots.txt`
  and `sitemap.xml` sit at the repo root. Change the deployed URL and all of these move.
- **`photography.html` is a separate page** with its own copy of the tokens and the same
  pre-paint theme script, reading the same `vc-theme` key. Theme changes must be made in
  both files or arriving from one to the other flashes the wrong ground.

## Assets

`assets/img/` holds 95 images (~15 MB): 28 loose (portrait, Pastime shots, client and
AI-tool logos, case-study covers, wordmarks, the social card), 49 under `cs/` (case-study
and Lab screenshots), 18 under `photography/`. Fonts are in `assets/fonts/`, and the
résumé PDF is `assets/vivien-chin-resume.pdf`.

Photographs and opaque screenshots are JPEG; PNG is kept only where the JPEG came out no
smaller or the image needs an alpha channel (logos, icons, `incar-wallet`, the SplitEasy
shots). Only the hero window's nine images load eagerly — every other `<img>` carries
`loading="lazy" decoding="async"`, which took first load from ~16 MB to under 0.5 MB.
Keep that attribute on anything you add outside the hero. Do not upscale a source to
match an older asset's dimensions (`sips -Z` upscales silently); the portrait slot is
170 CSS px wide.
