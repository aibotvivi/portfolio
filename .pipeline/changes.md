# Changes — Vivien Chin portfolio site

Branch: `feature/portfolio-site`
Commit: `408480d` — "Add single-file portfolio site for Vivien Chin"

## Files created

- `/Users/aiviv/portfolio/index.html` — the entire site (semantic HTML, one `<style>`
  block with `:root` design tokens, one inline non-module `<script>` at the end of
  `<body>`).
- `/Users/aiviv/portfolio/README.md` — what the project is, how to open it (`open
  index.html` or `python3 -m http.server`), a note that Lab links are localhost-only,
  and where to edit content (tokens block vs. section markup vs. script).
- `/Users/aiviv/portfolio/.gitignore` — `.DS_Store` and `*.log` only; `.pipeline/` is
  not ignored, nothing in `.pipeline/` or `.git/` was touched.

## How each spec section was implemented

**§2 Stack** — Single file, zero dependencies. No `<link>`, `<script src>`, `@import`,
or CDN reference anywhere. System font stack (`-apple-system, BlinkMacSystemFont,
"Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", "Hiragino Sans GB",
sans-serif`) doubles as the CJK-safe fallback for the "粵語" string in the Daily News
Dashboard card copy. All graphics are inline `<svg>` (only the dialog close-icon) or
pure CSS — zero `<img>` tags.

**§4.1 Header + hero** — `<header class="site-header">` holds the name/title/tab-nav
row plus a hero block below it (location with 🇬🇧, bio line, five employer chips as a
`<ul>`, secondary digital-marketing line), all always visible above the tab panels as
specified.

**§4.2 Tab navigation** — `<nav role="tablist">` with three real `<button role="tab">`
elements wired via `aria-selected`/`aria-controls`/`id`↔`aria-labelledby`. `activateTab()`
toggles the `hidden` attribute on the other two panels, sets `tabIndex` for roving
focus, and calls `history.replaceState('#'+name)` wrapped in `try/catch` (never
assigns `location.hash` directly). On load, an IIFE reads `location.hash` and defaults
to `work` for anything not in `['work','about','lab']`. Arrow keys move + activate;
Home/End jump to first/last. LinkedIn and Résumé render as a second, visually distinct
`<nav class="external-links">` in the header — using the **real resolved URLs** from
the spec's OPEN QUESTIONS answer (`https://www.linkedin.com/in/chincc` and
`https://vivchindesign.framer.website/resume`), not `data-todo="#"` placeholders,
since the spec states that question is resolved.

**§4.3 Work section** — 2-up grid at ≥900px, 1-up below (`.case-grid` + media query).
Each of the 4 cards is a real `<button>` with an ordinal, title, client, a `<dl>` of
role/timeline, and a summary line. I implemented case studies as **four pre-rendered
`<dialog>` elements** (the spec's explicit "implementer's choice" alternative to one
reused dialog), each with its own static, semantically-correct markup — this made the
exact-copy and per-study heading differences (see deviation note below) easy to get
right and easy for a tester to grep.

Dialog mechanics: `showModal()`/`close()` when
`HTMLDialogElement.prototype.showModal` exists, feature-detected once at load; a
`try/catch` around `showModal()` additionally falls back to manually setting the
`open` attribute if it throws. In both paths the same CSS makes `dialog.case-dialog`
a fixed, full-viewport, dark-backdrop flex container keyed purely off the `[open]`
attribute — so clicking anywhere on the dialog element itself (outside
`.dialog-inner`) closes it as a backdrop click, in both the native-modal and
manual-fallback code paths, with no separate overlay `<div>` needed. Escape is handled
natively by the browser when `showModal()` is available; a document-level `keydown`
listener additionally closes the active dialog on Escape only when native dialog
support is absent. A `close` event listener on every dialog is the single place that
un-locks `document.body` scroll and restores focus to the triggering card — this runs
whether the dialog was closed via the close button, backdrop click, or (native) Escape.
A light `Tab`-key focus trap keeps keyboard focus inside the open dialog.

Case study content: all four follow **Role & timeline · Problem · Process · Outcome**
except case study 3, where — per the spec's own explicit instruction in §4.3 — the
process/solution block is headed **"Solution"** instead of "Process", and the
"Outcome" heading is omitted entirely (never invented, never printed as "N/A"). Case
study 2's overlay includes a 4-item stat row (`32%`, `13%`, `74%`, `85%`) plus the
closing research line; case study 4's overlay includes a 3-item stat row (`90%`,
`67%`, `34%`) inside its Problem section, plus separate Process and Solution
paragraphs (no Outcome text existed in the source copy, so none is shown).

**§4.4 About Me** — Intro paragraph, a pull-quote `<blockquote class="philosophy">`,
three chip/list blocks (7 product-design clients, 8 digital-marketing entries
including the "and other luxury & retail brands" line, 4 training/focus areas), a
4-item "Beyond work" grid, and a links row (LinkedIn, Résumé, Photography portfolio —
all three real URLs, `target="_blank" rel="noopener noreferrer"`).

**§4.5 Currently Building (Lab)** — Exactly 4 `<article class="lab-card">` elements
with the exact hrefs from the spec table (`http://localhost:8787`,
`http://127.0.0.1:8793`, `http://localhost:3000`, `http://127.0.0.1:8083`), each
carrying a persistent `.badge` reading "Runs locally" (not conditional on anything —
no `fetch`, no health check, no `<img>` ping anywhere in the file), `target="_blank"
rel="noopener noreferrer"` on every link, and a `<code>` line showing the address.
Taroscope's card explicitly notes the front end is a local `index.html` and that
`localhost:8787` is the reading API. A single footnote below the grid reads "If a
link doesn't load, that app's local server isn't running."

**§4.6 Footer** — `© 2026 Vivien Chin · London` plus LinkedIn/Résumé links, no form.

**§5 Visual direction** — All colour/spacing/radius/type values are CSS custom
properties in one `:root` block at the top of `<style>`. Type scale uses `clamp()`
throughout (`--fs-h1` through `--fs-eyebrow`, plus `--fs-stat` for the stat numbers).
`:focus-visible` outlines are applied globally via `a:focus-visible,
button:focus-visible, [tabindex]:focus-visible`. `prefers-reduced-motion: reduce`
zeroes out all transition/animation durations. A `@media print` block hides the tab
nav and forces `.panel[hidden] { display: block !important; }` so all three panels
print expanded, with a subtle rule between them. Verified with a contrast-ratio script
(see below) — the lightest body text (`--color-ink-faint` on `--color-bg`) still comes
in at ~4.68:1, everything else higher.

## Deviations from the spec (with reasons)

1. **Acceptance criterion 8 vs. case study 3's explicit content instructions.**
   Criterion 8 says all four overlays should contain "that study's Problem and
   Process sections." Section 4.3's case-study-3 entry explicitly instructs: *"Process
   / Solution (label this block **Solution**)"* and to omit Outcome. I followed the
   more specific, explicit instruction — case study 3's overlay has a "Problem"
   heading but no "Process" heading (it says "Solution" instead), matching criterion 9
   ("no Outcome heading") and the spec's own worked example. **Tester note:** if you
   grep for the literal word "Process" inside dialog 3, it will not be found — this is
   intentional per §4.3, not a bug.
2. **Single container for the four dialogs.** The page-structure sketch in §4 shows one
   `<div id="case-dialog">` before `</body>`; I used four sibling `<dialog>` elements
   (`#dialog-1..4`) directly before the `<script>`, per §4.3's explicit "four
   pre-rendered dialog elements" alternative. No wrapping `<div id="case-dialog">`
   exists — each dialog is addressed by its own id.
3. **Fallback overlay re-uses the `<dialog>` element rather than a separate `<div>`.**
   §4.3 describes falling back to "toggling a plain `.is-open` class on an
   absolutely-positioned overlay `<div>`" when `showModal` is unavailable. I instead
   toggle the `open` attribute (and an `.is-open` class, kept for parity) directly on
   the same `<dialog>` element, with CSS that makes `dialog.case-dialog[open]` a fixed,
   full-viewport, backdrop-tinted flex container regardless of whether `open` was set
   by `showModal()` or manually. This produces the same visual/functional result
   (never-unopenable card, working Escape/backdrop-click/close-button, scroll lock)
   with less duplicated markup. Flagged for tester awareness in case the review checks
   for a literal separate overlay `<div>`.

## What the tester should focus on

- Open `index.html` via both `file://` and `python3 -m http.server` and confirm
  identical rendering (already verified headlessly with Playwright — see below).
- Exercise all three tabs by click, by keyboard (Arrow/Home/End), and via
  `#work`/`#about`/`#lab`/`#nonsense` hashes.
- Open each of the 4 case-study cards; confirm dialog 3 has no "Outcome" heading and
  uses "Solution" where the others would say "Process" (deviation #1 above);
  confirm the stat rows in dialogs 2 and 4.
- Confirm the 4 Lab cards' hrefs, `target="_blank"`, `rel="noopener noreferrer"`, and
  persistent "Runs locally" badges, and that opening the Lab tab issues no network
  requests even with no local servers running.
- Resize/re-view at 320px, 375px, 768px, 1440px for horizontal scroll and layout.
- This was verified with a headless Playwright script exercising 35 checks (tab
  switching/exclusivity, hash sync + fallback, arrow/Home/End keyboard nav, all 4
  dialogs open/close/focus-return, backdrop-click close, stat-row content, Lab badge
  count and zero-network-requests, no-horizontal-scroll at all 4 required widths, and
  console-error-free load under both `file://` and `http.server`) — all 35 passed.
  Manual grep checks also confirmed: only one HTML file at repo root, no
  `cdn`/`fonts.googleapis`/`unpkg`/`jsdelivr` strings, zero `<img>` tags, all 7
  stat percentages present, all 7 product-design clients + 4 "Beyond work" items
  present, and a computed WCAG contrast check on every colour-token pairing used for
  text (all ≥ 4.68:1, most well above 7:1).

CHANGES: COMPLETE
