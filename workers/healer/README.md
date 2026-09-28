# The Healer — Worker

The proxy between the portfolio's **Askme.bot** window (`#ask`) and Claude. It answers as **Healer Viv** on the healing path and **Vivi at work** on the hiring path. The page
posts `{ path, messages }`; this Worker adds the persona and the archive, calls
`claude-haiku-4-5`, and returns `{ reply }`. The API key is a Worker secret, so it never
reaches the browser.

Until this is deployed and its URL set as `HEALER_ENDPOINT` in `index.html`, the window
answers from `assets/healer-archive.json` alone. It does the same whenever this Worker
errors, times out (15 s) or rate-limits, so a visitor always gets an answer.

## One source of facts

`assets/healer-archive.json` is read by both sides: the page fetches it for its offline
answers, and `src/worker.js` imports it at bundle time for the system prompt. Edit facts
there, then redeploy the Worker. A fact typed into `src/prompt.js` is a fact the offline
path cannot see.

## Deploy

```bash
cd workers/healer
npm install
npx wrangler login
npx wrangler secret put ANTHROPIC_API_KEY
npx wrangler deploy          # prints https://healer.<account>.workers.dev
```

Then set `var HEALER_ENDPOINT = 'https://healer.<account>.workers.dev';` in `setupHealer`
in `index.html`, and push.

Before deploying, set a **monthly spend limit** on the key's workspace in the Anthropic
Console. That is the real ceiling on cost; the rate limit here (10 requests a minute per
address) only stops one tab hammering it.

## Guards

- `ALLOWED_ORIGINS` in `wrangler.toml`: any other `Origin` gets a 403 before a token is spent.
- `path` must be `"healing"` or `"hiring"`; each gets its own persona and its own half of the archive. Anything else gets a 400.
- At most 12 messages of 600 characters each; the page is stateless, and so is this Worker.
- Replies are capped at 400 tokens. Nothing is logged except error statuses.

## Test

```bash
npm run check                 # unit tests for prompt + validation, plain Node
npx wrangler dev --port 8797  # 8787 is taken by the InnerWaves API on this machine
```

For a local key, put `ANTHROPIC_API_KEY=...` in `.dev.vars` (gitignored).
