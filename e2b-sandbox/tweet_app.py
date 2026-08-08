#!/usr/bin/env python3
"""One-click web UI: AI generate tweet + publish to X/Twitter."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS

from config import ROOT
from tweet_pipeline import append_history, generate_tweet, post_tweet

load_dotenv(ROOT / ".env")

app = Flask(__name__)
CORS(app)

PAGE = """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Pzhisen — 一键生成并发布推文</title>
  <style>
    :root {
      --bg: #0b1220;
      --panel: #121a2b;
      --text: #eef3ff;
      --muted: #9aa8c7;
      --accent: #1d9bf0;
      --ok: #22c55e;
      --warn: #f59e0b;
      --danger: #ef4444;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0; min-height: 100vh; color: var(--text);
      font-family: "Segoe UI", "PingFang SC", sans-serif;
      background:
        radial-gradient(900px 500px at 10% -10%, #1d9bf033, transparent 55%),
        radial-gradient(700px 400px at 100% 0%, #22c55e22, transparent 50%),
        var(--bg);
    }
    main { max-width: 720px; margin: 0 auto; padding: 40px 20px 80px; }
    h1 { margin: 0 0 8px; font-size: 1.7rem; letter-spacing: -0.02em; }
    .sub { color: var(--muted); margin-bottom: 28px; line-height: 1.5; }
    label { display: block; margin: 14px 0 6px; color: var(--muted); font-size: .9rem; }
    input, select, textarea {
      width: 100%; border: 1px solid #2a3757; background: var(--panel);
      color: var(--text); border-radius: 10px; padding: 12px 14px; font-size: 1rem;
    }
    textarea { min-height: 120px; resize: vertical; line-height: 1.45; }
    .row { display: grid; grid-template-columns: 1fr 140px; gap: 12px; }
    .actions { display: flex; gap: 10px; margin-top: 18px; flex-wrap: wrap; }
    button {
      border: 0; border-radius: 999px; padding: 12px 18px; font-weight: 600;
      cursor: pointer; font-size: .95rem;
    }
    .primary { background: var(--accent); color: #fff; }
    .secondary { background: #24304a; color: var(--text); }
    .danger { background: #3a1d24; color: #fecaca; }
    button:disabled { opacity: .55; cursor: wait; }
    .card {
      margin-top: 22px; background: var(--panel); border: 1px solid #2a3757;
      border-radius: 14px; padding: 16px;
    }
    .meta { color: var(--muted); font-size: .85rem; margin-bottom: 8px; }
    .status { margin-top: 12px; font-size: .92rem; white-space: pre-wrap; }
    .ok { color: var(--ok); }
    .err { color: #fecaca; }
    a { color: #7dd3fc; }
  </style>
</head>
<body>
  <main>
    <h1>一键生成并发布</h1>
    <p class="sub">
      Claude Code 云沙箱生成文案 → X/Twitter API 发布到
      <a href="https://x.com/Pzhise" target="_blank" rel="noreferrer">@Pzhise</a>
    </p>

    <label for="topic">主题 / Brief</label>
    <input id="topic" placeholder="例如：Pzhisen AI 员工团队通宵帮你运营公司" value="Pzhisen AI employee team that builds, markets, and supports your company overnight" />

    <div class="row">
      <div>
        <label for="brand">品牌语气</label>
        <input id="brand" value="Pzhisen" />
      </div>
      <div>
        <label for="lang">语言</label>
        <select id="lang">
          <option value="en" selected>English</option>
          <option value="zh">中文</option>
        </select>
      </div>
    </div>

    <label for="tweet">推文预览（可编辑后再发布）</label>
    <textarea id="tweet" placeholder="点「生成」后这里会出现文案"></textarea>

    <div class="actions">
      <button class="secondary" id="btnGen" onclick="generateTweet()">只生成</button>
      <button class="primary" id="btnPublish" onclick="publishTweet()">一键生成并发布</button>
      <button class="danger" id="btnPostOnly" onclick="postOnly()">发布当前文案</button>
    </div>

    <div class="card">
      <div class="meta">结果</div>
      <div id="status" class="status">待命</div>
    </div>
  </main>
  <script>
    function setBusy(b) {
      ['btnGen','btnPublish','btnPostOnly'].forEach(id => document.getElementById(id).disabled = b);
    }
    function show(msg, ok) {
      const el = document.getElementById('status');
      el.textContent = msg;
      el.className = 'status ' + (ok ? 'ok' : 'err');
    }
    async function generateTweet() {
      setBusy(true); show('正在用 Claude Code 生成…', true);
      try {
        const r = await fetch('/api/generate', {
          method: 'POST', headers: {'Content-Type':'application/json'},
          body: JSON.stringify({
            topic: topic.value, brand: brand.value, lang: lang.value
          })
        });
        const data = await r.json();
        if (!r.ok) throw new Error(data.error || JSON.stringify(data));
        tweet.value = data.tweet;
        show('生成成功，可编辑后点「发布当前文案」', true);
      } catch (e) { show('生成失败: ' + e.message, false); }
      finally { setBusy(false); }
    }
    async function publishTweet() {
      setBusy(true); show('生成并发布中…', true);
      try {
        const r = await fetch('/api/one-click', {
          method: 'POST', headers: {'Content-Type':'application/json'},
          body: JSON.stringify({
            topic: topic.value, brand: brand.value, lang: lang.value
          })
        });
        const data = await r.json();
        if (!r.ok) throw new Error(data.error || JSON.stringify(data));
        tweet.value = data.tweet;
        const id = data.result?.data?.id;
        const url = id ? ('https://x.com/Pzhise/status/' + id) : '';
        show('发布成功' + (url ? '\\n' + url : '\\n' + JSON.stringify(data.result, null, 2)), true);
      } catch (e) { show('发布失败: ' + e.message, false); }
      finally { setBusy(false); }
    }
    async function postOnly() {
      if (!tweet.value.trim()) { show('请先生成或填写推文', false); return; }
      setBusy(true); show('正在发布当前文案…', true);
      try {
        const r = await fetch('/api/publish', {
          method: 'POST', headers: {'Content-Type':'application/json'},
          body: JSON.stringify({ tweet: tweet.value, topic: topic.value })
        });
        const data = await r.json();
        if (!r.ok) throw new Error(data.error || JSON.stringify(data));
        const id = data.result?.data?.id;
        const url = id ? ('https://x.com/Pzhise/status/' + id) : '';
        show('发布成功' + (url ? '\\n' + url : '\\n' + JSON.stringify(data.result, null, 2)), true);
      } catch (e) { show('发布失败: ' + e.message, false); }
      finally { setBusy(false); }
    }
  </script>
</body>
</html>
"""


@app.get("/")
def index():
    return render_template_string(PAGE)


@app.post("/api/generate")
def api_generate():
    body = request.get_json(force=True, silent=True) or {}
    topic = (body.get("topic") or "").strip()
    if not topic:
        return jsonify({"error": "topic is required"}), 400
    try:
        tweet = generate_tweet(
            topic=topic,
            lang=(body.get("lang") or "en").strip(),
            brand=(body.get("brand") or "Pzhisen").strip(),
        )
        append_history({"topic": topic, "tweet": tweet, "source": "ui-generate"})
        return jsonify({"tweet": tweet})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.post("/api/publish")
def api_publish():
    body = request.get_json(force=True, silent=True) or {}
    tweet = (body.get("tweet") or "").strip()
    if not tweet:
        return jsonify({"error": "tweet is required"}), 400
    try:
        result = post_tweet(tweet, dry_run=False)
        append_history(
            {
                "topic": body.get("topic"),
                "tweet": tweet,
                "source": "ui-publish",
                "result": result,
            }
        )
        return jsonify({"tweet": tweet, "result": result})
    except SystemExit as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.post("/api/one-click")
def api_one_click():
    body = request.get_json(force=True, silent=True) or {}
    topic = (body.get("topic") or "").strip()
    if not topic:
        return jsonify({"error": "topic is required"}), 400
    try:
        tweet = generate_tweet(
            topic=topic,
            lang=(body.get("lang") or "en").strip(),
            brand=(body.get("brand") or "Pzhisen").strip(),
        )
        result = post_tweet(tweet, dry_run=False)
        append_history(
            {
                "topic": topic,
                "tweet": tweet,
                "source": "ui-one-click",
                "result": result,
            }
        )
        return jsonify({"tweet": tweet, "result": result})
    except SystemExit as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


def main() -> None:
    port = int(os.getenv("TWEET_APP_PORT", "8787"))
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
