/* The Healer's proxy: the portfolio page posts { path, messages }, this Worker
   adds the persona and the archive, asks Claude, and returns { reply }.
   The API key is a Worker secret, so it never reaches the browser. */
import Anthropic from '@anthropic-ai/sdk';
import archive from '../../../assets/healer-archive.json';
import { MODEL, MAX_TOKENS, PATHS, buildSystem, validate } from './prompt.js';

const SYSTEM = {};
PATHS.forEach(function (p) { SYSTEM[p] = buildSystem(archive, p); });

function cors(origin) {
  return {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin'
  };
}

function json(status, data, origin) {
  return new Response(JSON.stringify(data), {
    status: status,
    headers: Object.assign({ 'Content-Type': 'application/json' }, origin ? cors(origin) : {})
  });
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const allowed = (env.ALLOWED_ORIGINS || '').split(',').map(function (s) { return s.trim(); });
    if (!allowed.includes(origin)) { return json(403, { error: 'origin' }); }

    if (request.method === 'OPTIONS') { return new Response(null, { status: 204, headers: cors(origin) }); }
    if (request.method !== 'POST') { return json(405, { error: 'method' }, origin); }

    if (env.LIMITER) {
      const key = request.headers.get('CF-Connecting-IP') || 'anon';
      const { success } = await env.LIMITER.limit({ key: key });
      if (!success) { return json(429, { error: 'slow-down' }, origin); }
    }

    let body;
    try { body = await request.json(); } catch (e) { body = null; }
    const v = validate(body);
    if (v.error) { return json(400, { error: v.error }, origin); }

    const client = new Anthropic({ apiKey: env.ANTHROPIC_API_KEY });
    try {
      const msg = await client.messages.create({
        model: MODEL,
        max_tokens: MAX_TOKENS,
        cache_control: { type: 'ephemeral' },
        system: SYSTEM[v.path],
        messages: v.messages
      });
      const reply = msg.content
        .filter(function (b) { return b.type === 'text'; })
        .map(function (b) { return b.text; })
        .join('')
        .trim();
      if (!reply) { return json(502, { error: 'empty' }, origin); }
      return json(200, { reply: reply }, origin);
    } catch (err) {
      /* The page falls back to its own archive on any non-200, so the visitor
         still gets an answer; the detail only goes to `wrangler tail`. */
      if (err instanceof Anthropic.RateLimitError) {
        console.error('anthropic rate limit', err.status);
        return json(429, { error: 'busy' }, origin);
      }
      if (err instanceof Anthropic.APIError) {
        console.error('anthropic api error', err.status, err.message);
        return json(502, { error: 'upstream' }, origin);
      }
      console.error('worker error', err && err.message);
      return json(500, { error: 'worker' }, origin);
    }
  }
};
