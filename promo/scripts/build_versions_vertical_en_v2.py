#!/usr/bin/env python3
"""Build NEW 5 vertical EN promo MP4s (unique presenters/scripts; not prior pack)."""
from __future__ import annotations

import math
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "versions-en-v2"
OUT_DIR = ROOT / "versions-en-v2"
SHARED = ASSETS
VW, VH = 1080, 1920
FPS = 24

VERSION_META = [
    {"id": "v1", "name": "Ryan", "title": "Meet Ryan"},
    {"id": "v2", "name": "Marcus", "title": "Meet Marcus"},
    {"id": "v3", "name": "Ethan", "title": "Meet Ethan"},
    {"id": "v4", "name": "Noah", "title": "Meet Noah"},
    {"id": "v5", "name": "Jackson", "title": "Meet Jackson"},
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


def parse_srt_cues(srt: Path) -> list[tuple[float, float, str]]:
    text = srt.read_text(encoding="utf-8")
    blocks = re.split(r"\n\s*\n", text.strip())
    cues: list[tuple[float, float, str]] = []

    def parse_ts(t: str) -> float:
        t = t.strip().replace(",", ".")
        h, m, rest = t.split(":")
        s = float(rest)
        return int(h) * 3600 + int(m) * 60 + s

    for block in blocks:
        lines = [ln for ln in block.splitlines() if ln.strip()]
        if not lines:
            continue
        if re.fullmatch(r"\d+", lines[0].strip()):
            lines = lines[1:]
        if not lines or "-->" not in lines[0]:
            continue
        a, b = [p.strip() for p in lines[0].split("-->")]
        body = " ".join(lines[1:]).strip()
        cues.append((parse_ts(a), parse_ts(b.split()[0]), body))
    return cues


def scene_plan(duration: float, ver_dir: Path) -> list[tuple[float, float, Path, str]]:
    """Face-led cut with a different beat order than the previous pack."""
    front = ver_dir / "front.png"
    gesture = ver_dir / "gesture.png"
    desk = ver_dir / "desk.png"
    success = ver_dir / "success.png"
    title = SHARED / "title-bg.png"
    site = SHARED / "site-index.png"
    dash = SHARED / "ui-dashboard.png"
    publish = SHARED / "ui-publish.png"
    analytics = SHARED / "ui-analytics.png"
    platforms = SHARED / "platforms-bg.png"

    # Distinct pacing vs prior pack
    beats = [
        (0.00, 0.04, front, "Open · presenter"),
        (0.04, 0.12, title, "Pzhisen"),
        (0.12, 0.22, gesture, "Easy launch"),
        (0.22, 0.30, site, "pzhisen.online"),
        (0.30, 0.42, desk, "Always-on agents"),
        (0.42, 0.50, dash, "AI employee team"),
        (0.50, 0.58, publish, "Email worldwide"),
        (0.58, 0.68, gesture, "Support · analysis"),
        (0.68, 0.76, analytics, "Markets · sales · trends"),
        (0.76, 0.86, platforms, "Global platforms"),
        (0.86, 0.94, success, "$1,000,000 / month"),
        (0.94, 1.00, front, "Start today"),
    ]
    scenes: list[tuple[float, float, Path, str]] = []
    for a, b, img, label in beats:
        scenes.append((a * duration, b * duration, img, label))
    last = scenes[-1]
    scenes[-1] = (last[0], duration, last[2], last[3])
    return scenes


def render_scene_clip(
    img: Path,
    duration: float,
    out_clip: Path,
    *,
    zoom_in: bool,
    is_broll: bool,
) -> None:
    frames = max(1, int(math.ceil(duration * FPS)))
    if zoom_in:
        z_expr = "min(zoom+0.0009,1.14)"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"
    else:
        z_expr = "if(eq(on,1),1.14,max(zoom-0.0009,1.0))"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"

    if is_broll:
        vf = (
            f"scale={VW}:{VH}:force_original_aspect_ratio=decrease,"
            f"pad={VW}:{VH}:(ow-iw)/2:(oh-ih)/2:color=0x07101f,"
            f"zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}':d={frames}:s={VW}x{VH}:fps={FPS},"
            f"format=yuv420p"
        )
    else:
        vf = (
            f"scale={VW}:{VH}:force_original_aspect_ratio=increase,"
            f"crop={VW}:{VH},"
            f"zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}':d={frames}:s={VW}x{VH}:fps={FPS},"
            f"format=yuv420p"
        )

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(img),
            "-vf",
            vf,
            "-t",
            f"{duration:.3f}",
            "-r",
            str(FPS),
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            str(out_clip),
        ],
        check=True,
        capture_output=True,
    )


def wrap_caption(text: str, max_chars: int = 40) -> str:
    words = text.split()

    def pack(limit: int) -> list[str]:
        lines: list[str] = []
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            if len(test) <= limit:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    lines = pack(max_chars)
    if len(lines) > 3:
        lines = pack(48)
    if len(lines) > 4:
        lines = pack(56)
    return "\\N".join(lines)


def srt_to_vertical_ass(srt: Path, ass: Path) -> None:
    cues = parse_srt_cues(srt)

    def ass_ts(seconds: float) -> str:
        if seconds < 0:
            seconds = 0.0
        cs = int(round(seconds * 100))
        h, cs = divmod(cs, 360000)
        m, cs = divmod(cs, 6000)
        s, cs = divmod(cs, 100)
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {VW}
PlayResY: {VH}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,34,&H00FFFFFF,&H000000FF,&H82000000,&H70000000,0,0,0,0,100,100,0,0,3,2,0,2,48,48,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events: list[str] = []
    for start, end, body in cues:
        text = wrap_caption(body)
        text = text.replace("{", "\\{").replace("}", "\\}")
        events.append(
            f"Dialogue: 0,{ass_ts(start)},{ass_ts(end)},Default,,0,0,0,,{text}"
        )
    ass.write_text(header + "\n".join(events) + "\n", encoding="utf-8")


def burn_subtitles(video: Path, srt: Path, audio: Path, outfile: Path) -> None:
    ass = srt.with_suffix(".ass")
    srt_to_vertical_ass(srt, ass)
    ass_esc = str(ass.resolve()).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-i",
            str(audio),
            "-vf",
            f"ass={ass_esc}",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            "-movflags",
            "+faststart",
            str(outfile),
        ],
        check=True,
    )


def build_one(meta: dict) -> Path:
    vid = meta["id"]
    ver_dir = ASSETS / vid
    audio = ver_dir / "narration.mp3"
    srt = ver_dir / "narration.srt"
    if not audio.exists() or not srt.exists():
        raise FileNotFoundError(f"Missing narration for {vid}")

    duration = probe_duration(audio)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Distinct filenames from the old pack
    outfile = OUT_DIR / f"pzhisen-promo-en2-{vid}-vertical.mp4"

    scenes = scene_plan(duration, ver_dir)
    print(f"\n=== Building NEW {vid} ({meta['name']}) {duration:.1f}s vertical ===")

    with tempfile.TemporaryDirectory(prefix=f"pzhisen-en2-{vid}-") as tmp:
        tmp_path = Path(tmp)
        clips: list[Path] = []
        for i, (a, b, img, label) in enumerate(scenes):
            dur = max(0.35, b - a)
            if not img.exists():
                raise FileNotFoundError(img)
            clip = tmp_path / f"clip_{i:02d}.mp4"
            is_broll = img.name.startswith("ui-") or img.name in {
                "site-index.png",
                "platforms-bg.png",
                "title-bg.png",
            }
            print(f"  scene {i+1:02d}/{len(scenes)} {dur:5.2f}s  {img.name}  ({label})")
            render_scene_clip(img, dur, clip, zoom_in=(i % 2 == 0), is_broll=is_broll)
            clips.append(clip)

        concat_list = tmp_path / "concat.txt"
        concat_list.write_text(
            "\n".join(f"file '{c}'" for c in clips) + "\n", encoding="utf-8"
        )
        silent = tmp_path / "silent.mp4"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_list),
                "-c",
                "copy",
                str(silent),
            ],
            check=True,
            capture_output=True,
        )
        print(f"  Burning English subtitles → {outfile.name}")
        burn_subtitles(silent, srt, audio, outfile)

    size_mb = outfile.stat().st_size / (1024 * 1024)
    print(f"  Done: {outfile} ({size_mb:.1f} MB)")
    return outfile


def main() -> None:
    import sys

    only = sys.argv[1] if len(sys.argv) > 1 else "all"
    for meta in VERSION_META:
        if only != "all" and only != meta["id"]:
            continue
        build_one(meta)
    print("\nAll NEW unique vertical videos built.")


if __name__ == "__main__":
    main()
