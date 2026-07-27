# Test results — Vivien Chin portfolio site

Tester independently re-verified every acceptance criterion in `.pipeline/spec.md` §6 (did
not trust `.pipeline/changes.md`'s own claims). Verification used: `grep` against
`index.html`, a headless Chromium session driven via Playwright (both `file://` and
`python3 -m http.server 8095` from the repo root, port killed after testing), and manual
reading of `index.html`, `README.md`, `.gitignore`.

Scripts used (not committed to the repo): `/private/tmp/claude-502/-Users-aiviv/f579ca94-157e-4022-b814-f19cef6d37dd/scratchpad/test.js`,
`test-hash.js`, plus a couple of ad-hoc one-liners for tab-order and focus checks.

## Acceptance criteria (spec §6)

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| 1 | `index.html` exists, only HTML file at repo root | PASS | `ls` at repo root: only `index.html`, `README.md`, `.gitignore`, `.git/`, `.pipeline/` — no other `.html`. |
| 2 | `file://` renders full site, no console errors; `python3 -m http.server` renders identically | PASS | Playwright: 0 console errors / 0 page errors under both `file:///Users/aiviv/portfolio/index.html` and `http://localhost:8095/index.html`. Same DOM/text content and structure in both — no server-dependent behaviour exists (no fetches, no relative-asset paths). |
| 3 | No external URL in `src`/stylesheet/`<script src>`/`@import` position; no `cdn`/`fonts.googleapis`/`unpkg`/`jsdelivr` strings; only permitted absolute URLs present | PASS | `grep -n "<link\|<script src\|@import"` → no matches. `grep -ni "cdn\|fonts.googleapis\|unpkg\|jsdelivr"` → no matches. All 11 `http(s)://` occurrences are `<a href>` values: 3× LinkedIn/Résumé/Photography repeated across header/about/footer, and the 4 Lab `localhost`/`127.0.0.1` links — matches the permitted list exactly. |
| 4 | Zero `<img>` tags | PASS | `grep -n "<img"` → no matches. Only graphic is one inline `<svg>` (dialog close icon), reused 4×. |
| 5 | Three tabs exist, exclusive; Work active on load | PASS | Playwright: on load, `#tab-work[aria-selected=true]`, `#work` has no `hidden`, `#about`/`#lab` both `hidden`. Clicking About → only `#about` un-hidden; clicking Currently Building → only `#lab` un-hidden. Verified under both `file://` and http-server contexts. |
| 6 | `#lab` activates Currently Building; `#nonsense` falls back to Work without error | PASS | Verified via **fresh** page navigations (`browser.newPage()` then a single `page.goto(url+'#lab')`) so the load-time hash-read IIFE actually runs: `index.html#lab` → `tab-lab` selected, `#lab` panel un-hidden. `index.html#nonsense` → `tab-work` selected, no page errors. **Tester note:** an initial version of my test navigated to `url+'#lab'` on a page that was *already* loaded (same-document, fragment-only navigation) and saw `lab-selected=false` — that is expected browser behaviour (the site's hash-read logic runs once at initial load, not on `hashchange`, matching the spec's wording "Loading `index.html#lab`" = a fresh load) and is **not a bug**; re-tested correctly with a fresh page per URL and it passes. |
| 7 | Arrow-key nav between tabs; every tab/card reachable by Tab key with visible focus ring | PASS | ArrowRight/ArrowRight/ArrowLeft/ArrowLeft cycle correctly moved focus + `aria-selected` through work→about→lab→about→work. Tab-key traversal from page top reached `card-1`..`card-4`, then the LinkedIn/Résumé header links, then wrapped to `tab-work`. Computed style on a focused tab: `outline: solid rgb(51, 50, 154) 2px` (from the global `a:focus-visible, button:focus-visible, [tabindex]:focus-visible` rule). |
| 8 | All four case-study cards open an overlay containing that study's Problem section and its Process section — **except case study 3, whose process block is deliberately headed "Solution" per §4.3** (amended wording) | PASS | **Amendment note:** the orchestrator adjudicated the spec conflict I flagged and updated `.pipeline/spec.md` §6 criterion 8 to explicitly carve out case study 3 (verified by re-reading the file myself — line 201 now reads the amended text, not just taking the coordinator's word for it). Re-evaluated against the amended wording: dialogs 1, 2, 4 each contain literal `<h3>Problem</h3>` and `<h3>Process</h3>` headings with the specified content; dialog 3 contains `<h3>Problem</h3>` and `<h3>Solution</h3>` (no "Process" heading), which now matches the criterion exactly as amended. No re-run of the browser suite was needed — the existing DOM evidence (`#dialog-3` headings: `["Role & timeline","Problem","Solution"]`, collected earlier this session) already fully covers the amended wording. |
| 9 | Case study 3's overlay contains no "Outcome" heading | PASS | `#dialog-3` headings: `["Role & timeline", "Problem", "Solution"]` — no "Outcome". |
| 10 | Case study 2 overlay contains `32%`,`13%`,`74%`,`85%`; case study 4 contains `90%`,`67%`,`34%` | PASS | Playwright text-content check on `#dialog-2` and `#dialog-4` confirms all 7 strings present, each in its own `.stat-number` element within a `stat-row-4` / `stat-row-3` grid. |
| 11 | About panel contains all 7 product-design clients and all 4 "Beyond work" items | PASS | Product-design chips: JP Morgan (Payments), QVC, BT Group, Upgrade Pack, Ordre, Sun Life Financial Insurance, Attitude is Everything (7/7). Beyond-work items: Volunteer design, Sound healing, Photography & travel, Aerial arts (4/4). |
| 12 | Lab panel: exactly 4 cards, correct hrefs, `target="_blank"`, `rel` contains `noopener`, "Runs locally" badge on each | PASS | `.lab-card` count = 4. Hrefs match `http://localhost:8787`, `http://127.0.0.1:8793`, `http://localhost:3000`, `http://127.0.0.1:8083` exactly. All 4 links: `target="_blank"`, `rel="noopener noreferrer"`. All 4 badges read exactly "Runs locally". |
| 13 | With servers stopped, Lab panel renders fully; zero network requests | PASS | None of the 4 target apps (taroscope :8787, news dashboard :8793, finance-hub :3000, orchestrator :8083) were running during this test. Playwright's request listener recorded **only the document request itself** across an entire session that included switching to every tab, opening all 4 case dialogs, and viewing the Lab panel — zero secondary requests, no spinner/error markup exists in the DOM (badges and cards are static). |
| 14 | No horizontal scroll at 320/375/768/1440px | PASS | At each width, `document.documentElement.scrollWidth === clientWidth` (no overflow) under both `file://` and http-server contexts. |
| 15 | `README.md` and `.gitignore` exist at repo root | PASS | Both present. `.gitignore` contains exactly `.DS_Store` and `*.log` (matches spec, `.pipeline/` correctly not ignored). `README.md` covers what/how-to-open/Lab-localhost-note/where-to-edit as required. |

## Additional checks performed (beyond the numbered list)

- Focus moves into the dialog on open: confirmed — `document.activeElement` becomes the `.dialog-close` button immediately after `showModal()`.
- Backdrop click closes the dialog: confirmed on dialog 1 (click at viewport corner, outside `.dialog-inner`).
- `body.scroll-locked` is applied while any dialog is open and removed on close: confirmed for all 4 dialogs.
- Escape closes each of the 4 dialogs and returns focus to its triggering card: confirmed individually for cards 1–4.

## Limitations / things not fully verifiable in this environment

- **`prefers-reduced-motion: reduce` and `@media print` behaviour** were checked only by reading the CSS (rules exist and target the right selectors); I did not drive Playwright with `page.emulateMedia({ reducedMotion: 'reduce' })` / `{ media: 'print' }` to assert computed durations/visibility. Reading confirms the rules are structurally correct (`animation-duration: 0.001ms !important` etc., and `.panel[hidden] { display: block !important; }` under `@media print` with the tablist hidden), but this is a static read, not a rendered assertion.
- **WCAG contrast ratios** were not independently recomputed; I read the token values and the coder's claimed ~4.68:1 minimum in `changes.md` but did not run a contrast calculator myself. This is a §5 visual-direction requirement, not one of the 15 numbered acceptance criteria, so it doesn't affect the PASS/FAIL roll-up, but flagging it as unverified.
- Real-browser/manual visual QA (actual pixel rendering, hover states, print preview) was not performed — only DOM/computed-style/behavioural checks via headless Chromium.

## Result

62 of the 66 automated Playwright assertions I wrote passed outright; 2 of the 4 "failures" in my first draft script were test-methodology artifacts (same-document hash navigation) and were re-verified as passing with a corrected test (see criterion 6 note). The remaining discrepancy was criterion 8 vs. dialog 3, stemming from a genuine contradiction between the generic acceptance-criterion wording and the case-study-3-specific instruction elsewhere in the same spec — not a coding defect. I declined to resolve that judgment call myself and flagged it for Review.

## Addendum — spec amendment and re-adjudication

The orchestrator adjudicated the flagged conflict: `.pipeline/spec.md` §6 criterion 8 was amended to explicitly except case study 3 ("...except case study 3, whose process block is deliberately headed 'Solution' per §4.3"). I independently re-read `spec.md` to confirm the amendment is actually present in the file (not just asserted) before accepting it. Against the amended wording, the implementation is correct as built — dialog 3's "Solution" heading (no "Process" heading) is now the specified behaviour, not a deviation. No other criterion is affected by this change, and no re-run of the browser suite was necessary since the DOM evidence already collected covers the amended wording. All 15 acceptance criteria now pass, with the documented limitations (prefers-reduced-motion / @media print verified only by reading CSS, not by driving emulated media; WCAG contrast not independently recomputed — neither is a numbered acceptance criterion) still standing as honest, non-blocking gaps.

RESULT: PASS
