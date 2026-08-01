# V0 ↔ Pzhisen Tweet API 对接

用自然语言在 V0 页面输入 → 后端自动发到 `@Pzhise`。

另：tok.mom（OpenAI 兼容）安全代理见 `SERP_README.md`、`app/api/chat/route.ts`、`app/api/serp/route.ts`。

## 架构

```
V0 / Next.js UI
   POST /api/tweet  { "prompt": "自然语言..." }
        ↓
Next.js route (v0-integration/app/api/tweet/route.ts)
        ↓
x-multi-agent  HTTP  :8787/api/v0/tweet
        ↓
Official X API  →  @Pzhise
```

## 1) 启动发推后端（本机或服务器）

```bash
cd x-multi-agent
# .env 已含 TWITTER_API_* 与 GEMINI_API_KEY
npm run server
# listening :8787
```

健康检查：

```bash
curl http://127.0.0.1:8787/health
```

自然语言发推：

```bash
curl -X POST http://127.0.0.1:8787/api/v0/tweet \
  -H "Authorization: Bearer change-me-to-a-long-random-secret" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"发一条 Pzhisen AI 店铺凌晨自动出单的推广推文"}'
```

预览不发：

```bash
curl -X POST http://127.0.0.1:8787/api/v0/tweet \
  -H "Authorization: Bearer change-me-to-a-long-random-secret" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"推广 Pzhisen","dryRun":true}'
```

## 2) 接到 V0 / Next.js 项目

把本目录文件拷进你的 V0 项目：

| 本仓库文件 | 放到 V0 项目 |
|-----------|-------------|
| `app/api/tweet/route.ts` | `app/api/tweet/route.ts` |
| `components/TweetComposer.tsx` | `components/TweetComposer.tsx` |

在页面里使用：

```tsx
import TweetComposer from "@/components/TweetComposer";
export default function Page() {
  return <TweetComposer />;
}
```

或把 `V0_PROMPT.md` 全文粘贴给 v0.app，让它按说明生成页面。

## 3) V0 / Vercel 环境变量

| Name | Value |
|------|--------|
| `TWEET_AGENT_URL` | 发推后端地址，如 `https://your-vps-domain.com` 或本机调试用 tunnel |
| `TWEET_AGENT_TOKEN` | 与后端 `.env` 的 `AGENT_API_TOKEN` 相同 |

> 本机调试时，V0 云端访问不到 `127.0.0.1`。请用 ngrok / cloudflared 把 `:8787` 暴露为 HTTPS，再填到 `TWEET_AGENT_URL`。

示例：

```bash
# 终端 A
cd x-multi-agent && npm run server

# 终端 B
npx cloudflared tunnel --url http://127.0.0.1:8787
# 把给出的 https://xxxx.trycloudflare.com 填进 TWEET_AGENT_URL
```

## 4) 请求 / 响应约定（给 V0 用）

**Request**

```json
{
  "prompt": "用自然语言描述要发的内容",
  "dryRun": false
}
```

也接受：`message` / `topic` / `input`，或精确文案字段 `text`。

**Success response**

```json
{
  "ok": true,
  "account": "@Pzhise",
  "text": "generated or posted tweet",
  "tweetId": "2083...",
  "tweetUrl": "https://x.com/i/web/status/2083...",
  "message": "Tweet posted to X"
}
```

## 安全

- 不要把 Twitter API 密钥写进 V0 前端
- 只把 `TWEET_AGENT_TOKEN` 放在服务端环境变量
- 生产环境请把 `AGENT_API_TOKEN` 改成强随机串
