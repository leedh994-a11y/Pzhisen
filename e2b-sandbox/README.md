# Aliyun FC E2B — Claude Code 沙箱模板

基于阿里云函数计算云沙箱，把官方 Claude Code 镜像构建成可复用模板，并一键拉起 Sandbox 跑任务。

流程：`构建 Template` → `创建 Sandbox` → `运行 Claude Code` → `销毁沙箱`。

## 前置条件

1. 在阿里云函数计算控制台创建 **云沙箱 API Key**
2. 中国站准备百炼 API Key（`sk-` 开头）
3. Python 3.10+

```bash
cd e2b-sandbox
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env：填入 E2B_API_KEY、BAILIAN_API_KEY
```

## 1) 构建模板

```bash
python build_template.py
```

默认按杭州地域（与 API Key 所属地域一致）：

- 镜像：`fc-e2b-registry.cn-hangzhou.cr.aliyuncs.com/runtime/claude-code:v0.0.37`
- 规格：`cpu_count=2`，`memory_mb=8192`
- 接入：`api.cn-hangzhou.e2b.fc.aliyuncs.com`

若 Key 在北京创建，把 `.env` 里的 `E2B_API_URL` / `E2B_DOMAIN` / `E2B_FROM_IMAGE` 改成 `cn-beijing`。

常用参数：

```bash
# 稳定名复用（默认 claude-code）
python build_template.py --name claude-code

# 每次生成唯一名：claude-code-<timestamp>
python build_template.py --unique

# 换镜像版本
python build_template.py --from-image \
  fc-e2b-registry.cn-beijing.cr.aliyuncs.com/runtime/claude-code:v0.0.44
```

构建成功后会写入 `.template-state.json`，后续创建沙箱自动读取模板名。控制台模板状态应为 `ready`。

## 2) 长期使用（推荐）

一次启动，反复提问；沙箱 ID 保存在 `.sandbox-state.json`，每次 prompt 自动续期：

```bash
# 启动长期沙箱（默认存活 3600 秒，可续期）
python session.py start --timeout 3600

# 单次任务
python session.py prompt "Create a hello world HTTP server in Go"

# 交互多轮（输入 /quit 退出交互，沙箱继续存活）
python session.py shell

# 查看状态 / 结束后销毁
python session.py status
python session.py stop
```

## 3) 一次性跑完即销毁

冒烟（只验证启动与 `claude --version`）：

```bash
python run_sandbox.py --smoke
```

跑一个 prompt：

```bash
python run_sandbox.py --prompt "Create a hello world HTTP server in Go"
```

保留沙箱不销毁：

```bash
python run_sandbox.py --keep-alive --prompt "List files in /home/user"
```

## 环境变量

| 变量 | 说明 |
|---|---|
| `E2B_API_KEY` | 云沙箱 API Key |
| `E2B_API_URL` | 默认杭州 `https://api.cn-hangzhou.e2b.fc.aliyuncs.com` |
| `E2B_DOMAIN` | 默认 `cn-hangzhou.e2b.fc.aliyuncs.com` |
| `E2B_FROM_IMAGE` | Claude Code 预置镜像 |
| `E2B_TEMPLATE_NAME` | 模板名，默认 `claude-code` |
| `BAILIAN_API_KEY` | 百炼 Key，注入为 `ANTHROPIC_AUTH_TOKEN` |
| `ANTHROPIC_MODEL` | 默认 `qwen3.7-max` |

## 4) AI 写推文并自动发到 Twitter/X

整体链路：

```text
V0 Web 应用（选题/审核 UI）
    ↓ 调用或人工触发
Claude Code 云沙箱（百炼 Token 生成文案）
    ↓
X/Twitter API（Access Token 发推）
```

1. 去 [X Developer Portal](https://developer.x.com/) 创建 App，权限选 **Read and Write**
2. 复制 4 个密钥到 `.env`：`TWITTER_API_KEY` / `TWITTER_API_SECRET` / `TWITTER_ACCESS_TOKEN` / `TWITTER_ACCESS_TOKEN_SECRET`
3. 确保长期沙箱已启动：`python session.py start`
4. 先干跑（只生成不发）：

```bash
pip install -r requirements.txt
python tweet_pipeline.py --topic "Pzhisen AI agents that run your company overnight" --dry-run
```

5. 确认文案后真实发推：

```bash
python tweet_pipeline.py --topic "Pzhisen AI agents that run your company overnight"
```

6. **一键 Web 界面（推荐）**：

```bash
python tweet_app.py
# 打开 http://127.0.0.1:8787
# 按钮：只生成 / 一键生成并发布 / 发布当前文案
```

API：
- `POST /api/generate` — 只生成
- `POST /api/one-click` — 生成并发布
- `POST /api/publish` — 发布已有文案

V0 应用可直接调用上述 API，把 UI 换成你的页面即可。

## 说明

- 同一模板名可反复 `Sandbox.create()`，不必每次重新 build
- 首次进沙箱会执行 `echo '{}' > ~/.claude.json`，避免配置损坏
- 非交互用 `claude -p`，并加 `--dangerously-skip-permissions` 与 `< /dev/null`
- 官方依赖版本：`e2b==2.31.0`、`e2b-code-interpreter==2.8.1`
- X API 发推通常需付费/按量套餐；App-only Bearer 不能发推，必须用户 Access Token
