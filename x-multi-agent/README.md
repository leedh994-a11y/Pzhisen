# Pzhisen x-multi Twitter AI Agent

真正能发推的 AI Agent：

- Google Gemini 按话题生成推文
- **推荐：Cookie 发推**（不需要远程桌面 / `npm run login`）
- 备选：x-multi 浏览器自动化发推

## 推荐方案：Cookie 发推（最简单）

不需要 Cursor「控制桌面」，也不依赖 `npm run login`。

### 1) 从浏览器导出 Cookie（电脑 Chrome）

1. 用 Chrome 打开 https://x.com 并确保**已登录**
2. 按 `F12` 打开开发者工具
3. 打开 **Application（应用程序）** → **Cookies** → `https://x.com`
4. 找到并复制这两个值：
   - `auth_token`
   - `ct0`

### 2) 写入 `.env`

```bash
cd x-multi-agent
cp .env.example .env
```

填入：

```bash
GEMINI_API_KEY=你的Gemini密钥
TWITTER_AUTH_TOKEN=粘贴auth_token
TWITTER_CT0=粘贴ct0
TWEET_MODE=cookie
```

### 3) 发推

```bash
npm install
npm run tweet:cookie "Pzhisen AI store overnight first sale"
```

或启动 HTTP API：

```bash
npm run server
curl -X POST http://127.0.0.1:8787/api/tweet \
  -H "Authorization: Bearer change-me-to-a-long-random-secret" \
  -H "Content-Type: application/json" \
  -d '{"topic":"Pzhisen AI store overnight first sale"}'
```

---

## 备选方案：浏览器登录（x-multi）

## 前置条件

- Node.js **18+**
- Chrome / Edge 浏览器
- [Google Gemini API Key](https://aistudio.google.com/app/apikey)
- 可用的 Twitter / X 账号

## 1. 安装

```bash
cd x-multi-agent
npm install
npm run setup
```

编辑 `.env`：

```bash
GEMINI_API_KEY=你的_Gemini_密钥
```

## 2. 首次登录（保存登录态）

在**有图形界面**的电脑上运行（会打开浏览器）：

```bash
npm run login
```

按提示在浏览器里手动登录 Twitter/X（含 2FA），登录成功后按 Enter。  
登录态保存在 `browser-profiles/twitter-pzhisen/`，之后发推一般不用再登。

## 3. AI 生成并发布

```bash
npm run tweet "你的话题"
```

示例：

```bash
npm run tweet "Pzhisen AI store first overnight sale"
npm run tweet "Wake up to orders — AI ads + AI support at 3AM"
```

流程：

1. 打开浏览器 → 进入 Twitter  
2. 检查登录态（未登录则提示手动登录）  
3. Gemini 根据话题生成英文推文  
4. 自动填写并点击 Post  
5. 截图校验是否发布成功  

## 常用命令

| 命令 | 作用 |
|------|------|
| `npm run setup` | 初始化 `.env` + 默认 profile |
| `npm run login` | 预登录并保存会话 |
| `npm run tweet "话题"` | AI 生成内容并真正发推 |
| `npm run profile:list` | 查看账号 profile |
| `npm run persona:list` | 查看发文人设 |

## 目录说明

```
x-multi-agent/
├── .env.example          # 环境变量模板
├── .env                  # 本地密钥（勿提交）
├── config/profiles.json  # 账号配置（可提交）
├── browser-profiles/     # 登录 Cookie / 会话（勿提交）
├── scripts/tweet.mjs     # npm run tweet 入口
├── scripts/setup.mjs     # 一键初始化
└── package.json
```

## 安全注意

- **不要**把 `.env` 或 `browser-profiles/` 提交到 Git
- 密钥与登录 Cookie 只保存在本机 / 服务器私有目录
- 首次登录必须人工完成，Agent **不会**替你存密码

## 故障排查

| 问题 | 处理 |
|------|------|
| 缺少 `GEMINI_API_KEY` | 复制 `.env.example` → `.env` 并填写密钥 |
| 浏览器打不开 | 确认已安装 Chrome/Edge；`HEADLESS=false` |
| 登录校验失败 | 等首页 Timeline 完全加载后再按 Enter |
| 发推失败 | 确认文案 ≤280 字；确认仍在首页而非个人页 |

## 与 v0 / 网站后端对接

本目录可作为网站后端旁路服务运行。在服务器上：

```bash
cd x-multi-agent
npm install
# 配置 .env + 完成 npm run login（首次需有显示环境或远程桌面）
npm run tweet "topic from your backend job"
```

也可启动 HTTP API，供 v0 / 网站调用：

```bash
npm run server
# POST http://127.0.0.1:8787/api/tweet
# Header: Authorization: Bearer <AGENT_API_TOKEN>
# Body: { "topic": "Pzhisen AI store overnight first sale" }
```

curl 示例：

```bash
curl -X POST http://127.0.0.1:8787/api/tweet \
  -H "Authorization: Bearer change-me-to-a-long-random-secret" \
  -H "Content-Type: application/json" \
  -d '{"topic":"Pzhisen AI store — wake up to your first order"}'
```

也可由后端 API / Cron 调用：

```bash
cd /path/to/x-multi-agent && npm run tweet "$TOPIC"
```

> 注意：真正发推依赖本机已保存的 Twitter 登录态（`npm run login`）和有效的 `GEMINI_API_KEY`。云端无图形界面时，请先在本地/带桌面的服务器完成首次登录。
