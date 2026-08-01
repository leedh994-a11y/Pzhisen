"use client";

import { useState } from "react";

/**
 * Example UI to call the secure /api/serp route from V0.
 * API key never leaves the server.
 */
export default function SerpSearchBox() {
  const [keyword, setKeyword] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<unknown>(null);
  const [error, setError] = useState<string | null>(null);

  async function search() {
    if (!keyword.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`/api/serp?keyword=${encodeURIComponent(keyword.trim())}`);
      const data = await res.json();
      if (!res.ok || data?.ok === false) {
        setError(data?.error || `Request failed (${res.status})`);
      } else {
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
      <h1 style={{ fontSize: 28, marginBottom: 8 }}>SERP Search</h1>
      <p style={{ color: "#555", marginBottom: 16 }}>
        Keyword goes to Next.js API route. Provider token stays in server env only.
      </p>
      <div style={{ display: "flex", gap: 8 }}>
        <input
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          placeholder="Enter keyword"
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
          {loading ? "Searching…" : "Search"}
        </button>
      </div>
      {error && <p style={{ color: "#c53030", marginTop: 16 }}>{error}</p>}
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
