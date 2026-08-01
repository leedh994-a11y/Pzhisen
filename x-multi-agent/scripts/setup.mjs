#!/usr/bin/env node
/**
 * One-time setup helper for Pzhisen x-multi Twitter AI Agent.
 */
import { existsSync, copyFileSync, mkdirSync } from "fs";
import { spawnSync } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");

console.log("🚀 Pzhisen x-multi AI Agent setup\n");

// 1. .env
const envPath = path.join(root, ".env");
const envExample = path.join(root, ".env.example");
if (!existsSync(envPath)) {
  copyFileSync(envExample, envPath);
  console.log("✅ Created .env from .env.example");
  console.log("   → Edit .env and set GEMINI_API_KEY\n");
} else {
  console.log("✅ .env already exists\n");
}

// 2. browser profiles dir
const bp = path.join(root, "browser-profiles");
if (!existsSync(bp)) {
  mkdirSync(bp, { recursive: true });
  console.log("✅ Created browser-profiles/\n");
}

// 3. ensure default profile exists
const list = spawnSync("npx", ["xm-profile", "list"], {
  cwd: root,
  encoding: "utf-8",
  shell: true,
});
console.log(list.stdout || list.stderr || "");

if (!(list.stdout || "").includes("pzhisen")) {
  console.log("Creating default profile: pzhisen ...");
  const create = spawnSync(
    "npx",
    [
      "xm-profile",
      "create",
      "pzhisen",
      "-h",
      "@pzhisen",
      "-p",
      "twitter",
      "-d",
      "Pzhisen official AI store marketing account",
      "-l",
      "en",
    ],
    { cwd: root, encoding: "utf-8", shell: true, stdio: "inherit" }
  );
  if (create.status !== 0) {
    console.warn("⚠️  Profile create may have failed; check config/profiles.json");
  }
} else {
  console.log("✅ Profile pzhisen is configured");
}

console.log(`
============================================================
Next steps (on a machine WITH a display / browser):
============================================================

1. Edit .env and set:
   GEMINI_API_KEY=your_key_from_https://aistudio.google.com/app/apikey

2. First login (opens browser — log into Twitter/X manually):
   npm run login

3. Post a tweet with AI-generated content:
   npm run tweet "Pzhisen AI store — wake up to your first order"

============================================================
`);
