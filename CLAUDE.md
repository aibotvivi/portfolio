# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-page portfolio site for Vivien Chin, Senior Product Designer. It reproduces the
content of her Framer site (Work, About Me) and adds a "Currently Building" (Lab) tab
linking to her other local/side projects, plus a Contact tab.

## Stack and constraints

Plain HTML + hand-written CSS + vanilla JS, all in **one file**: `index.html` (~1900
lines). No build step, no bundler, no npm dependencies, no framework, no CDN assets —
fonts and images are self-hosted under `assets/`. Edit `index.html` directly and
refresh the browser; there is nothing to compile.

## Running it

```bash
open index.html
```
or
```bash
python3 -m http.server 8090
# then open http://localhost:8090/
```

There is no lint, build, or test command configured for this repo. Verification has
historically been done with ad-hoc Playwright scripts (console errors, image/font
loading, tab and dialog behavior, scroll-lock, hash routing, horizontal overflow at
320/375/768/1440px) — write a throwaway script for this rather than expecting an
existing one in the repo.

## Structure of `index.html`

- `<head>`: `@font-face` declarations (Spectral serif, Satoshi sans, self-hosted
  `.woff2` under `assets/fonts/`), then all CSS — design tokens as custom properties in
  `:root`, with `:root[data-theme="light"]` / `:root[data-theme="dark"]` overrides for
  full theming (persisted via `localStorage['vc-theme']`).
- `.frame-bar` — outer bar (wordmark, LinkedIn/résumé links, theme toggle) that must
  also respect the light/dark tokens — it's a separate token scope from the inner
  `.page-card`, easy to leave stale when only one is restyled.
- `.page-card` → `<main id="panels">` containing four `role="tabpanel"` sections:
  `#about` (default landing panel — no `hidden` attribute), `#work`, `#lab`, `#contact`.
- `.dock` — fixed bottom nav, ARIA tablist pattern (`role="tab"`, `aria-selected`,
  roving tabindex, arrow-key navigation) driving tab switching, plus a sliding
  `.dock-pill` indicator and a magnetic pointer-follow effect (`pointermove`, gated to
  `(hover: hover)`).
- Work section: bento-grid `.work-card`s, each with a `.work-cta[data-dialog="dialog-N"]`
  button opening the matching `<dialog id="dialog-N">` (4 case studies, `dialog-1..4`).
- Lab section: `.lab-card`s (Taroscope, Daily News, Finance Hub, Orchestrator, Project
  Hub, Postmarked, Anti-Flare, SplitEasy, Dream Oracle), same pattern, opening
  `<dialog id="lab-{slug}">`.
- All case-study `<dialog>` elements live together near the end of `<body>`, before the
  `<script>`. Each follows the same internal structure: eyebrow/title/blurb,
  `.dialog-meta` (definition list), hero image, prose sections, `.dialog-list`,
  `.dialog-figure` screenshots with captions, and (Lab only) `.lab-links`.
- Single `<script>` IIFE at the end handles: theme init/toggle, tab activation
  (`activateTab`, hash-based deep links `#work`/`#about`/`#lab`/`#contact`, guarded
  `history.replaceState` for `file://`), dock pill positioning, dialog open/close with
  focus trap (`trapFocus`) and scroll lock (`setScrollLock` toggles a class on
  `<html>`, not `<body>`), a count-up animation for stats (`countUp`), and a
  scroll-reveal `IntersectionObserver` gated behind `prefers-reduced-motion`.

## Non-obvious behaviors worth knowing before editing

- **Scroll lock is applied to `<html>`, not `<body>`** — this was a deliberate fix for
  a viewport-overflow propagation bug. Don't "simplify" it back to body-only.
- **Focus calls into dialogs use `{ preventScroll: true }`** (open and close) —
  omitting this reintroduces an unwanted page-scroll-on-dialog-close bug.
- **Dialog backdrop-click-to-close matches `pointerdown` and `click` targets** rather
  than just `click`, specifically to avoid closing the dialog when a user drags to
  select text and releases outside the content box.
- **The hash is only written on user interaction, not on initial load** — writing it
  unconditionally on load caused unwanted scroll-into-view on first paint.
- **`logo-chin.png` has a hand-added `tRNS` transparency chunk** (it's a palette PNG
  that didn't ship with one) so `filter: invert()` works correctly across themes. If
  you regenerate/replace this asset, it needs the same treatment or it will render as
  a solid box.
- **The outer `.frame-bar` and the inner `.page-card` are separate token scopes** —
  when changing theme colors, update both or the outer frame can end up stuck on the
  wrong theme while the inner card switches correctly.
- **Finance Hub screenshots under `assets/img/cs/` are deliberately blurred** at
  numeric figures (balances/percentages) since that app shows real personal financial
  data — preserve this if recapturing those screenshots.
- `README.md` describes an earlier, smaller version of this site (3 panels, 4 Lab
  cards/dialogs) and is out of date relative to the current 4-panel, 9-Lab-card
  structure described above; prefer this file and the actual markup over the README
  when they disagree.
