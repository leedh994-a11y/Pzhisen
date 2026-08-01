#!/usr/bin/env node
/**
 * Optional HTTP backend for triggering tweets from a website / v0 API route.
 * Usage: npm run server
 * POST /api/tweet  { "topic": "..." }
 *
 * Security: set AGENT_API_TOKEN in .env and send Authorization: Bearer <token>
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
  return ["TWITTER_API_KEY", "TWITTER_API_SECRET", "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_SECRET"]
    .every((k) => (process.env[k] || "").trim());
}

function resolveMode() {
  const mode = (process.env.TWEET_MODE || "").toLowerCase();
  if (mode === "api" || mode === "cookie" || mode === "browser") return mode;
  if (hasOfficialApi()) return "api";
  if (hasCookies()) return "cookie";
  return "browser";
}

function runTweet(topic, text) {
  const mode = resolveMode();
  let cmd;
  if (mode === "api") {
    cmd = text
      ? ["node", "./scripts/tweet-api.mjs", "--text", text]
      : ["node", "./scripts/tweet-api.mjs", topic];
  } else if (mode === "cookie") {
    cmd = text
      ? ["node", "./scripts/tweet-cookie.mjs", "--text", text]
      : ["node", "./scripts/tweet-cookie.mjs", topic];
  } else {
    cmd = ["npx", "xm-post", topic || text, "--profile", process.env.DEFAULT_PROFILE || "pzhisen"];
  }

  console.log(`[api] mode=${mode}`);

  return new Promise((resolve) => {
    // Do NOT use shell:true — it splits tweet text on spaces.
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

const server = http.createServer(async (req, res) => {
  res.setHeader("Content-Type", "application/json");

  if (req.method === "GET" && req.url === "/health") {
    res.end(JSON.stringify({ ok: true, service: "pzhisen-x-multi-agent" }));
    return;
  }

  if (req.method === "POST" && req.url === "/api/tweet") {
    if (TOKEN) {
      const auth = req.headers.authorization || "";
      if (auth !== `Bearer ${TOKEN}`) {
        res.statusCode = 401;
        res.end(JSON.stringify({ ok: false, error: "unauthorized" }));
        return;
      }
    }

    try {
      const body = await readBody(req);
      const topic = (body.topic || "").trim();
      const text = (body.text || "").trim();
      if (!topic && !text) {
        res.statusCode = 400;
        res.end(JSON.stringify({ ok: false, error: 'missing "topic" or "text"' }));
        return;
      }

      console.log(`[api] tweet ${text ? "text" : "topic"}: ${(text || topic).slice(0, 80)}`);
      const result = await runTweet(topic, text);
      res.statusCode = result.code === 0 ? 200 : 500;
      res.end(
        JSON.stringify({
          ok: result.code === 0,
          code: result.code,
          mode: resolveMode(),
          output: result.out.slice(-4000),
          error: result.err.slice(-2000),
        })
      );
    } catch (e) {
      res.statusCode = 500;
      res.end(JSON.stringify({ ok: false, error: String(e.message || e) }));
    }
    return;
  }

  res.statusCode = 404;
  res.end(JSON.stringify({ ok: false, error: "not found" }));
});

server.listen(PORT, () => {
  console.log(`Pzhisen x-multi agent API listening on :${PORT}`);
  console.log(`POST /api/tweet  {"topic":"..."}`);
  if (!TOKEN) console.warn("⚠️  AGENT_API_TOKEN not set — endpoint is open");
});
