"""Shared Aliyun FC E2B connection / template settings."""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
STATE_FILE = ROOT / ".template-state.json"

load_dotenv(ROOT / ".env")

DEFAULT_FROM_IMAGE = (
    "fc-e2b-registry.cn-hangzhou.cr.aliyuncs.com/runtime/claude-code:v0.0.37"
)
DEFAULT_TEMPLATE_NAME = "claude-code"


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(
            f"Missing {name}. Copy .env.example to .env and fill in credentials."
        )
    return value


def e2b_opts() -> dict[str, str]:
    return {
        "api_key": require_env("E2B_API_KEY"),
        "api_url": os.getenv(
            "E2B_API_URL", "https://api.cn-hangzhou.e2b.fc.aliyuncs.com"
        ).strip(),
        "domain": os.getenv(
            "E2B_DOMAIN", "cn-hangzhou.e2b.fc.aliyuncs.com"
        ).strip(),
    }


def from_image() -> str:
    return os.getenv("E2B_FROM_IMAGE", DEFAULT_FROM_IMAGE).strip() or DEFAULT_FROM_IMAGE


def template_name_base() -> str:
    return (
        os.getenv("E2B_TEMPLATE_NAME", DEFAULT_TEMPLATE_NAME).strip()
        or DEFAULT_TEMPLATE_NAME
    )


def cpu_count() -> int:
    return int(os.getenv("E2B_CPU_COUNT", "2"))


def memory_mb() -> int:
    return int(os.getenv("E2B_MEMORY_MB", "8192"))


def sandbox_timeout() -> int:
    return int(os.getenv("E2B_SANDBOX_TIMEOUT", "600"))


def model_envs() -> dict[str, str]:
    """Bailian / DashScope Anthropic-compatible env for Claude Code."""
    token = os.getenv("BAILIAN_API_KEY", "").strip() or os.getenv(
        "ANTHROPIC_AUTH_TOKEN", ""
    ).strip()
    if not token:
        raise SystemExit(
            "Missing BAILIAN_API_KEY (or ANTHROPIC_AUTH_TOKEN). "
            "Get a sk- key from Bailian console."
        )

    model = os.getenv("ANTHROPIC_MODEL", "qwen3.7-max").strip() or "qwen3.7-max"
    base_url = (
        os.getenv(
            "ANTHROPIC_BASE_URL",
            "https://dashscope.aliyuncs.com/apps/anthropic",
        ).strip()
        or "https://dashscope.aliyuncs.com/apps/anthropic"
    )
    return {
        "ANTHROPIC_AUTH_TOKEN": token,
        "ANTHROPIC_BASE_URL": base_url,
        "ANTHROPIC_MODEL": model,
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": model,
        "ANTHROPIC_DEFAULT_SONNET_MODEL": model,
        "ANTHROPIC_DEFAULT_OPUS_MODEL": model,
    }


def save_template_state(name: str, *, from_image_value: str) -> None:
    STATE_FILE.write_text(
        json.dumps(
            {
                "template": name,
                "from_image": from_image_value,
                "api_url": e2b_opts()["api_url"],
                "domain": e2b_opts()["domain"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def load_template_name(cli_name: str | None = None) -> str:
    if cli_name:
        return cli_name
    if STATE_FILE.exists():
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        name = str(data.get("template") or "").strip()
        if name:
            return name
    env_name = os.getenv("E2B_TEMPLATE_NAME", "").strip()
    if env_name:
        return env_name
    raise SystemExit(
        "No template name. Run build_template.py first, or pass --template NAME."
    )
