#!/usr/bin/env python3
"""Recreate the axi channel banner in Chinese (orange → magenta → purple)."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "promo" / "banners"

STOPS = (
    (0.00, (255, 94, 48)),
    (0.34, (242, 52, 128)),
    (0.62, (196, 42, 186)),
    (1.00, (72, 48, 214)),
)

FONT_BOLD = "/tmp/fonts/NotoSansSC-Bold.otf"
FONT_REGULAR = "/tmp/fonts/NotoSansSC-Regular.otf"
FONT_FALLBACK = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"

TITLE = "你好，我是 abiao！"
SUBTITLE = "我是一名独立开发者，持续分享有价值的内容。"
CTA = "关注我！"


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_color(c0: tuple[int, int, int], c1: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return (
        int(lerp(c0[0], c1[0], t) + 0.5),
        int(lerp(c0[1], c1[1], t) + 0.5),
        int(lerp(c0[2], c1[2], t) + 0.5),
    )


def color_at(t: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    for i in range(len(STOPS) - 1):
        t0, c0 = STOPS[i]
        t1, c1 = STOPS[i + 1]
        if t <= t1:
            u = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            return lerp_color(c0, c1, u)
    return STOPS[-1][1]


def make_gradient(width: int, height: int) -> Image.Image:
    img = Image.new("RGB", (width, height))
    px = img.load()
    for x in range(width):
        rgb = color_at(x / max(width - 1, 1))
        for y in range(height):
            px[x, y] = rgb
    return img


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.truetype(FONT_FALLBACK, size)


def cubic_bezier(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    steps: int = 80,
) -> list[tuple[float, float]]:
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts


def draw_polyline(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[float, float]],
    width: float,
    fill: tuple[int, int, int, int],
) -> None:
    if len(points) < 2:
        return
    draw.line(points, fill=fill, width=int(round(width)), joint="curve")
    r = width / 2
    x0, y0 = points[0]
    x1, y1 = points[-1]
    draw.ellipse((x0 - r, y0 - r, x0 + r, y0 + r), fill=fill)
    draw.ellipse((x1 - r, y1 - r, x1 + r, y1 + r), fill=fill)


def draw_arrowhead(
    draw: ImageDraw.ImageDraw,
    p_prev: tuple[float, float],
    p_tip: tuple[float, float],
    length: float,
    half_w: float,
    fill: tuple[int, int, int, int],
) -> None:
    dx = p_tip[0] - p_prev[0]
    dy = p_tip[1] - p_prev[1]
    mag = math.hypot(dx, dy) or 1.0
    ux, uy = dx / mag, dy / mag
    px, py = -uy, ux
    tip = (p_tip[0] + ux * length * 0.12, p_tip[1] + uy * length * 0.12)
    base = (p_tip[0] - ux * length * 0.72, p_tip[1] - uy * length * 0.72)
    left = (base[0] + px * half_w, base[1] + py * half_w)
    right = (base[0] - px * half_w, base[1] - py * half_w)
    draw.polygon([left, tip, right], fill=fill)


def draw_curly_arrow(overlay: Image.Image, origin: tuple[float, float], scale: float) -> None:
    """Small curl, then a shaft that points down-right toward the corner."""
    ox, oy = origin
    s = scale
    layer = Image.new("RGBA", overlay.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    white = (255, 255, 255, 255)
    stroke = max(4.5, 5.6 * s)

    curl = cubic_bezier(
        (ox - 6 * s, oy + 4 * s),
        (ox - 22 * s, oy - 18 * s),
        (ox + 30 * s, oy - 16 * s),
        (ox + 22 * s, oy + 18 * s),
        steps=90,
    )
    shaft = cubic_bezier(
        (ox + 22 * s, oy + 18 * s),
        (ox + 16 * s, oy + 48 * s),
        (ox + 42 * s, oy + 78 * s),
        (ox + 70 * s, oy + 104 * s),
        steps=80,
    )
    path = curl + shaft[1:]
    draw_polyline(draw, path, stroke, white)
    draw_arrowhead(draw, path[-8], path[-1], length=28 * s, half_w=13 * s, fill=white)

    blurred = layer.filter(ImageFilter.GaussianBlur(radius=0.35 * s))
    overlay.alpha_composite(blurred)
    overlay.alpha_composite(layer)


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int, tuple[int, int, int, int]]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1], bbox


def render_banner(width: int, height: int, scale: float) -> Image.Image:
    base = make_gradient(width, height).convert("RGBA")
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    title_font = load_font(FONT_BOLD, int(round(92 * scale)))
    sub_font = load_font(FONT_REGULAR, int(round(36 * scale)))
    cta_font = load_font(FONT_BOLD, int(round(28 * scale)))
    white = (255, 255, 255, 255)

    tw, th, tb = text_size(draw, TITLE, title_font)
    sw, sh, sb = text_size(draw, SUBTITLE, sub_font)
    gap = int(round(22 * scale))
    block_h = th + gap + sh
    y0 = (height - block_h) / 2 - 6 * scale

    title_x = (width - tw) / 2 - tb[0]
    title_y = y0 - tb[1]
    draw.text((title_x, title_y), TITLE, font=title_font, fill=white)

    sub_x = (width - sw) / 2 - sb[0]
    sub_y = y0 + th + gap - sb[1]
    draw.text((sub_x, sub_y), SUBTITLE, font=sub_font, fill=white)

    cw, ch, cb = text_size(draw, CTA, cta_font)
    margin_r = int(round(96 * scale))
    margin_b = int(round(168 * scale))
    cta_x = width - margin_r - cw - cb[0]
    cta_y = height - margin_b - ch - cb[1]
    draw.text((cta_x, cta_y), CTA, font=cta_font, fill=white)

    arrow_origin = (cta_x + cw * 0.38, cta_y + ch + 8 * scale)
    draw_curly_arrow(overlay, arrow_origin, scale)

    return Image.alpha_composite(base, overlay).convert("RGB")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    banner = render_banner(2560, 854, scale=1.15)
    wide_path = OUT_DIR / "axi-banner-zh.png"
    banner.save(wide_path, "PNG", optimize=True)

    yt = make_gradient(2560, 1440)
    yt.paste(banner, (0, (1440 - 854) // 2))
    yt_path = OUT_DIR / "axi-banner-zh-youtube.png"
    yt.save(yt_path, "PNG", optimize=True)

    print(f"wrote {wide_path}")
    print(f"wrote {yt_path}")


if __name__ == "__main__":
    main()
