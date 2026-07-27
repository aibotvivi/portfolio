# Vivien Chin — Portfolio

A single-page portfolio site for Vivien Chin, Senior Product Designer. Reproduces the
content of her Framer site (Work, About Me) and adds a fourth section, **Currently
Building**, linking to locally-running side projects.

## Stack

Plain HTML + hand-written CSS + vanilla JS, all inline in one file. No build step, no
CDN, no framework, no npm dependencies. Everything lives in `index.html`.

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

## Notes on the "Currently Building" tab

The four Lab cards link to `localhost` / `127.0.0.1` addresses for projects that only
run on the author's own machine (Taroscope, Daily News Dashboard, Finance Hub,
Orchestrator). Each card carries a persistent "Runs locally" badge — the page never
checks whether those servers are actually up (no `fetch`, no health checks), so if a
link doesn't load, that app's local server simply isn't running.

## Editing content

- **Design tokens** (colour, spacing, radius, type scale) — the `:root { ... }` block
  at the top of the `<style>` element in `index.html`. Change values there to restyle
  the whole page.
- **Copy and structure** — the semantic markup inside `<body>`: `<header>` for the
  hero, the three `<section>` panels (`#work`, `#about`, `#lab`) for tab content, and
  the four `<dialog>` elements at the end of `<body>` for the full case-study text.
- **Tab / dialog behaviour** — the single `<script>` block at the end of the file.

There is no build step: edit `index.html` directly and refresh the browser.
