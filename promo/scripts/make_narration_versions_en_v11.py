#!/usr/bin/env python3
"""Generate EN narrations for promo pack v11 — 25 cuts (V1–V5 × orders 2–6)."""
from __future__ import annotations

import asyncio
import subprocess
import sys
import tempfile
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "versions-en-v11"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from v11_matrix import all_cuts  # noqa: E402


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


async def build_cut(cut: dict) -> float:
    cid = cut["id"]
    out_dir = ASSETS / cid
    out_dir.mkdir(parents=True, exist_ok=True)
    cues = list(cut["cues"])
    gap = float(cut["gap"])

    with tempfile.TemporaryDirectory(prefix=f"pzhisen-v11-{cid}-tts-") as tmp:
        tmp_path = Path(tmp)
        parts: list[Path] = []
        durations: list[float] = []
        print(f"\n=== {cid} / {cut['name']} / {cut['voice']} {cut['rate']} {cut['pitch']} ===")
        for i, text in enumerate(cues):
            part = tmp_path / f"cue_{i:02d}.mp3"
            await synth_cue(text, cut["voice"], part, rate=cut["rate"], pitch=cut["pitch"])
            dur = probe_duration(part)
            parts.append(part)
            durations.append(dur)
            print(f"  [{i+1:02d}/{len(cues)}] {dur:5.2f}s  {text[:52]}…")

        list_file = tmp_path / "concat.txt"
        lines: list[str] = []
        for i, p in enumerate(parts):
            lines.append(f"file '{p}'")
            if i < len(parts) - 1:
                silence = tmp_path / f"gap_{i:02d}.mp3"
                subprocess.run(
                    [
                        "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                        "-t", str(gap), "-q:a", "9", "-acodec", "libmp3lame", str(silence),
                    ],
                    check=True,
                    capture_output=True,
                )
                lines.append(f"file '{silence}'")
        list_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

        mp3 = out_dir / "narration.mp3"
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
                "-c:a", "libmp3lame", "-q:a", "4", str(mp3),
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
            start, end = t, t + dur
            vtt_lines += [f"{fmt_ts(start)} --> {fmt_ts(end)}", text, ""]
            srt_blocks.append(f"{i+1}\n{fmt_ts(start, srt=True)} --> {fmt_ts(end, srt=True)}\n{text}\n")
            t = end + gap
        (out_dir / "narration.vtt").write_text("\n".join(vtt_lines) + "\n", encoding="utf-8")
        (out_dir / "narration.srt").write_text("\n".join(srt_blocks) + "\n", encoding="utf-8")
        (out_dir / "script.txt").write_text("\n\n".join(cues) + "\n", encoding="utf-8")
        print(f"  Wrote narration.mp3 ({total:.2f}s)")
        return total


async def main() -> None:
    only = sys.argv[1] if len(sys.argv) > 1 else "all"
    ASSETS.mkdir(parents=True, exist_ok=True)
    for cut in all_cuts():
        if only != "all" and only != cut["id"] and only != cut["vid"]:
            continue
        await build_cut(cut)
    print("\nAll v11 narrations ready.")


if __name__ == "__main__":
    asyncio.run(main())
