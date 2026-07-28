#!/usr/bin/env python3
"""Build NEW 5 vertical EN promo MP4s — pack v10 (results + urgency 3-act).

Unique presenters/scripts/voices/UI vs all prior packs. Scene timing maps to:
  Act1 money (0–~15%), Act2 ops (~15–70%), Act3 urgency (~70–100%).
"""
from __future__ import annotations

import math
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "versions-en-v10"
OUT_DIR = ROOT / "versions-en-v10"
VW, VH = 1080, 1920
FPS = 24

VERSION_META = [
    {
        "id": "v1",
        "name": "Knox",
        "title": "Knox · Midnight Ledger",
        "beats": [
            ("title", 0.00, 0.05),
            ("revenue", 0.05, 0.18),
            ("site", 0.18, 0.28),
            ("setup", 0.28, 0.42),
            ("agents", 0.42, 0.55),
            ("ops", 0.55, 0.68),
            ("urgency", 0.68, 0.90),
            ("success", 0.90, 1.00),
        ],
        "subtitle_fs": 36,
        "subtitle_margin_v": 150,
        "subtitle_primary": "&H00D1FAE5",
        "drift_cycle": ["center", "up", "right", "center", "left", "up", "center", "right"],
        "zoom_alt": True,
        "zoom_speed": 0.00128,
    },
    {
        "id": "v2",
        "name": "Weston",
        "title": "Weston · Warm Storefront",
        "beats": [
            ("revenue", 0.00, 0.14),
            ("title", 0.14, 0.20),
            ("setup", 0.20, 0.34),
            ("site", 0.34, 0.44),
            ("ops", 0.44, 0.56),
            ("agents", 0.56, 0.68),
            ("urgency", 0.68, 0.88),
            ("success", 0.88, 1.00),
        ],
        "subtitle_fs": 35,
        "subtitle_margin_v": 168,
        "subtitle_primary": "&H00FFF7ED",
        "drift_cycle": ["up", "left", "center", "right", "up", "center", "left", "up"],
        "zoom_alt": False,
        "zoom_speed": 0.00098,
    },
    {
        "id": "v3",
        "name": "Callum",
        "title": "Callum · Ice Glass Console",
        "beats": [
            ("site", 0.00, 0.08),
            ("revenue", 0.08, 0.20),
            ("setup", 0.20, 0.33),
            ("agents", 0.33, 0.46),
            ("ops", 0.46, 0.58),
            ("title", 0.58, 0.66),
            ("urgency", 0.66, 0.88),
            ("success", 0.88, 1.00),
        ],
        "subtitle_fs": 37,
        "subtitle_margin_v": 140,
        "subtitle_primary": "&H00E0F2FE",
        "drift_cycle": ["left", "center", "up", "right", "center", "up", "left", "center"],
        "zoom_alt": True,
        "zoom_speed": 0.00115,
    },
    {
        "id": "v4",
        "name": "Dorian",
        "title": "Dorian · Graphite Signal",
        "beats": [
            ("title", 0.00, 0.06),
            ("revenue", 0.06, 0.18),
            ("ops", 0.18, 0.30),
            ("setup", 0.30, 0.42),
            ("site", 0.42, 0.52),
            ("agents", 0.52, 0.66),
            ("urgency", 0.66, 0.90),
            ("success", 0.90, 1.00),
        ],
        "subtitle_fs": 34,
        "subtitle_margin_v": 132,
        "subtitle_primary": "&H00ECFCCB",
        "drift_cycle": ["right", "up", "center", "left", "up", "right", "center", "up"],
        "zoom_alt": False,
        "zoom_speed": 0.00135,
    },
    {
        "id": "v5",
        "name": "Everett",
        "title": "Everett · Editorial Alert",
        "beats": [
            ("revenue", 0.00, 0.16),
            ("site", 0.16, 0.26),
            ("setup", 0.26, 0.40),
            ("agents", 0.40, 0.52),
            ("ops", 0.52, 0.64),
            ("urgency", 0.64, 0.86),
            ("title", 0.86, 0.92),
            ("success", 0.92, 1.00),
        ],
        "subtitle_fs": 38,
        "subtitle_margin_v": 175,
        "subtitle_primary": "&H00FEE2E2",
        "drift_cycle": ["center", "right", "up", "left", "center", "up", "right", "center"],
        "zoom_alt": True,
        "zoom_speed": 0.00108,
    },
]

BROLL_NAMES = {
    "site.png",
    "revenue.png",
    "setup.png",
    "agents.png",
    "ops.png",
    "urgency.png",
    "title.png",
    "success.png",
}


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


def scene_plan(duration: float, ver_dir: Path, meta: dict) -> list[tuple[float, float, Path, str]]:
    scenes: list[tuple[float, float, Path, str]] = []
    for name, a, b in meta["beats"]:
        img = ver_dir / f"{name}.png"
        scenes.append((a * duration, b * duration, img, name))
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
    zoom_speed: float,
) -> None:
    frames = max(1, int(math.ceil(duration * FPS)))
    if zoom_in:
        z_expr = f"min(zoom+{zoom_speed:.5f},1.18)"
    else:
        z_expr = f"if(eq(on,1),1.18,max(zoom-{zoom_speed:.5f},1.0))"

    if drift == "left":
        x_expr = "iw/2-(iw/zoom/2)-on*0.18"
        y_expr = "ih/2-(ih/zoom/2)"
    elif drift == "up":
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)-on*0.14"
    elif drift == "right":
        x_expr = "iw/2-(iw/zoom/2)+on*0.16"
        y_expr = "ih/2-(ih/zoom/2)"
    else:
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"

    if is_broll:
        vf = (
            f"scale={VW}:{VH}:force_original_aspect_ratio=decrease,"
            f"pad={VW}:{VH}:(ow-iw)/2:(oh-ih)/2:color=0x0a0a0a,"
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


def wrap_caption(text: str, max_chars: int = 34) -> str:
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
        lines = pack(42)
    if len(lines) > 4:
        lines = pack(50)
    return "\\N".join(lines)


def srt_to_vertical_ass(srt: Path, ass: Path, meta: dict) -> None:
    cues = parse_srt_cues(srt)

    def ass_ts(seconds: float) -> str:
        if seconds < 0:
            seconds = 0.0
        cs = int(round(seconds * 100))
        h, cs = divmod(cs, 360000)
        m, cs = divmod(cs, 6000)
        s, cs = divmod(cs, 100)
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    fs = meta["subtitle_fs"]
    mv = meta["subtitle_margin_v"]
    primary = meta["subtitle_primary"]
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {VW}
PlayResY: {VH}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,{fs},{primary},&H000000FF,&H88000000,&H64000000,-1,0,0,0,100,100,0,0,3,2.2,0,2,48,48,{mv},1

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


def burn_subtitles(video: Path, srt: Path, audio: Path, outfile: Path, meta: dict) -> None:
    ass = srt.with_suffix(".ass")
    srt_to_vertical_ass(srt, ass, meta)
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
    outfile = OUT_DIR / f"pzhisen-promo-en10-{vid}-vertical.mp4"

    scenes = scene_plan(duration, ver_dir, meta)
    print(f"\n=== Building v10 {vid} ({meta['name']}) {duration:.1f}s vertical ===")

    drifts = meta["drift_cycle"]
    zoom_alt = meta["zoom_alt"]
    zoom_speed = meta["zoom_speed"]

    with tempfile.TemporaryDirectory(prefix=f"pzhisen-en10-{vid}-") as tmp:
        tmp_path = Path(tmp)
        clips: list[Path] = []
        for i, (a, b, img, label) in enumerate(scenes):
            dur = max(0.35, b - a)
            if not img.exists():
                raise FileNotFoundError(img)
            clip = tmp_path / f"clip_{i:02d}.mp4"
            is_broll = img.name in BROLL_NAMES
            print(f"  scene {i+1:02d}/{len(scenes)} {dur:5.2f}s  {img.name}  ({label})")
            render_scene_clip(
                img,
                dur,
                clip,
                zoom_in=(i % 2 == 0) if zoom_alt else (i % 2 == 1),
                is_broll=is_broll,
                drift=drifts[i % len(drifts)],
                zoom_speed=zoom_speed,
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
        burn_subtitles(silent, srt, audio, outfile, meta)

    size_mb = outfile.stat().st_size / (1024 * 1024)
    print(f"  Done: {outfile} ({size_mb:.1f} MB)")
    return outfile


def zip_all(paths: list[Path]) -> Path:
    zpath = OUT_DIR / "pzhisen-promo-en10-5videos-vertical.zip"
    with zipfile.ZipFile(zpath, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            zf.write(p, arcname=p.name)
    print(f"ZIP: {zpath} ({zpath.stat().st_size / (1024*1024):.1f} MB)")
    return zpath


def main() -> None:
    import sys

    only = sys.argv[1] if len(sys.argv) > 1 else "all"
    built: list[Path] = []
    for meta in VERSION_META:
        if only != "all" and only != meta["id"]:
            continue
        built.append(build_one(meta))
    if only == "all" and len(built) == 5:
        zip_all(built)
    print("\nAll v10 unique vertical videos built.")


if __name__ == "__main__":
    main()
