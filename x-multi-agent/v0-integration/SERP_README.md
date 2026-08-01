# tok.mom（OpenAI 兼容）安全对接

服务商：`https://api.tok.mom`（Token 控制台：`https://api.tok.mom/console/token`）

按「Next.js API Route 保管密钥 → 前端只调自己的 `/api/chat` 或 `/api/serp`」集成。

> 这不是 Google SERP。上游请求格式是 **OpenAI Chat Completions**。

## Vercel / V0 环境变量（你已配置）

| Name | 值 |
|------|-----|
| `OPENAI_API_KEY` | tok.mom 的 `sk-...` |
| `OPENAI_API_BASE` | `https://api.tok.mom/v1`（也可用别名 `LLM_API_URL`） |
| `OPENAI_MODEL` | 可选，默认 `gpt-4o-mini` |

加完后 **Redeploy**。

## 上游真实请求（完全匹配服务商）

```http
POST https://api.tok.mom/v1/chat/completions
Authorization: Bearer sk-...
Content-Type: application/json

{
  "model": "gpt-4o-mini",
  "messages": [{ "role": "user", "content": "hello" }],
  "stream": false
}
```

服务端由 `OPENAI_API_BASE` + `/chat/completions` 拼出 URL，并用 `OPENAI_API_KEY` 填 Bearer。

## 文件

| 文件 | 作用 |
|------|------|
| `app/api/chat/route.ts` | 完整 OpenAI 透传代理（推荐） |
| `app/api/serp/route.ts` | 兼容旧路径：keyword → 同上 chat/completions |
| `components/ChatBox.tsx` | 调 `/api/chat` |
| `components/SerpSearchBox.tsx` | 调 `/api/serp` |

## 前端调用

```ts
// 推荐：完整 OpenAI 格式
await fetch('/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model: 'gpt-4o-mini',
    messages: [{ role: 'user', content: 'hello' }],
  }),
})

// 兼容：旧 /api/serp
await fetch('/api/serp', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model: 'gpt-4o-mini',
    messages: [{ role: 'user', content: 'hello' }],
    keyword: 'hello',
  }),
})
```

**不要**在浏览器代码里写 `OPENAI_API_KEY`。

## 贴给 v0.app

见 `V0_SERP_PROMPT.md`。
