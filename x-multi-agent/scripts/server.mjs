#!/usr/bin/env node
/**
 * V0 / website HTTP backend for natural-language tweeting to @Pzhise.
 *
 * Endpoints:
 *   GET  /health
 *   POST /api/tweet
 *   POST /api/v0/tweet   (alias for V0)
 *
 * Body (JSON):
 *   { "prompt": "自然语言描述要发什么" }   // preferred for V0
 *   { "topic": "..." }                     // same as prompt
 *   { "text": "exact tweet text" }         // skip AI generation
 *   { "dryRun": true }                     // optional: generate only, do not post
 *
 * Auth:
 *   Authorization: Bearer <AGENT_API_TOKEN>
 *
 * Usage: npm run server
 */
import http from "http";
import { spawn } from "child_process";
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
dotenv.config({ path: path.join(root, ".env") });

const PORT = Number(process.env.AGENT_PORT || 8787);
const TOKEN = process.env.AGENT_API_TOKEN || "";
const CORS_ORIGIN = process.env.CORS_ORIGIN || "*";

function setCors(res) {
  res.setHeader("Access-Control-Allow-Origin", CORS_ORIGIN);
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  res.setHeader(
    "Access-Control-Allow-Headers",
    "Content-Type, Authorization"
  );
}

function send(res, status, obj) {
  setCors(res);
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.end(JSON.stringify(obj));
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on("data", (c) => chunks.push(c));
    req.on("end", () => {
      try {
        resolve(JSON.parse(Buffer.concat(chunks).toString("utf8") || "{}"));
      } catch (e) {
        reject(e);
      }
    });
    req.on("error", reject);
  });
}

function hasCookies() {
  const a = (process.env.TWITTER_AUTH_TOKEN || "").trim();
  const c = (process.env.TWITTER_CT0 || "").trim();
  return Boolean(a && c);
}

function hasOfficialApi() {
  return [
    "TWITTER_API_KEY",
    "TWITTER_API_SECRET",
    "TWITTER_ACCESS_TOKEN",
    "TWITTER_ACCESS_SECRET",
  ].every((k) => (process.env[k] || "").trim());
}

function resolveMode() {
  const mode = (process.env.TWEET_MODE || "").toLowerCase();
  if (mode === "api" || mode === "cookie" || mode === "browser") return mode;
  if (hasOfficialApi()) return "api";
  if (hasCookies()) return "cookie";
  return "browser";
}

function requireAuth(req) {
  if (!TOKEN) return true;
  const auth = req.headers.authorization || "";
  return auth === `Bearer ${TOKEN}`;
}

function runTweet({ topic, text, dryRun }) {
  const mode = resolveMode();
  let cmd;

  if (dryRun) {
    // Generate only via tweet-api with a dry-run flag if we add it later;
    // for now run generate through tweet-api path using a special env.
    cmd = text
      ? ["node", "./scripts/tweet-api.mjs", "--text", text, "--dry-run"]
      : ["node", "./scripts/tweet-api.mjs", topic, "--dry-run"];
  } else if (mode === "api") {
    cmd = text
      ? ["node", "./scripts/tweet-api.mjs", "--text", text]
      : ["node", "./scripts/tweet-api.mjs", topic];
  } else if (mode === "cookie") {
    cmd = text
      ? ["node", "./scripts/tweet-cookie.mjs", "--text", text]
      : ["node", "./scripts/tweet-cookie.mjs", topic];
  } else {
    cmd = [
      "npx",
      "xm-post",
      topic || text,
      "--profile",
      process.env.DEFAULT_PROFILE || "pzhisen",
    ];
  }

  console.log(`[api] mode=${mode} dryRun=${Boolean(dryRun)}`);

  return new Promise((resolve) => {
    const child = spawn(cmd[0], cmd.slice(1), {
      cwd: root,
      env: process.env,
      shell: false,
    });
    let out = "";
    let err = "";
    child.stdout.on("data", (d) => (out += d.toString()));
    child.stderr.on("data", (d) => (err += d.toString()));
    child.on("exit", (code) => resolve({ code: code ?? 1, out, err }));
  });
}

function parseTweetResult(out) {
  const idMatch = out.match(/🆔\s+(\d+)/) || out.match(/status\/(\d+)/);
  const urlMatch = out.match(/https:\/\/x\.com\/i\/web\/status\/\d+/);
  const userMatch = out.match(/Auth OK as @(\w+)/);
  const tweetBlock = out.match(/📝 Tweet:\n─+\n([\s\S]*?)\n─+/);
  return {
    tweetId: idMatch?.[1] || null,
    tweetUrl: urlMatch?.[0] || (idMatch?.[1] ? `https://x.com/i/web/status/${idMatch[1]}` : null),
    username: userMatch?.[1] || "Pzhise",
    generatedText: tweetBlock?.[1]?.trim() || null,
  };
}

async function handleTweet(req, res) {
  if (!requireAuth(req)) {
    return send(res, 401, { ok: false, error: "unauthorized" });
  }

  let body;
  try {
    body = await readBody(req);
  } catch {
    return send(res, 400, { ok: false, error: "invalid JSON body" });
  }

  // Natural language fields accepted from V0 UIs
  const prompt = String(
    body.prompt || body.message || body.topic || body.input || ""
  ).trim();
  const text = String(body.text || body.tweet || "").trim();
  const dryRun = Boolean(body.dryRun || body.preview);

  if (!prompt && !text) {
    return send(res, 400, {
      ok: false,
      error: 'Provide natural language in "prompt" (or "topic"), or exact "text"',
      example: {
        prompt: "发一条关于 Pzhisen AI 店铺凌晨自动出单的推广推文",
      },
    });
  }

  console.log(
    `[api] ${dryRun ? "preview" : "tweet"}: ${(text || prompt).slice(0, 100)}`
  );

  const result = await runTweet({ topic: prompt, text, dryRun });
  const parsed = parseTweetResult(result.out);
  const ok = result.code === 0;

  return send(res, ok ? 200 : 500, {
    ok,
    mode: resolveMode(),
    dryRun,
    account: `@${parsed.username}`,
    prompt: prompt || null,
    text: parsed.generatedText || text || null,
    tweetId: parsed.tweetId,
    tweetUrl: parsed.tweetUrl,
    message: ok
      ? dryRun
        ? "Preview generated (not posted)"
        : "Tweet posted to X"
      : "Tweet failed",
    output: result.out.slice(-3000),
    error: result.err.slice(-1500) || null,
  });
}

const server = http.createServer(async (req, res) => {
  const url = (req.url || "").split("?")[0];

  if (req.method === "OPTIONS") {
    setCors(res);
    res.statusCode = 204;
    res.end();
    return;
  }

  if (req.method === "GET" && url === "/health") {
    return send(res, 200, {
      ok: true,
      service: "pzhisen-x-multi-agent",
      account: "@Pzhise",
      mode: resolveMode(),
      v0: {
        post: "/api/v0/tweet",
        body: { prompt: "natural language description" },
      },
    });
  }

  if (
    req.method === "POST" &&
    (url === "/api/tweet" || url === "/api/v0/tweet")
  ) {
    return handleTweet(req, res);
  }

  return send(res, 404, {
    ok: false,
    error: "not found",
    endpoints: ["GET /health", "POST /api/tweet", "POST /api/v0/tweet"],
  });
});

server.listen(PORT, () => {
  console.log(`Pzhisen V0 tweet API listening on :${PORT}`);
  console.log(`POST /api/v0/tweet  {"prompt":"自然语言..."}`);
  if (!TOKEN) console.warn("⚠️  AGENT_API_TOKEN not set — endpoint is open");
});
