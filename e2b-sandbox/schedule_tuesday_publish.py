#!/usr/bin/env python3
"""Publish the locked Tuesday @Pzhise long-form tweet (+ CTA reply).

Default: wait until 2026-08-11 09:00:00 UTC (17:00 Beijing), then post.
Use --now to publish immediately (manual override).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from requests_oauthlib import OAuth1
import requests

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
load_dotenv(ROOT / ".env")

DRAFT_FILE = REPO / "twitter-ops" / "drafts" / "2026-08-11-ops-agent.md"
LOG_FILE = REPO / "twitter-ops" / "logs" / "tweet-log.md"
RESULT_FILE = REPO / "twitter-ops" / "logs" / "tuesday-publish-result.json"
HISTORY_FILE = ROOT / ".tweet-history.jsonl"

# 2026-08-11 17:00 Asia/Shanghai == 09:00 UTC
PUBLISH_AT_UTC = datetime(2026, 8, 11, 9, 0, 0, tzinfo=timezone.utc)

TWEET_BODY = (
    "我昨晚把两个一人公司案例翻来覆去对：Broca的Polsia，8个月付费过万、年营收近千万美元，"
    "人还是他一个；Gallagher的Medvi，兄弟俩第一年营收超四亿。共同点不是AI替掉某个岗，"
    "是吃掉传统公司那层中间人力。Stripe数据更刺眼——百万营收个人创业者翻倍有余。"
    "工具人人能用，真正拉开差距的是市场判断。我做Pzhisen，把CEO/工程/营销/增长/客服/运维"
    "交给一人公司，只放大你值得放大的核心能力。"
)

CTA_REPLY = (
    "地址见评论：免费体验 3 天全功能 → https://www.pzhisen.online"
)


def char_count(text: str) -> int:
    return len(text.replace("\n", "").strip())


def require_creds() -> dict[str, str]:
    keys = [
        "TWITTER_API_KEY",
        "TWITTER_API_SECRET",
        "TWITTER_ACCESS_TOKEN",
        "TWITTER_ACCESS_TOKEN_SECRET",
    ]
    missing = [k for k in keys if not os.getenv(k, "").strip()]
    if missing:
        raise SystemExit("Missing Twitter creds: " + ", ".join(missing))
    return {k: os.environ[k].strip() for k in keys}


def auth_from_creds(creds: dict[str, str]) -> OAuth1:
    return OAuth1(
        creds["TWITTER_API_KEY"],
        creds["TWITTER_API_SECRET"],
        creds["TWITTER_ACCESS_TOKEN"],
        creds["TWITTER_ACCESS_TOKEN_SECRET"],
    )


def post_once(auth: OAuth1, text: str, *, in_reply_to: str | None = None) -> dict:
    payload: dict = {"text": text}
    if in_reply_to:
        payload["reply"] = {"in_reply_to_tweet_id": in_reply_to}
    last_err = None
    for attempt in range(3):
        r = requests.post(
            "https://api.x.com/2/tweets",
            auth=auth,
            json=payload,
            timeout=30,
        )
        if r.status_code < 300:
            return r.json()
        last_err = f"Twitter API {r.status_code}: {r.text}"
        if r.status_code in {403, 429, 500, 502, 503} and attempt < 2:
            time.sleep(1.5 * (attempt + 1))
            continue
        break
    raise SystemExit(last_err or "publish failed")


def wait_until(target: datetime) -> None:
    while True:
        now = datetime.now(timezone.utc)
        remaining = (target - now).total_seconds()
        if remaining <= 0:
            return
        # wake periodically so logs show progress
        sleep_for = min(remaining, 300)
        print(
            f"[schedule] now={now.isoformat()} target={target.isoformat()} "
            f"sleep={sleep_for:.0f}s remaining={remaining:.0f}s",
            flush=True,
        )
        time.sleep(sleep_for)


def append_log(tweet_id: str, url: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.write_text(
            "| 日期 | 时间 | Tweet ID | 类型+摘要 | 展示量 | 互动 | 备注 |\n"
            "|------|------|----------|-----------|--------|------|------|\n",
            encoding="utf-8",
        )
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d | %H:%M UTC")
    line = (
        f"| {now.split(' | ')[0]} | {now.split(' | ')[1]} | {tweet_id} | "
        f"长文·一人公司案例→Pzhisen | - | - | 周二自动发布；CTA reply |\n"
    )
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--now", action="store_true", help="Publish immediately")
    p.add_argument("--dry-run", action="store_true", help="Validate only, do not post")
    args = p.parse_args()

    n = char_count(TWEET_BODY)
    print(f"char_count={n} golden={120 <= n <= 220}")
    print("--- body ---")
    print(TWEET_BODY)
    print("--- cta reply ---")
    print(CTA_REPLY)
    if not (120 <= n <= 220):
        raise SystemExit(f"Body length {n} outside golden 120-220")
    if "http://" in TWEET_BODY or "https://" in TWEET_BODY:
        raise SystemExit("Body contains URL — SOP forbids links in main tweet")

    if args.dry_run:
        print(json.dumps({"dry_run": True, "char_count": n}, ensure_ascii=False, indent=2))
        return

    if not args.now:
        wait_until(PUBLISH_AT_UTC)

    creds = require_creds()
    auth = auth_from_creds(creds)
    main_res = post_once(auth, TWEET_BODY)
    tweet_id = main_res.get("data", {}).get("id")
    if not tweet_id:
        raise SystemExit(f"No tweet id in response: {main_res}")
    url = f"https://x.com/Pzhise/status/{tweet_id}"
    print(f"published: {url}", flush=True)

    reply_res = None
    try:
        time.sleep(1.5)
        reply_res = post_once(auth, CTA_REPLY, in_reply_to=tweet_id)
        print(f"cta reply: {reply_res}", flush=True)
    except SystemExit as e:
        print(f"cta reply failed (main already live): {e}", flush=True)

    result = {
        "published_at_utc": datetime.now(timezone.utc).isoformat(),
        "char_count": n,
        "tweet_id": tweet_id,
        "url": url,
        "reply": reply_res,
        "draft_file": str(DRAFT_FILE),
    }
    RESULT_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with HISTORY_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"topic": "tuesday-solo-founder-longform", "result": result}, ensure_ascii=False) + "\n")
    append_log(tweet_id, url)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
