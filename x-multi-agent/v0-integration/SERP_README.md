# V0 SERP API 安全对接（服务端代理）

按「Next.js API Route 保管密钥 → 前端只调自己的 `/api/serp`」模式集成你的 SERP 服务商。

> 我无法登录操作你的私有 V0 聊天页；请把本目录文件拷进 V0 项目，或把下面提示词贴给 v0.app。

## 文件

| 文件 | 作用 |
|------|------|
| `app/api/serp/route.ts` | 安全调用第三方 SERP（密钥只在服务端） |
| `components/SerpSearchBox.tsx` | 前端示例（只请求 `/api/serp`） |

## Vercel / V0 环境变量

| Name | 必填 | 说明 |
|------|------|------|
| `SERP_API_KEY` | 是 | 你的服务商 API Token |
| `SERP_API_URL` | 是 | 服务商完整接口地址，如 `https://api.xxx.com/v1/search` |
| `SERP_API_METHOD` | 否 | `POST`（默认）或 `GET` |
| `SERP_API_AUTH_HEADER` | 否 | 默认 `Authorization` |
| `SERP_API_AUTH_PREFIX` | 否 | 默认 `Bearer`；若服务商要原始 token，设为空字符串 |
| `SERP_API_KEY_QUERY` | 否 | 设为 `true` 时把 key 放进 query（部分旧接口） |

加完后 **Redeploy**。

## 调用方式

前端 / V0 页面：

```ts
// GET
fetch('/api/serp?keyword=' + encodeURIComponent('ai store'))

// POST
fetch('/api/serp', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ keyword: 'ai store', gl: 'us', hl: 'en' }),
})
```

**不要**在浏览器代码里写 `SERP_API_KEY`。

## 贴给 v0.app 的提示词

打开：https://v0.app/leedh994-3414s-projects/chat/mLYABHGNIet

发送：

```
Add a secure Next.js App Router API route at app/api/serp/route.ts that proxies to my third-party SERP provider.

Rules:
1. Read SERP_API_KEY and SERP_API_URL from process.env only (never expose to client).
2. Support GET /api/serp?keyword=... and POST /api/serp with JSON { keyword, gl?, hl?, engine?, num? }.
3. Default upstream method POST with Authorization: Bearer <SERP_API_KEY> and JSON body { q, keyword, ... }.
4. Return JSON { ok, keyword, data } on success; clear errors if env missing or upstream fails.
5. Add a simple client component components/SerpSearchBox.tsx that calls /api/serp only.
6. Remind me to set Vercel env: SERP_API_KEY, SERP_API_URL, then Redeploy.

Use this implementation pattern (adapt as needed):
- token = process.env.SERP_API_KEY
- if (!token) return 500
- fetch(SERP_API_URL, { method:'POST', headers:{Authorization:`Bearer ${token}`,'Content-Type':'application/json'}, body: JSON.stringify({ q: keyword }) })
- return NextResponse.json(data)
```

## 和发推 API 的关系

- 发推：`/api/tweet` → `TWEET_AGENT_URL`
- 搜索：`/api/serp` → `SERP_API_URL` + `SERP_API_KEY`

两套互不影响，都是「密钥只放服务端」同一模式。
