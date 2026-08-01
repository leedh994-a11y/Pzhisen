import { NextRequest, NextResponse } from "next/server";

/**
 * Secure server-side proxy for tok.mom (OpenAI-compatible).
 *
 * Vercel / V0 env (already configured by you):
 *   OPENAI_API_KEY=sk-...
 *   OPENAI_API_BASE=https://api.tok.mom/v1
 *   # alias also accepted: LLM_API_URL
 *   OPENAI_MODEL=gpt-4o-mini   (optional default model)
 *
 * Upstream (exact provider format):
 *   POST {OPENAI_API_BASE}/chat/completions
 *   Authorization: Bearer {OPENAI_API_KEY}
 *   Content-Type: application/json
 *   body: { model, messages, temperature?, max_tokens?, stream?, ... }
 *
 * Frontend only calls this route — never the provider key.
 *   POST /api/chat  { "model"?, "messages": [...], ... }
 *   GET  /api/chat?prompt=hello&model=gpt-4o-mini
 */
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type ChatMessage = {
  role: string;
  content: string;
};

type ChatBody = {
  model?: string;
  messages?: ChatMessage[];
  prompt?: string;
  temperature?: number;
  max_tokens?: number;
  stream?: boolean;
  [key: string]: unknown;
};

function getApiKey() {
  return (
    process.env.OPENAI_API_KEY ||
    process.env.LLM_API_KEY ||
    process.env.TOK_API_KEY ||
    ""
  ).trim();
}

/** Normalize to .../v1 (no trailing slash). */
function getApiBase() {
  let base = (
    process.env.OPENAI_API_BASE ||
    process.env.LLM_API_URL ||
    process.env.OPENAI_BASE_URL ||
    "https://api.tok.mom/v1"
  ).trim();

  base = base.replace(/\/+$/, "");
  // Allow pasting full chat URL by mistake
  base = base.replace(/\/chat\/completions$/i, "");
  // If only host given, append /v1
  if (!/\/v\d+$/i.test(base) && !base.endsWith("/v1")) {
    base = `${base}/v1`;
  }
  return base;
}

function getDefaultModel() {
  return (process.env.OPENAI_MODEL || process.env.LLM_MODEL || "gpt-4o-mini").trim();
}

function chatCompletionsUrl() {
  return `${getApiBase()}/chat/completions`;
}

async function callTokMom(body: Record<string, unknown>) {
  const apiKey = getApiKey();
  if (!apiKey) {
    return NextResponse.json(
      {
        ok: false,
        error:
          "OPENAI_API_KEY not configured. Set it in Vercel/V0 env (tok.mom sk- token).",
      },
      { status: 500 }
    );
  }

  const upstream = chatCompletionsUrl();
  const { model: bodyModel, stream: bodyStream, ...rest } = body;
  const payload: Record<string, unknown> = {
    ...rest,
    model:
      typeof bodyModel === "string" && bodyModel.trim()
        ? bodyModel.trim()
        : getDefaultModel(),
    stream: bodyStream === true,
  };

  const response = await fetch(upstream, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(payload),
    cache: "no-store",
  });

  // Streaming passthrough if requested
  if (payload.stream && response.ok && response.body) {
    return new NextResponse(response.body, {
      status: response.status,
      headers: {
        "Content-Type":
          response.headers.get("Content-Type") || "text/event-stream",
        "Cache-Control": "no-cache",
      },
    });
  }

  const text = await response.text();
  let data: unknown = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { raw: text.slice(0, 2000) };
  }

  if (!response.ok) {
    return NextResponse.json(
      {
        ok: false,
        error: `tok.mom chat/completions failed (${response.status})`,
        status: response.status,
        upstream,
        data,
      },
      { status: 502 }
    );
  }

  // Return provider JSON as-is, plus a thin ok wrapper for UI convenience
  return NextResponse.json({
    ok: true,
    upstream,
    data,
  });
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const prompt = (
    searchParams.get("prompt") ||
    searchParams.get("q") ||
    searchParams.get("keyword") ||
    ""
  ).trim();
  const model = (searchParams.get("model") || "").trim();

  if (!prompt) {
    return NextResponse.json(
      { ok: false, error: "prompt (or q / keyword) query param is required" },
      { status: 400 }
    );
  }

  try {
    return await callTokMom({
      ...(model ? { model } : {}),
      messages: [{ role: "user", content: prompt }],
    });
  } catch (error) {
    console.error("tok.mom GET /api/chat error:", error);
    return NextResponse.json(
      { ok: false, error: "Failed to call tok.mom" },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  let body: ChatBody = {};
  try {
    body = (await request.json()) as ChatBody;
  } catch {
    return NextResponse.json(
      { ok: false, error: "Invalid JSON body" },
      { status: 400 }
    );
  }

  // Full OpenAI-compatible pass-through when messages present
  let messages = Array.isArray(body.messages) ? body.messages : undefined;
  if (!messages || messages.length === 0) {
    const prompt = String(body.prompt || "").trim();
    if (!prompt) {
      return NextResponse.json(
        {
          ok: false,
          error:
            'Provide OpenAI-format "messages", or a string "prompt" / use GET ?prompt=',
        },
        { status: 400 }
      );
    }
    messages = [{ role: "user", content: prompt }];
  }

  const { prompt: _p, ...rest } = body;

  try {
    return await callTokMom({
      ...rest,
      messages,
    });
  } catch (error) {
    console.error("tok.mom POST /api/chat error:", error);
    return NextResponse.json(
      { ok: false, error: "Failed to call tok.mom" },
      { status: 500 }
    );
  }
}
