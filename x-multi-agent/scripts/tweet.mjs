#!/usr/bin/env node
/**
 * npm run tweet "your topic"
 * Wrapper around xm-post with default Pzhisen profile.
 */
import { spawn } from "child_process";
import dotenv from "dotenv";
import { fileURLToPath } from "url";
import path from "path";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
dotenv.config({ path: path.join(root, ".env") });

const topic = process.argv.slice(2).join(" ").trim();
if (!topic) {
  console.error('Usage: npm run tweet "your topic"');
  console.error('Example: npm run tweet "Pzhisen AI store first sale overnight"');
  process.exit(1);
}

if (!process.env.GEMINI_API_KEY && !process.env.GOOGLE_API_KEY) {
  console.error("❌ Missing GEMINI_API_KEY in .env");
  console.error("   1. Copy .env.example → .env");
  console.error("   2. Add your key from https://aistudio.google.com/app/apikey");
  process.exit(1);
}

const profile = process.env.DEFAULT_PROFILE || "pzhisen";
console.log(`🐦 Posting with profile "${profile}"`);
console.log(`📌 Topic: ${topic}\n`);

const child = spawn(
  "npx",
  ["xm-post", topic, "--profile", profile],
  { cwd: root, stdio: "inherit", env: process.env, shell: true }
);

child.on("exit", (code) => process.exit(code ?? 1));
