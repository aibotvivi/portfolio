# Review — Vivien Chin portfolio site

Reviewer: final gate, branch `feature/portfolio-site`, commit `408480d`.
Method: read `spec.md`, `changes.md`, `test-results.md`, `site-content.md`; `git show --stat 408480d`
and `git diff main...feature/portfolio-site`; full read of `index.html` (1208 lines), `README.md`,
`.gitignore`; independent headless-Chromium probes of the things the tester's criteria could not
catch (real layout overflow with the blanket `overflow-x:hidden` neutralised, actual background
scroll while a modal is open, load-time scroll position, print/reduced-motion emulation, accessible
names, contrast recomputed from the tokens).

## Summary

This is a genuinely well-built single file: the content is faithful to `site-content.md` and the
spec's copy almost word-for-word, the token block is disciplined and complete (every declared custom
property is used, none undefined), the tab/dialog JS is small, defensive and free of `innerHTML`,
`eval`, inline handlers or `target="_blank"` without `rel="noopener noreferrer"`, and every
acceptance criterion in §6 is literally satisfied. Contrast, which the tester explicitly did not
recompute, checks out: I recomputed every token pair actually used for text and the worst case is
`--color-ink-faint` on `--color-bg` at **4.68:1**, everything else 5.1:1 and up — the coder's claim
was honest. However, three of the spec's *non-numbered* requirements are broken in ways the
acceptance criteria were structurally incapable of detecting, and two of them are the first thing a
human will see: **the page auto-scrolls ~570–790px past the hero on every load**, and **the header
nav is clipped off-screen at 320px and 375px** — hidden from the tester because `html, body {
overflow-x: hidden }` makes criterion 14 vacuously true. A third, the required modal scroll lock, is
inert for the same root cause. All three are small, local fixes; the architecture, content and
security posture need no rework. Hence FIX FIRST rather than REJECT.

## Blockers

**B1. Every page load jumps past the hero.** `index.html:1041-1067` — `activateTab()`
unconditionally calls `history.replaceState(null, '', '#' + name)`, and `initFromHash`
(`index.html:1095-1098`) calls it during parse even when there is no hash. The document URL
therefore carries `#work` before the load completes, the browser then performs fragment
scrolling/focusing on the matching `<section id="work">`, and the visitor arrives mid-page with the
entire identity block — "Vivien Chin", Senior Product Designer, location, bio, employer chips —
scrolled off the top.

Measured (Chromium, both `file://` and `python3 -m http.server`):

| viewport | scrollY after plain load of `index.html` |
|---|---|
| 375 | 790 |
| 900 | 582 |
| 1440 | 571 |

Causality confirmed: stubbing `history.replaceState` to a no-op before page scripts run gives
`scrollY = 0`. This directly contradicts §4.1 ("The hero sits above the tab panels and is **always
visible**") and is the single worst defect here — a designer's portfolio that opens on the middle of
the page. **Fix:** on the initial activation, skip the URL write when `location.hash` is empty
(e.g. `activateTab(name, { silent: true })` from `initFromHash`), or write the hash only in the
click/keydown handlers. Do not "fix" it with a `scrollTo(0,0)` after load — that flashes.

**B2. Header navigation is clipped at 320px and 375px.** With `html, body { overflow-x: hidden }`
(`index.html:84`) temporarily neutralised, the document overflows by **84px at 320px** and **31px at
375px**; at 768px and 1440px there is no overflow. Offenders are `.header-actions` / `.tablist` /
`.external-links` (`index.html:164-213`), which have no narrow-width treatment.

Measured element rects (viewport width in brackets):

- `#tab-lab` "Currently Building": right edge 400 [320] → **80px clipped**; right edge 402 [375] →
  **27px clipped**. The pill has no visible right end and the label is cut.
- `.external-links` "Résumé": spans 353–406 at 375px → only ~22px of the link is on screen; at 320px
  it is 84px clipped and effectively invisible. LinkedIn is clipped by 8px at 320px.

Screenshot at 375px confirms visually: the Currently Building pill runs off the right edge and the
second header link reads "Rés". This violates §5 ("must be usable and attractive at 375px") and
§4.2 (the Résumé link is not usable). **Fix:** at narrow widths let `.header-actions` be full width
with `align-items: stretch`, allow the `.tablist` to wrap (or shrink `--space-m` padding / use a
horizontally scrollable tablist with `overflow-x:auto` **on the tablist only**), and let
`.external-links` wrap. Then verify with `html,body{overflow-x:visible}` — see B2a.

**B2a (same root cause, must be fixed alongside).** `html, body { overflow-x: hidden }` at
`index.html:84` clips overflow instead of preventing it, which is why the tester's criterion-14
check (`documentElement.scrollWidth === clientWidth`) passed while content was actually falling off
the page. Once the header is fixed, remove the blanket `overflow-x: hidden` (or keep it only as a
belt-and-braces after re-verifying there is zero real overflow at 320/375/768/1440).

**B3. The required modal scroll lock does nothing.** §4.3: "Body scroll is locked while the overlay
is open." `body.scroll-locked { overflow: hidden }` (`index.html:95`) is applied correctly, but
because `html` has `overflow-x: hidden` (`index.html:84`) the root's overflow is no longer
`visible`, so the viewport takes its overflow from `<html>` and the body's `overflow` is **not**
propagated. Measured with a dialog open at 900×700: six wheel events over the backdrop scrolled the
background **398px** (570 → 968). Applying the same lock to `<html>` instead gives a delta of **0**.
The tester's check ("`body.scroll-locked` is applied … confirmed") only asserted the class was
present, not that scrolling stopped — a textbook green-test/wrong-behaviour pair. **Fix:** lock the
scrolling element (`document.documentElement.classList.add('scroll-locked')` plus
`html.scroll-locked { overflow: hidden }`), keeping the body rule for browsers where body is the
scroller.

## Should fix

**S1. Case-study cards are invalid HTML and destroy the Work section's heading outline.**
`index.html:739-781` — each `.case-card` is a `<button>` whose children are `<h3>`, `<p>` and `<dl>`.
`<button>`'s content model is *phrasing* content; `h3`/`p`/`dl`/`div` are flow content, so this will
not validate. The practical consequence is worse than pedantry: the accessible name of card 1 is the
whole card concatenated —

> `"01 Mobile App & In-Car Infotainment Mobility Payments Solutions RoleSenior Product Designer TimelineQ3 2022 – present Researched and developed a design system utilising Google Automotive OS — shown at CES 2024/2025."`

— and because headings inside a button are collapsed into the button's name, the Work panel exposes
**no case-study headings at all** to a screen-reader heading list. For a portfolio whose own About
copy claims a commitment to accessibility and inclusive design, this is the finding most at odds
with the site's message. **Fix:** make the card an `<article>` containing a real `<h3>` and a
"View case study" `<button>` stretched over the card with `::after { position:absolute; inset:0 }`
(the standard card-link pattern), or keep the button but replace the inner flow elements with
`<span>`s and give it an explicit `aria-label` ("Case study 1: Mobile App & In-Car Infotainment").
Spec §4.3 only requires the card be a keyboard-focusable button — the first pattern satisfies that
while staying valid.

**S2. Print output omits the case studies.** `index.html:687` hides all four `<dialog>`s in print
while `.panel[hidden]` is forced visible. The printed "single document" therefore contains the four
card summaries and nothing of the actual case-study text — the substance of the Work section.
§5 only literally requires the three panels expanded and the tab nav hidden, so this is not a
criterion failure, but the intent ("prints as a single document") is not met. Consider printing the
dialog contents inline (`@media print { dialog.case-dialog { display:block !important; position:static; background:none } dialog.case-dialog::backdrop{display:none} .dialog-close{display:none} }`).

**S3. Selecting text inside a dialog and releasing on the backdrop closes it.** `index.html:1186-1188`
closes on any `click` whose `target === dialog`; a drag that starts inside `.dialog-inner` and ends
over the padding fires `click` on the dialog. Verified: the dialog closed mid-selection. **Fix:**
record the `mousedown`/`pointerdown` target and only close when both down and up landed on the
dialog element.

## Nice to have

- **N1. No `hashchange` listener** (`index.html:1095-1098`). Changing the fragment on an already-open
  page (pasting `#lab` into the address bar, or Back after switching tabs) does not change the tab —
  verified. The spec only demands on-load hash reading, so this is within contract, but a three-line
  `window.addEventListener('hashchange', ...)` would remove a surprising dead end.
- **N2. Backdrop is tinted twice.** `dialog.case-dialog` has `background: var(--color-backdrop)`
  (`index.html:590`) *and* `::backdrop` uses the same 0.6-alpha colour (`index.html:598`); in the
  native path they composite to ~0.84 alpha, darker than the token implies. Harmless, but the token
  no longer means what it says.
- **N3. Dead code.** `.visually-hidden` (`index.html:97-105`) is never used in the markup; the
  `.is-open` class toggled at `index.html:1110/1129/1133` has no CSS rule anywhere (the CSS keys off
  `[open]`), so it is inert — `changes.md` calls it "kept for parity", which is fine but should be a
  comment in the file, not a mystery for the next editor.
- **N4. `粵語` has no `lang` attribute** (`index.html:882`). The CJK font fallback is present as
  specified, but `<span lang="yue">粵語</span>` (or `zh-Hant`) would fix screen-reader pronunciation
  and font selection — again, cheap, and consistent with the site's accessibility claim.
- **N5. Close button overlaps the title box on narrow dialogs.** At 375px the `h2` box (right edge
  335) overlaps the close button box (left edge 299) in `#dialog-2`; today the titles wrap early
  enough that nothing visually collides, but a longer title would run under the ✕. `padding-right`
  on `.dialog-inner h2` is `--space-l` (2.5rem) while the button occupies ~3.75rem from the edge.
- **N6. Content details for the human, not for the coder:** the hero chip reads "JP Morgan & Chase"
  (`index.html:720`) — the employer's actual name is **JPMorgan Chase**; the spec and
  `site-content.md` both carry the same wording, so the implementation is faithful, but a factual
  employer name on a portfolio is worth Vivien correcting at source. Also, case study 4's Problem
  prose (`index.html:1014`) softens the spec's figures to "were common, often lasted hours" with the
  precise 90/67/34% carried only by the stat row — accurate, and the spec did ask for a stat row, but
  the prose alone reads vaguer than the source.
- **N7. README wording** (`README.md:3-5`) says the site "reproduces … (Work, About Me) and adds a
  fourth section" — it lists two sections and then calls the third "fourth" (inherited from the
  spec's own phrasing). Trivial, but it is the first sentence a reader sees.
- **N8. No favicon.** Under a real browser + `http.server` the page triggers one `GET /favicon.ico`
  404 — not a spec violation (criterion 13 concerns requests the *page* issues, and headless
  Chromium confirmed exactly one request: the document), but `<link rel="icon" href="data:,">` would
  make the "zero network requests" claim airtight without any external dependency.

## Repo hygiene — clean

- `408480d` adds exactly three files: `.gitignore`, `README.md`, `index.html`. Nothing stray, no
  `node_modules`, no test scripts, no `.DS_Store`, no edits to `.pipeline/` or `.git/`.
- `.gitignore` is `.DS_Store` + `*.log` only; `.pipeline/` is correctly **not** ignored (per §3).
- `.pipeline/spec.md`, `changes.md`, `test-results.md` are present but untracked — the human should
  decide whether to commit the pipeline record alongside the feature (`site-content.md` already is,
  from `dd5dbd0` on main).
- `git branch --merged main` lists only `main`: the feature branch has **not** been merged. Correct.
- README is otherwise accurate: run instructions, the localhost-only Lab note and the "where to edit"
  pointers all match the file as built.

## Pipeline deviation: the mid-run amendment to acceptance criterion 8

What happened: the tester found that criterion 8 ("…an overlay containing that study's Problem
section and its Process section") contradicted §4.3's case-study-3 instruction ("Process / Solution
— label this block **Solution**"); rather than call it a defect, the tester escalated, the
orchestrator edited `spec.md` §6 criterion 8 to carve out case study 3, and the tester re-read the
file to confirm the amendment existed before re-scoring it PASS.

**I agree with the amendment, on the merits and on the process.** On the merits: §4.3 is the specific
instruction and §6 the generic restatement, the specific governs, and `site-content.md:50`
independently confirms the source site labels that block "Solution" — the amended criterion is
*narrower* than the original (it still requires a Problem section and still requires the process
content to be present, merely under its correct heading), so nothing was loosened to accommodate the
code. On the process: the tester refused to adjudicate its own spec conflict, escalated it, and then
verified the amendment in the file rather than taking it on assertion — that is exactly right.

The residual hazard is worth naming for the human: amending a spec mid-run to match an
implementation is the classic way a pipeline marks its own homework, and it is only safe because
this amendment is traceable to a pre-existing, more specific clause and to the source content.
`.pipeline/spec.md` is untracked, so the amendment leaves no diff — if you want an audit trail,
commit the pipeline docs. I found no other place where the spec was bent toward the code.

## Recommendation for the human reviewer

Do not merge as-is; the fixes are ~20 lines and do not touch the architecture, content or security
posture. Ask the coder for one follow-up commit covering **B1, B2/B2a and B3** (all three share a
root cause chain — the `replaceState`-on-load and the blanket `overflow-x: hidden`), plus **S1** if
you want the accessibility claim in the About copy to survive an audit. Then re-verify by opening the
page yourself at 375px and confirming three things the automated suite cannot: that the page opens
on "Vivien Chin" and not on "Work"; that all three tabs and both header links are fully on screen;
and that the page behind an open case study does not scroll. Everything else in the build — content
fidelity, tokens, contrast, keyboard model, dialog fallback, zero network requests, repo hygiene —
is solid and needs no rework.

VERDICT: FIX FIRST
