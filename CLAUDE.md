# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-page portfolio site for Vivien Chin, Senior Product Designer. The landing view
is a 90s desktop rather than a scrolling page: a dithered desk, a menu bar, ten icons
(one hidden), and windows that drag, stack and close. Client Work and The Lab are Finder
list views, each case study or side project opens as its own window, and Paint and Games
are small toys of their own.

It reproduces the content of her Framer site (Work, About Me) and adds The Lab — her
own side projects — plus contact, résumé, Pastime (photo cards), Paint and Games.

## Stack and constraints

Plain HTML + hand-written CSS + vanilla JS, all in **one file**: `index.html` (~7,000
lines). No build step, no bundler, no npm dependencies, no framework, **no CDN assets** —
fonts and images are self-hosted under `assets/`. The Google Analytics tag is the
single exception, and a deliberate one: gtag.js cannot be self-hosted on a static
host. It is the only third-party request the site makes. Edit `index.html` directly and refresh
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
- Inside `.desk-inner`, in order: the hero window, `.icons`, then the remaining 26
  windows. Order matters only on mobile, where the hero and icons stack as a home screen.
- 27 windows total: 12 top-level (hero, work, lab, about, beyond, gallery, contact,
  resume, paint, games, atlas, screensaver) and 15 long-form (4 case studies, 11 Lab write-ups). The
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
- **The travel map's world is data, not an image or a library.** `setupAtlas` draws a
  168×66 land grid on a canvas; the grid was rasterised offline from Natural Earth's
  public-domain 110m land polygons and ships as ~2.7 KB of hex, four cells per character.
  That is what keeps a world map inside the no-CDN rule. Pins are grid coordinates, so
  they scale with the cell size; cells stay whole numbers because a fractional cell is
  what makes a pixel map look blurred. The window is 760px wide for a reason — at 720
  the cell size fell to 3 and the desktop map came out smaller than the phone's.
- **The map has two views, and the second one needs its own data.** Pin view marks each
  place with a numbered pin; land view shades the whole of every country visited. That
  needs country identity, which the land grid does not carry, so `VISIT` holds a second
  map — one hex digit per cell, 0 for land nobody has been to, else the 1-based index
  into `PLACES`, in base 36 since there are more than fifteen — rasterised from the same
  Natural Earth release's country polygons. Hong Kong and Singapore have no polygon at
  110m (both are smaller than one cell) so their cells are set by hand. Every figure on
  show is written from the data at run time: the share was once typed into the markup
  and went stale the moment the list changed.
- **Do not hand-edit `MAP`, `VISIT`, `SHARE` or `PLACES`.** Add a name to `PLACES` in
  `scripts/build-travel-map.py` and run it (`python3 scripts/build-travel-map.py`); it
  rasterises both grids and rewrites those four values in place, touching nothing else.
  It caches the Natural Earth downloads in a gitignored `.cache/`. Two rules it encodes,
  both learned the hard way: countries are painted **largest first** so a small one is
  not erased by its neighbours — in list order Belgium lost every cell it shares with
  France, Germany and the Netherlands — and the script **exits rather than emit a place
  with no cells**, so a country can never quietly vanish from the map. `SHARE` is cos-latitude weighted, so it is a real area share rather than
  a cell count, and it is of the land the grid covers — Antarctica is outside it.
  Both numbers describe whole countries visited, not ground walked; the note under the
  map says so, and it should keep saying so.
- **The map pans and zooms, and the canvas is a viewport, not the map.** `ox`/`oy` hold
  the map's top-left corner in viewport pixels, `zoom` multiplies the cell size, and
  only the cells inside the viewport are drawn. Two things it needs: `touch-action:
  none` on the canvas, or a drag scrolls the window instead of moving the map; and
  `setPointerCapture` wrapped in try/catch, since it throws `NotFoundError` when the
  browser does not consider the id active and an uncaught throw there kills the whole
  pointerdown handler, leaving the map undraggable.
- **Five games share one window.** `gameSwitcher` sets `data-active-game` and fires
  `gamechange`; every game gates its loop on that plus `win.hidden`, or panels nobody is
  looking at hold frames. Deadline Crossing and Scope Snake came from prototypes whose
  loops rescheduled unconditionally — that gate was added when they were folded in.
  Minesweeper has no loop. Colours that live in the DOM (level markers, Minesweeper's
  cells) are tokens; the canvases keep literals, which a canvas has to.
- **Seven tabs do not fit a phone.** At `@container (max-width: 560px)` the tab strip
  stops wrapping and scrolls sideways instead, with a fade at the right edge to say so —
  wrapped, it ran to three lines and pushed the board off the screen. Adding an eighth
  game costs nothing there; adding one to a wrapping row would.
- **Every game reports its start, and its end where it has one.** `game_start` carries
  the game's name for all seven. Endings: `frogger_over`, `snake_over`,
  `minesweeper_cleared` / `minesweeper_over`, `solitaire_won`, `journey_complete`,
  `sky_over` / `sky_complete`. Rhythm Deck has no end state, so it reports only its
  start. Solitaire deals at load, so its start hangs off the first move, not the deal,
  or every visitor would look like a player.
- **The screen saver waits on a timer, not on frames.** After the chosen wait — 10s by
  default, or 20s, 60s, or off — with no pointer, key, wheel or touch, `setupSaver` covers
  everything at `z-index: 9500`; anything wakes it. Five scenes, a live preview and the
  wait are chosen in the `screensaver` window, reached from its icon, because the menu
  titles are chrome. Frames are only requested while something is actually on screen:
  the saver when it is running, the preview only while its window is open — the
  prototype held one permanently just to watch the clock. It never starts while
  `document.hidden`, since a background tab is not somebody sitting still.
- **The Lab sign-up posts to Supabase, and sits OUTSIDE the lock.** `setupSignup` holds
  `SUPABASE_URL`, `SUPABASE_KEY` and `SUPABASE_TABLE`; empty values leave the form up but
  answering in plain words rather than swallowing an address it cannot store. It is the
  second deliberate exception to the no-CDN rule, for the same reason as analytics: there
  is no server here to post to. **The anon key is public by design — the table needs a
  row-level-security policy that allows insert and nothing else**, or the list is readable
  by anyone who reads this page. A 409 is the unique constraint and means "already on the
  list", not a failure. The block is above `.lock` deliberately: inside it, nobody could
  subscribe without the password.
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
- **Two Google tags ship, and both must stay literal.** Tag Manager (container
  `GTM-5FTTLHDT`) is high in `<head>` with its `<noscript>` iframe right after
  `<body>`, and the GA4 tag (`G-NW60T4SQ4X`) follows in `<head>` — on both pages.
  They share `dataLayer` safely. **An empty GTM container sends nothing**, so the
  two only start double counting if a GA4 tag for the same id is configured inside
  GTM; if that happens, delete the on-page GA4 snippet rather than leaving both.
- **Two GA4 properties are configured from one `gtag.js` load** (`G-JHW1TZ9QH5` first,
  then `G-NW60T4SQ4X`). That is Google's documented way to send to more than one:
  each property receives a full copy of every hit, nothing is split. Only the id in
  the `<script src>` is findable by Google's installation check, so the newer property
  holds that slot and the older one will report as "not detected" if tested — it is
  still collecting. Dropping a property is one `gtag('config', ...)` line, in every page.
- **Keep the analytics tag as Google's literal snippet in BOTH `index.html` and
  `photography.html`.** Google's installation check reads the HTML as served and does
  not run the page, so a tag whose URL is assembled in JavaScript reports as "not
  detected" even though it works in a browser — that is exactly what a tidier
  dynamic version did here. The Measurement ID must appear verbatim in the
  `<script src>` and in a `gtag('config', ...)` call, on both pages — and on the bare
  domain's redirect page, which lives in the separate `aibotvivi.github.io` repo and is
  the URL the data stream checks. To switch analytics off, delete both script tags
  rather than blanking the id.
- **Windows are pages, and every one of them is reported by hand.** `index.html`
  configures GA with `send_page_view: false`, because Google's automatic view fires
  before any window opens and reports the bare URL with the fragment stripped — an
  arrival on a shared `#lab/spliteasy` link was being recorded as a visit to the desk.
  Instead `reportLanding()` sends exactly one view on arrival, naming the window the
  URL opened, and `trackView(win)` reports each window a person opens afterwards, with
  its slug and `aria-label`. Windows `landing()` opens by itself are not counted, or
  one arrival would be three views.
- **Every window also has a real page, generated — never hand-written.**
  `python3 scripts/build-pages.py` emits `<slug>/index.html` for each window with a
  slug, so `#work/apex-ai` is also served at `/portfolio/work/apex-ai/`. That is the
  convention: a new window with a `data-slug` gets its page by re-running the script,
  and its address matches what analytics already reports. The script lifts the content
  and the stylesheet out of `index.html` (into `assets/site.css`), so the pages cannot
  drift from the desktop, and it rewrites `sitemap.xml`. `index.html` keeps its inline
  styles and stays a single file. Paint, Games and the travel map are listed in `APPS`
  because they are running programs, not documents: copying their markup would publish
  dead buttons and a blank canvas, so they get a description and a link to the desktop
  instead. `PAGE_TITLE` overrides labels that read as filenames (`resume.pdf`).
  **Regenerate after editing any window's content**, or the page and the desktop diverge.
- **Paint and the games send events, and the grain is deliberate.** `track(name, params)`
  sits beside `trackView`; both properties receive whatever it sends. It fires on
  *choices and milestones only* — `paint_tool`, `paint_stamp`, `paint_start` (first
  stroke, once), `paint_add_image`, `paint_save`, `game_start`, `journey_checkpoint`,
  `journey_extra`, `journey_complete`, `sky_over`, `sky_complete`. Never per frame or
  per brush stroke: that is thousands of hits a visit, and Analytics starts dropping
  them. A parameter (`tool`, `checkpoint`, `score`) is only visible in reports once it
  is registered as a custom dimension in Admin → Custom definitions.
- **Report a window's slug as a path, never as a fragment.** Analytics builds its page
  path from the URL's path and drops `#…`, so reporting `#lab/spliteasy` filed all 26
  windows under one row for the desk — indistinguishable from tracking nothing at all.
  `viewUrl(slug)` returns `/portfolio/lab/spliteasy/` — with the trailing slash, so the
  row in a report is the address the generated page actually serves. `photography.html` and the root redirect page are
  ordinary pages and keep Google's automatic view.
- **Analytics cookies need consent in the UK and EU** (PECR / GDPR). There is no
  consent banner on the site yet, so switching on a real ID is a decision to make
  knowingly, not a formality.
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
