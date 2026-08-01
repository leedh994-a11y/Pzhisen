import { NextRequest, NextResponse } from "next/server";

/**
 * Compatibility route: /api/serp → tok.mom OpenAI chat/completions.
 *
 * Your provider (tok.mom) is an LLM gateway, not a SERP API.
 * This route maps keyword/q into the exact OpenAI request format.
 *
 * Env (Vercel / V0):
 *   OPENAI_API_KEY=sk-...
 *   OPENAI_API_BASE=https://api.tok.mom/v1
 *   OPENAI_MODEL=gpt-4o-mini   (optional)
 *
 * Prefer /api/chat for full OpenAI pass-through.
 */
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type SerpBody = {
  keyword?: string;
  q?: string;
  prompt?: string;
  model?: string;
  messages?: Array<{ role: string; content: string }>;
  [key: string]: unknown;
};

function getApiKey() {
  return (
    process.env.OPENAI_API_KEY ||
    process.env.LLM_API_KEY ||
    process.env.TOK_API_KEY ||
    process.env.SERP_API_KEY ||
    ""
  ).trim();
}

function getApiBase() {
  let base = (
    process.env.OPENAI_API_BASE ||
    process.env.LLM_API_URL ||
    process.env.OPENAI_BASE_URL ||
    process.env.SERP_API_URL ||
    "https://api.tok.mom/v1"
  ).trim();

  base = base.replace(/\/+$/, "");
  base = base.replace(/\/chat\/completions$/i, "");
  if (!/\/v\d+$/i.test(base) && !base.endsWith("/v1")) {
    base = `${base}/v1`;
  }
  return base;
}

function getDefaultModel() {
  return (process.env.OPENAI_MODEL || process.env.LLM_MODEL || "gpt-4o-mini").trim();
}

async function callChatCompletions(input: {
  keyword: string;
  model?: string;
  messages?: Array<{ role: string; content: string }>;
  extra?: Record<string, unknown>;
}) {
  const apiKey = getApiKey();
  if (!apiKey) {
    return NextResponse.json(
      {
        ok: false,
        error:
          "OPENAI_API_KEY not configured. Set tok.mom sk- token in Vercel/V0 env.",
      },
      { status: 500 }
    );
  }

  const upstream = `${getApiBase()}/chat/completions`;
  const model = (input.model || getDefaultModel()).trim();
  const messages =
    input.messages && input.messages.length > 0
      ? input.messages
      : [{ role: "user", content: input.keyword }];

  // Exact tok.mom / OpenAI chat.completions payload
  const payload: Record<string, unknown> = {
    model,
    messages,
    stream: false,
    ...(input.extra || {}),
  };
  // Do not let leftover SERP fields override OpenAI shape
  delete payload.keyword;
  delete payload.q;
  delete payload.gl;
  delete payload.hl;
  delete payload.engine;
  delete payload.num;
  delete payload.prompt;

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

  const content =
    data &&
    typeof data === "object" &&
    Array.isArray((data as { choices?: unknown }).choices)
      ? (data as { choices: Array<{ message?: { content?: string } }> }).choices[0]
          ?.message?.content
      : undefined;

  return NextResponse.json({
    ok: true,
    keyword: input.keyword,
    model,
    upstream,
    content: content ?? null,
    data,
  });
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const keyword = (
    searchParams.get("keyword") ||
    searchParams.get("q") ||
    searchParams.get("prompt") ||
    ""
  ).trim();
  const model = (searchParams.get("model") || "").trim() || undefined;

  if (!keyword) {
    return NextResponse.json(
      { ok: false, error: "keyword (or q / prompt) parameter is required" },
      { status: 400 }
    );
  }

  try {
    return await callChatCompletions({ keyword, model });
  } catch (error) {
    console.error("Error calling tok.mom via /api/serp:", error);
    return NextResponse.json(
      { ok: false, error: "Failed to call tok.mom" },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  let body: SerpBody = {};
  try {
    body = (await request.json()) as SerpBody;
  } catch {
    return NextResponse.json(
      { ok: false, error: "Invalid JSON body" },
      { status: 400 }
    );
  }

  const {
    keyword: bodyKeyword,
    q,
    prompt,
    gl: _gl,
    hl: _hl,
    engine: _e,
    num: _n,
    model,
    messages,
    ...extra
  } = body;

  const keyword = String(bodyKeyword || q || prompt || "").trim();
  const hasMessages = Array.isArray(messages) && messages.length > 0;

  if (!keyword && !hasMessages) {
    return NextResponse.json(
      {
        ok: false,
        error: 'Provide "keyword" / "q" / "prompt", or OpenAI "messages"',
      },
      { status: 400 }
    );
  }

  const firstUser =
    hasMessages
      ? String(messages!.find((m) => m.role === "user")?.content || "")
      : "";

  try {
    return await callChatCompletions({
      keyword: keyword || firstUser || "chat",
      model: model ? String(model) : undefined,
      messages: hasMessages ? messages : undefined,
      extra,
    });
  } catch (error) {
    console.error("Error calling tok.mom via /api/serp:", error);
    return NextResponse.json(
      { ok: false, error: "Failed to call tok.mom" },
      { status: 500 }
    );
  }
}
