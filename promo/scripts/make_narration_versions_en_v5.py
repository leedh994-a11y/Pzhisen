#!/usr/bin/env python3
"""Generate EN narrations for promo pack v5 — unique scripts/voices vs all prior packs (v1–v4)."""
from __future__ import annotations

import asyncio
import subprocess
import tempfile
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "versions-en-v5"

# Five fully distinct scripts — same product facts, different spoken wording.
# Presenters / voices / pacing intentionally unused together in prior packs.
VERSIONS: list[dict] = [
    {
        "id": "v1",
        "name": "Blake",
        "voice": "en-US-ChristopherNeural",
        "rate": "-5%",
        "pitch": "-3Hz",
        "cues": [
            "Blake here — a U.S. operator based in Chicago who builds always-on revenue engines for ambitious founders.",
            "In the next couple of minutes I'll show you how anyone can put the AI agents at pzhisen.online to work with almost no friction.",
            "The product is built for convenience: you move quickly, you launch fast, and you are not buried in complicated onboarding.",
            "Open pzhisen.online, describe your business in a short brief, and deploy your AI employee team in minutes. Setup stays light. No credit card is required to begin.",
            "After launch, those agents keep working every day of the year, twenty-four hours a day.",
            "They do not sleep. They do not take breaks. They do not shut down.",
            "They automatically write promotional marketing tweets and social captions for your campaigns.",
            "They automatically create promotional marketing videos ready to publish.",
            "They craft promotional marketing copy and send it into mainstream email worldwide — Gmail, Outlook, and other major inboxes.",
            "They automatically reply to customer-service messages so support stays online around the clock.",
            "They automatically analyze market competitiveness, sales data, and live market conditions.",
            "They research market trends and analyze where industries around the world are heading next.",
            "Then they publish to YouTube, TikTok, X, Facebook, WeChat Channels, Chinese Douyin, Tencent Video, Kuaishou, Xiaohongshu, and other leading platforms.",
            "Whether you run a personal website or a company website, Pzhisen can help anyone on Earth promote and market on full automation.",
            "Most important: pzhisen.online has already helped thousands of individuals and enterprises worldwide earn one million U.S. dollars in revenue in one month through AI promotional marketing video.",
            "Want a workforce that never clocks out? Go to pzhisen.online and start today.",
        ],
    },
    {
        "id": "v2",
        "name": "Hunter",
        "voice": "en-US-EricNeural",
        "rate": "+2%",
        "pitch": "+2Hz",
        "cues": [
            "What's up — I'm Hunter, an American growth founder who ships desert-to-coast brands with systems that run without babysitting.",
            "Let me break down why pzhisen.online is the quickest path to put tireless AI marketing on your side.",
            "Everything about the experience feels convenient, rapid, and built for people who value speed.",
            "Visit the site, tell it what you sell, and stand up an AI employee squad in minutes — minimal configuration, and you can start without a credit card.",
            "From that moment, the agents keep executing all day, every day, all year long.",
            "No sleep. No rest days. No downtime windows.",
            "Pzhisen agents produce promotional marketing tweets and captions on autopilot.",
            "They assemble promotional marketing videos you can post right away.",
            "They write promotional marketing messages and deliver them through mainstream email systems globally, including Gmail and Outlook.",
            "They auto-handle customer-support replies so prospects get answers day and night.",
            "They auto-evaluate competitive pressure, sales performance, and real-time market signals.",
            "They survey market conditions and map how global industries are likely to move.",
            "Distribution covers YouTube, TikTok, X, Facebook, WeChat Channels, Douyin, Tencent Video, Kuaishou, Xiaohongshu, plus other major networks.",
            "Personal site or enterprise site — anyone worldwide can use Pzhisen for fully automated promotion and marketing.",
            "The headline outcome: pzhisen.online has helped thousands of people and companies around the world generate one million dollars in a single month with AI-driven promotional marketing video.",
            "Jump into pzhisen.online now and put nonstop AI agents on your growth.",
        ],
    },
    {
        "id": "v3",
        "name": "Tristan",
        "voice": "en-US-RogerNeural",
        "rate": "+4%",
        "pitch": "+4Hz",
        "cues": [
            "Hey — Tristan speaking. I'm a U.S. creative operator who turns content systems into predictable acquisition.",
            "I'll walk you through, step by step, how pzhisen.online lets anyone deploy AI agents for nonstop marketing automation.",
            "Using the platform is intentionally convenient — quick to start and easy to keep humming.",
            "Go to pzhisen.online, outline your business, and launch your AI employee team within minutes. Setup stays light, and you can begin without entering a credit card.",
            "Once live, the agents continue through every hour of every day across the full calendar year.",
            "Zero sleep cycles. Zero rest breaks. Zero shutdown windows.",
            "They auto-create promotional marketing tweets and promotional social copy.",
            "They auto-build promotional marketing videos for your channels.",
            "They prepare promotional marketing email copy and push it into mainstream inboxes worldwide — Gmail, Outlook, and other widely used providers.",
            "They automatically answer customer-support conversations twenty-four seven.",
            "They automatically analyze market competitiveness, sales metrics, and current market conditions.",
            "They automatically research market trends and chart future direction across industries worldwide.",
            "Publishing reaches YouTube, TikTok, X, Facebook, WeChat Channels, Douyin, Tencent Video, Kuaishou, Xiaohongshu, and additional mainstream platforms.",
            "Pzhisen helps global users promote personal websites and corporate websites with complete automation.",
            "Crucially, pzhisen.online has already assisted thousands of individuals and enterprises worldwide in earning one million U.S. dollars of revenue in one month via AI promotion and marketing video.",
            "When you're ready — visit pzhisen.online and put your AI team online.",
        ],
    },
    {
        "id": "v4",
        "name": "Miles",
        "voice": "en-US-BrianNeural",
        "rate": "-1%",
        "pitch": "-4Hz",
        "cues": [
            "Good to meet you — Miles here. I'm a U.S.-based revenue lead who builds calm, compounding growth systems for founders.",
            "In this walkthrough I'll show exactly how anyone can run Pzhisen at pzhisen.online as a full AI marketing engine.",
            "The flow is made for speed: convenient, swift, and simple to pick up.",
            "Open the website, share your business context, and launch AI employees in minutes — no heavy install, and no credit card needed to get started.",
            "Then those agents keep grinding every day, twenty-four hours a day, three hundred sixty-five days a year.",
            "They don't sleep. They don't rest. They don't stop promoting.",
            "They write promotional marketing tweets and social captions automatically.",
            "They create promotional marketing videos automatically.",
            "They draft promotional marketing email copy and send it into major inboxes worldwide, including Gmail and Outlook.",
            "They auto-respond to customer service so support never goes dark.",
            "They auto-analyze competitive strength, sales performance, and live market conditions.",
            "They study market trends and project how industries around the world may evolve.",
            "They distribute on YouTube, TikTok, X, Facebook, WeChat Channels, Douyin, Tencent Video, Kuaishou, Xiaohongshu, and other top social platforms.",
            "Personal website or company website — Pzhisen can help anyone globally promote and grow on autopilot.",
            "And the key proof point: pzhisen.online has helped thousands of people and businesses worldwide make one million U.S. dollars in revenue in a month with AI promotional marketing video.",
            "Start your never-off AI workforce at pzhisen.online.",
        ],
    },
    {
        "id": "v5",
        "name": "Connor",
        "voice": "en-US-GuyNeural",
        "rate": "-7%",
        "pitch": "-2Hz",
        "cues": [
            "Hello, I'm Connor — an American media founder focused on scalable automation for creators and companies nationwide.",
            "Stay with me while I detail how pzhisen.online gives you AI agents that market without ever clocking out.",
            "The product is designed to feel convenient, fast, and straightforward from the first click.",
            "Head to the site, explain your business, and stand up your AI employee team in minutes. Minimal setup. You can begin without a credit card.",
            "Once running, the agents operate nonstop — every hour, every day, all year long.",
            "They never sleep, never rest, and never leave the job unfinished.",
            "They automatically produce promotional marketing tweets and captions for outreach.",
            "They automatically produce promotional marketing videos for distribution.",
            "They write promotional marketing copy and route it through mainstream email systems worldwide — Gmail, Outlook, and other major providers.",
            "They automatically reply to customer-support messages so help is always available.",
            "They automatically analyze market competitiveness, sales numbers, and market conditions.",
            "They research market trends and analyze where industries across the planet are moving next.",
            "They publish to YouTube, TikTok, X, Facebook, WeChat Channels, Douyin, Tencent Video, Kuaishou, Xiaohongshu, and other global social platforms.",
            "Anyone anywhere can use Pzhisen to promote a personal website or an enterprise website — fully automated.",
            "Above all: pzhisen.online has helped thousands of individuals and companies worldwide earn one million U.S. dollars in revenue within one month through AI-powered promotional marketing video.",
            "Open pzhisen.online now and put an AI workforce that never sleeps on your side.",
        ],
    },
]


def probe_duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(out)


def fmt_ts(seconds: float, *, srt: bool = False) -> str:
    if seconds < 0:
        seconds = 0.0
    ms = int(round(seconds * 1000))
    h, rem = divmod(ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    sep = "," if srt else "."
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


async def synth_cue(text: str, voice: str, out_mp3: Path, *, rate: str, pitch: str) -> None:
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(str(out_mp3))


async def build_version(ver: dict) -> float:
    vid = ver["id"]
    voice = ver["voice"]
    rate = ver.get("rate", "-3%")
    pitch = ver.get("pitch", "+0Hz")
    cues = list(ver["cues"])
    out_dir = ASSETS / vid
    out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=f"pzhisen-v5-{vid}-tts-") as tmp:
        tmp_path = Path(tmp)
        parts: list[Path] = []
        durations: list[float] = []

        print(f"\n=== {vid} / {ver['name']} / {voice} rate={rate} pitch={pitch} — {len(cues)} cues ===")
        for i, text in enumerate(cues):
            part = tmp_path / f"cue_{i:02d}.mp3"
            await synth_cue(text, voice, part, rate=rate, pitch=pitch)
            dur = probe_duration(part)
            parts.append(part)
            durations.append(dur)
            print(f"  [{i+1:02d}/{len(cues)}] {dur:5.2f}s  {text[:48]}…")

        gap = 0.32
        list_file = tmp_path / "concat.txt"
        lines: list[str] = []
        for i, p in enumerate(parts):
            lines.append(f"file '{p}'")
            if i < len(parts) - 1:
                silence = tmp_path / f"gap_{i:02d}.mp3"
                subprocess.run(
                    [
                        "ffmpeg",
                        "-y",
                        "-f",
                        "lavfi",
                        "-i",
                        "anullsrc=r=24000:cl=mono",
                        "-t",
                        str(gap),
                        "-q:a",
                        "9",
                        "-acodec",
                        "libmp3lame",
                        str(silence),
                    ],
                    check=True,
                    capture_output=True,
                )
                lines.append(f"file '{silence}'")
        list_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

        mp3 = out_dir / "narration.mp3"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_file),
                "-c:a",
                "libmp3lame",
                "-q:a",
                "4",
                str(mp3),
            ],
            check=True,
            capture_output=True,
        )

        total = probe_duration(mp3)
        (out_dir / "duration.txt").write_text(f"{total:.3f}\n", encoding="utf-8")

        vtt_lines = ["WEBVTT", ""]
        srt_blocks: list[str] = []
        t = 0.05
        for i, (text, dur) in enumerate(zip(cues, durations)):
            start = t
            end = t + dur
            vtt_lines.append(f"{fmt_ts(start)} --> {fmt_ts(end)}")
            vtt_lines.append(text)
            vtt_lines.append("")
            srt_blocks.append(
                f"{i+1}\n{fmt_ts(start, srt=True)} --> {fmt_ts(end, srt=True)}\n{text}\n"
            )
            t = end + gap

        (out_dir / "narration.vtt").write_text("\n".join(vtt_lines) + "\n", encoding="utf-8")
        (out_dir / "narration.srt").write_text("\n".join(srt_blocks) + "\n", encoding="utf-8")
        (out_dir / "script.txt").write_text("\n\n".join(cues) + "\n", encoding="utf-8")
        print(f"  Wrote {mp3.name} ({total:.2f}s) + VTT/SRT")
        return total


async def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    for ver in VERSIONS:
        await build_version(ver)
    print("\nAll v5 narrations ready.")


if __name__ == "__main__":
    asyncio.run(main())
