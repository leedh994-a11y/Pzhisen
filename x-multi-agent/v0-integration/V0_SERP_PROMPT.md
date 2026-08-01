Add a secure Next.js App Router proxy for my LLM provider tok.mom (OpenAI-compatible).

Provider docs / token console: https://api.tok.mom/console/token
Base URL: https://api.tok.mom/v1
Endpoint: POST /chat/completions

Vercel env (already set — use these exact names):
- OPENAI_API_KEY = sk-...
- OPENAI_API_BASE = https://api.tok.mom/v1
- OPENAI_MODEL = gpt-4o-mini (optional default)

Implement:

1) app/api/chat/route.ts
- Server-only. Read OPENAI_API_KEY and OPENAI_API_BASE (alias LLM_API_URL).
- Upstream URL = `${OPENAI_API_BASE.replace(/\/+$/,'')}/chat/completions`
- POST with headers:
  Authorization: Bearer ${OPENAI_API_KEY}
  Content-Type: application/json
- Body must be exact OpenAI chat.completions JSON:
  { "model": "...", "messages": [{ "role": "user", "content": "..." }], "stream": false, ... }
- Accept POST /api/chat with that body (or { prompt } → wrap into messages).
- Accept GET /api/chat?prompt=...
- Never expose the key to the client.
- Return { ok: true, data: <provider json> } on success.

2) app/api/serp/route.ts
- Compatibility wrapper: map keyword/q/prompt → same tok.mom chat/completions call (same env vars, same request shape). Do NOT call a SERP search API.

3) components/ChatBox.tsx and/or SerpSearchBox.tsx
- Client only fetches /api/chat or /api/serp. No keys in client code.

Remind me: after copying, Redeploy on Vercel so env vars apply.
