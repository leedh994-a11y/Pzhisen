#!/usr/bin/env node
/**
 * Cookie → Chrome CDP/Puppeteer → real X post.
 * Requires Chrome with --remote-debugging-port=9222 (auto-launched if missing).
 *
 * Usage:
 *   npm run tweet:cookie "topic"
 *   npm run tweet:cookie -- --text "exact tweet"
 */
import { spawn } from "child_process";
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";
import puppeteer from "puppeteer-core";
import { createGoogleGenerativeAI } from "@ai-sdk/google";
import { generateText } from "ai";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
dotenv.config({ path: path.join(root, ".env") });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const PROFILE_DIR = path.join(root, "browser-profiles", "twitter-pzhisen");
const CDP = "http://127.0.0.1:9222";

function requireEnv(name) {
  const v = (process.env[name] || "").trim();
  if (!v) throw new Error(`Missing ${name} in .env`);
  return v;
}

function parseArgs(argv) {
  let text = null;
  const rest = [];
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--text") text = argv[++i] || "";
    else rest.push(argv[i]);
  }
  return { text, topic: rest.join(" ").trim() };
}

function localTweetFromPrompt(topic) {
  const cleaned = String(topic || "")
    .replace(/^(请|帮我|发一条|写一条|发推|tweet|post)\s*/i, "")
    .replace(/[。！？]+$/g, "")
    .trim();
  // If user already pasted a full post, keep it.
  if (
    cleaned.length >= 40 ||
    /https?:\/\//i.test(cleaned) ||
    /[\u4e00-\u9fff]/.test(cleaned)
  ) {
    return cleaned.slice(0, 280);
  }
  let body = cleaned || "Pzhisen AI store — automated ecommerce";
  if (!/pzhisen\.online/i.test(body)) {
    body = `${body} — try Pzhisen AI store: https://pzhisen.online`;
  }
  return body.slice(0, 280);
}

async function generateTweet(topic) {
  const apiKey = (process.env.GEMINI_API_KEY || "").trim();
  if (!apiKey || apiKey.includes("your_gemini")) {
    console.warn("⚠️  No GEMINI_API_KEY — using local prompt→tweet fallback");
    return localTweetFromPrompt(topic);
  }
  try {
    const google = createGoogleGenerativeAI({ apiKey });
    const model = process.env.GEMINI_MODEL || "gemini-2.0-flash";
    const { text } = await generateText({
      model: google(model),
      prompt: `Write ONE Twitter/X post in English about: ${topic}
Max 270 chars. No wrapping quotes. 0-2 hashtags. Mention pzhisen.online if relevant.
Return ONLY the tweet text.`,
    });
    return text.replace(/^["']|["']$/g, "").trim().slice(0, 280);
  } catch (e) {
    console.warn(
      "⚠️  Gemini failed, using local fallback:",
      String(e.message || e).slice(0, 120)
    );
    return localTweetFromPrompt(topic);
  }
}

async function cdpUp() {
  try {
    const r = await fetch(`${CDP}/json/version`);
    return r.ok;
  } catch {
    return false;
  }
}

async function ensureChrome() {
  if (await cdpUp()) return;
  console.log("🚀 Launching Chrome...");
  spawn(
    "google-chrome",
    [
      `--user-data-dir=${PROFILE_DIR}`,
      "--no-first-run",
      "--no-default-browser-check",
      "--no-sandbox",
      "--remote-debugging-port=9222",
      "--remote-allow-origins=*",
      "--window-size=1400,900",
      "about:blank",
    ],
    {
      env: { ...process.env, DISPLAY: process.env.DISPLAY || ":1" },
      detached: true,
      stdio: "ignore",
    }
  ).unref();
  for (let i = 0; i < 30; i++) {
    await sleep(500);
    if (await cdpUp()) return;
  }
  throw new Error("Chrome CDP not available on :9222");
}

async function main() {
  const { text: fixed, topic } = parseArgs(process.argv.slice(2));
  if (!fixed && !topic) {
    console.error('Usage: npm run tweet:cookie "topic"');
    console.error('   or: npm run tweet:cookie -- --text "exact tweet"');
    process.exit(1);
  }

  let tweet = fixed;
  if (!tweet) {
    console.log(`🤖 Generating for: ${topic}`);
    tweet = await generateTweet(topic);
  }
  console.log("📝", tweet);

  const auth = requireEnv("TWITTER_AUTH_TOKEN");
  const ct0 = requireEnv("TWITTER_CT0");
  await ensureChrome();

  const browser = await puppeteer.connect({
    browserURL: CDP,
    defaultViewport: null,
    protocolTimeout: 180000,
  });
  try {
    // Close leftover tabs so CDP stays responsive
    const existing = await browser.pages();
    for (const p of existing.slice(1)) {
      try {
        await p.close();
      } catch {
        // ignore
      }
    }

    const page = await browser.newPage();
    page.setDefaultNavigationTimeout(120000);
    page.setDefaultTimeout(120000);
    const cookieBase = [
      {
        name: "auth_token",
        value: auth,
        path: "/",
        secure: true,
        httpOnly: true,
      },
      {
        name: "ct0",
        value: ct0,
        path: "/",
        secure: true,
        httpOnly: false,
      },
    ];
    await page.setCookie(
      ...cookieBase.map((c) => ({ ...c, domain: ".x.com" })),
      ...cookieBase.map((c) => ({ ...c, domain: ".twitter.com" }))
    );

    /** @type {{ status: number, id: string|null, error: string|null }[]} */
    const creates = [];
    page.on("response", async (res) => {
      try {
        const url = res.url();
        if (!/\/CreateTweet/i.test(url)) return;
        const body = await res.text();
        let id = null;
        let error = null;
        try {
          const json = JSON.parse(body);
          const result = json?.data?.create_tweet?.tweet_results?.result;
          id = result?.rest_id || result?.tweet?.rest_id || null;
          if (!id) {
            // Prefer status-like rest_ids near create_tweet payload
            const ids = [...body.matchAll(/"rest_id":"(\d{15,})"/g)].map(
              (m) => m[1]
            );
            // Filter out known user id prefix if present
            id = ids.find((x) => !x.startsWith("2064722622160756736")) || ids[0] || null;
          }
          error =
            json?.errors?.[0]?.message ||
            (typeof result?.reason === "string" ? result.reason : null);
          if (/duplicate|already posted|Status is a duplicate/i.test(body) && !id) {
            error = error || "Status is a duplicate";
          }
        } catch {
          const m = body.match(/"rest_id":"(\d{15,})"/);
          if (m) id = m[1];
        }
        creates.push({ status: res.status(), id, error: error ? String(error) : null });
      } catch {
        // ignore
      }
    });

    await page.goto("https://x.com/compose/post", {
      waitUntil: "domcontentloaded",
      timeout: 120000,
    });
    await sleep(4000);

    const sel = '[data-testid="tweetTextarea_0"], div[role="textbox"]';
    await page.waitForSelector(sel, { timeout: 30000 });
    await page.click(sel);
    await page.keyboard.down("Control");
    await page.keyboard.press("KeyA");
    await page.keyboard.up("Control");
    await page.keyboard.press("Backspace");
    // insertText is more reliable than type() for multilanguage
    try {
      await page.keyboard.insertText(tweet);
    } catch {
      await page.type(sel, tweet, { delay: 10 });
    }
    await sleep(2000);

    // Wait until Post is enabled
    for (let i = 0; i < 20; i++) {
      const ready = await page.evaluate(() => {
        const b =
          document.querySelector('[data-testid="tweetButton"]') ||
          document.querySelector('[data-testid="tweetButtonInline"]');
        if (!b) return false;
        return b.getAttribute("aria-disabled") !== "true";
      });
      if (ready) break;
      await sleep(250);
    }

    const clicked = await page.evaluate(() => {
      const b =
        document.querySelector('[data-testid="tweetButton"]') ||
        document.querySelector('[data-testid="tweetButtonInline"]');
      if (!b) return "missing";
      b.click();
      return "clicked";
    });
    if (clicked !== "clicked") throw new Error("Post button not found");

    // Fallback shortcut if GraphQL hasn't fired
    for (let i = 0; i < 10 && creates.length === 0; i++) {
      await sleep(500);
    }
    if (creates.length === 0) {
      await page.keyboard.down("Control");
      await page.keyboard.press("Enter");
      await page.keyboard.up("Control");
    }

    for (let i = 0; i < 40 && creates.length === 0; i++) {
      await sleep(500);
    }

    const hit = creates.find((c) => c.id) || creates[0];
    if (!hit?.id) {
      const detail = hit
        ? `status=${hit.status} error=${hit.error || "no rest_id"}`
        : "no CreateTweet response (button click did not publish)";
      console.error("❌ Publish not confirmed:", detail);
      console.error(
        "   Tip: change the wording (X rejects duplicates) and retry; confirm you are viewing @Pzhise."
      );
      process.exit(1);
    }

    const tweetUrl = `https://x.com/Pzhise/status/${hit.id}`;
    console.log("🎉 Tweet posted successfully!");
    console.log(`🔗 ${tweetUrl}`);
    console.log(`🆔 ${hit.id}`);
    console.log("URL:", tweetUrl);
  } finally {
    await browser.disconnect();
  }
}

main().catch((e) => {
  console.error("❌", e.message || e);
  process.exit(1);
});
