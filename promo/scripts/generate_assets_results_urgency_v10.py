#!/usr/bin/env python3
"""Generate brand-new per-video UI / site / urgency frames for EN pack v10 (results+urgency).

Every frame is unique across v1–v5 and deliberately unlike prior packs' asset look.
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "versions-en-v10"
SITE_SHOTS = Path("/tmp/pzhisen-shots")
W, H = 1080, 1920

# Distinct visual systems per cut — colors, layout language, chrome style.
VERSIONS = [
    {
        "id": "v1",
        "label": "Knox · Midnight Ledger",
        "bg": (8, 12, 18),
        "panel": (16, 24, 36),
        "accent": (52, 211, 153),  # emerald
        "accent2": (250, 204, 21),
        "text": (236, 253, 245),
        "muted": (148, 163, 184),
        "danger": (248, 113, 113),
        "amount": "$47",
        "quota": "10/50",
        "time_setup": "3:00 PM",
        "time_order": "this morning",
        "agent_hour": "3:00 AM",
        "owner": "solo website owner",
        "layout": "ledger",  # stacked ledger cards
        "site_shot": "shot1.png",
        "site_tint": (16, 185, 129, 70),
        "font_mode": "mono",
    },
    {
        "id": "v2",
        "label": "Weston · Warm Storefront",
        "bg": (255, 247, 237),
        "panel": (255, 255, 255),
        "accent": (234, 88, 12),  # orange
        "accent2": (14, 116, 144),
        "text": (67, 20, 7),
        "muted": (120, 113, 108),
        "danger": (185, 28, 28),
        "amount": "$87",
        "quota": "12/50",
        "time_setup": "4:00 PM",
        "time_order": "this afternoon",
        "agent_hour": "4:00 AM",
        "owner": "small business owner",
        "layout": "cards",
        "site_shot": "shot2.png",
        "site_tint": (251, 146, 60, 55),
        "font_mode": "sans",
    },
    {
        "id": "v3",
        "label": "Callum · Ice Glass Console",
        "bg": (241, 245, 249),
        "panel": (255, 255, 255),
        "accent": (2, 132, 199),  # sky
        "accent2": (15, 23, 42),
        "text": (15, 23, 42),
        "muted": (100, 116, 139),
        "danger": (220, 38, 38),
        "amount": "$47",
        "quota": "10/50",
        "time_setup": "3:00 PM",
        "time_order": "this afternoon",
        "agent_hour": "3:00 AM",
        "owner": "agency website founder",
        "layout": "glass",
        "site_shot": "shot5.png",
        "site_tint": (56, 189, 248, 50),
        "font_mode": "sans",
    },
    {
        "id": "v4",
        "label": "Dorian · Graphite Signal",
        "bg": (10, 10, 10),
        "panel": (24, 24, 27),
        "accent": (163, 230, 53),  # lime
        "accent2": (244, 244, 245),
        "text": (250, 250, 250),
        "muted": (161, 161, 170),
        "danger": (251, 113, 133),
        "amount": "$87",
        "quota": "12/50",
        "time_setup": "4:00 PM",
        "time_order": "this morning",
        "agent_hour": "4:00 AM",
        "owner": "enterprise site operator",
        "layout": "signal",
        "site_shot": "shot4.png",
        "site_tint": (132, 204, 22, 60),
        "font_mode": "mono",
    },
    {
        "id": "v5",
        "label": "Everett · Editorial Alert",
        "bg": (254, 242, 242),
        "panel": (255, 255, 255),
        "accent": (185, 28, 28),  # crimson
        "accent2": (28, 25, 23),
        "text": (28, 25, 23),
        "muted": (87, 83, 78),
        "danger": (153, 27, 27),
        "amount": "$47",
        "quota": "10/50",
        "time_setup": "3:00 PM",
        "time_order": "this morning",
        "agent_hour": "3:00 AM",
        "owner": "independent web shop owner",
        "layout": "editorial",
        "site_shot": "shot6.png",
        "site_tint": (248, 113, 113, 45),
        "font_mode": "serif",
    },
]


def font(size: int, mode: str = "sans", bold: bool = False) -> ImageFont.FreeTypeFont:
    paths = {
        "sans": [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ],
        "mono": [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf",
        ],
        "serif": [
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        ],
    }
    for p in paths.get(mode, paths["sans"]):
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def rr(draw: ImageDraw.ImageDraw, box, fill, radius=28, outline=None, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def noise_bg(base: tuple[int, int, int], seed: int) -> Image.Image:
    rng = random.Random(seed)
    img = Image.new("RGB", (W, H), base)
    px = img.load()
    for y in range(0, H, 3):
        for x in range(0, W, 3):
            j = rng.randint(-10, 10)
            px[x, y] = tuple(max(0, min(255, c + j)) for c in base)
    return img.filter(ImageFilter.GaussianBlur(0.6))


def draw_header(draw, ver, title: str, y=48):
    f = font(28, ver["font_mode"], True)
    draw.text((64, y), "Pzhisen", fill=ver["accent"], font=f)
    draw.text((64, y + 40), "pzhisen.online", fill=ver["muted"], font=font(22, ver["font_mode"]))
    draw.text((64, y + 90), title, fill=ver["text"], font=font(42, ver["font_mode"], True))


def make_revenue(ver: dict) -> Image.Image:
    img = noise_bg(ver["bg"], hash(ver["id"] + "rev") % 10_000)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_header(draw, ver, "First order landed")
    # Big amount panel
    if ver["layout"] == "ledger":
        rr(draw, (64, 280, 1016, 620), ver["panel"], 20, ver["accent"], 3)
        draw.text((96, 320), "STORE PAYOUT", fill=ver["muted"], font=font(26, "mono"))
        draw.text((96, 380), ver["amount"], fill=ver["accent"], font=font(120, "mono", True))
        draw.text((96, 530), f"Order #1001 · auto-closed {ver['time_order']}", fill=ver["text"], font=font(28, "mono"))
    elif ver["layout"] == "editorial":
        draw.rectangle((48, 260, 1032, 268), fill=ver["accent"])
        draw.text((64, 300), "BREAKING", fill=ver["accent"], font=font(36, "serif", True))
        draw.text((64, 360), ver["amount"], fill=ver["text"], font=font(140, "serif", True))
        draw.text((64, 540), "AI STORE · ORDER #1 CONFIRMED", fill=ver["muted"], font=font(30, "serif"))
        draw.rectangle((48, 620, 1032, 628), fill=ver["accent"])
    elif ver["layout"] == "signal":
        rr(draw, (80, 300, 1000, 700), ver["panel"], 8, ver["accent"], 4)
        draw.text((120, 340), "▸ LIVE REVENUE PING", fill=ver["accent"], font=font(28, "mono", True))
        draw.text((120, 420), ver["amount"], fill=ver["accent2"], font=font(130, "mono", True))
        draw.text((120, 590), "status: paid · source: AI storefront", fill=ver["muted"], font=font(26, "mono"))
    else:
        rr(draw, (72, 290, 1008, 680), ver["panel"], 36, None)
        draw.text((110, 340), "Revenue snapshot", fill=ver["muted"], font=font(28, ver["font_mode"]))
        draw.text((110, 400), ver["amount"], fill=ver["accent"], font=font(128, ver["font_mode"], True))
        draw.text((110, 560), f"First sale · {ver['time_order']}", fill=ver["text"], font=font(32, ver["font_mode"]))
        draw.text((110, 610), "via AI store on pzhisen.online", fill=ver["muted"], font=font(26, ver["font_mode"]))

    # Mini chart / metrics
    chart_y0, chart_y1 = 760, 1180
    rr(draw, (64, chart_y0, 1016, chart_y1), ver["panel"], 24)
    draw.text((96, chart_y0 + 30), "Ad / store performance", fill=ver["text"], font=font(30, ver["font_mode"], True))
    pts = [(120 + i * 90, 1100 - int(80 + 40 * math.sin(i * 0.7 + hash(ver["id"]) % 7) + i * 18)) for i in range(9)]
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill=ver["accent"], width=6)
    for p in pts:
        draw.ellipse((p[0] - 7, p[1] - 7, p[0] + 7, p[1] + 7), fill=ver["accent2"])

    # Bottom proof chips
    chips = ["Product name ✓", "3 photos ✓", "Payments ✓", f"Setup {ver['time_setup']}"]
    x = 64
    for c in chips:
        tw = draw.textlength(c, font=font(24, ver["font_mode"]))
        rr(draw, (x, 1280, x + tw + 40, 1360), ver["panel"], 18, ver["accent"], 2)
        draw.text((x + 20, 1300), c, fill=ver["text"], font=font(24, ver["font_mode"]))
        x += tw + 56

    draw.text((64, 1480), f"{ver['owner'].title()} · powered by Pzhisen", fill=ver["muted"], font=font(26, ver["font_mode"]))
    draw.text((64, 1760), "CONFIDENTIAL STORE METRICS", fill=ver["muted"], font=font(20, ver["font_mode"]))
    return img


def make_setup(ver: dict) -> Image.Image:
    img = noise_bg(ver["bg"], hash(ver["id"] + "setup") % 10_000)
    draw = ImageDraw.Draw(img)
    draw_header(draw, ver, "Three steps. Zero code.")
    steps = [
        ("01", "Enter product name", "AI fills store catalog fields"),
        ("02", "Upload 3 product photos", "Vision model builds the listing"),
        ("03", "Bind payment", "Checkout goes live instantly"),
    ]
    y = 280
    for num, title, sub in steps:
        rr(draw, (64, y, 1016, y + 260), ver["panel"], 28 if ver["layout"] != "signal" else 6, ver["accent"] if ver["layout"] in ("ledger", "signal") else None, 3)
        draw.text((100, y + 40), num, fill=ver["accent"], font=font(56, ver["font_mode"], True))
        draw.text((220, y + 55), title, fill=ver["text"], font=font(40, ver["font_mode"], True))
        draw.text((220, y + 130), sub, fill=ver["muted"], font=font(28, ver["font_mode"]))
        y += 300
    draw.text((64, 1280), "No code written. No copy typed.", fill=ver["text"], font=font(34, ver["font_mode"], True))
    draw.text((64, 1340), "pzhisen.online handles the rest.", fill=ver["muted"], font=font(28, ver["font_mode"]))
    return img


def make_agents(ver: dict) -> Image.Image:
    img = noise_bg(ver["bg"], hash(ver["id"] + "agents") % 10_000)
    draw = ImageDraw.Draw(img)
    draw_header(draw, ver, f"AI agents @ {ver['agent_hour']}")
    agents = [
        ("Ads Agent", "Campaigns live · spend optimized"),
        ("Support Agent", "Customer replies sent"),
        ("Store Agent", "Listing + checkout watching"),
        ("Growth Agent", "Organic push queued"),
    ]
    y = 280
    for name, detail in agents:
        rr(draw, (64, y, 1016, y + 220), ver["panel"], 24)
        draw.ellipse((100, y + 70, 170, y + 140), fill=ver["accent"])
        draw.text((200, y + 55), name, fill=ver["text"], font=font(38, ver["font_mode"], True))
        draw.text((200, y + 120), detail, fill=ver["muted"], font=font(28, ver["font_mode"]))
        draw.text((780, y + 85), "AUTO", fill=ver["accent"], font=font(30, ver["font_mode"], True))
        y += 250
    draw.text((64, 1400), "Working while the founder sleeps.", fill=ver["text"], font=font(32, ver["font_mode"], True))
    return img


def make_ops(ver: dict) -> Image.Image:
    img = noise_bg(ver["bg"], hash(ver["id"] + "ops") % 10_000)
    draw = ImageDraw.Draw(img)
    draw_header(draw, ver, "Backend on autopilot")
    rows = [
        ("Ads", "Meta + TikTok creatives pushed", "done"),
        ("Copy", "Landing headlines generated", "done"),
        ("Inbox", "12 buyer questions answered", "done"),
        ("Checkout", f"Payment capture {ver['amount']}", "paid"),
        ("Code", "Human edits required", "none"),
    ]
    y = 280
    for left, mid, right in rows:
        rr(draw, (64, y, 1016, y + 150), ver["panel"], 18)
        draw.text((96, y + 50), left, fill=ver["accent"], font=font(30, ver["font_mode"], True))
        draw.text((280, y + 55), mid, fill=ver["text"], font=font(28, ver["font_mode"]))
        draw.text((860, y + 55), right.upper(), fill=ver["accent2"], font=font(26, ver["font_mode"], True))
        y += 180
    return img


def make_urgency(ver: dict) -> Image.Image:
    img = noise_bg(ver["bg"], hash(ver["id"] + "urg") % 10_000)
    draw = ImageDraw.Draw(img)
    draw_header(draw, ver, "Limited free tests")
    # Giant quota
    if ver["layout"] == "editorial":
        draw.rectangle((0, 420, W, 980), fill=ver["accent"])
        draw.text((64, 480), "TODAY LEFT", fill=(255, 255, 255), font=font(48, "serif", True))
        draw.text((64, 580), ver["quota"], fill=(255, 255, 255), font=font(160, "serif", True))
        draw.text((64, 820), "NEW STORES / DAY CAP", fill=(255, 240, 240), font=font(34, "serif"))
    elif ver["layout"] == "signal":
        rr(draw, (64, 360, 1016, 980), (0, 0, 0), 4, ver["accent"], 6)
        draw.text((120, 420), "⚠ CAPACITY ALERT", fill=ver["accent"], font=font(36, "mono", True))
        draw.text((120, 540), ver["quota"], fill=ver["accent"], font=font(150, "mono", True))
        draw.text((120, 760), "slots remaining today", fill=ver["text"], font=font(36, "mono"))
        draw.text((120, 840), "hard limit: 50 new stores / day", fill=ver["muted"], font=font(28, "mono"))
    else:
        rr(draw, (64, 360, 1016, 980), ver["panel"], 32, ver["danger"], 4)
        draw.text((110, 430), "Today remaining seats", fill=ver["muted"], font=font(34, ver["font_mode"]))
        draw.text((110, 520), ver["quota"], fill=ver["danger"], font=font(150, ver["font_mode"], True))
        draw.text((110, 740), "AI agent daily onboarding cap: 50", fill=ver["text"], font=font(30, ver["font_mode"]))
        draw.text((110, 820), "When full → wait until next month", fill=ver["muted"], font=font(28, ver["font_mode"]))

    rr(draw, (64, 1100, 1016, 1320), ver["accent"], 28)
    cta = "Claim free test → pzhisen.online"
    draw.text((120, 1175), cta, fill=(255, 255, 255) if sum(ver["accent"]) < 500 else (10, 10, 10), font=font(36, ver["font_mode"], True))
    draw.text((64, 1450), "Wake up to orders. Tap the link below.", fill=ver["text"], font=font(32, ver["font_mode"], True))
    return img


def compose_site(ver: dict) -> Image.Image:
    """Unique treatment of real pzhisen.online screenshot per version."""
    shot_path = SITE_SHOTS / ver["site_shot"]
    if not shot_path.exists():
        shot_path = SITE_SHOTS / "home.png"
    base = Image.open(shot_path).convert("RGB")
    # Fit to 9:16 canvas with unique crop offsets
    target_ratio = W / H
    bw, bh = base.size
    if bw / bh > target_ratio:
        new_w = int(bh * target_ratio)
        # unique horizontal crop per version
        ox = (hash(ver["id"]) % max(1, bw - new_w))
        base = base.crop((ox, 0, ox + new_w, bh))
    else:
        new_h = int(bw / target_ratio)
        oy = (hash(ver["id"] + "y") % max(1, bh - new_h))
        base = base.crop((0, oy, bw, oy + new_h))
    base = base.resize((W, H), Image.Resampling.LANCZOS)

    # Unique color grade / frame chrome
    overlay = Image.new("RGBA", (W, H), ver["site_tint"])
    framed = base.convert("RGBA")
    framed = Image.alpha_composite(framed, overlay)

    # Device chrome / banner unique per layout
    draw = ImageDraw.Draw(framed)
    if ver["layout"] == "ledger":
        draw.rectangle((0, 0, W, 110), fill=(8, 12, 18, 230))
        draw.text((40, 35), "LIVE · pzhisen.online", fill=ver["accent"], font=font(32, "mono", True))
    elif ver["layout"] == "cards":
        rr(draw, (40, 40, 1040, 150), (255, 255, 255, 230), 24)
        draw.text((70, 75), "Visit pzhisen.online — AI employee team", fill=ver["text"], font=font(30, "sans", True))
    elif ver["layout"] == "glass":
        rr(draw, (50, 60, 1030, 170), (255, 255, 255, 180), 30)
        draw.text((80, 95), "pzhisen.online · watch agents work live", fill=ver["text"], font=font(30, "sans", True))
    elif ver["layout"] == "signal":
        draw.rectangle((0, H - 160, W, H), fill=(10, 10, 10, 230))
        draw.text((48, H - 110), "▸ OPEN pzhisen.online", fill=ver["accent"], font=font(40, "mono", True))
    else:
        draw.rectangle((0, 0, W, 16), fill=ver["accent"] + (255,))
        draw.rectangle((0, H - 180, W, H), fill=(28, 25, 23, 230))
        draw.text((48, H - 120), "pzhisen.online — claim today's seat", fill=(255, 255, 255), font=font(34, "serif", True))

    # Side accent bar unique
    bar_x = 0 if ver["id"] in ("v1", "v4") else W - 18
    draw.rectangle((bar_x, 0, bar_x + 18, H), fill=ver["accent"] + (255,))
    return framed.convert("RGB")


def make_title(ver: dict) -> Image.Image:
    img = noise_bg(ver["bg"], hash(ver["id"] + "title") % 10_000)
    draw = ImageDraw.Draw(img)
    draw.text((64, 420), "PZHISEN", fill=ver["accent"], font=font(72, ver["font_mode"], True))
    draw.text((64, 530), "Results + limited seats", fill=ver["text"], font=font(48, ver["font_mode"], True))
    draw.text((64, 640), ver["label"], fill=ver["muted"], font=font(30, ver["font_mode"]))
    draw.text((64, 780), "AI store · first order · free test", fill=ver["text"], font=font(34, ver["font_mode"]))
    draw.text((64, 1600), "pzhisen.online", fill=ver["accent"], font=font(40, ver["font_mode"], True))
    return img


def make_success(ver: dict) -> Image.Image:
    img = noise_bg(ver["bg"], hash(ver["id"] + "ok") % 10_000)
    draw = ImageDraw.Draw(img)
    draw_header(draw, ver, "Order confirmed")
    rr(draw, (140, 420, 940, 1100), ver["panel"], 40, ver["accent"], 4)
    draw.ellipse((420, 500, 660, 740), outline=ver["accent"], width=10)
    draw.line([(480, 620), (545, 680), (620, 560)], fill=ver["accent"], width=14)
    draw.text((220, 800), f"Paid {ver['amount']}", fill=ver["text"], font=font(56, ver["font_mode"], True))
    draw.text((220, 900), "AI storefront · no human ops", fill=ver["muted"], font=font(30, ver["font_mode"]))
    draw.text((220, 980), "pzhisen.online", fill=ver["accent"], font=font(32, ver["font_mode"], True))
    return img


GENERATORS = {
    "title.png": make_title,
    "revenue.png": make_revenue,
    "setup.png": make_setup,
    "agents.png": make_agents,
    "ops.png": make_ops,
    "site.png": compose_site,
    "urgency.png": make_urgency,
    "success.png": make_success,
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for ver in VERSIONS:
        d = OUT / ver["id"]
        d.mkdir(parents=True, exist_ok=True)
        print(f"=== assets {ver['id']} / {ver['label']} ===")
        for name, fn in GENERATORS.items():
            path = d / name
            img = fn(ver)
            img.save(path, "PNG", optimize=True)
            print(f"  wrote {path.name} ({path.stat().st_size // 1024} KB)")
    print("All v10 unique assets ready.")


if __name__ == "__main__":
    main()
