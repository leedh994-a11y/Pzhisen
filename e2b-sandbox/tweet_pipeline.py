#!/usr/bin/env python3
"""AI generate tweet via Claude Code sandbox, then post to X/Twitter.

Flow:
  1) Claude Code (Aliyun FC sandbox + Bailian) writes tweet text
  2) X API v2 posts it with your user tokens

Required .env extras:
  TWITTER_API_KEY
  TWITTER_API_SECRET
  TWITTER_ACCESS_TOKEN
  TWITTER_ACCESS_TOKEN_SECRET
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv
from requests_oauthlib import OAuth1

from config import ROOT, load_template_name
from session import (
    STATE_FILE,
    create_sandbox,
    ensure_running,
    run_claude,
    save_state,
)

load_dotenv(ROOT / ".env")

HISTORY_FILE = ROOT / ".tweet-history.jsonl"

# Never auto-publish quiz/test tweets to @Pzhise.
TEST_MARKERS = (
    "测试",
    "测验",
    "试发",
    "试运行",
    "连通性",
    "联调",
    "test",
    "testing",
    "quiz",
    "dry-run",
    "dry run",
    "connectivity",
    "ops check",
    "publish path ok",
    "check ",
    " check",
)


def is_test_content(*parts: str | None) -> bool:
    """Return True if topic/tweet looks like a test/quiz post."""
    blob = " ".join(p for p in parts if p).strip().lower()
    if not blob:
        return False
    return any(marker.lower() in blob for marker in TEST_MARKERS)


def assert_not_test_publish(topic: str | None, text: str | None, *, force: bool = False) -> None:
    if force:
        return
    if is_test_content(topic, text):
        raise SystemExit(
            "已拦截：检测为「测试/测验」类推文，禁止自动发布到 @Pzhise。"
            " 仅可生成预览；正式内容请去掉测试字样后再发布。"
        )


def require_twitter_creds() -> dict[str, str]:
    keys = [
        "TWITTER_API_KEY",
        "TWITTER_API_SECRET",
        "TWITTER_ACCESS_TOKEN",
        "TWITTER_ACCESS_TOKEN_SECRET",
    ]
    missing = [k for k in keys if not os.getenv(k, "").strip()]
    if missing:
        raise SystemExit(
            "Missing Twitter API credentials in .env: "
            + ", ".join(missing)
            + "\nCreate an app at https://developer.x.com/ and enable Read+Write."
        )
    return {k: os.environ[k].strip() for k in keys}


def extract_tweet(text: str) -> str:
    """Prefer fenced/json blocks; otherwise keep full generated body (no length cap)."""
    raw = text.strip()
    # ```json {"tweet":"..."} ``` — allow long nested content
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw, re.S | re.I)
    if m:
        try:
            data = json.loads(m.group(1))
            for key in ("tweet", "text", "content"):
                if isinstance(data.get(key), str) and data[key].strip():
                    return data[key].strip()
        except json.JSONDecodeError:
            pass
    # ``` ... ```
    m = re.search(r"```(?:text|tweet)?\s*(.*?)\s*```", raw, re.S | re.I)
    if m and m.group(1).strip():
        return m.group(1).strip()
    # Keep full plain text; strip only common wrapper lead-ins
    lines = raw.splitlines()
    while lines and lines[0].lower().startswith(
        ("here", "sure", "i've", "i have", "以下", "推文", "okay", "ok,", "当然")
    ):
        lines.pop(0)
    return "\n".join(lines).strip() or raw


def generate_tweet(topic: str, lang: str, brand: str) -> str:
    prompt = f"""
You are a social media copywriter for {brand}.
Write ONE single complete ready-to-post tweet about: {topic}
Language: {lang}
Constraints:
- Write as ONE whole post only — never a thread, never numbered parts, never split sections meant for separate tweets
- Put ALL copy together in a single continuous body
- NO character / word / length limit — write as long as needed, but still as one undivided post
- do not truncate, summarize down, or force a short caption style unless the topic asks for it
- no hashtag spam (at most 2 hashtags)
- no quotation marks wrapping the whole tweet
- return ONLY JSON in a fenced block:
```json
{{"tweet":"..."}}
```
""".strip()
    if STATE_FILE.exists():
        sandbox = ensure_running()
    else:
        template = load_template_name(None)
        sandbox = create_sandbox(template, ttl=3600)
        save_state(sandbox.sandbox_id, template, 3600)
    out = run_claude(sandbox, prompt)
    return extract_tweet(out)


def post_tweet(
    text: str,
    dry_run: bool = False,
    *,
    topic: str | None = None,
    force_publish_test: bool = False,
) -> dict:
    """Always publish as ONE single complete tweet — never split into a thread."""
    import time

    body = (text or "").strip()
    if dry_run:
        return {
            "dry_run": True,
            "text": body,
            "thread_count": 1,
            "single_post": True,
            "blocked_test_publish": is_test_content(topic, body),
        }

    assert_not_test_publish(topic, body, force=force_publish_test)
    if not body:
        raise SystemExit("Empty tweet text")

    creds = require_twitter_creds()
    auth = OAuth1(
        creds["TWITTER_API_KEY"],
        creds["TWITTER_API_SECRET"],
        creds["TWITTER_ACCESS_TOKEN"],
        creds["TWITTER_ACCESS_TOKEN_SECRET"],
    )

    last_err = None
    for attempt in range(3):
        r = requests.post(
            "https://api.x.com/2/tweets",
            auth=auth,
            json={"text": body},
            timeout=30,
        )
        if r.status_code < 300:
            data = r.json()
            tweet_id = data.get("data", {}).get("id")
            return {
                "data": data.get("data"),
                "thread_count": 1,
                "single_post": True,
                "url": f"https://x.com/Pzhise/status/{tweet_id}" if tweet_id else None,
            }
        last_err = f"Twitter API error {r.status_code}: {r.text}"
        if r.status_code in {403, 429, 500, 502, 503} and attempt < 2:
            time.sleep(1.5 * (attempt + 1))
            continue
        break

    raise SystemExit(
        (last_err or "Twitter publish failed")
        + "\n提示：已按「单条完整推文」发布（不再拆分）。"
        + " 若内容过长被拒，请为 @Pzhise 开通支持长文的 X Premium，或缩短后再发。"
    )


def append_history(record: dict) -> None:
    with HISTORY_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate + post tweets with Claude Code sandbox")
    p.add_argument("--topic", required=True, help="Topic / brief for the tweet")
    p.add_argument("--lang", default="en", help="en / zh / ...")
    p.add_argument("--brand", default="Pzhisen", help="Brand voice")
    p.add_argument("--dry-run", action="store_true", help="Only generate, do not post")
    p.add_argument("--post-text", default=None, help="Skip generation; post this text")
    p.add_argument(
        "--force-publish-test",
        action="store_true",
        help="DANGEROUS: override test-tweet publish block (not exposed in web UI)",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if args.post_text:
        tweet = args.post_text.strip()
        source = "manual"
    else:
        print(f"Generating tweet via Claude Code sandbox… topic={args.topic!r}")
        tweet = generate_tweet(args.topic, args.lang, args.brand)
        source = "claude"
    print("--- tweet ---")
    print(tweet)
    print("-------------")
    if is_test_content(args.topic, tweet) and not args.dry_run and not args.force_publish_test:
        print("检测到测试/测验内容：已强制改为只生成、不发布到 @Pzhise")
        args.dry_run = True
    result = post_tweet(
        tweet,
        dry_run=args.dry_run,
        topic=args.topic,
        force_publish_test=args.force_publish_test,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    append_history(
        {
            "topic": args.topic,
            "tweet": tweet,
            "source": source,
            "result": result,
        }
    )


if __name__ == "__main__":
    main()
