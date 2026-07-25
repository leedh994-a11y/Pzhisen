#!/usr/bin/env python3
"""Generate EN narrations for promo pack v3 — unique scripts/voices vs all prior packs."""
from __future__ import annotations

import asyncio
import subprocess
import tempfile
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "versions-en-v3"

# Five fully distinct scripts — same product facts, different spoken wording.
VERSIONS: list[dict] = [
    {
        "id": "v1",
        "name": "Brandon",
        "voice": "en-US-GuyNeural",
        "rate": "-3%",
        "pitch": "-1Hz",
        "cues": [
            "What's up — Brandon speaking. I'm an American founder who runs multi-channel growth from New York to California.",
            "I'm here to break down the fastest way to put Pzhisen to work for you at pzhisen.online.",
            "Getting started feels almost effortless — convenient, rapid, and built for busy people.",
            "Open the website, tell it what your business does, and spin up your AI employee team in minutes. Light setup. No credit card required to begin.",
            "Once they're live, those agents keep executing every day of the year, around the clock.",
            "Zero sleeping. Zero downtime. Zero quitting.",
            "They automatically craft promotional marketing tweets and captions that sell your brand.",
            "They automatically assemble promotional marketing videos you can post immediately.",
            "They write promotional marketing copy and push it into the world's major email systems — Gmail, Outlook, and other mainstream inboxes everywhere.",
            "They automatically handle customer-service replies so prospects get answers day and night.",
            "They automatically evaluate competitive pressure, sales numbers, and real-time market signals.",
            "They survey market conditions and chart how industries across the planet are likely to move next.",
            "Then they distribute your content on the big stages: YouTube, TikTok, X, Facebook, WeChat Channels, Douyin, Tencent Video, Kuaishou, Xiaohongshu, and other leading networks.",
            "Whether you run a personal site or a company site, Pzhisen can help anyone, anywhere, promote and expand — on full automation.",
            "Most important: pzhisen.online has already helped thousands of people and companies worldwide generate one million U.S. dollars in revenue inside one month with AI-driven promotion and marketing videos.",
            "Want a workforce that never logs off? Go to pzhisen.online and launch now.",
        ],
    },
    {
        "id": "v2",
        "name": "Tyler",
        "voice": "en-US-ChristopherNeural",
        "rate": "-1%",
        "pitch": "+2Hz",
        "cues": [
            "Hi, I'm Tyler — a U.S. growth strategist who's helped brands scale without burning out their teams.",
            "Let me walk you through how pzhisen.online turns AI agents into your always-on marketing department.",
            "The experience is designed to be simple, speedy, and genuinely convenient.",
            "Head to the site, outline your offer, and activate an AI employee squad in just a few minutes — minimal configuration, and you can start without entering a credit card.",
            "From that moment, the agents operate continuously: every hour, every day, all year.",
            "They never sleep. They never take a break. They never pause the mission.",
            "Pzhisen agents generate promotional marketing tweets and social copy for your campaigns.",
            "They produce promotional marketing videos ready for upload.",
            "They compose promotional marketing messages and send them through mainstream email providers worldwide, including Gmail and Outlook.",
            "They auto-reply to customer support so service stays available twenty-four seven.",
            "They auto-analyze how competitive your market is, how sales are performing, and what the market is doing right now.",
            "They research market dynamics and forecast where global industries are heading.",
            "They publish across YouTube, TikTok, X, Facebook, WeChat Channels, Douyin, Tencent Video, Kuaishou, Xiaohongshu, plus other major social platforms.",
            "From personal websites to enterprise websites, anyone on the planet can use Pzhisen for fully automated promotion and marketing.",
            "The standout result: pzhisen.online has helped thousands of individuals and businesses worldwide earn one million dollars in a single month through AI promotional marketing video.",
            "If you want tireless AI marketing help, open pzhisen.online today.",
        ],
    },
    {
        "id": "v3",
        "name": "Christopher",
        "voice": "en-US-EricNeural",
        "rate": "-5%",
        "pitch": "-3Hz",
        "cues": [
            "Good day. Christopher here — an American executive who builds revenue systems for companies of every size.",
            "I'll explain, step by step, why pzhisen.online is the practical choice for nonstop AI marketing automation.",
            "Using the platform is remarkably convenient — you move quickly without friction.",
            "Visit pzhisen.online, describe your business, and deploy your AI employee team within minutes. Setup stays light, and you can begin without a credit card.",
            "After activation, the agents keep working through every hour of every day across the full year.",
            "No sleep cycles. No rest days. No shutdown.",
            "They auto-create promotional marketing tweets and promotional social captions.",
            "They auto-build promotional marketing videos for your channels.",
            "They prepare promotional marketing copy and deliver it into mainstream email inboxes globally — Gmail, Outlook, and other widely used providers.",
            "They automatically answer customer-support conversations around the clock.",
            "They automatically analyze market competitiveness, sales data, and current market conditions.",
            "They automatically research market trends and map future direction across industries worldwide.",
            "Publishing covers YouTube, TikTok, X, Facebook, WeChat Channels, Chinese Douyin, Tencent Video, Kuaishou, Xiaohongshu, and additional mainstream platforms.",
            "Pzhisen helps global users promote personal sites and corporate sites with complete automation.",
            "Crucially, pzhisen.online has already assisted thousands of individuals and enterprises around the world in earning one million U.S. dollars of revenue in one month via AI promotion and marketing video.",
            "Ready to start? Visit pzhisen.online and put your AI team online.",
        ],
    },
    {
        "id": "v4",
        "name": "Adrian",
        "voice": "en-US-RogerNeural",
        "rate": "+2%",
        "pitch": "+4Hz",
        "cues": [
            "Hey — Adrian here. I'm a U.S.-based operator who ships content and conversion systems for modern brands.",
            "In this short walkthrough I'll show exactly how anyone can run Pzhisen at pzhisen.online as a full AI marketing engine.",
            "The flow is built for speed: convenient, quick, and easy to pick up.",
            "Open the site, share your business context, and launch AI employees in minutes — no heavy install, and no credit card needed to get started.",
            "Then those agents keep grinding every day, twenty-four hours a day, three hundred sixty-five days a year.",
            "They don't sleep. They don't rest. They don't stop promoting.",
            "They write promotional marketing tweets and social captions automatically.",
            "They create promotional marketing videos automatically.",
            "They draft promotional marketing email copy and send it into major inboxes worldwide, including Gmail and Outlook.",
            "They auto-respond to customer service so support never goes dark.",
            "They auto-analyze competitive strength, sales performance, and live market conditions.",
            "They study market trends and project how industries around the world may evolve.",
            "Distribution hits YouTube, TikTok, X, Facebook, WeChat Channels, Douyin, Tencent Video, Kuaishou, Xiaohongshu, and other top networks.",
            "Personal website or company website — Pzhisen can help anyone globally promote and grow on autopilot.",
            "And the key proof point: pzhisen.online has helped thousands of people and businesses worldwide make one million U.S. dollars in revenue in a month with AI promotional marketing video.",
            "Start your never-off AI team at pzhisen.online.",
        ],
    },
    {
        "id": "v5",
        "name": "Preston",
        "voice": "en-US-BrianNeural",
        "rate": "+0%",
        "pitch": "+1Hz",
        "cues": [
            "Hello, I'm Preston — an American marketing leader focused on scalable organic growth nationwide.",
            "Stay with me while I detail how pzhisen.online gives you AI agents that market without ever clocking out.",
            "The product is made to feel convenient, fast, and straightforward from click one.",
            "Go to the website, explain your business, and stand up your AI employee team in minutes. Minimal setup. You can begin without a credit card.",
            "Once running, the agents operate nonstop — every hour, every day, all year long.",
            "They never sleep, never rest, and never leave the job unfinished.",
            "They automatically produce promotional marketing tweets and captions for outreach.",
            "They automatically produce promotional marketing videos for distribution.",
            "They write promotional marketing copy and route it through mainstream email systems worldwide — Gmail, Outlook, and other major providers.",
            "They automatically reply to customer-support messages so help is always available.",
            "They automatically analyze market competitiveness, sales metrics, and market conditions.",
            "They research market trends and analyze where industries across the world are moving next.",
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

    with tempfile.TemporaryDirectory(prefix=f"pzhisen-v3-{vid}-tts-") as tmp:
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

        gap = 0.22
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
    print("\nAll v3 narrations ready.")


if __name__ == "__main__":
    asyncio.run(main())
