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
Write ONE ready-to-post tweet/thread content about: {topic}
Language: {lang}
Constraints:
- NO character / word / length limit — write as long as needed for a complete post
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


# X single-post hard limit is ~280 weighted chars; long AI copy must become a thread.
MAX_POST_CHARS = 270


def split_for_twitter(text: str, max_chars: int = MAX_POST_CHARS) -> list[str]:
    """Split unlimited generated content into tweet-sized chunks for a thread."""
    text = (text or "").strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []
    # Prefer paragraph / sentence boundaries
    paragraphs = re.split(r"\n\s*\n+", text)
    buf = ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        pieces = re.split(r"(?<=[.!?。！？])\s+", para) if len(para) > max_chars else [para]
        for piece in pieces:
            piece = piece.strip()
            if not piece:
                continue
            # Hard-wrap oversized pieces
            while len(piece) > max_chars:
                cut = piece.rfind(" ", 0, max_chars)
                if cut < max_chars // 2:
                    cut = max_chars
                part = piece[:cut].strip()
                piece = piece[cut:].strip()
                if buf:
                    chunks.append(buf)
                    buf = ""
                chunks.append(part)
            candidate = f"{buf}\n\n{piece}".strip() if buf else piece
            if len(candidate) <= max_chars:
                buf = candidate
            else:
                if buf:
                    chunks.append(buf)
                buf = piece
    if buf:
        chunks.append(buf)
    return chunks or [text[:max_chars]]


def post_tweet(text: str, dry_run: bool = False) -> dict:
    """Post one tweet, or auto-thread when content exceeds X single-post limit."""
    parts = split_for_twitter(text)
    if dry_run:
        return {
            "dry_run": True,
            "text": text,
            "parts": parts,
            "thread_count": len(parts),
        }

    creds = require_twitter_creds()
    auth = OAuth1(
        creds["TWITTER_API_KEY"],
        creds["TWITTER_API_SECRET"],
        creds["TWITTER_ACCESS_TOKEN"],
        creds["TWITTER_ACCESS_TOKEN_SECRET"],
    )

    posted: list[dict] = []
    reply_to: str | None = None
    for i, part in enumerate(parts):
        payload: dict = {"text": part}
        if reply_to:
            payload["reply"] = {"in_reply_to_tweet_id": reply_to}
        r = requests.post(
            "https://api.x.com/2/tweets",
            auth=auth,
            json=payload,
            timeout=30,
        )
        if r.status_code >= 300:
            raise SystemExit(
                f"Twitter API error {r.status_code} on thread part {i + 1}/{len(parts)}: {r.text}"
            )
        data = r.json()
        posted.append(data)
        reply_to = data.get("data", {}).get("id") or reply_to

    first_id = posted[0].get("data", {}).get("id") if posted else None
    return {
        "data": posted[0].get("data") if posted else None,
        "thread": posted,
        "thread_count": len(posted),
        "url": f"https://x.com/Pzhise/status/{first_id}" if first_id else None,
    }


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
    result = post_tweet(tweet, dry_run=args.dry_run)
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
