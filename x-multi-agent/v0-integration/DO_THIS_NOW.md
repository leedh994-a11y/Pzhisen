# 同步进 V0 并 Redeploy

## 我这边卡在哪

Cloud Agent **没有**你的 V0 / Vercel 登录态，也没有 `VERCEL_TOKEN`，所以无法替你点 Publish / Redeploy。

任选一条路径即可完成：

---

## 路径 1（最快）：把提示词贴进你的 V0 聊天

打开：https://v0.app/leedh994-3414s-projects/chat/mLYABHGNIet

粘贴发送下面整段，等它改完文件后点 **Publish / Redeploy**：

```
Sync these server routes and UI into this Next.js App Router project.

IMPORTANT:
- Provider is tok.mom (OpenAI-compatible), NOT a SERP search API.
- Upstream request must be EXACTLY:
  POST ${OPENAI_API_BASE}/chat/completions
  Authorization: Bearer ${OPENAI_API_KEY}
  Content-Type: application/json
  body: { "model": "gpt-4o-mini", "messages": [...], "stream": false }

Env already configured on Vercel/V0 (use these names only):
- OPENAI_API_KEY
- OPENAI_API_BASE=https://api.tok.mom/v1
- OPENAI_MODEL=gpt-4o-mini (optional)

Create / overwrite these files:

1) app/api/chat/route.ts
- runtime nodejs, dynamic force-dynamic
- Read OPENAI_API_KEY and OPENAI_API_BASE (alias LLM_API_URL)
- Normalize base: strip trailing slash and trailing /chat/completions; if no /v1 suffix, append /v1
- POST and GET handlers
- GET ?prompt=... wraps into messages
- POST accepts full OpenAI body { model, messages, ... } or { prompt }
- On success return { ok:true, upstream, data:<provider json> }
- Never expose the API key to the client

2) app/api/serp/route.ts
- Compatibility wrapper: keyword/q/prompt OR messages → same tok.mom chat/completions call
- Same env vars and same Authorization Bearer + JSON body shape
- Return { ok, keyword, model, upstream, content, data }

3) components/ChatBox.tsx
- Client component; only fetch('/api/chat') with OpenAI body
- Show response content from data.choices[0].message.content

4) components/SerpSearchBox.tsx
- Client component; only fetch('/api/serp') with { model, messages, keyword }
- Show content + raw JSON

5) Update the main page to render ChatBox (and optionally SerpSearchBox).

Frontend must ONLY call /api/chat or /api/serp. Do not call api.tok.mom from the browser.
After generating, remind me to Redeploy / Publish so env vars apply.
```

确认环境变量仍在（Settings → Environment Variables）：

| Name | Value |
|------|--------|
| `OPENAI_API_KEY` | 你的 tok.mom `sk-...` |
| `OPENAI_API_BASE` | `https://api.tok.mom/v1` |

然后 **Redeploy**。

---

## 路径 2：给我 Vercel Token，我用 CLI 部署本仓库

1. 打开 https://vercel.com/account/tokens → Create  
2. 把 token 发我（或设到对话里），并告诉我要部署到哪个 Vercel 项目名  
3. 我会在 `x-multi-agent/v0-integration` 执行：

```bash
cd x-multi-agent/v0-integration
npx vercel pull --yes --environment=production --token "$VERCEL_TOKEN"
npx vercel deploy --prod --token "$VERCEL_TOKEN"
```

本目录已是可部署的 Next.js 应用（含 `/api/chat`、`/api/serp`、`/api/tweet`）。

---

## 本地自测（部署后）

```bash
curl -X POST "https://你的域名/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"ping"}]}'
```

应返回 `{ "ok": true, "data": { "choices": [...] } }`。
