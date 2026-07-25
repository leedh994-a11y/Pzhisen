#!/usr/bin/env python3
"""Build NEW 5 vertical EN promo MP4s — pack v3 (unique presenters/scripts vs prior packs)."""
from __future__ import annotations

import math
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "versions-en-v3"
OUT_DIR = ROOT / "versions-en-v3"
SHARED = ASSETS
VW, VH = 1080, 1920
FPS = 24

VERSION_META = [
    {"id": "v1", "name": "Brandon", "title": "Meet Brandon"},
    {"id": "v2", "name": "Tyler", "title": "Meet Tyler"},
    {"id": "v3", "name": "Christopher", "title": "Meet Christopher"},
    {"id": "v4", "name": "Adrian", "title": "Meet Adrian"},
    {"id": "v5", "name": "Preston", "title": "Meet Preston"},
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
    """Distinct beat order / pacing from prior packs to reduce near-duplicate fingerprints."""
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

    # Different cut rhythm vs en-v2
    beats = [
        (0.00, 0.06, front, "Hook · presenter"),
        (0.06, 0.14, gesture, "Easy · convenient"),
        (0.14, 0.22, title, "Pzhisen brand"),
        (0.22, 0.30, site, "pzhisen.online"),
        (0.30, 0.40, desk, "24/7 agents"),
        (0.40, 0.48, dash, "AI workforce"),
        (0.48, 0.56, publish, "Tweets · video · email"),
        (0.56, 0.64, gesture, "Support replies"),
        (0.64, 0.74, analytics, "Market · sales · trends"),
        (0.74, 0.84, platforms, "Global social publish"),
        (0.84, 0.93, success, "$1M / month outcome"),
        (0.93, 1.00, front, "CTA start today"),
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
    drift: str,
) -> None:
    frames = max(1, int(math.ceil(duration * FPS)))
    if zoom_in:
        z_expr = "min(zoom+0.00105,1.16)"
    else:
        z_expr = "if(eq(on,1),1.16,max(zoom-0.00105,1.0))"

    if drift == "left":
        x_expr = "iw/2-(iw/zoom/2)-on*0.15"
        y_expr = "ih/2-(ih/zoom/2)"
    elif drift == "up":
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)-on*0.12"
    else:
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"

    if is_broll:
        vf = (
            f"scale={VW}:{VH}:force_original_aspect_ratio=decrease,"
            f"pad={VW}:{VH}:(ow-iw)/2:(oh-ih)/2:color=0x04121c,"
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


def wrap_caption(text: str, max_chars: int = 38) -> str:
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
        lines = pack(46)
    if len(lines) > 4:
        lines = pack(54)
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

    # Slightly different subtitle styling vs prior pack
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {VW}
PlayResY: {VH}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,36,&H00F8FAFC,&H000000FF,&H9008121C,&H78000000,-1,0,0,0,100,100,0,0,3,2.4,0,2,52,52,140,1

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
    outfile = OUT_DIR / f"pzhisen-promo-en3-{vid}-vertical.mp4"

    scenes = scene_plan(duration, ver_dir)
    print(f"\n=== Building v3 {vid} ({meta['name']}) {duration:.1f}s vertical ===")

    drifts = ["center", "left", "up", "center", "left", "up", "center", "left", "up", "center", "left", "center"]

    with tempfile.TemporaryDirectory(prefix=f"pzhisen-en3-{vid}-") as tmp:
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
            render_scene_clip(
                img,
                dur,
                clip,
                zoom_in=(i % 2 == 1),
                is_broll=is_broll,
                drift=drifts[i % len(drifts)],
            )
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
    print("\nAll v3 unique vertical videos built.")


if __name__ == "__main__":
    main()
