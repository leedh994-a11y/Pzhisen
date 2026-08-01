#!/usr/bin/env node
/**
 * Inject cookies into Chrome via CDP and post a tweet through the UI.
 * Requires Chrome --remote-debugging-port=9222
 */
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";
import CDP from "chrome-remote-interface";
import { createGoogleGenerativeAI } from "@ai-sdk/google";
import { generateText } from "ai";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.resolve(__dirname, "../.env") });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function requireEnv(name) {
  const v = (process.env[name] || "").trim();
  if (!v) throw new Error(`Missing ${name}`);
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

async function evalJson(Runtime, expression) {
  const r = await Runtime.evaluate({
    expression: `(${expression})`,
    returnByValue: true,
    awaitPromise: true,
  });
  if (r.exceptionDetails) {
    throw new Error(r.exceptionDetails.text || "Runtime.evaluate failed");
  }
  return r.result.value;
}

async function waitFor(Runtime, expression, timeoutMs = 20000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    const v = await evalJson(Runtime, expression);
    if (v) return v;
    await sleep(500);
  }
  return null;
}

async function main() {
  const { text: fixed, topic } = parseArgs(process.argv.slice(2));
  if (!fixed && !topic) {
    console.error('Usage: node scripts/tweet-cdp.mjs --text "..."');
    process.exit(1);
  }

  let tweet = fixed;
  if (!tweet) {
    console.log("🤖 Generating...");
    tweet = await generateTweet(topic);
  }
  console.log("📝", tweet);

  const auth = requireEnv("TWITTER_AUTH_TOKEN");
  const ct0 = requireEnv("TWITTER_CT0");

  const client = await CDP({ port: 9222 });
  const { Network, Page, Runtime, Input } = client;
  await Promise.all([Network.enable(), Page.enable(), Runtime.enable()]);

  for (const domain of [".x.com", ".twitter.com"]) {
    await Network.setCookie({
      name: "auth_token",
      value: auth,
      domain,
      path: "/",
      secure: true,
      httpOnly: true,
    });
    await Network.setCookie({
      name: "ct0",
      value: ct0,
      domain,
      path: "/",
      secure: true,
      httpOnly: false,
    });
  }
  console.log("✅ Cookies injected");

  // Don't await loadEventFired (SPA often hangs) — navigate then poll
  await Page.navigate({ url: "https://x.com/compose/post" });
  await sleep(6000);

  const pageInfo = await evalJson(
    Runtime,
    `() => ({url: location.href, text: (document.body?.innerText||'').slice(0,180)})`
  );
  console.log("📍", pageInfo);

  const composerReady = await waitFor(
    Runtime,
    `() => !!(document.querySelector('[data-testid="tweetTextarea_0"]') || document.querySelector('[role="textbox"]'))`,
    25000
  );
  if (!composerReady) {
    console.error("❌ Composer not found — cookie may be invalid");
    await client.close();
    process.exit(1);
  }

  await evalJson(
    Runtime,
    `() => {
      const el = document.querySelector('[data-testid="tweetTextarea_0"]') || document.querySelector('[role="textbox"]');
      el.focus(); el.click();
      return true;
    }`
  );
  await sleep(400);

  // Clear existing
  await Input.dispatchKeyEvent({
    type: "keyDown",
    modifiers: 2,
    key: "a",
    code: "KeyA",
    windowsVirtualKeyCode: 65,
  });
  await Input.dispatchKeyEvent({
    type: "keyUp",
    modifiers: 2,
    key: "a",
    code: "KeyA",
    windowsVirtualKeyCode: 65,
  });
  await Input.dispatchKeyEvent({
    type: "keyDown",
    key: "Backspace",
    code: "Backspace",
    windowsVirtualKeyCode: 8,
  });
  await Input.dispatchKeyEvent({
    type: "keyUp",
    key: "Backspace",
    code: "Backspace",
    windowsVirtualKeyCode: 8,
  });
  await sleep(200);
  await Input.insertText({ text: tweet });
  await sleep(1500);

  // Fallback: set via execCommand if button still disabled
  let state = await evalJson(
    Runtime,
    `() => {
      const el = document.querySelector('[data-testid="tweetTextarea_0"]') || document.querySelector('[role="textbox"]');
      const btn = document.querySelector('[data-testid="tweetButton"]') || document.querySelector('[data-testid="tweetButtonInline"]');
      return { text: (el?.innerText||'').slice(0,120), disabled: btn?.getAttribute('aria-disabled'), btn: !!btn };
    }`
  );
  console.log("🧾 state", state);

  if (state?.disabled === "true" || !(state?.text || "").trim()) {
    console.log("↪️ fallback paste via clipboard API / beforeinput");
    await evalJson(
      Runtime,
      `() => {
        const el = document.querySelector('[data-testid="tweetTextarea_0"]') || document.querySelector('[role="textbox"]');
        el.focus();
        const text = ${JSON.stringify(tweet)};
        // Draft.js-friendly: dispatch input events
        document.execCommand('selectAll', false, null);
        document.execCommand('insertText', false, text);
        el.dispatchEvent(new InputEvent('input', { bubbles: true, data: text, inputType: 'insertText' }));
        return (el.innerText||'').slice(0,120);
      }`
    );
    await sleep(1000);
    state = await evalJson(
      Runtime,
      `() => {
        const el = document.querySelector('[data-testid="tweetTextarea_0"]') || document.querySelector('[role="textbox"]');
        const btn = document.querySelector('[data-testid="tweetButton"]') || document.querySelector('[data-testid="tweetButtonInline"]');
        return { text: (el?.innerText||'').slice(0,120), disabled: btn?.getAttribute('aria-disabled'), btn: !!btn };
      }`
    );
    console.log("🧾 state2", state);
  }

  const posted = await evalJson(
    Runtime,
    `() => {
      const btn = document.querySelector('[data-testid="tweetButton"]') || document.querySelector('[data-testid="tweetButtonInline"]');
      if (!btn) return 'no-button';
      if (btn.getAttribute('aria-disabled') === 'true') return 'disabled';
      btn.click();
      return 'clicked';
    }`
  );
  console.log("📤", posted);
  await sleep(5000);

  const after = await evalJson(
    Runtime,
    `() => ({
      url: location.href,
      sent: /your post was sent|已发送|post was sent/i.test(document.body?.innerText||'')
    })`
  );
  console.log("✅ after", after);

  await client.close();
  if (posted !== "clicked") process.exit(1);
}

main().catch((e) => {
  console.error("❌", e.message || e);
  process.exit(1);
});
