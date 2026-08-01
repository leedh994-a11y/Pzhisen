#!/usr/bin/env node
/**
 * Official X API v2 posting (OAuth 1.0a user context).
 *
 * Required in .env:
 *   TWITTER_API_KEY
 *   TWITTER_API_SECRET
 *   TWITTER_ACCESS_TOKEN
 *   TWITTER_ACCESS_SECRET
 * Optional:
 *   GEMINI_API_KEY  (for topic → AI copy)
 *
 * Usage:
 *   npm run tweet:api "your topic"
 *   npm run tweet:api -- --text "exact tweet text"
 */
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";
import { TwitterApi } from "twitter-api-v2";
import { createGoogleGenerativeAI } from "@ai-sdk/google";
import { generateText } from "ai";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.resolve(__dirname, "../.env") });

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
  const apiKey = requireEnv("GEMINI_API_KEY");
  const google = createGoogleGenerativeAI({ apiKey });
  const model = process.env.GEMINI_MODEL || "gemini-2.0-flash";
  const { text } = await generateText({
    model: google(model),
    prompt: `Write ONE Twitter/X post in English about: ${topic}
Max 270 characters. No wrapping quotes. 0-2 hashtags max.
Mention https://pzhisen.online naturally if relevant to AI ecommerce / automated stores.
Return ONLY the tweet text.`,
  });
  return text.replace(/^["']|["']$/g, "").trim().slice(0, 280);
}

function client() {
  return new TwitterApi({
    appKey: requireEnv("TWITTER_API_KEY"),
    appSecret: requireEnv("TWITTER_API_SECRET"),
    accessToken: requireEnv("TWITTER_ACCESS_TOKEN"),
    accessSecret: requireEnv("TWITTER_ACCESS_SECRET"),
  });
}

async function main() {
  const { text: fixed, topic } = parseArgs(process.argv.slice(2));
  if (!fixed && !topic) {
    console.error('Usage: npm run tweet:api "topic"');
    console.error('   or: npm run tweet:api -- --text "exact tweet"');
    process.exit(1);
  }

  let tweet = fixed;
  if (!tweet) {
    console.log(`🤖 Generating tweet for: ${topic}`);
    tweet = await generateTweet(topic);
  }

  console.log("📝 Tweet:");
  console.log("─".repeat(48));
  console.log(tweet);
  console.log("─".repeat(48));
  console.log(`📊 Length: ${tweet.length}/280\n`);

  const rw = client().readWrite;
  try {
    const me = await rw.v2.me();
    console.log(`✅ Auth OK as @${me.data.username} (${me.data.name})`);
  } catch (e) {
    console.error("❌ Auth/verify failed:", e?.data || e.message || e);
    console.error("   Check keys, App permissions = Read and Write, and regenerate Access Token after permission change.");
    process.exit(1);
  }

  try {
    const res = await rw.v2.tweet(tweet);
    const id = res?.data?.id;
    console.log("🎉 Tweet posted via official X API");
    if (id) {
      console.log(`🔗 https://x.com/i/web/status/${id}`);
      console.log(`🆔 ${id}`);
    }
  } catch (e) {
    console.error("❌ Post failed:", e?.data || e.message || e);
    const msg = JSON.stringify(e?.data || e.message || "");
    if (/403|forbidden|client-not-enrolled|payment|credits/i.test(msg)) {
      console.error("   Tip: ensure Billing/Credits > 0 and the App is allowed to write.");
    }
    process.exit(1);
  }
}

main();
