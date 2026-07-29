#!/usr/bin/env python3
"""Build 25 vertical EN promo MP4s — pack v11 (V1–V5 × orders 2–6)."""
from __future__ import annotations

import math
import re
import subprocess
import sys
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "versions-en-v11"
OUT_DIR = ROOT / "versions-en-v11"
VW, VH = 1080, 1920
FPS = 24

sys.path.insert(0, str(Path(__file__).resolve().parent))
from v11_matrix import all_cuts  # noqa: E402

BROLL_NAMES = {
    "site.png", "revenue.png", "setup.png", "agents.png",
    "ops.png", "urgency.png", "title.png", "success.png",
}


def probe_duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=nw=1:nk=1", str(path),
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
        return int(h) * 3600 + int(m) * 60 + float(rest)

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


def scene_plan(duration: float, ver_dir: Path, cut: dict) -> list[tuple[float, float, Path, str]]:
    scenes = []
    for name, a, b in cut["beats"]:
        scenes.append((a * duration, b * duration, ver_dir / f"{name}.png", name))
    last = scenes[-1]
    scenes[-1] = (last[0], duration, last[2], last[3])
    return scenes


def render_scene_clip(img, duration, out_clip, *, zoom_in, is_broll, drift, zoom_speed):
    frames = max(1, int(math.ceil(duration * FPS)))
    z_expr = f"min(zoom+{zoom_speed:.5f},1.18)" if zoom_in else f"if(eq(on,1),1.18,max(zoom-{zoom_speed:.5f},1.0))"
    if drift == "left":
        x_expr, y_expr = "iw/2-(iw/zoom/2)-on*0.18", "ih/2-(ih/zoom/2)"
    elif drift == "up":
        x_expr, y_expr = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)-on*0.14"
    elif drift == "right":
        x_expr, y_expr = "iw/2-(iw/zoom/2)+on*0.16", "ih/2-(ih/zoom/2)"
    else:
        x_expr, y_expr = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"

    if is_broll:
        vf = (
            f"scale={VW}:{VH}:force_original_aspect_ratio=decrease,"
            f"pad={VW}:{VH}:(ow-iw)/2:(oh-ih)/2:color=0x0a0a0a,"
            f"zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}':d={frames}:s={VW}x{VH}:fps={FPS},format=yuv420p"
        )
    else:
        vf = (
            f"scale={VW}:{VH}:force_original_aspect_ratio=increase,crop={VW}:{VH},"
            f"zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}':d={frames}:s={VW}x{VH}:fps={FPS},format=yuv420p"
        )
    subprocess.run(
        [
            "ffmpeg", "-y", "-loop", "1", "-i", str(img), "-vf", vf,
            "-t", f"{duration:.3f}", "-r", str(FPS), "-an",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
            "-pix_fmt", "yuv420p", str(out_clip),
        ],
        check=True,
        capture_output=True,
    )


def wrap_caption(text: str, max_chars: int = 34) -> str:
    words = text.split()

    def pack(limit: int) -> list[str]:
        lines, cur = [], ""
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


def srt_to_vertical_ass(srt: Path, ass: Path, cut: dict) -> None:
    cues = parse_srt_cues(srt)

    def ass_ts(seconds: float) -> str:
        cs = int(round(max(0.0, seconds) * 100))
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
Style: Default,DejaVu Sans,{cut['subtitle_fs']},{cut['subtitle_primary']},&H000000FF,&H88000000,&H64000000,-1,0,0,0,100,100,0,0,3,2.2,0,2,48,48,{cut['subtitle_margin_v']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for start, end, body in cues:
        text = wrap_caption(body).replace("{", "\\{").replace("}", "\\}")
        events.append(f"Dialogue: 0,{ass_ts(start)},{ass_ts(end)},Default,,0,0,0,,{text}")
    ass.write_text(header + "\n".join(events) + "\n", encoding="utf-8")


def burn_subtitles(video: Path, srt: Path, audio: Path, outfile: Path, cut: dict) -> None:
    ass = srt.with_suffix(".ass")
    srt_to_vertical_ass(srt, ass, cut)
    ass_esc = str(ass.resolve()).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(video), "-i", str(audio),
            "-vf", f"ass={ass_esc}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
            "-shortest", "-movflags", "+faststart", str(outfile),
        ],
        check=True,
        capture_output=True,
    )


def build_one(cut: dict) -> Path:
    cid = cut["id"]
    ver_dir = ASSETS / cid
    audio = ver_dir / "narration.mp3"
    srt = ver_dir / "narration.srt"
    if not audio.exists() or not srt.exists():
        raise FileNotFoundError(f"Missing narration for {cid}")

    duration = probe_duration(audio)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outfile = OUT_DIR / f"pzhisen-promo-en11-{cid}-vertical.mp4"
    scenes = scene_plan(duration, ver_dir, cut)
    print(f"\n=== Building v11 {cid} ({cut['name']} order {cut['order']}) {duration:.1f}s ===")

    drifts = cut["drift_cycle"]
    with tempfile.TemporaryDirectory(prefix=f"pzhisen-en11-{cid}-") as tmp:
        tmp_path = Path(tmp)
        clips = []
        for i, (a, b, img, label) in enumerate(scenes):
            dur = max(0.35, b - a)
            if not img.exists():
                raise FileNotFoundError(img)
            clip = tmp_path / f"clip_{i:02d}.mp4"
            print(f"  scene {i+1:02d}/{len(scenes)} {dur:5.2f}s  {img.name}")
            render_scene_clip(
                img, dur, clip,
                zoom_in=(i % 2 == 0) if cut["zoom_alt"] else (i % 2 == 1),
                is_broll=img.name in BROLL_NAMES,
                drift=drifts[i % len(drifts)],
                zoom_speed=cut["zoom_speed"],
            )
            clips.append(clip)

        concat_list = tmp_path / "concat.txt"
        concat_list.write_text("\n".join(f"file '{c}'" for c in clips) + "\n", encoding="utf-8")
        silent = tmp_path / "silent.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(silent)],
            check=True,
            capture_output=True,
        )
        burn_subtitles(silent, srt, audio, outfile, cut)

    print(f"  Done: {outfile.name} ({outfile.stat().st_size / (1024*1024):.1f} MB)")
    return outfile


def zip_all(paths: list[Path]) -> list[Path]:
    """Write 5 per-persona ZIPs (GitHub-friendly sizes) instead of one huge archive."""
    out: list[Path] = []
    by_vid: dict[str, list[Path]] = {"v1": [], "v2": [], "v3": [], "v4": [], "v5": []}
    for p in paths:
        for vid in by_vid:
            if f"-{vid}o" in p.name:
                by_vid[vid].append(p)
                break
    for vid, files in by_vid.items():
        if not files:
            continue
        zpath = OUT_DIR / f"pzhisen-promo-en11-{vid}-orders2to6-vertical.zip"
        with zipfile.ZipFile(zpath, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(files, key=lambda x: x.name):
                zf.write(f, arcname=f.name)
        print(f"ZIP: {zpath.name} ({zpath.stat().st_size / (1024*1024):.1f} MB)")
        out.append(zpath)
    return out


def main() -> None:
    only = sys.argv[1] if len(sys.argv) > 1 else "all"
    parallel = 2
    if len(sys.argv) > 2 and sys.argv[2].startswith("j"):
        parallel = int(sys.argv[2][1:])

    cuts = [c for c in all_cuts() if only == "all" or only == c["id"] or only == c["vid"]]
    built: list[Path] = []

    if parallel <= 1 or len(cuts) == 1:
        for cut in cuts:
            built.append(build_one(cut))
    else:
        with ThreadPoolExecutor(max_workers=parallel) as ex:
            futs = {ex.submit(build_one, cut): cut for cut in cuts}
            for fut in as_completed(futs):
                built.append(fut.result())

    built.sort(key=lambda p: p.name)
    if only == "all" and len(built) == 25:
        zip_all(built)
    print(f"\nBuilt {len(built)} v11 vertical videos.")


if __name__ == "__main__":
    main()
