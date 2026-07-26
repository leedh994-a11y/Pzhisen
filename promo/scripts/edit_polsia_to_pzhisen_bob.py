#!/usr/bin/env python3
"""Rewrite burned-in Polsia/Ben Cera names to Pzhisen/Bob in a vertical promo clip."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 30
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"

# Subtitle band in source frames (approx).
SUB_Y0, SUB_Y1 = 1380, 1620

# Timed subtitle rewrites: (start_sec, end_sec, [line1, line2?])
# Windows padded slightly so transitions stay covered.
SUB_EDITS: list[tuple[float, float, list[str]]] = [
    (10.6, 12.35, ["它叫Pzhisen"]),
    (12.35, 14.85, ["Pzhisen到底在干什么"]),
    (26.9, 30.15, ["追踪收入 全流程一条龙", "创始人Bob"]),
    (30.15, 33.35, ["Bob自己就是零员工运营"]),
    (52.7, 55.85, ["这才是真正的一人公司革命", "那这个Bob"]),
    (55.85, 58.15, ["Bob到底是什么来头"]),
    (84.4, 87.0, ["做成了Pzhisen"]),
    (107.7, 111.85, ["现在你只需要一个好想法+", "Pzhisen这样"]),
    (113.4, 116.9, ["Pzhisen不是单纯的AI", "工具公司"]),
]

# Spoken name segments to duck + replace (from whisper word timestamps).
AUDIO_PATCHES: list[tuple[float, float, str]] = [
    (11.40, 11.92, "Pzhisen"),
    (11.92, 12.78, "Pzhisen"),
    (31.76, 32.22, "Bob"),
    (58.12, 58.56, "Bob"),
    (84.20, 84.64, "Pzhisen"),
    (109.84, 110.22, "Pzhisen"),
    (112.58, 113.44, "Pzhisen"),
]


def load_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size=size)


def inpaint_band(frame: np.ndarray, y0: int = SUB_Y0, y1: int = SUB_Y1) -> np.ndarray:
    """Remove burned-in subtitle glyphs in the lower text band."""
    band = frame[y0:y1]
    gray = cv2.cvtColor(band, cv2.COLOR_BGR2GRAY)
    # White fill + dark stroke of burned-in captions.
    bright = cv2.threshold(gray, 170, 255, cv2.THRESH_BINARY)[1]
    dark = cv2.threshold(gray, 55, 255, cv2.THRESH_BINARY_INV)[1]
    # Keep dark pixels only when near bright cores (stroke around glyphs).
    kernel_near = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    near_bright = cv2.dilate(bright, kernel_near, iterations=1)
    stroke = cv2.bitwise_and(dark, near_bright)
    mask = cv2.bitwise_or(bright, stroke)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    mask = cv2.dilate(mask, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
    mask[:6, :] = 0
    mask[-6:, :] = 0
    if mask.any():
        band = cv2.inpaint(band, mask, 7, cv2.INPAINT_TELEA)
    out = frame.copy()
    out[y0:y1] = band
    return out


def draw_subtitle_lines(frame: np.ndarray, lines: list[str]) -> np.ndarray:
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    font = load_font(70)
    # Two-line block centered in subtitle band
    line_heights = []
    line_widths = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=5)
        line_widths.append(bbox[2] - bbox[0])
        line_heights.append(bbox[3] - bbox[1])
    total_h = sum(line_heights) + (len(lines) - 1) * 10
    y = SUB_Y0 + (SUB_Y1 - SUB_Y0 - total_h) // 2
    for line, lw, lh in zip(lines, line_widths, line_heights):
        x = (W - lw) // 2
        draw.text(
            (x, y),
            line,
            font=font,
            fill=(255, 255, 255),
            stroke_width=5,
            stroke_fill=(0, 0, 0),
        )
        y += lh + 10
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def active_edit(t: float) -> list[str] | None:
    for start, end, lines in SUB_EDITS:
        if start <= t < end:
            return lines
    return None


def process_video(src: Path, silent_out: Path) -> None:
    cap = cv2.VideoCapture(str(src))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open {src}")
    fps = cap.get(cv2.CAP_PROP_FPS) or FPS
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    assert (w, h) == (W, H), f"Unexpected size {w}x{h}"

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "bgr24",
        "-s",
        f"{W}x{H}",
        "-r",
        str(fps),
        "-i",
        "-",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        "-an",
        str(silent_out),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None

    idx = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            t = idx / fps
            lines = active_edit(t)
            if lines is not None:
                frame = inpaint_band(frame)
                frame = draw_subtitle_lines(frame, lines)
            proc.stdin.write(frame.tobytes())
            idx += 1
            if idx % 90 == 0:
                print(f"  frames {idx} ({t:.1f}s)", flush=True)
    finally:
        cap.release()
        proc.stdin.close()
        rc = proc.wait()
        if rc != 0:
            raise RuntimeError(f"ffmpeg encode failed: {rc}")
    print(f"Wrote silent video: {silent_out} ({idx} frames)")


def synth_word(text: str, out_wav: Path, voice: str = "zh-CN-YunxiNeural") -> None:
    # Speak English brand/name with Chinese neural voice for cadence match.
    import asyncio
    import edge_tts

    async def _run() -> None:
        communicate = edge_tts.Communicate(text, voice=voice, rate="+5%")
        await communicate.save(str(out_wav.with_suffix(".mp3")))

    asyncio.run(_run())
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(out_wav.with_suffix(".mp3")),
            "-ac",
            "2",
            "-ar",
            "48000",
            str(out_wav),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def patch_audio(src_video: Path, out_wav: Path, work: Path) -> None:
    raw = work / "orig_audio.wav"
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src_video),
            "-vn",
            "-ac",
            "2",
            "-ar",
            "48000",
            str(raw),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Build ffmpeg filter: duck original at name spans, overlay TTS clips.
    inputs = ["-i", str(raw)]
    filter_parts = []
    # Start with ducked original
    duck_expr = "+".join(
        [f"between(t\\,{s:.3f}\\,{e:.3f})" for s, e, _ in AUDIO_PATCHES]
    )
    # volume=1 except near zero in patch windows
    filter_parts.append(
        f"[0:a]volume=enable='{duck_expr}':volume=0.05[base]"
    )

    overlay_labels = []
    for i, (start, end, text) in enumerate(AUDIO_PATCHES):
        clip = work / f"tts_{i}.wav"
        synth_word(text, clip)
        # Trim/pad TTS to patch duration
        dur = max(0.12, end - start)
        fitted = work / f"tts_{i}_fit.wav"
        subprocess.check_call(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(clip),
                "-af",
                f"atrim=0:{dur},asetpts=PTS-STARTPTS,apad=whole_dur={dur}",
                "-t",
                f"{dur:.3f}",
                "-ac",
                "2",
                "-ar",
                "48000",
                str(fitted),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        inputs += ["-i", str(fitted)]
        delay_ms = int(round(start * 1000))
        filter_parts.append(
            f"[{i+1}:a]adelay={delay_ms}|{delay_ms},volume=2.2[p{i}]"
        )
        overlay_labels.append(f"[p{i}]")

    mix_inputs = "[base]" + "".join(overlay_labels)
    n = 1 + len(AUDIO_PATCHES)
    filter_parts.append(
        f"{mix_inputs}amix=inputs={n}:duration=first:dropout_transition=0:normalize=0[aout]"
    )
    filt = ";".join(filter_parts)
    cmd = [
        "ffmpeg",
        "-y",
        *inputs,
        "-filter_complex",
        filt,
        "-map",
        "[aout]",
        str(out_wav),
    ]
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Wrote patched audio: {out_wav}")


def mux(video: Path, audio: Path, out: Path) -> None:
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-i",
            str(audio),
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            str(out),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"Wrote final: {out}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="pzhisen-edit-") as tmp:
        tmp_path = Path(tmp)
        silent = tmp_path / "silent.mp4"
        audio = tmp_path / "patched.wav"
        print("Processing video frames...")
        process_video(args.src, silent)
        print("Patching audio names...")
        patch_audio(args.src, audio, tmp_path)
        print("Muxing...")
        mux(silent, audio, args.out)


if __name__ == "__main__":
    main()
