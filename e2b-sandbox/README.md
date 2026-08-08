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

## 2) 创建沙箱并跑 Claude Code

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

## 说明

- 同一模板名可反复 `Sandbox.create()`，不必每次重新 build
- 首次进沙箱会执行 `echo '{}' > ~/.claude.json`，避免配置损坏
- 非交互用 `claude -p`，并加 `--dangerously-skip-permissions` 与 `< /dev/null`
- 官方依赖版本：`e2b==2.31.0`、`e2b-code-interpreter==2.8.1`
