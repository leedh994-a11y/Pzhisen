#!/usr/bin/env node
/**
 * Cookie-based tweet poster (no browser login / no Desktop needed).
 *
 * Required in .env:
 *   GEMINI_API_KEY=...
 *   TWITTER_AUTH_TOKEN=...
 *   TWITTER_CT0=...
 *
 * Usage:
 *   npm run tweet:cookie "your topic"
 *   npm run tweet:cookie -- --text "exact tweet text"
 */
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";
import { createGoogleGenerativeAI } from "@ai-sdk/google";
import { generateText } from "ai";
import { Scraper } from "agent-twitter-client";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
dotenv.config({ path: path.join(root, ".env") });

function parseArgs(argv) {
  const out = { text: null, topic: null };
  const rest = [];
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--text") {
      out.text = argv[++i] || "";
    } else {
      rest.push(argv[i]);
    }
  }
  out.topic = rest.join(" ").trim();
  return out;
}

function requireEnv(name) {
  const v = (process.env[name] || "").trim();
  if (!v || v.startsWith("your_") || v.includes("填这里")) {
    throw new Error(`Missing ${name} in .env`);
  }
  return v;
}

async function generateTweet(topic) {
  const apiKey = requireEnv("GEMINI_API_KEY");
  const google = createGoogleGenerativeAI({ apiKey });
  const modelName = process.env.GEMINI_MODEL || "gemini-2.0-flash";

  const { text } = await generateText({
    model: google(modelName),
    prompt: `Write ONE engaging Twitter/X post in English about this topic.
Rules:
- Max 270 characters
- No hashtag spam (0-2 hashtags max)
- No quotation marks wrapping the whole tweet
- Mention pzhisen.online naturally if relevant to AI store / ecommerce automation
- Topic: ${topic}

Return ONLY the tweet text.`,
  });

  return text.replace(/^["']|["']$/g, "").trim().slice(0, 280);
}

function buildCookies() {
  const auth = requireEnv("TWITTER_AUTH_TOKEN");
  const ct0 = requireEnv("TWITTER_CT0");
  // agent-twitter-client sets cookies against https://twitter.com — Domain must match
  return [
    `auth_token=${auth}; Domain=.twitter.com; Path=/; Secure; HttpOnly; SameSite=None`,
    `ct0=${ct0}; Domain=.twitter.com; Path=/; Secure; SameSite=Lax`,
  ];
}

async function main() {
  const { text: fixedText, topic } = parseArgs(process.argv.slice(2));

  if (!fixedText && !topic) {
    console.error('Usage: npm run tweet:cookie "your topic"');
    console.error('   or: npm run tweet:cookie -- --text "exact tweet"');
    process.exit(1);
  }

  let tweetText = fixedText;
  if (!tweetText) {
    console.log(`🤖 Generating tweet for topic: ${topic}`);
    try {
      tweetText = await generateTweet(topic);
    } catch (e) {
      console.error("❌ Gemini generation failed:", e.message);
      console.error("   Tip: AI Studio keys usually start with AIza...");
      process.exit(1);
    }
  }

  console.log("📝 Tweet:");
  console.log("─".repeat(48));
  console.log(tweetText);
  console.log("─".repeat(48));
  console.log(`📊 Length: ${tweetText.length}/280\n`);

  const scraper = new Scraper();
  try {
    await scraper.setCookies(buildCookies());
    const ok = await scraper.isLoggedIn();
    if (!ok) {
      console.error("❌ Cookie login failed. auth_token / ct0 may be expired.");
      console.error("   Re-copy cookies from a browser where you are logged into x.com");
      process.exit(1);
    }
    console.log("✅ Cookie auth OK — posting...");
    const res = await scraper.sendTweet(tweetText);
    // sendTweet returns a Response-like object in many versions
    const status = res?.status || res?.statusCode;
    console.log("✅ Tweet send requested", status ? `(HTTP ${status})` : "");
    console.log("🎉 Done. Check your X profile for the new post.");
  } catch (e) {
    console.error("❌ Post failed:", e.message || e);
    process.exit(1);
  }
}

main();
