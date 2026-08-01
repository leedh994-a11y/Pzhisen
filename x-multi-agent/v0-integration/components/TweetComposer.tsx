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
};

/**
 * Drop this component into a v0 / Next.js page.
 * It calls /api/tweet on the same site (proxy → x-multi-agent).
 */
export default function TweetComposer() {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TweetResult | null>(null);

  async function submit(dryRun = false) {
    if (!prompt.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch("/api/tweet", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, dryRun }),
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
        Describe what you want in natural language. AI writes the tweet and posts it to X.
      </p>

      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        rows={5}
        placeholder="Example: Announce that Pzhisen AI stores can get the first order overnight with zero coding"
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
          {loading ? "Posting…" : "Post to X"}
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
          <strong>{result.ok ? result.message : "Failed"}</strong>
          {result.account && <div>Account: {result.account}</div>}
          {result.text && (
            <pre style={{ whiteSpace: "pre-wrap", marginTop: 8 }}>{result.text}</pre>
          )}
          {result.tweetUrl && (
            <a href={result.tweetUrl} target="_blank" rel="noreferrer">
              Open tweet
            </a>
          )}
          {result.error && <div style={{ color: "#c53030" }}>{result.error}</div>}
        </div>
      )}
    </div>
  );
}
