# Spec — Vivien Chin portfolio site

Branch: `feature/portfolio-site` · Repo root: `/Users/aiviv/portfolio`

> This spec is self-contained. All copy you need is reproduced below — you do not need to read any other file.

---

## 1. Overview

Build a personal portfolio site for Vivien Chin, Senior Product Designer, that reproduces the content of her existing Framer site (identity, 4 case studies, About Me) and adds a fourth section, **Lab / Currently Building**, linking to 4 locally-running apps.

It is a static, single-page site with tabbed navigation. No backend, no forms, no analytics, no build step. This is a designer's own portfolio: visual polish and typographic craft are the primary quality bar.

---

## 2. Chosen stack

**Single self-contained `index.html`: semantic HTML + hand-written CSS in one `<style>` block + a small vanilla-JS block. Zero dependencies, zero CDN, zero build.**

Rationale: the content is entirely static, so React/Babel-Standalone would add a runtime transpile flash and a CDN dependency for no benefit — and a Tailwind CDN would not render at all offline. Hand-written CSS with custom properties gives full control over type scale and spacing, which matters most for a designer's portfolio, and guarantees identical rendering under `file://` and `python3 -m http.server`.

Hard rules:
- **No external network requests of any kind.** No Google Fonts, no CDN, no icon library, no analytics. Use a system font stack.
- **No `<img>` files.** No imagery from the Framer site is available. Use typography, colour, CSS gradients, and inline `<svg>` for all visual interest.
- All JS must be inline in `index.html` and run without modules (no `type="module"`, no `import`) so `file://` works.

---

## 3. File-by-file plan

| Path | Action | Contents |
|---|---|---|
| `/Users/aiviv/portfolio/index.html` | **create** | The entire site: `<head>` meta, `<style>`, semantic markup for all 4 sections, inline `<svg>` icons, and one `<script>` at end of `<body>`. |
| `/Users/aiviv/portfolio/README.md` | **create** | ~20 lines: what this is, how to open it (`open index.html` or `python3 -m http.server 8090`), a note that Lab links are localhost-only, and where to edit content (the `<style>` tokens block and the section markup). |
| `/Users/aiviv/portfolio/.gitignore` | **create** | `.DS_Store` and `.pipeline/` are NOT ignored — only add `.DS_Store` and `*.log`. |

Do **not** create `assets/`, `css/`, or `js/` directories. Do not modify anything in `.pipeline/` or `.git/`.

---

## 4. Page structure

```
<body>
  <header class="site-header">        ← name/title left, tab nav right
  <main>
    <section id="work"    role="tabpanel">
    <section id="about"   role="tabpanel">
    <section id="lab"     role="tabpanel">
  </main>
  <footer>
  <div id="case-dialog">              ← case-study overlay (see 4.3)
</body>
```

### 4.1 Header + hero

- **Name:** Vivien Chin
- **Title:** Senior Product Designer
- **Location:** London, United Kingdom 🇬🇧
- **Bio line:** "Senior Product Designer with 10+ years of experience in fintech, enterprise systems, and AI-driven design — turning complex business challenges into simple, delightful user experiences."
- Hero also shows, as small typographic chips/pills, the current + previous employers: `JP Morgan & Chase (Payments B2B2C) — current`, `QVC`, `BT`, `Ordre (Fashion Fintech)`, `Upgrade Pack (HR Fintech)`.
- Secondary line: "5+ years Digital Marketing in London and Hong Kong; background in data analytics."

The hero sits above the tab panels and is always visible (it is not part of any tab).

### 4.2 Tab navigation

Three tabs: **Work** · **About Me** · **Currently Building**. Work is the default.

Behaviour (vanilla JS):
- Tab buttons are real `<button>` elements inside `<nav role="tablist">`, each with `role="tab"`, `aria-selected`, `aria-controls`, and `id` wired to its panel's `aria-labelledby`.
- Clicking a tab: set `aria-selected="true"` on it and `false` on the others; show its panel (`hidden` attribute toggled on the other two).
- Also sync to `location.hash` (`#work`, `#about`, `#lab`) via `history.replaceState` so a tab is linkable; on load, read `location.hash` and activate the matching tab, defaulting to Work for any unknown/empty hash.
  - Note: `history.replaceState` throws in some `file://` contexts — wrap it in `try/catch` and fall back to doing nothing. Do **not** assign to `location.hash` directly (it scrolls the page).
- Keyboard: ArrowLeft/ArrowRight move between tabs and activate; Home/End jump to first/last.

The source site's nav also listed **LinkedIn** and **Résumé**. Render these as two right-aligned links in the header, styled distinctly from the tabs, both pointing to `#` with `data-todo` — see OPEN QUESTIONS.

### 4.3 Work section — 4 case-study cards

A responsive grid of 4 cards (2-up on ≥900px, 1-up below). Each card shows: an ordinal/index, the project title, the client, the role, the timeline, and a 1-line summary. Cards are keyboard-focusable buttons.

Clicking a card opens the **full case study** in a modal overlay built on the native `<dialog>` element (`showModal()` / `close()`), one `<dialog>` reused and populated from a JS data array, OR four pre-rendered `<dialog>` elements — implementer's choice. Requirements either way:
- `Escape` closes it; clicking the backdrop closes it; there is a visible close button.
- Focus moves into the dialog on open and returns to the triggering card on close.
- **Fallback:** if `HTMLDialogElement.prototype.showModal` is undefined, fall back to toggling a plain `.is-open` class on an absolutely-positioned overlay `<div>`. The site must never leave the user with an unopenable card.
- Body scroll is locked while the overlay is open.

Every case study uses the same sub-heading structure: **Role & timeline · Problem · Process · Outcome**. Where the source has no outcome, omit the Outcome block entirely (do not invent one, do not print "N/A").

#### Case study 1 — In-Car Payments
- **Card title:** Mobile App & In-Car Infotainment
- **Client / context:** Mobility Payments Solutions
- **Card summary:** "Researched and developed a design system utilising Google Automotive OS" — shown at CES 2024/2025.
- **Role:** Senior Product Designer · **Timeline:** Q3 2022 – present
- **Problem:** A white-label wallet for seamless, secure payments made directly from the automotive OS — covering EV charging, parking, QSR ordering, and device binding.
- **Process:** Competitive analysis; cross-functional workshops with product, legal and engineering; mobility-scenario user research (short trips, commuting, road trips); prototyping on Google Automotive OS with Samsung S9 tablet demos; iterating within Automotive OS and design-system constraints.
- **Outcome:** Secured key technical partnerships in 2023; pursuing a first pilot client and solution integration for 2024.
- **Target users:** Drivers and passengers; demoed to OEM brand partners.

#### Case study 2 — Livestreaming via Qurio App (QVC)
- **Card title:** Livestreaming via Qurio App
- **Client / context:** QVC — presenter, viewer and moderator flows
- **Card summary:** Designing a livestream experience for a 40–60 audience on small screens.
- **Role:** UX/UI Designer and Researcher · **Timeline:** 2 months (8 sprints)
- **Problem:** An aging user base (40–60) on smaller phones. Reduce cognitive load while balancing button sizes and feature prioritisation across viewing, questioning and interaction.
- **Process:** Host interviews (livestream setup, feature navigation, comment readability); validation sessions with 5 potential viewers (badge comprehension, reminders); a 5-person cross-functional team; systematised decision logic validated with developers plus clear documentation.
- **Outcome:** "First livestreaming was a success." Render these four as a stat row (big number + label):
  - **32%** of the user base joined
  - **13%** submitted questions
  - **74%** used hearts
  - **85%** badge comprehension
  - Plus a closing line: "Research also surfaced demand for native calendar integration and more product information for upcoming events."

#### Case study 3 — Merchants Onboarding (JP Morgan UK)
- **Card title:** Merchants Onboarding
- **Client / context:** JP Morgan UK
- **Card summary:** Complex onboarding process to activate payments and enable payouts (web, mobile) — KYB onboarding built on JPM's SALT design system.
- **Role:** Senior Product Designer, working with a product lead, PM, full-stack developers, legal and QA · **Timeline:** Q3 2025
- **Problem:** Merchants invited to additional programmes received Sign Up links instead of Sign In, and there was no automatic Sign In for ongoing onboardings — causing redundant steps and delays.
- **Process / Solution** (label this block **Solution**): Invitation-link logic that detects existing accounts and serves the right CTA; automatic Sign In flows for active onboardings; streamlined marketplace selection after authentication; the ability to edit multiple applications concurrently under one email.
- **Outcome:** *omit — not stated on source site.*

#### Case study 4 — Hackathon | APEX AI Assistant
- **Card title:** APEX AI Assistant
- **Client / context:** JP Morgan hackathon — 🏆 6th place of 32 groups
- **Card summary:** A 48-hour hackathon concept for automated internal tech-issue resolution.
- **Role:** UX/UI Designer and Researcher · **Timeline:** 48 hours, June 2024
- **Problem:** Research with internal respondents found **90%** faced tech problems preventing work, **67%** had issues lasting 2+ hours, and **34%** found resolution hard or very hard. The existing chatbot required website access and agent support. (Render the three percentages as a stat row.)
- **Process:** Research with 18 internal employees; 3 core user stories (issue identification, team communication, quick resolution); a team of product designers, service designers, LLM architects and developers.
- **Solution:** Automated issue identification; learns from internal data and past queries; resolves via automated fixes, suggested solutions, or ticket escalation; works online and offline.

### 4.4 About Me section

Structure it as an intro paragraph, then labelled blocks. Copy:

- **Intro:** "A curious and passionate problem-solver with a strong sense of empathy," committed to accessibility and inclusive design. UX/CX design across fintech, enterprise and AI, following five earlier years in digital advertising — fast-paced and client-facing, which built adaptability and communication.
- **Philosophy (pull-quote treatment):** "Design experiences that are not only impactful but also practical — delivering solutions that genuinely empower users."
- **Product design clients** (list/chips): JP Morgan (Payments), QVC, BT Group, Upgrade Pack, Ordre, Sun Life Financial Insurance, Attitude is Everything.
- **Digital marketing clients** (list/chips): Jack Wills, Links of London, Bare Minerals, Dixons, Currys PC World, Ralph Lauren, Hilton Worldwide, and other luxury and retail brands.
- **Training & focus areas** (list): Persuasive Emotional Design · Design Tradeoffs & UX Decision-Making · Facilitating UX Workshops · Complex Apps for Specialized Domains.
- **Beyond work** (4 items, each a short title + line):
  - *Volunteer design* — design guidelines for @buddhist.connected.hk since March 2024.
  - *Sound healing* — trained in Nepal in late 2024; hosts events in London.
  - *Photography & travel* — nature, architecture, dramatic skies.
  - *Aerial arts* — hoops, silks and trapeze since summer 2024.
- **Links:** LinkedIn · Résumé · Photography portfolio — same treatment as header links, see OPEN QUESTIONS.

### 4.5 Currently Building (Lab) section

Intro line: "Side projects I'm designing and building myself. These run locally on my own machine, so the links below only resolve there."

Four cards, each with: app name, one-liner, the link, a **"Runs locally"** badge, and a small `<code>` line showing the address.

| Name | href | One-liner | Address shown |
|---|---|---|---|
| Taroscope | `http://localhost:8787` | Tarot / I-Ching reading app with RAG and a feedback-loop learning layer. | `localhost:8787` — reading API; front end is a local `index.html` |
| Daily News Dashboard | `http://127.0.0.1:8793` | Bilingual EN/粵語 NYT-style daily news page covering UK, London, HK and Global. | `127.0.0.1:8793` |
| Finance Hub | `http://localhost:3000` | Personal finance dashboard — portfolio, spending, news and daily briefings. | `localhost:3000` |
| Orchestrator | `http://127.0.0.1:8083` | Director-driven planner → coder → tester → reviewer agent web app. | `127.0.0.1:8083` |

Graceful-degradation requirements (**no health checks, no `fetch`, no `<img>` pings — the page must make zero network requests**):
- Each card carries a persistent, always-visible "Runs locally" badge, so the state is honest whether or not the app is up.
- Links open in a new tab: `target="_blank" rel="noopener noreferrer"`.
- Below the grid, a single explanatory note: "If a link doesn't load, that app's local server isn't running." Do not attempt to detect this.
- Taroscope's card must note that its front end is a local HTML file and that `localhost:8787` is the reading API.

### 4.6 Footer

`© 2026 Vivien Chin · London` plus the LinkedIn / Résumé links. No form, no email harvest beyond what the source site had (the source had none — do not add one).

---

## 5. Visual direction

Not prescriptive on palette, but these are requirements:

- Define all colour, spacing, radius and type-scale values as CSS custom properties in a single `:root` block at the top of `<style>` so they are trivially editable.
- System font stack only, e.g. `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`, with a serif or mono stack available for accents. Include a CJK-safe fallback (e.g. `"PingFang SC", "Hiragino Sans GB", sans-serif`) so 粵語 renders correctly.
- Clean, minimal, contemporary — matching the source site's character. Sparing emoji (the 🇬🇧 and 🏆 above are the only ones required).
- Large, confident type scale using `clamp()` for fluid sizing. Generous whitespace.
- Responsive: must be usable and attractive at 375px, 768px and 1440px widths. No horizontal scrollbar at any width ≥320px.
- `prefers-reduced-motion: reduce` must disable all transitions/animations.
- Visible `:focus-visible` outlines on every interactive element.
- Text contrast at least 4.5:1 against its background (this is an accessibility-committed designer's site).
- A `@media print` block that shows all three panels expanded and hides the tab nav, so the page prints as a single document.

---

## 6. Acceptance criteria (tester-verifiable)

1. `/Users/aiviv/portfolio/index.html` exists and is the only HTML file at the repo root.
2. Opening the file via `file://` renders the full site with correct styling and no console errors. Opening via `python3 -m http.server` from the repo root renders identically.
3. The HTML source contains **no** `http://` or `https://` URL in a `src`, `href`-to-stylesheet, `<link rel="stylesheet">`, `<script src>`, or `@import` position. The only absolute URLs allowed are the four `localhost`/`127.0.0.1` Lab hrefs (and any external profile links resolved under OPEN QUESTIONS). Grep check: no `cdn`, no `fonts.googleapis`, no `unpkg`, no `jsdelivr`.
4. There are **zero** `<img>` tags. Any graphics are inline `<svg>` or CSS.
5. Three tabs exist and are exclusive: clicking each one shows exactly one panel and hides the other two. Work is active on load.
6. Loading `index.html#lab` activates the Currently Building tab; `index.html#nonsense` falls back to Work without error.
7. Arrow-key navigation moves between tabs; every tab and card is reachable by Tab key with a visible focus ring.
8. All four case-study cards open a readable overlay containing that study's Problem section and its Process section — except case study 3, whose process block is deliberately headed "Solution" per §4.3. Escape closes it. Focus returns to the card that opened it.
9. Case study 3's overlay contains no "Outcome" heading.
10. Case study 2's overlay contains the strings `32%`, `13%`, `74%`, `85%`; case study 4's contains `90%`, `67%`, `34%`.
11. The About panel contains all 7 product-design client names and all 4 "Beyond work" items.
12. The Lab panel contains exactly 4 cards with hrefs `http://localhost:8787`, `http://127.0.0.1:8793`, `http://localhost:3000`, `http://127.0.0.1:8083`, each with `target="_blank"` and `rel` containing `noopener`, and each showing a "Runs locally" badge.
13. With every local server stopped, the Lab panel still renders fully — no spinner, no error state, no blank card. The page issues no network requests at all (verifiable in the Network tab: only the document itself).
14. No horizontal scrollbar at 320px, 375px, 768px, 1440px viewport widths.
15. `README.md` and `.gitignore` exist at the repo root.

---

## 7. Out of scope

Contact form; blog; CMS; image assets; dark-mode toggle (a `prefers-color-scheme` block is optional and allowed, but not required); analytics; any server-side code; any npm dependency or `package.json`.

---

## OPEN QUESTIONS

*(Resolved by the orchestrator on 2026-07-27, fetched from the live Framer site — use these real URLs everywhere the spec says "see OPEN QUESTIONS"; no placeholders needed.)*

- **LinkedIn:** `https://www.linkedin.com/in/chincc`
- **Résumé:** `https://vivchindesign.framer.website/resume` (a page on the existing Framer site)
- **Photography portfolio:** `https://vivchindesign.framer.website/photography` (a page on the existing Framer site)

All three open in a new tab with `target="_blank" rel="noopener noreferrer"`. These are the only permitted external `href`s besides the four Lab localhost links (acceptance criterion 3 stands: still no external scripts, stylesheets, fonts, or images).

OPEN QUESTIONS: NONE
