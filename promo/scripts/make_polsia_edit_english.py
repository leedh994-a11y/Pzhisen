#!/usr/bin/env python3
"""Rebuild Polsia→Pzhisen/Bob cut with English narration + EN burned-in captions.

Ends the spoken commentary with https://pzhisen.online.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import tempfile
from pathlib import Path

import edge_tts

W, H = 1080, 1920
FONT_EN = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

VOICE = "en-US-AndrewNeural"
RATE = "+8%"
PITCH = "-2Hz"

# Timed English cues aligned to the original story beats.
# Each item: (start, end, spoken text, subtitle lines)
CUES: list[tuple[float, float, str, list[str]]] = [
    (0.0, 2.8, "Silicon Valley just produced a breakout one-person company.", ["Silicon Valley just produced", "a breakout one-person company."]),
    (2.8, 5.8, "It has only one person, yet hit a two hundred fifty million dollar valuation.", ["Only one person —", "$250 million valuation."]),
    (5.8, 8.6, "It just closed thirty million dollars in funding.", ["Just closed", "$30 million in funding."]),
    (8.6, 10.8, "Even wilder — the company itself is almost becoming AI.", ["Even wilder —", "the company is almost becoming AI."]),
    (10.8, 12.5, "It is called Pzhisen.", ["It is called Pzhisen."]),
    (12.5, 14.8, "What does Pzhisen actually do?", ["What does Pzhisen", "actually do?"]),
    (14.8, 19.0, "It is not selling AI tools. It gives you a never-sleeping AI co-founder.", ["Not an AI tools shop —", "a never-sleeping AI co-founder."]),
    (19.0, 23.0, "Type in a business idea, and it runs twenty-four seven on its own.", ["Type a business idea —", "it runs 24/7 on its own."]),
    (23.0, 27.5, "Market research, writing code, building websites, buying ads,", ["Market research, code,", "websites, ads,"]),
    (27.5, 31.0, "cold email, customer support, tracking revenue — a full end-to-end loop.", ["cold email, support, revenue —", "full end-to-end loop."]),
    (31.0, 34.0, "Founder Bob runs with zero employees.", ["Founder Bob", "runs with zero employees."]),
    (34.0, 37.8, "He only signs papers occasionally and leaves the rest to AI agents.", ["He signs papers occasionally —", "AI agents handle the rest."]),
    (37.8, 42.5, "The platform already powers over seventy-six hundred companies, with monthly revenue near one million dollars.", ["7,600+ companies live.", "Monthly revenue near $1M."]),
    (42.5, 45.5, "Annualized revenue is racing toward ten million.", ["Annualized revenue", "racing toward $10M."]),
    (45.5, 50.0, "The real problem it solves is letting ordinary people start like top Silicon Valley teams.", ["Ordinary people can start", "like top Silicon Valley teams."]),
    (50.0, 53.5, "You no longer need ten engineers and twenty operators.", ["No need for 10 engineers", "and 20 operators."]),
    (53.5, 57.5, "One person plus AI can run the company. That is the true one-person company revolution.", ["One person + AI", "can run the company."]),
    (57.5, 61.5, "So who is Bob? He is not a twenty-year-old genius hacker.", ["So who is Bob?", "Not a 20-year-old hacker."]),
    (61.5, 65.2, "He went all-in on AI at thirty-eight or thirty-nine.", ["He went all-in on AI", "at 38 or 39."]),
    (65.2, 72.5, "Before that, he spent five years at Travis Kalanick's Cloud Kitchens as a global G.M., running multi-country teams and hundred-million-dollar P and L.", ["5 years at Cloud Kitchens", "as global GM."]),
    (72.5, 77.3, "Then he quit, living between Paris, Los Angeles, and San Francisco.", ["Then he quit —", "Paris, L.A., San Francisco."]),
    (77.3, 81.5, "Coding with AI sixteen hours a day.", ["Coding with AI", "sixteen hours a day."]),
    (81.5, 86.5, "He first cloned himself with AI, then productized that ability into Pzhisen.", ["Cloned himself with AI,", "then built Pzhisen."]),
    (86.5, 91.5, "From zero to ten million ARR in under four months — all with zero employees.", ["$0 to $10M ARR", "in under 4 months."]),
    (91.5, 96.5, "His story proves that in the AI era, one person can outcompete a traditional team.", ["In the AI era,", "one person can beat a team."]),
    (96.5, 100.0, "So what is the takeaway?", ["So what is", "the takeaway?"]),
    (100.0, 105.0, "The future is not big companies eating small ones. It is AI-armed individuals eating traditional companies.", ["AI-armed individuals", "eat traditional companies."]),
    (105.0, 109.5, "Before, startups needed a team, funding, and an office.", ["Before: team, funding,", "and an office."]),
    (109.5, 113.5, "Now you only need a good idea plus AI infrastructure like Pzhisen — and you can start immediately.", ["Now: a good idea +", "Pzhisen infrastructure."]),
    (113.5, 119.0, "Pzhisen is not just an AI tools company. It is a leading player in one-person company infrastructure for the AI era.", ["Pzhisen is infrastructure", "for one-person companies."]),
    (119.0, 124.0, "It is turning the one-person company from a joke into a new species of business.", ["From a joke into", "a new business species."]),
    (124.0, 128.5, "So here is the question. When AI can already run your company, what are you waiting for?", ["When AI can run your company,", "what are you waiting for?"]),
    (128.5, 133.5, "Keep being a traditional worker — or go try to become the next one-person unicorn?", ["Stay a traditional worker —", "or become a one-person unicorn?"]),
    (133.5, 142.0, "Visit https://pzhisen.online and start today.", ["Visit https://pzhisen.online", "and start today."]),
]

TARGET_END = CUES[-1][1]


def ff(*args: str | Path, show: bool = False) -> None:
    cmd = ["ffmpeg", "-y", *[str(a) for a in args]]
    if show:
        subprocess.check_call(cmd)
    else:
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def probe_duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(out)


def ass_time(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def write_ass(path: Path, duration: float) -> None:
    # PlayRes matches vertical frame. Title stays on screen full length.
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TitleGold,Liberation Sans,64,&H0046D6FF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,0,8,40,40,70,1
Style: TitleWhite,Liberation Sans,52,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,0,8,40,40,140,1
Style: TitleWhite2,Liberation Sans,52,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,0,8,40,40,200,1
Style: Sub,Liberation Sans,46,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,0,2,50,50,280,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,{ass_time(duration)},TitleGold,,0,0,0,,$250M valuation
Dialogue: 0,0:00:00.00,{ass_time(duration)},TitleWhite,,0,0,0,,Silicon Valley
Dialogue: 0,0:00:00.00,{ass_time(duration)},TitleWhite2,,0,0,0,,one-person company
"""
    events = []
    for start, end, _spoken, lines in CUES:
        text = "\\N".join(lines)
        # Escape ASS special chars
        text = text.replace("{", "\\{").replace("}", "\\}")
        events.append(
            f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Sub,,0,0,0,,{text}"
        )
    path.write_text(header + "\n".join(events) + "\n", encoding="utf-8")


async def synth_cue(text: str, out_mp3: Path) -> None:
    communicate = edge_tts.Communicate(text, voice=VOICE, rate=RATE, pitch=PITCH)
    await communicate.save(str(out_mp3))


def build_narration(work: Path) -> Path:
    parts: list[Path] = []
    for i, (start, end, spoken, _lines) in enumerate(CUES):
        mp3 = work / f"cue_{i:02d}.mp3"
        wav = work / f"cue_{i:02d}.wav"
        fitted = work / f"cue_{i:02d}_fit.wav"
        asyncio.run(synth_cue(spoken, mp3))
        ff("-i", mp3, "-ac", "2", "-ar", "48000", wav)
        dur = max(0.15, end - start)
        actual = probe_duration(wav)
        if actual > dur * 0.98:
            tempo = min(1.35, actual / dur)
            ff(
                "-i",
                wav,
                "-filter:a",
                f"atempo={tempo:.4f},apad=whole_dur={dur:.3f}",
                "-t",
                f"{dur:.3f}",
                "-ac",
                "2",
                "-ar",
                "48000",
                fitted,
            )
        else:
            ff(
                "-i",
                wav,
                "-af",
                f"apad=whole_dur={dur:.3f}",
                "-t",
                f"{dur:.3f}",
                "-ac",
                "2",
                "-ar",
                "48000",
                fitted,
            )
        parts.append(fitted)
        print(f"  cue {i:02d} {start:.1f}-{end:.1f}s ok", flush=True)

    list_file = work / "concat.txt"
    final_parts: list[Path] = []
    cursor = 0.0
    for i, ((start, end, _, _), part) in enumerate(zip(CUES, parts)):
        if start > cursor + 0.01:
            gap = start - cursor
            sil = work / f"sil_{i}.wav"
            ff("-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{gap:.3f}", sil)
            final_parts.append(sil)
        final_parts.append(part)
        cursor = end
    with list_file.open("w") as f:
        for p in final_parts:
            f.write(f"file '{p}'\n")
    narration = work / "narration.wav"
    ff("-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", narration)
    print(f"Narration duration: {probe_duration(narration):.2f}s")
    return narration


def render(src: Path, narration: Path, ass_path: Path, out: Path, target: float) -> None:
    """Blur Chinese text bands, burn ASS English captions, mux EN audio."""
    src_dur = probe_duration(src)
    pad = max(0.0, target - src_dur)

    # Escape font dir / ass path for filtergraph
    ass_esc = str(ass_path).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
    fontsdir = str(Path(FONT_EN).parent).replace("\\", "/").replace(":", "\\:")

    # Fully obscure Chinese title/subtitle bands, then burn ASS English.
    # Title glyphs ~y=40..360; subs ~y=1360..1640.
    vf = (
        f"tpad=stop_mode=clone:stop_duration={pad:.3f},"
        f"split=3[base][traw][sraw];"
        f"[traw]crop={W}:360:0:20,gblur=sigma=50,eq=brightness=-0.25:saturation=0.7,"
        f"drawbox=x=0:y=0:w={W}:h=360:color=black@0.72:t=fill[tblur];"
        f"[sraw]crop={W}:300:0:1350,gblur=sigma=45,eq=brightness=-0.18,"
        f"drawbox=x=0:y=0:w={W}:h=300:color=black@0.62:t=fill[sblur];"
        f"[base][tblur]overlay=0:20[v1];"
        f"[v1][sblur]overlay=0:1350[v2];"
        f"[v2]ass='{ass_esc}':fontsdir='{fontsdir}'[vout]"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(src),
        "-i",
        str(narration),
        "-filter_complex",
        vf,
        "-map",
        "[vout]",
        "-map",
        "1:a:0",
        "-t",
        f"{target:.3f}",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "22",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-movflags",
        "+faststart",
        str(out),
    ]
    print("Rendering with ffmpeg (blur + ASS + EN audio)...")
    subprocess.check_call(cmd)
    size_mb = out.stat().st_size / (1024 * 1024)
    print(f"Wrote {out} ({size_mb:.1f} MB)")
    if size_mb > 49:
        tmp_out = out.with_suffix(".tmp.mp4")
        ff(
            "-i",
            out,
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-movflags",
            "+faststart",
            tmp_out,
        )
        tmp_out.replace(out)
        print(f"Compressed to {out.stat().st_size / (1024 * 1024):.1f} MB")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="pzhisen-en-") as tmp:
        work = Path(tmp)
        print("Building English narration...")
        narration = build_narration(work)
        target = max(TARGET_END, probe_duration(narration))
        ass_path = work / "en.ass"
        write_ass(ass_path, target)
        # Keep a copy of cues next to output
        cues_path = args.out.with_suffix(".cues.json")
        cues_path.write_text(
            json.dumps(
                [
                    {"start": s, "end": e, "spoken": sp, "subs": lines}
                    for s, e, sp, lines in CUES
                ],
                indent=2,
            )
        )
        (args.out.parent / "pzhisen-bob-english.ass").write_text(ass_path.read_text())
        render(args.src, narration, ass_path, args.out, target)


if __name__ == "__main__":
    main()
