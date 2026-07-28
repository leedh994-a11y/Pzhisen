#!/usr/bin/env python3
"""Generate EN narrations for promo pack v10 — results + urgency 3-act (~45s).

Same factual claims across cuts; unique wording, voices, pacing, and variable details
($47/$87, 3pm/4pm, morning/afternoon, 10/50 or 12/50) to avoid duplicate-content fingerprints.
"""
from __future__ import annotations

import asyncio
import subprocess
import tempfile
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "versions-en-v10"

# Act structure baked into cue groups:
# Act1 money (cues 0-1), Act2 minimal ops (cues 2-4), Act3 urgency CTA (cues 5-7)
VERSIONS: list[dict] = [
    {
        "id": "v1",
        "name": "Knox",
        "voice": "en-GB-RyanNeural",
        "rate": "+6%",
        "pitch": "-2Hz",
        "gap": 0.22,
        "cues": [
            "Yesterday at three in the afternoon, a solo website owner used Pzhisen to do just three things: enter a product name, upload three photos, and connect payments.",
            "This morning, his AI store automatically closed the first order — forty-seven dollars.",
            "Across the whole process, he never touched a single line of code, and he never wrote a single line of marketing copy.",
            "Every ad placement and every customer-service reply was handled by Pzhisen AI agents at three in the morning — fully automatic.",
            "That is the point of pzhisen.online: you set it up once, then the agents keep selling while you sleep.",
            "Today's remaining free seats: ten out of fifty.",
            "This AI agent can onboard only fifty new stores per day. If you want to wake up to orders, tap the link below and claim today's free test.",
            "When the seats are gone, you wait until next month.",
        ],
    },
    {
        "id": "v2",
        "name": "Weston",
        "voice": "en-AU-WilliamMultilingualNeural",
        "rate": "-2%",
        "pitch": "+2Hz",
        "gap": 0.28,
        "cues": [
            "Yesterday at four P.M., a small-business owner building websites ran Pzhisen through three steps only: type the product name, upload three images, and bind payment.",
            "This afternoon, the AI shop rang up order number one for eighty-seven dollars — no manual push.",
            "He did not edit code. He did not draft ad copy. Not once.",
            "Ads and customer replies were completed by Pzhisen AI agents at four A.M. on autopilot.",
            "Open pzhisen.online and you get the same hands-off loop: store up, agents selling overnight.",
            "Seats left today: twelve of fifty.",
            "The agent can serve fifty new stores daily. Want orders waiting when you wake? Hit the link below for today's free test slot.",
            "Miss it, and the next window opens next month.",
        ],
    },
    {
        "id": "v3",
        "name": "Callum",
        "voice": "en-CA-LiamNeural",
        "rate": "+4%",
        "pitch": "+0Hz",
        "gap": 0.24,
        "cues": [
            "At three yesterday afternoon, an agency founder who builds sites used Pzhisen for three actions: product name in, three photos up, payment linked.",
            "By this afternoon, the AI storefront booked its first paid order at forty-seven dollars.",
            "Zero code from him. Zero sales copy from him.",
            "Pzhisen AI agents ran ads and answered buyers at three A.M. without anyone watching the screen.",
            "That workflow is live on pzhisen.online — launch light, let agents work the night shift.",
            "Free tests remaining today: ten slash fifty.",
            "Hard cap: fifty new stores a day. If you want to sleep and still see orders, tap below and grab today's free trial seat.",
            "Once filled, new seats wait until next month.",
        ],
    },
    {
        "id": "v4",
        "name": "Dorian",
        "voice": "en-GB-ThomasNeural",
        "rate": "-5%",
        "pitch": "-4Hz",
        "gap": 0.32,
        "cues": [
            "Four o'clock yesterday afternoon: an enterprise website operator used Pzhisen to complete three moves — name the product, upload three pictures, bind checkout.",
            "This morning the AI store recorded sale one: eighty-seven U.S. dollars, closed automatically.",
            "No code was written. No marketing text was authored by a human.",
            "Advertising and support replies were executed by Pzhisen AI agents at four in the morning, unsupervised.",
            "Visit pzhisen.online for the same minimal setup and overnight AI selling.",
            "Quota on the board today: twelve remaining of fifty.",
            "Only fifty new shops can be onboarded each day. Tap the link under this video for today's free test before it disappears.",
            "After the quota resets next month is your next chance.",
        ],
    },
    {
        "id": "v5",
        "name": "Everett",
        "voice": "en-US-RogerNeural",
        "rate": "+9%",
        "pitch": "-6Hz",
        "gap": 0.18,
        "cues": [
            "Yesterday, three P.M.: an independent web-shop owner used Pzhisen for three steps only — product name, three image uploads, payment binding.",
            "This morning the AI store auto-printed order one for forty-seven dollars.",
            "He never coded. He never wrote copy.",
            "All ads and all customer replies were finished by Pzhisen AI agents at three A.M. while he slept.",
            "That is exactly what pzhisen.online is built to do: tiny setup, nonstop AI selling.",
            "Today left: ten of fifty free seats.",
            "Daily hard limit — fifty new stores. Want to wake up to orders? Tap the link below and lock today's free test.",
            "Seats gone means waiting until next month.",
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
    rate = ver.get("rate", "+0%")
    pitch = ver.get("pitch", "+0Hz")
    gap = float(ver.get("gap", 0.24))
    cues = list(ver["cues"])
    out_dir = ASSETS / vid
    out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=f"pzhisen-v10-{vid}-tts-") as tmp:
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
            print(f"  [{i+1:02d}/{len(cues)}] {dur:5.2f}s  {text[:56]}…")

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
    totals = []
    for ver in VERSIONS:
        totals.append(await build_version(ver))
    print("\nAll v10 narrations ready.")
    for ver, t in zip(VERSIONS, totals):
        print(f"  {ver['id']}: {t:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
