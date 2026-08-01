"use client";

import { useState } from "react";

type TweetResult = {
  ok: boolean;
  message?: string;
  account?: string;
  text?: string;
  tweetUrl?: string;
  tweetId?: string;
  error?: string;
  dryRun?: boolean;
  output?: string;
  mode?: string;
};

/**
 * Posts via /api/tweet on the same site.
 * Exact pasted posts are sent as `text` so cookie/agent path does not depend on Gemini.
 */
export default function TweetComposer() {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TweetResult | null>(null);

  function looksLikeFinishedTweet(value: string) {
    const v = value.trim();
    return (
      v.length >= 40 ||
      /https?:\/\//i.test(v) ||
      /[\u4e00-\u9fff]/.test(v) ||
      /\n/.test(v)
    );
  }

  async function submit(dryRun = false) {
    if (!prompt.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const finished = looksLikeFinishedTweet(prompt);
      const res = await fetch("/api/tweet", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(
          finished
            ? { prompt, text: prompt.trim(), dryRun }
            : { prompt: prompt.trim(), dryRun }
        ),
      });
      const data = (await res.json()) as TweetResult;
      setResult(data);
    } catch (e) {
      setResult({ ok: false, error: String(e) });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 640, margin: "0 auto", padding: 24, fontFamily: "system-ui, sans-serif" }}>
      <h1 style={{ fontSize: 28, marginBottom: 8 }}>Post to @Pzhise</h1>
      <p style={{ color: "#555", marginBottom: 16 }}>
        输入自然语言，或直接粘贴要发的完整推文，然后点 <strong>Post to X</strong>。
        请用线上地址：{" "}
        <a href="https://chirp-flow.vercel.app" target="_blank" rel="noreferrer">
          chirp-flow.vercel.app
        </a>
        （不是 localhost）。
      </p>

      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        rows={7}
        placeholder="直接粘贴完整推文，或写：发一条 Pzhisen AI 店铺凌晨自动出单的推广"
        style={{
          width: "100%",
          padding: 12,
          borderRadius: 8,
          border: "1px solid #ccc",
          fontSize: 16,
          resize: "vertical",
        }}
      />

      <div style={{ display: "flex", gap: 12, marginTop: 12 }}>
        <button
          disabled={loading || !prompt.trim()}
          onClick={() => submit(true)}
          style={{ padding: "10px 16px", borderRadius: 8, border: "1px solid #999" }}
        >
          Preview
        </button>
        <button
          disabled={loading || !prompt.trim()}
          onClick={() => submit(false)}
          style={{
            padding: "10px 16px",
            borderRadius: 8,
            border: "none",
            background: "#111",
            color: "#fff",
          }}
        >
          {loading ? "Posting…（约 20–60 秒）" : "Post to X"}
        </button>
      </div>

      {result && (
        <div
          style={{
            marginTop: 20,
            padding: 16,
            borderRadius: 8,
            background: result.ok ? "#f0fff4" : "#fff5f5",
            border: `1px solid ${result.ok ? "#9ae6b4" : "#feb2b2"}`,
          }}
        >
          <strong>{result.ok ? result.message || "OK" : "Failed"}</strong>
          {result.account && <div>Account: {result.account}</div>}
          {result.mode && <div>Mode: {result.mode}</div>}
          {result.text && (
            <pre style={{ whiteSpace: "pre-wrap", marginTop: 8 }}>{result.text}</pre>
          )}
          {result.ok && (
            <div style={{ marginTop: 8 }}>
              <a href="https://x.com/Pzhise" target="_blank" rel="noreferrer">
                打开 @Pzhise 主页查看
              </a>
              {result.tweetUrl ? (
                <>
                  {" · "}
                  <a href={result.tweetUrl} target="_blank" rel="noreferrer">
                    Open tweet
                  </a>
                </>
              ) : null}
            </div>
          )}
          {result.error && (
            <div style={{ color: "#c53030", marginTop: 8, whiteSpace: "pre-wrap" }}>
              {result.error}
            </div>
          )}
          {!result.ok && result.output && (
            <pre
              style={{
                marginTop: 8,
                fontSize: 12,
                whiteSpace: "pre-wrap",
                color: "#744210",
              }}
            >
              {result.output}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}
