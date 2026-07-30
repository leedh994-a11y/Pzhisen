#!/usr/bin/env python3
"""Generate unique per-cut UI / site / urgency frames for EN pack v11 (25 cuts)."""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from v11_matrix import all_cuts  # noqa: E402

OUT = ROOT / "assets" / "versions-en-v11"
SITE_SHOTS = list(Path("/tmp/pzhisen-shots").glob("*.png")) if Path("/tmp/pzhisen-shots").exists() else []
# Also reuse prior pack site-ish frames only as raw pixels with heavy regrade (never identical).
FALLBACK_SITES = list((ROOT / "assets" / "versions-en-v10").glob("v*/site.png"))
W, H = 1080, 1920


def font(size: int, mode: str = "sans", bold: bool = False) -> ImageFont.FreeTypeFont:
    paths = {
        "sans": [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ],
        "mono": [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        ],
        "serif": [
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        ],
    }
    for p in paths.get(mode, paths["sans"]):
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def rr(draw, box, fill, radius=28, outline=None, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def noise_bg(base: tuple[int, int, int], seed: int) -> Image.Image:
    rng = random.Random(seed)
    img = Image.new("RGB", (W, H), base)
    px = img.load()
    step = 2 + (seed % 3)
    for y in range(0, H, step):
        for x in range(0, W, step):
            j = rng.randint(-12, 12)
            px[x, y] = tuple(max(0, min(255, c + j)) for c in base)
    return img.filter(ImageFilter.GaussianBlur(0.5 + (seed % 5) * 0.1))


def header(draw, cut, title: str, y=48):
    c = cut["colors"]
    mode = cut["font_mode"]
    draw.text((64, y), "Pzhisen", fill=c["accent"], font=font(28, mode, True))
    draw.text((64, y + 40), "pzhisen.online", fill=c["muted"], font=font(22, mode))
    draw.text((64, y + 90), title, fill=c["text"], font=font(40, mode, True))


def make_revenue(cut: dict) -> Image.Image:
    c = cut["colors"]
    seed = hash(cut["id"] + "rev") % 10_000
    img = noise_bg(c["bg"], seed)
    draw = ImageDraw.Draw(img)
    header(draw, cut, f"Order {cut['ordinal_num']} landed")
    variant = cut["layout_variant"]
    amt = cut["amount_str"]
    when = cut["order_when"]

    if variant == 2:
        rr(draw, (64, 280, 1016, 700), c["panel"], 22, c["accent"], 3)
        draw.text((96, 320), f"ORDER {cut['ordinal_num'].upper()} · AUTO", fill=c["muted"], font=font(26, cut["font_mode"]))
        draw.text((96, 390), amt, fill=c["accent"], font=font(120, cut["font_mode"], True))
        draw.text((96, 560), f"Closed {when}", fill=c["text"], font=font(30, cut["font_mode"]))
        draw.text((96, 620), f"{cut['owner']} · AI storefront", fill=c["muted"], font=font(26, cut["font_mode"]))
    elif variant == 3:
        draw.rectangle((48, 280, 1032, 288), fill=c["accent"])
        draw.text((64, 320), "LIVE ORDER FEED", fill=c["accent"], font=font(28, cut["font_mode"], True))
        y = 400
        for i, label in enumerate([f"#{cut['order']} PAID {amt}", f"setup {cut['setup_clock_short']}", f"agents @{cut['agent_clock_short']}"]):
            rr(draw, (64, y, 1016, y + 110), c["panel"], 16)
            draw.text((100, y + 35), label, fill=c["text"] if i == 0 else c["muted"], font=font(34 if i == 0 else 28, cut["font_mode"], i == 0))
            y += 140
    elif variant == 4:
        rr(draw, (120, 340, 960, 900), c["panel"], 8 if cut["layout_family"] == "signal" else 40, c["accent"], 4)
        draw.text((180, 400), f"{cut['ordinal'].upper()} ORDER", fill=c["muted"], font=font(32, cut["font_mode"]))
        draw.text((180, 500), amt, fill=c["accent"], font=font(140, cut["font_mode"], True))
        draw.text((180, 720), "AI store · no human ops", fill=c["text"], font=font(30, cut["font_mode"]))
    elif variant == 5:
        # split metrics
        rr(draw, (64, 300, 520, 700), c["panel"], 24)
        rr(draw, (560, 300, 1016, 700), c["panel"], 24)
        draw.text((100, 360), "THIS ORDER", fill=c["muted"], font=font(24, cut["font_mode"]))
        draw.text((100, 430), amt, fill=c["accent"], font=font(72, cut["font_mode"], True))
        draw.text((100, 560), cut["ordinal_num"], fill=c["text"], font=font(40, cut["font_mode"], True))
        draw.text((600, 360), "TODAY CAP", fill=c["muted"], font=font(24, cut["font_mode"]))
        draw.text((600, 430), cut["quota"], fill=c["danger"], font=font(64, cut["font_mode"], True))
        draw.text((600, 560), "free tests", fill=c["text"], font=font(28, cut["font_mode"]))
    else:  # 6 timeline
        rr(draw, (64, 280, 1016, 980), c["panel"], 20, c["accent"], 3)
        draw.text((96, 320), "ORDER TIMELINE", fill=c["accent"], font=font(28, cut["font_mode"], True))
        steps = [
            f"Setup {cut['setup_clock_short']}",
            f"Agents @{cut['agent_clock_short']}",
            f"{cut['ordinal_num']} order {amt}",
            f"Status: paid · {when}",
        ]
        y = 420
        for s in steps:
            draw.ellipse((110, y + 10, 150, y + 50), fill=c["accent"])
            draw.text((180, y + 8), s, fill=c["text"], font=font(32, cut["font_mode"]))
            y += 110

    # sparkline unique per cut
    chart_y0 = 1100
    rr(draw, (64, chart_y0, 1016, 1480), c["panel"], 20)
    draw.text((96, chart_y0 + 24), f"Sales curve · order {cut['order']}", fill=c["text"], font=font(28, cut["font_mode"], True))
    pts = []
    for i in range(10):
        hgt = 80 + 30 * math.sin(i * 0.9 + seed) + i * (8 + cut["order"]) + (seed % 17)
        pts.append((130 + i * 85, 1400 - int(hgt)))
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill=c["accent"], width=5 + cut["order"] % 3)
    draw.text((64, 1600), f"pzhisen.online · {cut['title']}", fill=c["muted"], font=font(24, cut["font_mode"]))
    return img


def make_setup(cut: dict) -> Image.Image:
    c = cut["colors"]
    img = noise_bg(c["bg"], hash(cut["id"] + "setup") % 10_000)
    draw = ImageDraw.Draw(img)
    header(draw, cut, "Three steps. Zero code.")
    steps = [
        ("01", "Enter product name", "AI fills catalog fields"),
        ("02", "Upload 3 product photos", "Vision builds the listing"),
        ("03", "Bind payment", "Checkout goes live"),
    ]
    y = 280 + (cut["order"] % 3) * 10
    rad = 6 if cut["layout_family"] == "signal" else 26
    for num, title, sub in steps:
        rr(draw, (64, y, 1016, y + 250), c["panel"], rad, c["accent"], 3)
        draw.text((100, y + 40), num, fill=c["accent"], font=font(52, cut["font_mode"], True))
        draw.text((220, y + 50), title, fill=c["text"], font=font(38, cut["font_mode"], True))
        draw.text((220, y + 130), sub, fill=c["muted"], font=font(28, cut["font_mode"]))
        y += 290
    draw.text((64, 1300), f"Still running — order {cut['ordinal_num']} just paid {cut['amount_str']}", fill=c["text"], font=font(30, cut["font_mode"], True))
    return img


def make_agents(cut: dict) -> Image.Image:
    c = cut["colors"]
    img = noise_bg(c["bg"], hash(cut["id"] + "agents") % 10_000)
    draw = ImageDraw.Draw(img)
    header(draw, cut, f"AI agents @ {cut['agent_clock_short']}")
    agents = [
        ("Ads Agent", "Campaigns live"),
        ("Support Agent", "Buyer replies sent"),
        ("Store Agent", f"Watching order {cut['order']}"),
        ("Growth Agent", "Organic push queued"),
    ]
    y = 280
    for name, detail in agents:
        rr(draw, (64, y, 1016, y + 210), c["panel"], 22)
        draw.ellipse((100, y + 60, 170, y + 130), fill=c["accent"])
        draw.text((200, y + 50), name, fill=c["text"], font=font(36, cut["font_mode"], True))
        draw.text((200, y + 115), detail, fill=c["muted"], font=font(28, cut["font_mode"]))
        draw.text((780, y + 80), "AUTO", fill=c["accent"], font=font(28, cut["font_mode"], True))
        y += 240
    return img


def make_ops(cut: dict) -> Image.Image:
    c = cut["colors"]
    img = noise_bg(c["bg"], hash(cut["id"] + "ops") % 10_000)
    draw = ImageDraw.Draw(img)
    header(draw, cut, "Backend on autopilot")
    rows = [
        ("Ads", "Creatives pushed", "done"),
        ("Copy", "Headlines generated", "done"),
        ("Inbox", "Buyer questions answered", "done"),
        ("Checkout", f"Capture {cut['amount_str']}", "paid"),
        ("Code", "Human edits required", "none"),
        ("Order", f"{cut['ordinal_num']} confirmed", "live"),
    ]
    y = 260
    for left, mid, right in rows:
        rr(draw, (64, y, 1016, y + 130), c["panel"], 16)
        draw.text((96, y + 40), left, fill=c["accent"], font=font(28, cut["font_mode"], True))
        draw.text((280, y + 45), mid, fill=c["text"], font=font(26, cut["font_mode"]))
        draw.text((860, y + 45), right.upper(), fill=c["accent2"], font=font(24, cut["font_mode"], True))
        y += 155
    return img


def make_urgency(cut: dict) -> Image.Image:
    c = cut["colors"]
    img = noise_bg(c["bg"], hash(cut["id"] + "urg") % 10_000)
    draw = ImageDraw.Draw(img)
    header(draw, cut, "Limited free tests")
    fam = cut["layout_family"]
    quota = cut["quota"]
    if fam == "editorial":
        draw.rectangle((0, 400, W, 980), fill=c["accent"])
        draw.text((64, 460), "TODAY LEFT", fill=(255, 255, 255), font=font(46, "serif", True))
        draw.text((64, 560), quota, fill=(255, 255, 255), font=font(150, "serif", True))
        draw.text((64, 800), f"AFTER ORDER {cut['ordinal_num']}", fill=(255, 240, 240), font=font(32, "serif"))
    elif fam == "signal":
        rr(draw, (64, 360, 1016, 980), (0, 0, 0), 4, c["accent"], 6)
        draw.text((120, 420), "⚠ CAPACITY ALERT", fill=c["accent"], font=font(34, "mono", True))
        draw.text((120, 540), quota, fill=c["accent"], font=font(140, "mono", True))
        draw.text((120, 760), "slots remaining today", fill=c["text"], font=font(34, "mono"))
    else:
        rr(draw, (64, 360, 1016, 980), c["panel"], 30, c["danger"], 4)
        draw.text((110, 430), "Today remaining seats", fill=c["muted"], font=font(32, cut["font_mode"]))
        draw.text((110, 520), quota, fill=c["danger"], font=font(140, cut["font_mode"], True))
        draw.text((110, 740), "AI agent daily onboarding cap: 50", fill=c["text"], font=font(28, cut["font_mode"]))
        draw.text((110, 820), f"Order {cut['ordinal_num']} just printed — seats still limited", fill=c["muted"], font=font(26, cut["font_mode"]))

    rr(draw, (64, 1100, 1016, 1320), c["accent"], 26)
    ink = (255, 255, 255) if sum(c["accent"]) < 420 else (10, 10, 10)
    draw.text((110, 1170), "Claim free test → pzhisen.online", fill=ink, font=font(34, cut["font_mode"], True))
    return img


def make_title(cut: dict) -> Image.Image:
    c = cut["colors"]
    img = noise_bg(c["bg"], hash(cut["id"] + "title") % 10_000)
    draw = ImageDraw.Draw(img)
    draw.text((64, 380), "PZHISEN", fill=c["accent"], font=font(70, cut["font_mode"], True))
    draw.text((64, 490), f"Order {cut['ordinal_num']} + limited seats", fill=c["text"], font=font(44, cut["font_mode"], True))
    draw.text((64, 600), cut["title"], fill=c["muted"], font=font(28, cut["font_mode"]))
    draw.text((64, 720), f"{cut['amount_str']} · {cut['quota']}", fill=c["accent"], font=font(40, cut["font_mode"], True))
    draw.text((64, 1600), "pzhisen.online", fill=c["accent"], font=font(40, cut["font_mode"], True))
    return img


def make_success(cut: dict) -> Image.Image:
    c = cut["colors"]
    img = noise_bg(c["bg"], hash(cut["id"] + "ok") % 10_000)
    draw = ImageDraw.Draw(img)
    header(draw, cut, f"Order {cut['ordinal_num']} confirmed")
    rr(draw, (140, 420, 940, 1100), c["panel"], 36, c["accent"], 4)
    draw.ellipse((420, 500, 660, 740), outline=c["accent"], width=10)
    draw.line([(480, 620), (545, 680), (620, 560)], fill=c["accent"], width=14)
    draw.text((220, 800), f"Paid {cut['amount_str']}", fill=c["text"], font=font(52, cut["font_mode"], True))
    draw.text((220, 900), f"{cut['ordinal'].title()} AI-store order", fill=c["muted"], font=font(30, cut["font_mode"]))
    draw.text((220, 980), "pzhisen.online", fill=c["accent"], font=font(30, cut["font_mode"], True))
    return img


def compose_site(cut: dict) -> Image.Image:
    c = cut["colors"]
    sources = SITE_SHOTS or FALLBACK_SITES
    if not sources:
        # solid branded fallback
        img = noise_bg(c["bg"], hash(cut["id"] + "site") % 10_000)
        draw = ImageDraw.Draw(img)
        header(draw, cut, "pzhisen.online")
        draw.text((64, 400), "AI That Runs Your Company\nWhile You Sleep", fill=c["text"], font=font(48, cut["font_mode"], True))
        return img

    idx = abs(hash(cut["id"])) % len(sources)
    base = Image.open(sources[idx]).convert("RGB")
    # unique crop offset
    bw, bh = base.size
    target = W / H
    if bw / bh > target:
        new_w = int(bh * target)
        ox = abs(hash(cut["id"] + "x")) % max(1, bw - new_w)
        base = base.crop((ox, 0, ox + new_w, bh))
    else:
        new_h = int(bw / target)
        oy = abs(hash(cut["id"] + "y")) % max(1, bh - new_h)
        base = base.crop((0, oy, bw, oy + new_h))
    base = base.resize((W, H), Image.Resampling.LANCZOS)
    # unique color grade
    tint = (*c["accent"][:3], 40 + (cut["order"] * 7) % 40)
    framed = Image.alpha_composite(base.convert("RGBA"), Image.new("RGBA", (W, H), tint))
    draw = ImageDraw.Draw(framed)
    # unique chrome per order
    if cut["order"] == 2:
        draw.rectangle((0, 0, W, 120), fill=(*c["bg"], 230))
        draw.text((40, 40), f"LIVE · order {cut['ordinal_num']} · pzhisen.online", fill=c["accent"], font=font(30, cut["font_mode"], True))
    elif cut["order"] == 3:
        rr(draw, (40, 40, 1040, 150), (*c["panel"], 220), 22)
        draw.text((70, 75), f"pzhisen.online — {cut['amount_str']} just paid", fill=c["text"], font=font(28, cut["font_mode"], True))
    elif cut["order"] == 4:
        draw.rectangle((0, H - 170, W, H), fill=(*c["bg"], 230))
        draw.text((48, H - 110), f"▸ OPEN pzhisen.online · seats {cut['quota']}", fill=c["accent"], font=font(32, cut["font_mode"], True))
    elif cut["order"] == 5:
        draw.rectangle((0, 0, 22, H), fill=(*c["accent"], 255))
        draw.rectangle((W - 22, 0, W, H), fill=(*c["accent2"], 255))
        draw.text((60, 80), "pzhisen.online", fill=c["accent"], font=font(36, cut["font_mode"], True))
    else:
        rr(draw, (50, H - 220, 1030, H - 60), (*c["accent"], 230), 24)
        ink = (255, 255, 255) if sum(c["accent"]) < 420 else (10, 10, 10)
        draw.text((90, H - 165), f"Order {cut['ordinal_num']} live · claim free test", fill=ink, font=font(32, cut["font_mode"], True))
    return framed.convert("RGB")


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
    only = sys.argv[1] if len(sys.argv) > 1 else "all"
    OUT.mkdir(parents=True, exist_ok=True)
    for cut in all_cuts():
        if only != "all" and only != cut["id"] and only != cut["vid"]:
            continue
        d = OUT / cut["id"]
        d.mkdir(parents=True, exist_ok=True)
        print(f"=== assets {cut['id']} / {cut['title']} ===")
        for name, fn in GENERATORS.items():
            path = d / name
            fn(cut).save(path, "PNG", optimize=True)
            print(f"  {path.name} ({path.stat().st_size // 1024} KB)")
    print("All v11 assets ready.")


if __name__ == "__main__":
    main()
