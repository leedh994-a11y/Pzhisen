Add a secure Next.js App Router API route at app/api/serp/route.ts that proxies to my third-party SERP provider.

Rules:
1. Read SERP_API_KEY and SERP_API_URL from process.env only (never expose to client).
2. Support GET /api/serp?keyword=... and POST /api/serp with JSON { keyword, gl?, hl?, engine?, num? }.
3. Default upstream method POST with Authorization: Bearer <SERP_API_KEY> and JSON body { q, keyword, ... }.
4. Return JSON { ok, keyword, data } on success; clear errors if env missing or upstream fails.
5. Add a simple client component components/SerpSearchBox.tsx that calls /api/serp only.
6. Remind me to set Vercel env: SERP_API_KEY, SERP_API_URL, then Redeploy.

Do not put any API keys in client components. Frontend may only call /api/serp.
