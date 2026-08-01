# 请你自己在浏览器完成（我无法登录你的 v0 / Vercel 账号）

## 重要更正

`TWEET_AGENT_URL` **不能**填：
`https://v0.app/leedh994-3414s-projects/chat/mLYABHGNIet`

那是 V0 聊天页，不是发推后端。

当前已为你开好的发推后端公网地址：

```
TWEET_AGENT_URL=https://alumni-retreat-pension-presentations.trycloudflare.com
TWEET_AGENT_TOKEN=change-me-to-a-long-random-secret
```

---

## A. 把下面整段贴给 v0.app 聊天

打开：https://v0.app/leedh994-3414s-projects/chat/mLYABHGNIet

粘贴发送：

```
Build a clean single-page Next.js UI for posting tweets to X account @Pzhise via our backend.

Requirements:
1. One text area where the user types natural language (Chinese or English) describing what to post.
2. Two buttons: "Preview" and "Post to X".
3. Preview calls POST /api/tweet with JSON { "prompt": "<user input>", "dryRun": true }.
4. Post calls POST /api/tweet with JSON { "prompt": "<user input>" }.
5. Show loading state, success/error, generated tweet text, and tweetUrl link when present.
6. Keep the first viewport simple: brand "Pzhisen", one headline "Post to @Pzhise", one short sentence, the form. No cards clutter, no purple gradient theme.
7. Create these files:
   - app/api/tweet/route.ts that proxies to process.env.TWEET_AGENT_URL + "/api/v0/tweet" with Authorization: Bearer process.env.TWEET_AGENT_TOKEN
   - components/TweetComposer.tsx for the UI
8. Remind me to set env vars:
   - TWEET_AGENT_URL=https://alumni-retreat-pension-presentations.trycloudflare.com
   - TWEET_AGENT_TOKEN=change-me-to-a-long-random-secret

Do not invent Twitter API keys in the frontend. All posting goes through /api/tweet only.
```

---

## B. 在 V0 / Vercel 加环境变量

1. 打开 V0 项目 Settings → Environment Variables  
   或 Vercel 项目：https://vercel.com → 你的项目 → Settings → Environment Variables
2. 新增：

| Name | Value |
|------|--------|
| `TWEET_AGENT_URL` | `https://alumni-retreat-pension-presentations.trycloudflare.com` |
| `TWEET_AGENT_TOKEN` | `change-me-to-a-long-random-secret` |

3. 保存后 **Redeploy** 一次

---

## C. 自测后端（可选）

```bash
curl https://alumni-retreat-pension-presentations.trycloudflare.com/health
```

应返回 `"ok": true` 和 `"account": "@Pzhise"`。
