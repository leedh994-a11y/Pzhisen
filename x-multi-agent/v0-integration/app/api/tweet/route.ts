import { NextRequest, NextResponse } from "next/server";

/**
 * V0 / Next.js App Router proxy → Pzhisen tweet agent
 *
 * Env (Vercel / v0 project settings):
 *   TWEET_AGENT_URL=https://your-agent-host   (no trailing slash)
 *   TWEET_AGENT_TOKEN=your-AGENT_API_TOKEN
 *
 * Local example:
 *   TWEET_AGENT_URL=http://127.0.0.1:8787
 *   TWEET_AGENT_TOKEN=change-me-to-a-long-random-secret
 */
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  const agentUrl = (process.env.TWEET_AGENT_URL || "").replace(/\/$/, "");
  const token = process.env.TWEET_AGENT_TOKEN || "";

  if (!agentUrl) {
    return NextResponse.json(
      {
        ok: false,
        error: "Missing TWEET_AGENT_URL in environment",
      },
      { status: 500 }
    );
  }

  let body: Record<string, unknown>;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ ok: false, error: "Invalid JSON" }, { status: 400 });
  }

  const prompt = String(
    body.prompt || body.message || body.topic || body.input || ""
  ).trim();
  const text = String(body.text || body.tweet || "").trim();
  const dryRun = Boolean(body.dryRun || body.preview);

  if (!prompt && !text) {
    return NextResponse.json(
      {
        ok: false,
        error: 'Send {"prompt":"natural language what to tweet"}',
      },
      { status: 400 }
    );
  }

  const upstream = await fetch(`${agentUrl}/api/v0/tweet`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ prompt, text, dryRun }),
    cache: "no-store",
  });

  const data = await upstream.json().catch(() => ({
    ok: false,
    error: "Upstream returned non-JSON",
  }));

  return NextResponse.json(data, { status: upstream.status });
}
