# V0 生成发推 App 的提示词（可直接粘贴）

把下面整段粘贴到 [v0.dev](https://v0.dev)：

---

Build a clean Twitter/X posting dashboard for brand **Pzhisen**.

## Layout
- Title: “Pzhisen Tweet Studio”
- Input: topic / brief (textarea)
- Selects: language (`en` / `zh`), brand voice (default `Pzhisen`)
- Tweet preview textarea (editable)
- Buttons:
  1. Generate (AI only)
  2. One-click Generate & Publish
  3. Publish current draft
- Result panel showing success/error and tweet URL

## Backend API (already running)
Call these JSON APIs (no auth header needed for local demo):

Base URL: `http://127.0.0.1:8787`

1) Generate only
`POST /api/generate`
```json
{ "topic": "...", "lang": "en", "brand": "Pzhisen" }
```
Response: `{ "tweet": "..." }`

2) One-click generate + publish
`POST /api/one-click`
```json
{ "topic": "...", "lang": "en", "brand": "Pzhisen" }
```
Response: `{ "tweet": "...", "result": { "data": { "id": "...", "text": "..." } } }`
Tweet URL = `https://x.com/Pzhise/status/{id}`

3) Publish current draft
`POST /api/publish`
```json
{ "tweet": "...", "topic": "..." }
```

## UX
- Disable buttons while loading
- Show toast / status text
- After publish, show clickable X status link
- Mobile responsive, dark modern UI
- Do not invent other backend routes

Use Next.js App Router + TypeScript + Tailwind.

---

生成后：
1. 把 V0 代码下载/同步到本地
2. 若 V0 预览域名跨域，确认后端已开 CORS（`tweet_app.py` 已开）
3. 本地同时运行后端：`python tweet_app.py`
4. 前端里把 API base 配成 `http://127.0.0.1:8787`
