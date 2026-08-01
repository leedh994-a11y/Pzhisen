"use client";

import { useState } from "react";

/**
 * Example UI for tok.mom via secure /api/serp (→ chat/completions).
 * OPENAI_API_KEY never leaves the server.
 */
export default function SerpSearchBox() {
  const [keyword, setKeyword] = useState("");
  const [loading, setLoading] = useState(false);
  const [content, setContent] = useState<string | null>(null);
  const [result, setResult] = useState<unknown>(null);
  const [error, setError] = useState<string | null>(null);

  async function search() {
    if (!keyword.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setContent(null);
    try {
      const res = await fetch("/api/serp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          // OpenAI-compatible shape (tok.mom)
          model: "gpt-4o-mini",
          messages: [{ role: "user", content: keyword.trim() }],
          // also accepted: keyword / prompt
          keyword: keyword.trim(),
        }),
      });
      const data = await res.json();
      if (!res.ok || data?.ok === false) {
        setError(data?.error || `Request failed (${res.status})`);
      } else {
        setContent(typeof data.content === "string" ? data.content : null);
        setResult(data);
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 720, margin: "0 auto", padding: 24, fontFamily: "system-ui, sans-serif" }}>
      <h1 style={{ fontSize: 28, marginBottom: 8 }}>tok.mom Chat</h1>
      <p style={{ color: "#555", marginBottom: 16 }}>
        Calls Next.js <code>/api/serp</code> →{" "}
        <code>POST https://api.tok.mom/v1/chat/completions</code>. Key stays in
        server env (<code>OPENAI_API_KEY</code> + <code>OPENAI_API_BASE</code>).
      </p>
      <div style={{ display: "flex", gap: 8 }}>
        <input
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          placeholder="Ask anything…"
          style={{ flex: 1, padding: 12, borderRadius: 8, border: "1px solid #ccc", fontSize: 16 }}
        />
        <button
          onClick={search}
          disabled={loading || !keyword.trim()}
          style={{
            padding: "10px 16px",
            borderRadius: 8,
            border: "none",
            background: "#111",
            color: "#fff",
          }}
        >
          {loading ? "Calling…" : "Send"}
        </button>
      </div>
      {error && <p style={{ color: "#c53030", marginTop: 16 }}>{error}</p>}
      {content && (
        <div style={{ marginTop: 16, padding: 12, background: "#f0f7ff", borderRadius: 8, whiteSpace: "pre-wrap" }}>
          {content}
        </div>
      )}
      {result != null && (
        <pre
          style={{
            marginTop: 16,
            padding: 12,
            background: "#f7f7f7",
            borderRadius: 8,
            overflow: "auto",
            fontSize: 12,
          }}
        >
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
