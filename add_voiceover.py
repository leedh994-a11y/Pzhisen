#!/usr/bin/env python3
"""
Add unique English TTS voiceover to each of the 5 Pzhisen marketing videos.
Uses continuous natural narration (not chipmunk-sped short segments).
Each video gets a different voice so audio fingerprints stay distinct.
"""

import asyncio
import os
import re
import shutil
import subprocess
import edge_tts

VIDEOS_DIR = "/workspace/videos"
AUDIO_DIR = "/tmp/pzhisen_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

VOICES = [
    "en-US-GuyNeural",
    "en-US-JennyNeural",
    "en-GB-RyanNeural",
    "en-US-ChristopherNeural",
    "en-AU-NatashaNeural",
]

# Slightly different rates so they don't fingerprint identically
RATES = ["+5%", "+2%", "+8%", "+0%", "+4%"]

NARRATIONS = [
    # Video 1 dark_neon
    """Yesterday at 3 PM, one store owner took three steps on Pzhisen.
Product name. Three photos. Payment connected.
This morning, his AI store received its first order: forty-seven dollars.
He never wrote a single line of code. Not one word of ad copy.
At 3 AM, Pzhisen's AI agent launched all ad campaigns automatically.
Customer replies and order fulfillment were all handled by AI while he slept.
Zero human effort. One hundred percent automated. Every night.
The AI agent serves only fifty new stores per day.
Today's slots: ten out of fifty remaining.
Click the link below to claim your free trial access.
Slots reset monthly. Once they're gone, you wait.""",

    # Video 2 clean_white
    """At 4 PM yesterday, a business owner set up his Pzhisen store.
Step one: product name. Step two: three images. Step three: payment linked.
This afternoon, his dashboard showed the first sale — eighty-seven dollars!
He coded absolutely nothing. Wrote zero marketing copy.
While he slept, Pzhisen's AI ran every ad campaign.
It answered every customer chat and closed every sale, at 4 AM.
Fully automated. Professional grade. No tech skills required.
Pzhisen AI opens only fifty store slots daily.
Available today: twelve out of fifty — going fast.
Tap the link to lock in your free test slot now.
Start tonight. See your first order by morning.""",

    # Video 3 cyberpunk
    """3 PM. One entrepreneur. Three taps on Pzhisen.
Name typed. Photos uploaded. Stripe activated.
Next morning — ding. First order. Forty-seven dollars. While he slept.
No code. No copywriting. No late nights staring at screens.
Pzhisen's AI agent went live at 3 AM.
It ran ads, chatted with buyers, and processed payments — all autonomous.
The system never sleeps. Your store never stops.
Alert: only fifty AI stores can launch each day.
Remaining slots: ten out of fifty.
Smash the link below and grab your free access before midnight.
Quota resets monthly. Don't miss today's window.""",

    # Video 4 terminal_green
    """Pzhisen store setup initiated at 4 PM.
Input complete: product name, three images, payment gateway — done.
At 7:23 AM, transaction received: plus eighty-seven dollars USD. Success.
Operator actions: zero code commits. Zero ad copies written.
AI agent status: running since 4 AM.
Tasks completed: ad launch, customer reply, and order fulfill.
All processes fully automated. Human input not required.
Warning: daily slot capacity equals fifty stores.
Available slots: twelve out of fifty — diminishing.
Action required: click the link to claim your free trial slot.
Quota resets monthly. Act now, or wait.""",

    # Video 5 warm_gold
    """Yesterday at 3 PM. One product. One dream. One decision.
Product name entered. Three photos uploaded. Payment set.
This morning — the moment every entrepreneur dreams of: first sale, forty-seven dollars.
Not one line of code. Not one marketing strategy meeting.
At 3 AM, Pzhisen's AI worked in the dark.
Creating ads, handling customers, generating revenue — for you.
This is what passive income actually looks like in twenty twenty-five.
The AI can serve only fifty entrepreneurs per day.
Today's remaining spots: ten out of fifty.
Click the link below — your free trial awaits.
Wake up tomorrow to your first automated sale.""",
]

FILES = [
    "pzhisen_video_1_dark_neon.mp4",
    "pzhisen_video_2_clean_white.mp4",
    "pzhisen_video_3_cyberpunk.mp4",
    "pzhisen_video_4_terminal_green.mp4",
    "pzhisen_video_5_warm_gold.mp4",
]


def get_duration(path: str) -> float:
    out = subprocess.check_output(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            path,
        ],
        text=True,
    ).strip()
    return float(out)


def clean_text(text: str) -> str:
    text = text.replace("—", ",").replace("–", ",")
    text = re.sub(r"\s+", " ", text).strip()
    return text


async def synth(text: str, voice: str, rate: str, out_mp3: str):
    communicate = edge_tts.Communicate(clean_text(text), voice, rate=rate)
    await communicate.save(out_mp3)


def fit_audio(src: str, dst: str, target_dur: float):
    actual = get_duration(src)
    print(f"    raw speech={actual:.2f}s, target={target_dur:.2f}s")

    if abs(actual - target_dur) < 0.3:
        subprocess.run(
            ["ffmpeg", "-y", "-i", src, "-c:a", "aac", "-b:a", "128k", "-ar", "44100", dst],
            capture_output=True, check=True,
        )
        return

    if actual < target_dur:
        # pad silence at end
        pad = target_dur - actual
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", src,
                "-af", f"apad=pad_dur={pad:.3f}",
                "-t", f"{target_dur:.3f}",
                "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
                dst,
            ],
            capture_output=True, check=True,
        )
    else:
        # mild speed-up to fit; keep natural if possible (cap ~1.25x)
        ratio = min(actual / target_dur, 1.35)
        rem = ratio
        filters = []
        while rem > 2.0:
            filters.append("atempo=2.0")
            rem /= 2.0
        filters.append(f"atempo={rem:.4f}")
        af = ",".join(filters) + f",apad=pad_dur=1,atrim=0:{target_dur:.3f}"
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", src,
                "-af", af,
                "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
                dst,
            ],
            capture_output=True, check=True,
        )


def mux(video_in: str, audio_in: str, video_out: str):
    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", video_in,
            "-i", audio_in,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "128k",
            "-shortest",
            "-movflags", "+faststart",
            video_out,
        ],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr[-800:])


async def process(idx: int):
    work = f"{AUDIO_DIR}/v{idx}"
    os.makedirs(work, exist_ok=True)
    voice = VOICES[idx]
    rate = RATES[idx]
    video_path = f"{VIDEOS_DIR}/{FILES[idx]}"
    vdur = get_duration(video_path)

    print(f"\n[{idx+1}/5] {FILES[idx]}")
    print(f"  voice={voice} rate={rate} video={vdur:.1f}s")

    raw = f"{work}/voice.mp3"
    fitted = f"{work}/voice_fit.m4a"
    await synth(NARRATIONS[idx], voice, rate, raw)
    fit_audio(raw, fitted, vdur)

    tmp_out = f"{work}/final.mp4"
    mux(video_path, fitted, tmp_out)
    shutil.move(tmp_out, video_path)

    # verify audio stream
    probe = subprocess.check_output(
        [
            "ffprobe", "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=codec_name,channels,sample_rate",
            "-of", "default=noprint_wrappers=1",
            video_path,
        ],
        text=True,
    ).strip()
    mb = os.path.getsize(video_path) / 1024 / 1024
    print(f"  ✓ {mb:.1f} MB\n  {probe}")


async def main():
    for i in range(5):
        await process(i)
    print("\n=== All 5 videos now have English voiceover ===")


if __name__ == "__main__":
    asyncio.run(main())
