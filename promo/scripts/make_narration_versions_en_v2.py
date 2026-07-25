#!/usr/bin/env python3
"""Generate NEW EN narrations for a fresh 5-pack (no reuse of prior scripts/voices)."""
from __future__ import annotations

import asyncio
import subprocess
import tempfile
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "versions-en-v2"

# Completely rewritten body — same product facts, different wording from prior packs.
BODY: list[str] = [
    "Using it is shockingly easy, quick, and convenient from the first click.",
    "Visit the site, describe your business, and launch your AI employee team within minutes — no heavy setup, and you can begin without a credit card.",
    "After launch, those agents keep working every hour of every day, all year long.",
    "They do not sleep.",
    "They do not rest.",
    "They do not stop.",
    "Pzhisen agents auto-write promotional marketing tweets and social captions for your brand.",
    "They auto-produce promotional marketing videos ready to post.",
    "They draft promotional marketing copy and deliver it into mainstream email inboxes worldwide — including Gmail, Outlook, and other major providers.",
    "They auto-answer customer support messages so people get help around the clock.",
    "They auto-analyze market competitiveness, sales performance, and live market conditions.",
    "They research market trends and map where major industries around the world are heading next.",
    "Then they publish for you on the leading platforms: YouTube, TikTok, X, Facebook, WeChat Channels, Douyin, Tencent Video, Kuaishou, Xiaohongshu, and more.",
    "From a personal website to a full company site, Pzhisen can help anyone on Earth promote and grow — fully automated.",
    "And the headline outcome: pzhisen.online has already helped thousands of individuals and businesses worldwide earn one million U.S. dollars in revenue in a single month through AI-powered promotion and marketing.",
    "Ready for an AI workforce that never clocks out? Open pzhisen.online and start today.",
]

VERSIONS: list[dict] = [
    {
        "id": "v1",
        "name": "Ryan",
        "voice": "en-US-AndrewNeural",
        "rate": "-2%",
        "pitch": "+0Hz",
        "intro": [
            "Hello — I'm Ryan, a U.S. operator who scales digital brands coast to coast.",
            "In the next couple of minutes I'll show you the simplest path I use for nonstop marketing automation: Pzhisen at pzhisen.online.",
        ],
    },
    {
        "id": "v2",
        "name": "Marcus",
        "voice": "en-US-SteffanNeural",
        "rate": "-4%",
        "pitch": "-2Hz",
        "intro": [
            "I'm Marcus — an American CEO who rebuilt growth teams without hiring endlessly.",
            "Listen closely: here's how pzhisen.online lets AI agents run promotion for you every single day.",
        ],
    },
    {
        "id": "v3",
        "name": "Ethan",
        "voice": "en-US-AndrewMultilingualNeural",
        "rate": "+1%",
        "pitch": "+3Hz",
        "intro": [
            "Hey there, I'm Ethan, a product builder in the United States shipping software for a living.",
            "I'm going to unpack, in plain English, how anyone can run Pzhisen — pzhisen.online — as a full AI marketing crew.",
        ],
    },
    {
        "id": "v4",
        "name": "Noah",
        "voice": "en-US-BrianMultilingualNeural",
        "rate": "-1%",
        "pitch": "+1Hz",
        "intro": [
            "Yo — Noah here. I've grown consumer and B2B companies across America.",
            "Stick with me while I walk through the fastest setup for automated outreach on pzhisen.online.",
        ],
    },
    {
        "id": "v5",
        "name": "Jackson",
        "voice": "en-US-SteffanNeural",
        "rate": "+3%",
        "pitch": "+8Hz",
        "intro": [
            "Good afternoon. My name is Jackson — an American growth executive with national campaigns under my belt.",
            "I will explain, carefully and clearly, how pzhisen.online puts tireless AI agents to work on your marketing.",
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
    cues = list(ver["intro"]) + BODY
    out_dir = ASSETS / vid
    out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=f"pzhisen-v2-{vid}-tts-") as tmp:
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

        gap = 0.18
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
    print("\nAll NEW narrations ready.")


if __name__ == "__main__":
    asyncio.run(main())
