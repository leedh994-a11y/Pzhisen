#!/usr/bin/env python3
"""Create a Claude Code sandbox from the built template and run a prompt."""

from __future__ import annotations

import argparse
import shlex

from e2b_code_interpreter import Sandbox

from config import e2b_opts, load_template_name, model_envs, sandbox_timeout


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Create Aliyun E2B Claude Code sandbox and run a prompt"
    )
    p.add_argument(
        "--template",
        default=None,
        help="Template name (default: .template-state.json / E2B_TEMPLATE_NAME)",
    )
    p.add_argument(
        "--prompt",
        default="Create a hello world HTTP server in Go under /home/user/hello",
        help="Prompt passed to `claude -p`",
    )
    p.add_argument(
        "--timeout",
        type=int,
        default=None,
        help="Sandbox lifetime timeout in seconds (default E2B_SANDBOX_TIMEOUT)",
    )
    p.add_argument(
        "--keep-alive",
        action="store_true",
        help="Do not kill sandbox after the prompt finishes",
    )
    p.add_argument(
        "--smoke",
        action="store_true",
        help="Only verify sandbox boot (claude --version), skip prompt",
    )
    return p.parse_args()


def init_claude_config(sandbox: Sandbox) -> None:
    # Required on first boot; otherwise Claude Code may report corrupt config.
    sandbox.commands.run("echo '{}' > /home/user/.claude.json")


def main() -> None:
    args = parse_args()
    template = load_template_name(args.template)
    opts = e2b_opts()
    envs = model_envs()
    timeout = args.timeout if args.timeout is not None else sandbox_timeout()

    print(f"Creating sandbox from template: {template}")
    sandbox = Sandbox.create(
        template=template,
        envs=envs,
        timeout=timeout,
        **opts,
    )
    print(f"sandbox: {sandbox.sandbox_id}")

    try:
        init_claude_config(sandbox)

        version = sandbox.commands.run("claude --version")
        print("claude --version:")
        print((version.stdout or version.stderr or "").strip())

        if args.smoke:
            check = sandbox.commands.run("uname -a && pwd && which claude")
            print(check.stdout.strip())
            return

        cmd = (
            "claude --dangerously-skip-permissions < /dev/null "
            f"-p {shlex.quote(args.prompt)}"
        )
        print(f"Running: {cmd}")
        result = sandbox.commands.run(cmd, timeout=0)
        print(result.stdout)
        if result.stderr:
            print("--- stderr ---")
            print(result.stderr)
    finally:
        if args.keep_alive:
            print(f"Keeping sandbox alive: {sandbox.sandbox_id}")
        else:
            sandbox.kill()
            print("sandbox destroyed")


if __name__ == "__main__":
    main()
