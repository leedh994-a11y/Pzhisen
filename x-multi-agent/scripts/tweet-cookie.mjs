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

async function generateTweet(topic) {
  const google = createGoogleGenerativeAI({ apiKey: requireEnv("GEMINI_API_KEY") });
  const model = process.env.GEMINI_MODEL || "gemini-2.0-flash";
  const { text } = await generateText({
    model: google(model),
    prompt: `Write ONE Twitter/X post in English about: ${topic}
Max 270 chars. No wrapping quotes. 0-2 hashtags. Mention pzhisen.online if relevant.
Return ONLY the tweet text.`,
  });
  return text.replace(/^["']|["']$/g, "").trim().slice(0, 280);
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

    await page.goto("https://x.com/compose/post", {
      waitUntil: "domcontentloaded",
      timeout: 120000,
    });
    await sleep(5000);

    const sel = '[data-testid="tweetTextarea_0"], div[role="textbox"]';
    await page.waitForSelector(sel, { timeout: 25000 });
    await page.click(sel);
    await page.keyboard.down("Control");
    await page.keyboard.press("KeyA");
    await page.keyboard.up("Control");
    await page.keyboard.press("Backspace");
    await page.type(sel, tweet, { delay: 12 });
    await sleep(1200);

    const btn =
      (await page.$('[data-testid="tweetButton"]')) ||
      (await page.$('[data-testid="tweetButtonInline"]'));
    if (!btn) throw new Error("Post button not found");
    const disabled = await page.evaluate(
      (el) => el.getAttribute("aria-disabled"),
      btn
    );
    if (disabled === "true") {
      await page.keyboard.down("Control");
      await page.keyboard.press("Enter");
      await page.keyboard.up("Control");
    } else {
      await btn.click();
    }
    await sleep(5000);

    const ok = await page.evaluate(() =>
      /your post was sent|已发送|post was sent/i.test(document.body.innerText)
    );
    console.log(ok ? "🎉 Tweet posted successfully!" : "⚠️ Posted (verify on profile)");
    console.log("URL:", page.url());
    if (!ok) process.exitCode = 2;
  } finally {
    await browser.disconnect();
  }
}

main().catch((e) => {
  console.error("❌", e.message || e);
  process.exit(1);
});
