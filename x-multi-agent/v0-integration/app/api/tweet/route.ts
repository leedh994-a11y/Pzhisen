import { NextRequest, NextResponse } from "next/server";
import { TwitterApi } from "twitter-api-v2";

/**
 * Post to X (@Pzhise) directly from Vercel — no tunnel required.
 *
 * Env:
 *   TWITTER_API_KEY or TWITTER_CONSUMER_KEY
 *   TWITTER_API_SECRET or TWITTER_CONSUMER_SECRET
 *   TWITTER_ACCESS_TOKEN
 *   TWITTER_ACCESS_SECRET
 * Optional NL via tok.mom:
 *   OPENAI_API_KEY + OPENAI_API_BASE
 */
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function env(...names: string[]) {
  for (const n of names) {
    const v = (process.env[n] || "").trim();
    if (v) return v;
  }
  return "";
}

function hasXKeys() {
  return Boolean(
    env("TWITTER_API_KEY", "TWITTER_CONSUMER_KEY") &&
      env("TWITTER_API_SECRET", "TWITTER_CONSUMER_SECRET") &&
      env("TWITTER_ACCESS_TOKEN") &&
      env("TWITTER_ACCESS_SECRET")
  );
}

function localTweetFromPrompt(topic: string) {
  const cleaned = topic
    .replace(/^(请|帮我|发一条|写一条|发推|tweet|post)\s*/i, "")
    .replace(/[。！？]+$/g, "")
    .trim();
  let body = cleaned || "Pzhisen AI store — automated ecommerce";
  if (!/pzhisen\.online/i.test(body)) {
    body = `${body} — try Pzhisen AI store: https://pzhisen.online`;
  }
  if (body.length > 270) body = `${body.slice(0, 267)}...`;
  return body;
}

async function generateTweet(topic: string) {
  const apiKey = env("OPENAI_API_KEY", "LLM_API_KEY");
  let base = env("OPENAI_API_BASE", "LLM_API_URL", "OPENAI_BASE_URL");
  if (!apiKey || !base) return localTweetFromPrompt(topic);

  base = base.replace(/\/+$/, "").replace(/\/chat\/completions$/i, "");
  if (!/\/v\d+$/i.test(base)) base = `${base}/v1`;

  try {
    const res = await fetch(`${base}/chat/completions`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: env("OPENAI_MODEL", "LLM_MODEL") || "gpt-4o-mini",
        messages: [
          {
            role: "user",
            content: `Write ONE Twitter/X post in English about: ${topic}
Max 270 characters. No wrapping quotes. 0-2 hashtags max.
Mention https://pzhisen.online naturally if relevant.
Return ONLY the tweet text.`,
          },
        ],
        stream: false,
        max_tokens: 120,
      }),
      cache: "no-store",
    });
    const data = (await res.json()) as {
      choices?: Array<{ message?: { content?: string } }>;
    };
    const text = data?.choices?.[0]?.message?.content?.trim();
    if (text) return text.replace(/^["']|["']$/g, "").slice(0, 280);
  } catch {
    // fall through
  }
  return localTweetFromPrompt(topic);
}

function xClient() {
  return new TwitterApi({
    appKey: env("TWITTER_API_KEY", "TWITTER_CONSUMER_KEY"),
    appSecret: env("TWITTER_API_SECRET", "TWITTER_CONSUMER_SECRET"),
    accessToken: env("TWITTER_ACCESS_TOKEN"),
    accessSecret: env("TWITTER_ACCESS_SECRET"),
  });
}

async function viaAgent(body: {
  prompt: string;
  text: string;
  dryRun: boolean;
}) {
  const agentUrl = env("TWEET_AGENT_URL").replace(/\/$/, "");
  const token = env("TWEET_AGENT_TOKEN");
  if (!agentUrl) return null;
  const upstream = await fetch(`${agentUrl}/api/v0/tweet`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  const data = await upstream.json().catch(() => ({
    ok: false,
    error: "Upstream returned non-JSON",
  }));
  return { status: upstream.status, data };
}

export async function POST(req: NextRequest) {
  let body: Record<string, unknown>;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ ok: false, error: "Invalid JSON" }, { status: 400 });
  }

  const prompt = String(
    body.prompt || body.message || body.topic || body.input || ""
  ).trim();
  const fixedText = String(body.text || body.tweet || "").trim();
  const dryRun = Boolean(body.dryRun || body.preview);

  if (!prompt && !fixedText) {
    return NextResponse.json(
      { ok: false, error: 'Send {"prompt":"natural language what to tweet"}' },
      { status: 400 }
    );
  }

  // Prefer tunnel agent when configured (supports cookie posting if X API keys are 401).
  const preferAgent =
    env("TWEET_PREFER_AGENT", "TWEET_MODE") === "cookie" ||
    env("TWEET_PREFER_AGENT") === "1" ||
    env("TWEET_PREFER_AGENT").toLowerCase() === "true" ||
    Boolean(env("TWEET_AGENT_URL"));

  if (preferAgent && env("TWEET_AGENT_URL")) {
    try {
      const via = await viaAgent({ prompt, text: fixedText, dryRun });
      if (via && via.status < 500) {
        return NextResponse.json(via.data, { status: via.status });
      }
      // if agent 5xx, fall through to direct API / better error
      if (via) {
        // keep trying API below; remember agent error
        console.error("tweet agent failed", via.status, via.data);
      }
    } catch (e) {
      console.error("tweet agent unreachable", e);
    }
  }

  if (hasXKeys()) {
    try {
      const text = fixedText || (await generateTweet(prompt));
      if (dryRun) {
        return NextResponse.json({
          ok: true,
          dryRun: true,
          account: "@Pzhise",
          text,
          message: "Preview only — not posted",
        });
      }

      const client = xClient().readWrite;
      let account = "@Pzhise";
      try {
        const me = await client.v2.me();
        if (me?.data?.username) account = `@${me.data.username}`;
      } catch {
        // continue to post even if /me fails
      }

      const res = await client.v2.tweet(text);
      const id = res?.data?.id;
      return NextResponse.json({
        ok: true,
        account,
        text,
        tweetId: id,
        tweetUrl: id ? `https://x.com/i/web/status/${id}` : undefined,
        message: "Posted via X API on Vercel",
      });
    } catch (e: unknown) {
      const err = e as { message?: string; data?: unknown; code?: number };
      // Last resort: agent if not already preferred
      if (env("TWEET_AGENT_URL")) {
        try {
          const via = await viaAgent({ prompt, text: fixedText, dryRun });
          if (via) return NextResponse.json(via.data, { status: via.status });
        } catch {
          // ignore
        }
      }
      return NextResponse.json(
        {
          ok: false,
          error: err.message || "X API post failed",
          data: err.data,
          code: err.code,
          hint: "Official X API returned unauthorized. Cookie agent via TWEET_AGENT_URL is the fallback.",
        },
        { status: 502 }
      );
    }
  }

  return NextResponse.json(
    {
      ok: false,
      error:
        "Cannot post: set TWEET_AGENT_URL (cookie agent) or valid TWITTER_API_KEY/SECRET + ACCESS_TOKEN/SECRET",
    },
    { status: 500 }
  );
}
