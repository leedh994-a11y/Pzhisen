"use client";

import { useState } from "react";

/**
 * Full OpenAI-compatible client for /api/chat → tok.mom.
 */
export default function ChatBox() {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [content, setContent] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function send() {
    if (!prompt.trim()) return;
    setLoading(true);
    setError(null);
    setContent(null);
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "gpt-4o-mini",
          messages: [{ role: "user", content: prompt.trim() }],
        }),
      });
      const data = await res.json();
      if (!res.ok || data?.ok === false) {
        setError(data?.error || `Request failed (${res.status})`);
        return;
      }
      const text =
        data?.data?.choices?.[0]?.message?.content ??
        data?.content ??
        null;
      setContent(typeof text === "string" ? text : JSON.stringify(data, null, 2));
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 720, margin: "0 auto", padding: 24, fontFamily: "system-ui, sans-serif" }}>
      <h1 style={{ fontSize: 28, marginBottom: 8 }}>tok.mom /api/chat</h1>
      <p style={{ color: "#555", marginBottom: 16 }}>
        OpenAI-compatible body → server env <code>OPENAI_API_BASE</code> +{" "}
        <code>OPENAI_API_KEY</code>.
      </p>
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        rows={4}
        placeholder="Message…"
        style={{ width: "100%", padding: 12, borderRadius: 8, border: "1px solid #ccc", fontSize: 16 }}
      />
      <button
        onClick={send}
        disabled={loading || !prompt.trim()}
        style={{
          marginTop: 8,
          padding: "10px 16px",
          borderRadius: 8,
          border: "none",
          background: "#111",
          color: "#fff",
        }}
      >
        {loading ? "Calling…" : "Send"}
      </button>
      {error && <p style={{ color: "#c53030", marginTop: 16 }}>{error}</p>}
      {content && (
        <div style={{ marginTop: 16, padding: 12, background: "#f0f7ff", borderRadius: 8, whiteSpace: "pre-wrap" }}>
          {content}
        </div>
      )}
    </div>
  );
}
