#!/usr/bin/env python3
"""Long-lived Claude Code sandbox session (create / reuse / prompt / stop)."""

from __future__ import annotations

import argparse
import json
import shlex
import sys
from pathlib import Path

from e2b_code_interpreter import Sandbox

from config import ROOT, e2b_opts, load_template_name, model_envs, sandbox_timeout

STATE_FILE = ROOT / ".sandbox-state.json"
DEFAULT_TTL = 3600  # 1 hour; renewed on each prompt


def save_state(sandbox_id: str, template: str, ttl: int) -> None:
    STATE_FILE.write_text(
        json.dumps(
            {
                "sandbox_id": sandbox_id,
                "template": template,
                "ttl": ttl,
                "api_url": e2b_opts()["api_url"],
                "domain": e2b_opts()["domain"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def load_state() -> dict:
    if not STATE_FILE.exists():
        raise SystemExit(
            "No active session. Run: python session.py start"
        )
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def clear_state() -> None:
    if STATE_FILE.exists():
        STATE_FILE.unlink()


def init_claude_config(sandbox: Sandbox) -> None:
    sandbox.commands.run("echo '{}' > /home/user/.claude.json")


def connect_sandbox(sandbox_id: str, ttl: int | None = None) -> Sandbox:
    opts = e2b_opts()
    return Sandbox.connect(sandbox_id, timeout=ttl, **opts)


def create_sandbox(template: str, ttl: int) -> Sandbox:
    opts = e2b_opts()
    sandbox = Sandbox.create(
        template=template,
        envs=model_envs(),
        timeout=ttl,
        metadata={"purpose": "claude-code-long-session"},
        **opts,
    )
    init_claude_config(sandbox)
    return sandbox


def ensure_running(ttl: int | None = None) -> Sandbox:
    state = load_state()
    sandbox_id = state["sandbox_id"]
    renew = ttl or int(state.get("ttl") or DEFAULT_TTL)
    try:
        sandbox = connect_sandbox(sandbox_id, renew)
        if not sandbox.is_running():
            raise RuntimeError("sandbox not running")
        sandbox.set_timeout(renew)
        return sandbox
    except Exception as exc:
        raise SystemExit(
            f"Cannot reuse sandbox {sandbox_id}: {exc}\n"
            "Start a new one: python session.py start"
        ) from exc


def run_claude(sandbox: Sandbox, prompt: str) -> str:
    cmd = (
        "claude --dangerously-skip-permissions < /dev/null "
        f"-p {shlex.quote(prompt)}"
    )
    result = sandbox.commands.run(cmd, timeout=0)
    out = (result.stdout or "").strip()
    err = (result.stderr or "").strip()
    if err:
        return f"{out}\n--- stderr ---\n{err}".strip()
    return out


def cmd_start(args: argparse.Namespace) -> None:
    template = load_template_name(args.template)
    ttl = args.timeout or sandbox_timeout() or DEFAULT_TTL
    if STATE_FILE.exists() and not args.force:
        state = load_state()
        sid = state.get("sandbox_id")
        try:
            sbx = connect_sandbox(sid, ttl)
            if sbx.is_running():
                sbx.set_timeout(ttl)
                print(f"Reusing running sandbox: {sid}")
                print(f"TTL renewed to {ttl}s")
                save_state(sid, template, ttl)
                return
        except Exception:
            pass

    print(f"Creating long-lived sandbox from template: {template}")
    sandbox = create_sandbox(template, ttl)
    save_state(sandbox.sandbox_id, template, ttl)
    ver = sandbox.commands.run("claude --version")
    print(f"sandbox: {sandbox.sandbox_id}")
    print(f"ttl: {ttl}s (renewed on each prompt)")
    print(f"claude: {(ver.stdout or '').strip()}")
    print("Next: python session.py prompt \"你的任务\"")
    print("Or:   python session.py shell")


def cmd_prompt(args: argparse.Namespace) -> None:
    ttl = args.timeout
    sandbox = ensure_running(ttl)
    state = load_state()
    renew = ttl or int(state.get("ttl") or DEFAULT_TTL)
    sandbox.set_timeout(renew)
    print(f"sandbox: {sandbox.sandbox_id}")
    print(f"prompt: {args.prompt}")
    print(run_claude(sandbox, args.prompt))


def cmd_shell(args: argparse.Namespace) -> None:
    sandbox = ensure_running(args.timeout)
    state = load_state()
    renew = args.timeout or int(state.get("ttl") or DEFAULT_TTL)
    print(f"Interactive Claude Code session — sandbox {sandbox.sandbox_id}")
    print("Commands: /status  /renew  /quit")
    print("Anything else is sent to: claude -p \"...\"")
    while True:
        try:
            line = input("claude> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSession kept alive. Stop later with: python session.py stop")
            return
        if not line:
            continue
        if line in {"/quit", "/exit", ":q"}:
            print("Session kept alive. Stop later with: python session.py stop")
            return
        if line == "/status":
            info = sandbox.get_info()
            print(info)
            continue
        if line == "/renew":
            sandbox.set_timeout(renew)
            print(f"TTL renewed to {renew}s")
            continue
        sandbox.set_timeout(renew)
        print(run_claude(sandbox, line))
        print()


def cmd_status(_: argparse.Namespace) -> None:
    state = load_state()
    sid = state["sandbox_id"]
    try:
        sandbox = connect_sandbox(sid)
        running = sandbox.is_running()
        info = sandbox.get_info() if running else None
        print(f"sandbox_id: {sid}")
        print(f"running: {running}")
        if info:
            print(info)
    except Exception as exc:
        print(f"sandbox_id: {sid}")
        print(f"running: False ({exc})")


def cmd_stop(_: argparse.Namespace) -> None:
    if not STATE_FILE.exists():
        print("No session file.")
        return
    state = load_state()
    sid = state["sandbox_id"]
    try:
        sandbox = connect_sandbox(sid)
        sandbox.kill()
        print(f"Destroyed sandbox: {sid}")
    except Exception as exc:
        print(f"Could not destroy {sid}: {exc}")
    clear_state()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Long-lived Claude Code sandbox session")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("start", help="Create or reuse a long-lived sandbox")
    s.add_argument("--template", default=None)
    s.add_argument(
        "--timeout",
        type=int,
        default=None,
        help=f"Lifetime in seconds (default {DEFAULT_TTL} or E2B_SANDBOX_TIMEOUT)",
    )
    s.add_argument("--force", action="store_true", help="Always create a new sandbox")
    s.set_defaults(func=cmd_start)

    pr = sub.add_parser("prompt", help="Run one Claude Code prompt on the session")
    pr.add_argument("prompt", help="Prompt text")
    pr.add_argument("--timeout", type=int, default=None, help="Renew TTL seconds")
    pr.set_defaults(func=cmd_prompt)

    sh = sub.add_parser("shell", help="Interactive multi-prompt session")
    sh.add_argument("--timeout", type=int, default=None)
    sh.set_defaults(func=cmd_shell)

    st = sub.add_parser("status", help="Show session status")
    st.set_defaults(func=cmd_status)

    sp = sub.add_parser("stop", help="Destroy the long-lived sandbox")
    sp.set_defaults(func=cmd_stop)
    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
