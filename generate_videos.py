#!/usr/bin/env python3
"""
Generate 5 unique vertical marketing videos for Pzhisen AI store.
Uses ffmpeg concat with still images + subtitle overlay for speed.
"""

import os
import subprocess
import shutil
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np

OUTPUT_DIR = "/workspace/videos"
ASSETS_DIR = "/opt/cursor/artifacts/assets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H = 1080, 1920

# ─────────────────────────── scripts ────────────────────────────────────────
# Each script: list of (duration_secs, act_number, subtitle_text)
VIDEO_CONFIGS = [
    {
        "name": "dark_neon",
        "slots": "10 / 50",
        "sale_amount": "$47",
        "time_morning": "morning",
        "time_yesterday": "3 PM",
        "night_time": "3 AM",
        "segments": [
            # (duration, act, subtitle_en)
            (1.5, 1, "Yesterday at 3 PM — one store owner. Three steps on Pzhisen."),
            (1.5, 1, "Product name. 3 photos. Payment connected."),
            (4.0, 2, "This morning his AI store received its FIRST order: $47"),
            (5.5, 2, "He never wrote a single line of code. Not one word of ad copy."),
            (5.5, 2, "At 3 AM, Pzhisen's AI agent launched all ad campaigns automatically."),
            (5.5, 2, "Customer replies, order fulfillment — all handled by AI while he slept."),
            (5.0, 2, "Zero human effort. 100% automated. Every night."),
            (4.5, 3, "⚠ The AI agent serves only 50 new stores per day."),
            (4.5, 3, "TODAY'S SLOTS: 10 / 50 remaining."),
            (4.5, 3, "Click the link below to claim your FREE trial access."),
            (3.5, 3, "Slots reset monthly. Once they're gone — you wait."),
        ]
    },
    {
        "name": "clean_white",
        "slots": "12 / 50",
        "sale_amount": "$87",
        "time_morning": "afternoon",
        "time_yesterday": "4 PM",
        "night_time": "4 AM",
        "segments": [
            (1.5, 1, "4 PM yesterday. A business owner set up his Pzhisen store."),
            (1.5, 1, "Step 1: product name. Step 2: 3 images. Step 3: payment linked."),
            (4.0, 2, "This afternoon his dashboard showed: First sale — $87!"),
            (5.5, 2, "He coded absolutely nothing. Wrote zero marketing copy."),
            (5.5, 2, "While he slept, Pzhisen's AI ran every ad campaign."),
            (5.5, 2, "Answered every customer chat. Closed every sale. At 4 AM."),
            (5.0, 2, "Fully automated. Professional-grade. No tech skills required."),
            (4.5, 3, "Pzhisen AI opens only 50 store slots daily."),
            (4.5, 3, "Available today: 12 / 50 — going fast."),
            (4.5, 3, "Tap the link to lock in your free test slot now."),
            (3.5, 3, "Start tonight. See your first order by morning."),
        ]
    },
    {
        "name": "cyberpunk",
        "slots": "10 / 50",
        "sale_amount": "$47",
        "time_morning": "morning",
        "time_yesterday": "3 PM",
        "night_time": "3 AM",
        "segments": [
            (1.5, 1, "3 PM. One entrepreneur. Three taps on Pzhisen."),
            (1.5, 1, "Name typed. Photos uploaded. Stripe activated."),
            (4.0, 2, "Next morning — DING. First order. $47. While he slept."),
            (5.5, 2, "No code. No copywriting. No late nights staring at screens."),
            (5.5, 2, "Pzhisen's AI agent went live at 3 AM —"),
            (5.5, 2, "Ran ads, chatted with buyers, processed payments — all autonomous."),
            (5.0, 2, "The system never sleeps. Your store never stops."),
            (4.5, 3, "ALERT: Only 50 AI stores can launch each day."),
            (4.5, 3, "REMAINING SLOTS: 10 / 50"),
            (4.5, 3, "Smash the link below — grab your free access before midnight."),
            (3.5, 3, "Quota resets monthly. Don't miss today's window."),
        ]
    },
    {
        "name": "terminal_green",
        "slots": "12 / 50",
        "sale_amount": "$87",
        "time_morning": "afternoon",
        "time_yesterday": "4 PM",
        "night_time": "4 AM",
        "segments": [
            (1.5, 1, "> PZHISEN STORE SETUP INITIATED — 4:00 PM"),
            (1.5, 1, "> INPUT: product_name, images[3], payment_gateway — DONE"),
            (4.0, 2, "> 07:23 AM — TRANSACTION RECEIVED: +$87.00 USD — SUCCESS"),
            (5.5, 2, "> OPERATOR ACTIONS: 0 code commits. 0 ad copies written."),
            (5.5, 2, "> AI AGENT STATUS: RUNNING since 4:00 AM"),
            (5.5, 2, "> Tasks completed: ad_launch, customer_reply, order_fulfill"),
            (5.0, 2, "> All processes fully automated. Human input: NOT REQUIRED."),
            (4.5, 3, "> WARNING: Daily slot capacity = 50 stores"),
            (4.5, 3, "> AVAILABLE SLOTS: 12 / 50 — DIMINISHING"),
            (4.5, 3, "> ACTION REQUIRED: Click link to claim FREE trial slot"),
            (3.5, 3, "> QUOTA RESETS: monthly. ACT NOW or WAIT."),
        ]
    },
    {
        "name": "warm_gold",
        "slots": "10 / 50",
        "sale_amount": "$47",
        "time_morning": "morning",
        "time_yesterday": "3 PM",
        "night_time": "3 AM",
        "segments": [
            (1.5, 1, "Yesterday 3 PM. One product. One dream. One decision."),
            (1.5, 1, "Product name entered. 3 photos uploaded. Payment set."),
            (4.0, 2, "This morning — the moment every entrepreneur dreams of: First sale $47"),
            (5.5, 2, "Not one line of code. Not one marketing strategy meeting."),
            (5.5, 2, "At 3 AM, Pzhisen's AI worked in the dark —"),
            (5.5, 2, "Creating ads, handling customers, generating revenue. For you."),
            (5.0, 2, "This is what passive income actually looks like in 2025."),
            (4.5, 3, "The AI can serve only 50 entrepreneurs per day."),
            (4.5, 3, "Today's remaining spots: 10 out of 50."),
            (4.5, 3, "Click the link below — your free trial awaits."),
            (3.5, 3, "Wake up tomorrow to your first automated sale."),
        ]
    },
]


# ─────────────────────────── style definitions ───────────────────────────────
STYLES = {
    "dark_neon": {
        "bg": (8, 8, 25),
        "accent": (0, 255, 128),
        "text": (255, 255, 255),
        "sub_bg": (0, 0, 0),
        "sub_text": (255, 255, 255),
        "font_style": "bold",
    },
    "clean_white": {
        "bg": (248, 249, 255),
        "accent": (37, 99, 235),
        "text": (15, 23, 42),
        "sub_bg": (15, 23, 42),
        "sub_text": (255, 255, 255),
        "font_style": "regular",
    },
    "cyberpunk": {
        "bg": (5, 0, 15),
        "accent": (255, 0, 200),
        "text": (0, 255, 255),
        "sub_bg": (20, 0, 30),
        "sub_text": (0, 255, 255),
        "font_style": "bold",
    },
    "terminal_green": {
        "bg": (0, 10, 0),
        "accent": (0, 230, 0),
        "text": (0, 230, 0),
        "sub_bg": (0, 20, 0),
        "sub_text": (0, 230, 0),
        "font_style": "mono",
    },
    "warm_gold": {
        "bg": (25, 12, 0),
        "accent": (255, 180, 0),
        "text": (255, 240, 200),
        "sub_bg": (30, 15, 0),
        "sub_text": (255, 240, 200),
        "font_style": "bold",
    },
}


def get_font(size, style="bold"):
    font_paths = {
        "bold":    ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"],
        "regular": ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"],
        "mono":    ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"],
    }
    for path in font_paths.get(style, font_paths["bold"]):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def make_act1_image(cfg, style, dashboard_path):
    """Dashboard reveal - zoomed, darkened, with accent bar."""
    img = Image.open(dashboard_path).convert("RGB")
    img = img.resize((W, H), Image.LANCZOS)
    
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(0.65)
    
    draw = ImageDraw.Draw(img)
    r, g, b = style["accent"]
    draw.rectangle([0, 0, W, 10], fill=(r, g, b))
    draw.rectangle([0, H - 10, W, H], fill=(r, g, b))
    
    font = get_font(40, style["font_style"])
    badge = "  pzhisen.online  "
    bbox = draw.textbbox((0, 0), badge, font=font)
    bw = bbox[2] - bbox[0]
    draw.rectangle([20, 20, 20 + bw + 20, 74], fill=(r, g, b))
    draw.text((30, 28), badge.strip(), font=font, fill=(0, 0, 0))
    
    # "RESULTS" header
    font_h = get_font(60, style["font_style"])
    header = "REAL RESULTS"
    bbox2 = draw.textbbox((0, 0), header, font=font_h)
    hx = (W - (bbox2[2] - bbox2[0])) // 2
    draw.text((hx + 2, H - 180 + 2), header, font=font_h, fill=(0, 0, 0))
    draw.text((hx, H - 180), header, font=font_h, fill=(r, g, b))
    
    return img


def make_act2_image(cfg, style, dashboard_path):
    """Dashboard with operations highlight overlay."""
    img = Image.open(dashboard_path).convert("RGB")
    img = img.resize((W, H), Image.LANCZOS)
    
    # Desaturate slightly
    gray = img.convert("L").convert("RGB")
    img = Image.blend(img, gray, 0.3)
    
    # Dark overlay on lower half
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov = ImageDraw.Draw(overlay)
    ov.rectangle([0, H // 2, W, H], fill=(0, 0, 0, 160))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    
    draw = ImageDraw.Draw(img)
    r, g, b = style["accent"]
    
    # AI badge
    font_b = get_font(38, style["font_style"])
    badge_txt = "AI AGENT ACTIVE 24/7 — NO CODE REQUIRED"
    bbox = draw.textbbox((0, 0), badge_txt, font=font_b)
    bw = bbox[2] - bbox[0]
    bx = (W - bw) // 2
    draw.rectangle([bx - 16, 30, bx + bw + 16, 84], fill=(r, g, b))
    draw.text((bx, 38), badge_txt, font=font_b, fill=(0, 0, 0))
    
    # Steps list
    steps = ["✓ No code written", "✓ No ads manually created", "✓ AI handled all customer chat",
             "✓ Orders fulfilled automatically"]
    font_s = get_font(44, style["font_style"])
    y = H // 2 + 30
    for step in steps:
        draw.text((60, y + 2), step, font=font_s, fill=(0, 0, 0))
        draw.text((60, y), step, font=font_s, fill=style["text"])
        y += 60
    
    return img


def make_act3_image(cfg, style, dashboard_path):
    """Urgent counter screen."""
    img = Image.open(dashboard_path).convert("RGB")
    img = img.resize((W, H), Image.LANCZOS)
    img = img.filter(ImageFilter.GaussianBlur(radius=15))
    
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(0.4)
    
    draw = ImageDraw.Draw(img)
    r, g, b = style["accent"]
    
    # Top warning bar
    draw.rectangle([0, 0, W, 110], fill=(r, g, b))
    font_warn = get_font(46, style["font_style"])
    warn = "⚠  LIMITED DAILY SLOTS  ⚠"
    bbox = draw.textbbox((0, 0), warn, font=font_warn)
    wx = (W - (bbox[2] - bbox[0])) // 2
    draw.text((wx, 28), warn, font=font_warn, fill=(0, 0, 0))
    
    # Counter box
    box_y = 200
    draw.rectangle([60, box_y, W - 60, box_y + 300], fill=style["bg"],
                   outline=(r, g, b), width=5)
    
    font_label = get_font(40, style["font_style"])
    label = "TODAY'S AVAILABLE SLOTS"
    bbox = draw.textbbox((0, 0), label, font=font_label)
    lx = (W - (bbox[2] - bbox[0])) // 2
    draw.text((lx, box_y + 30), label, font=font_label, fill=style["text"])
    
    font_num = get_font(140, style["font_style"])
    slots = cfg["slots"]
    bbox2 = draw.textbbox((0, 0), slots, font=font_num)
    nx = (W - (bbox2[2] - bbox2[0])) // 2
    draw.text((nx + 3, box_y + 100 + 3), slots, font=font_num, fill=(0, 0, 0))
    draw.text((nx, box_y + 100), slots, font=font_num, fill=(r, g, b))
    
    font_sub = get_font(44, style["font_style"])
    sub = "out of 50 daily limit"
    bbox3 = draw.textbbox((0, 0), sub, font=font_sub)
    sx = (W - (bbox3[2] - bbox3[0])) // 2
    draw.text((sx, box_y + 248), sub, font=font_sub, fill=style["text"])
    
    # CTA
    cta_y = box_y + 340
    font_cta = get_font(52, style["font_style"])
    cta = "👇 CLAIM FREE TRIAL NOW 👇"
    bbox4 = draw.textbbox((0, 0), cta, font=font_cta)
    cx = (W - (bbox4[2] - bbox4[0])) // 2
    draw.text((cx, cta_y), cta, font=font_cta, fill=(r, g, b))
    
    # URL
    font_url = get_font(48, style["font_style"])
    url = "pzhisen.online"
    bbox5 = draw.textbbox((0, 0), url, font=font_url)
    ux = (W - (bbox5[2] - bbox5[0])) // 2
    draw.rectangle([ux - 20, cta_y + 80, ux + (bbox5[2] - bbox5[0]) + 20, cta_y + 150],
                   fill=(r, g, b))
    draw.text((ux, cta_y + 88), url, font=font_url, fill=(0, 0, 0))
    
    # "Reset monthly" warning
    font_rst = get_font(38, style["font_style"])
    rst = "Slots reset monthly — don't miss today!"
    bbox6 = draw.textbbox((0, 0), rst, font=font_rst)
    rx = (W - (bbox6[2] - bbox6[0])) // 2
    draw.text((rx, H - 100), rst, font=font_rst, fill=style["text"])
    
    return img


def add_subtitle(img, text, style):
    if not text:
        return img
    draw_img = img.copy().convert("RGBA")
    overlay = Image.new("RGBA", draw_img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    font = get_font(46, style["font_style"])
    max_w = W - 80
    dummy = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    lines = wrap_text(text, font, max_w, dummy)
    
    line_h = 58
    total_h = len(lines) * line_h + 24
    bar_y = H - total_h - 60
    
    r, g, b = style["sub_bg"]
    draw.rectangle([0, bar_y - 8, W, bar_y + total_h + 8], fill=(r, g, b, 210))
    
    y = bar_y
    sr, sg, sb = style["sub_text"]
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        # shadow
        draw.text(((W - tw) // 2 + 2, y + 2), line, font=font, fill=(0, 0, 0, 255))
        draw.text(((W - tw) // 2, y), line, font=font, fill=(sr, sg, sb, 255))
        y += line_h
    
    result = Image.alpha_composite(draw_img, overlay)
    return result.convert("RGB")


def build_video(idx):
    cfg = VIDEO_CONFIGS[idx]
    style = STYLES[cfg["name"]]
    dashboard = f"{ASSETS_DIR}/dashboard_v{idx + 1}.png"
    out_path = f"{OUTPUT_DIR}/pzhisen_video_{idx + 1}_{cfg['name']}.mp4"
    tmp_dir = f"/tmp/pz_frames_{idx}"
    os.makedirs(tmp_dir, exist_ok=True)
    
    print(f"\n[Video {idx+1}] Style: {cfg['name']}")
    
    act1_img = make_act1_image(cfg, style, dashboard)
    act2_img = make_act2_image(cfg, style, dashboard)
    act3_img = make_act3_image(cfg, style, dashboard)
    
    segments = cfg["segments"]
    
    # Build concat list and still images
    concat_lines = []
    frame_num = 0
    
    for seg_i, (duration, act, subtitle) in enumerate(segments):
        base = [act1_img, act2_img, act3_img][act - 1]
        frame = add_subtitle(base, subtitle, style)
        frame_path = f"{tmp_dir}/seg_{seg_i:03d}.png"
        frame.save(frame_path)
        concat_lines.append(f"file '{frame_path}'")
        concat_lines.append(f"duration {duration}")
        frame_num += 1
    
    # Add final frame to avoid ffmpeg truncation
    last_seg = segments[-1]
    last_base = [act1_img, act2_img, act3_img][last_seg[1] - 1]
    last_frame = add_subtitle(last_base, last_seg[2], style)
    last_path = f"{tmp_dir}/seg_last.png"
    last_frame.save(last_path)
    concat_lines.append(f"file '{last_path}'")
    
    concat_file = f"{tmp_dir}/concat.txt"
    with open(concat_file, "w") as f:
        f.write("\n".join(concat_lines))
    
    print(f"  Encoding {len(segments)} segments into MP4...")
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-vf", f"scale={W}:{H}:force_original_aspect_ratio=disable,fps=30",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        out_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  FFmpeg ERROR:\n{result.stderr[-800:]}")
    else:
        size_mb = os.path.getsize(out_path) / 1024 / 1024
        print(f"  ✓ Saved: {out_path} ({size_mb:.1f} MB)")
    
    shutil.rmtree(tmp_dir, ignore_errors=True)
    return out_path


if __name__ == "__main__":
    import sys
    indices = list(range(5))
    if len(sys.argv) > 1:
        indices = [int(x) for x in sys.argv[1:]]
    
    results = []
    for i in indices:
        p = build_video(i)
        results.append(p)
    
    print("\n=== DONE ===")
    for p in results:
        if os.path.exists(p):
            mb = os.path.getsize(p) / 1024 / 1024
            print(f"  {p}  ({mb:.1f} MB)")
        else:
            print(f"  MISSING: {p}")
