import { NextRequest, NextResponse } from "next/server";

/**
 * Secure server-side SERP proxy for V0 / Next.js.
 *
 * Env (Vercel / v0 project → Environment Variables):
 *   SERP_API_KEY=your_provider_token
 *   SERP_API_URL=https://api.your-serp-provider.com/v1/search
 *   SERP_API_METHOD=POST          (optional, default POST)
 *   SERP_API_AUTH_HEADER=Authorization  (optional)
 *   SERP_API_AUTH_PREFIX=Bearer         (optional, use "" for raw token)
 *
 * Frontend NEVER sees SERP_API_KEY — only calls this route:
 *   GET  /api/serp?keyword=ai+store
 *   POST /api/serp  { "keyword": "ai store", "gl": "us", "hl": "en" }
 */
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type SerpBody = {
  keyword?: string;
  q?: string;
  gl?: string;
  hl?: string;
  engine?: string;
  num?: number;
  [key: string]: unknown;
};

function getToken() {
  return (process.env.SERP_API_KEY || process.env.SERPAPI_API_KEY || "").trim();
}

function getUpstreamUrl() {
  return (
    process.env.SERP_API_URL ||
    process.env.SERPAPI_API_URL ||
    "https://api.your-serp-provider.com/v1/search"
  ).trim();
}

function buildAuthHeader(token: string): Record<string, string> {
  const headerName = (process.env.SERP_API_AUTH_HEADER || "Authorization").trim();
  const prefix = process.env.SERP_API_AUTH_PREFIX;
  // default Bearer; set SERP_API_AUTH_PREFIX= to send raw token
  const value =
    prefix === undefined || prefix === null
      ? `Bearer ${token}`
      : prefix === ""
        ? token
        : `${prefix} ${token}`.trim();
  return { [headerName]: value };
}

async function callSerp(params: {
  keyword: string;
  gl?: string;
  hl?: string;
  engine?: string;
  num?: number;
  extra?: Record<string, unknown>;
}) {
  const token = getToken();
  const upstream = getUpstreamUrl();
  const method = (process.env.SERP_API_METHOD || "POST").toUpperCase();

  if (!token) {
    return NextResponse.json(
      { ok: false, error: "SERP_API_KEY not configured" },
      { status: 500 }
    );
  }

  if (!upstream || upstream.includes("your-serp-provider.com")) {
    return NextResponse.json(
      {
        ok: false,
        error:
          "SERP_API_URL not configured. Set it to your provider endpoint in Vercel env.",
      },
      { status: 500 }
    );
  }

  const payload = {
    q: params.keyword,
    keyword: params.keyword,
    ...(params.gl ? { gl: params.gl } : {}),
    ...(params.hl ? { hl: params.hl } : {}),
    ...(params.engine ? { engine: params.engine } : {}),
    ...(params.num ? { num: params.num } : {}),
    ...(params.extra || {}),
  };

  let response: Response;

  if (method === "GET") {
    const url = new URL(upstream);
    for (const [k, v] of Object.entries(payload)) {
      if (v !== undefined && v !== null) url.searchParams.set(k, String(v));
    }
    // Some providers use ?api_key=
    if (process.env.SERP_API_KEY_QUERY === "true") {
      url.searchParams.set("api_key", token);
    }
    response = await fetch(url.toString(), {
      method: "GET",
      headers: {
        Accept: "application/json",
        ...buildAuthHeader(token),
      },
      cache: "no-store",
    });
  } else {
    response = await fetch(upstream, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...buildAuthHeader(token),
      },
      body: JSON.stringify(payload),
      cache: "no-store",
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
        error: `Upstream SERP failed with status ${response.status}`,
        status: response.status,
        data,
      },
      { status: 502 }
    );
  }

  return NextResponse.json({
    ok: true,
    keyword: params.keyword,
    data,
  });
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const keyword = (searchParams.get("keyword") || searchParams.get("q") || "").trim();

  if (!keyword) {
    return NextResponse.json(
      { ok: false, error: "keyword parameter is required" },
      { status: 400 }
    );
  }

  try {
    return await callSerp({
      keyword,
      gl: searchParams.get("gl") || undefined,
      hl: searchParams.get("hl") || undefined,
      engine: searchParams.get("engine") || undefined,
      num: searchParams.get("num")
        ? Number(searchParams.get("num"))
        : undefined,
    });
  } catch (error) {
    console.error("Error fetching SERP data:", error);
    return NextResponse.json(
      { ok: false, error: "Failed to fetch SERP data" },
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

  const keyword = String(body.keyword || body.q || "").trim();
  if (!keyword) {
    return NextResponse.json(
      { ok: false, error: 'Provide "keyword" (or "q")' },
      { status: 400 }
    );
  }

  const {
    keyword: _k,
    q: _q,
    gl,
    hl,
    engine,
    num,
    ...extra
  } = body;

  try {
    return await callSerp({
      keyword,
      gl: gl ? String(gl) : undefined,
      hl: hl ? String(hl) : undefined,
      engine: engine ? String(engine) : undefined,
      num: typeof num === "number" ? num : undefined,
      extra,
    });
  } catch (error) {
    console.error("Error fetching SERP data:", error);
    return NextResponse.json(
      { ok: false, error: "Failed to fetch SERP data" },
      { status: 500 }
    );
  }
}
