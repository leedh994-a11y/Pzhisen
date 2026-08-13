#!/usr/bin/env python3
"""Recreate the AI channel banner in English (teal → violet gradient)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "promo" / "banners"

# Original: dark teal → deep blue → electric violet
STOPS = (
    (0.00, (8, 96, 111)),
    (0.42, (18, 70, 150)),
    (0.72, (40, 45, 220)),
    (1.00, (60, 33, 255)),
)

FONT_BOLD = "/usr/share/fonts/truetype/macos/Inter-Bold.ttf"
FONT_SEMIBOLD = "/usr/share/fonts/truetype/macos/Inter-SemiBold.ttf"

LINE1 = "Sharing AI, AI agents, and everything new"
LINE2 = "related to AI"
CTA = "Follow me!"


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


def draw_curly_arrow(overlay: Image.Image, origin: tuple[float, float], scale: float) -> None:
    """Hand-drawn curl that then points straight down, matching the original CTA."""
    ox, oy = origin
    s = scale
    layer = Image.new("RGBA", overlay.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    white = (255, 255, 255, 255)
    stroke = max(4.5, 6.0 * s)

    # Small open flourish (not a closed circle), then a mostly vertical shaft.
    curl = cubic_bezier(
        (ox - 18 * s, oy + 10 * s),
        (ox - 22 * s, oy - 16 * s),
        (ox + 28 * s, oy - 18 * s),
        (ox + 16 * s, oy + 14 * s),
        steps=90,
    )
    shaft = cubic_bezier(
        (ox + 16 * s, oy + 14 * s),
        (ox + 8 * s, oy + 32 * s),
        (ox + 4 * s, oy + 70 * s),
        (ox + 3 * s, oy + 108 * s),
        steps=80,
    )
    path = curl + shaft[1:]
    draw_polyline(draw, path, stroke, white)

    tip_x, tip_y = path[-1]
    tip_y += 2 * s
    head_len = 26 * s
    head_w = 16 * s
    left = (tip_x - head_w, tip_y - head_len * 0.72)
    right = (tip_x + head_w, tip_y - head_len * 0.72)
    tip = (tip_x, tip_y + head_len * 0.28)
    draw.polygon([left, tip, right], fill=white)

    blurred = layer.filter(ImageFilter.GaussianBlur(radius=0.35 * s))
    overlay.alpha_composite(blurred)
    overlay.alpha_composite(layer)


def centered_text_block(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    font: ImageFont.FreeTypeFont,
    canvas_size: tuple[int, int],
    fill: tuple[int, int, int, int],
    line_gap: int,
    y_offset: int = 0,
) -> None:
    w, h = canvas_size
    sizes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    heights = [b[3] - b[1] for b in sizes]
    total_h = sum(heights) + line_gap * (len(lines) - 1)
    y = (h - total_h) / 2 + y_offset
    for line, bbox, lh in zip(lines, sizes, heights):
        tw = bbox[2] - bbox[0]
        x = (w - tw) / 2 - bbox[0]
        draw.text((x, y - bbox[1]), line, font=font, fill=fill)
        y += lh + line_gap


def render_banner(width: int, height: int, scale: float) -> Image.Image:
    base = make_gradient(width, height).convert("RGBA")
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    title_size = int(round(72 * scale))
    cta_size = int(round(28 * scale))
    title_font = ImageFont.truetype(FONT_BOLD, title_size)
    cta_font = ImageFont.truetype(FONT_SEMIBOLD, cta_size)

    centered_text_block(
        draw,
        [LINE1, LINE2],
        title_font,
        (width, height),
        (255, 255, 255, 255),
        line_gap=int(round(18 * scale)),
        y_offset=int(round(-8 * scale)),
    )

    # CTA in the bottom-right, with padding matching the original
    cta_bbox = draw.textbbox((0, 0), CTA, font=cta_font)
    cta_w = cta_bbox[2] - cta_bbox[0]
    cta_h = cta_bbox[3] - cta_bbox[1]
    margin_r = int(round(86 * scale))
    margin_b = int(round(168 * scale))
    cta_x = width - margin_r - cta_w - cta_bbox[0]
    cta_y = height - margin_b - cta_h - cta_bbox[1]
    draw.text((cta_x, cta_y), CTA, font=cta_font, fill=(255, 255, 255, 255))

    arrow_origin = (
        cta_x + cta_w * 0.42,
        cta_y + cta_h + 10 * scale,
    )
    draw_curly_arrow(overlay, arrow_origin, scale)

    return Image.alpha_composite(base, overlay).convert("RGB")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Match the original wide banner (~3:1)
    banner = render_banner(2560, 854, scale=1.15)
    wide_path = OUT_DIR / "ai-channel-banner-en.png"
    banner.save(wide_path, "PNG", optimize=True)

    # YouTube channel art: 2560×1440 with the same strip in the safe center.
    yt = make_gradient(2560, 1440)
    yt.paste(banner, (0, (1440 - 854) // 2))
    yt_path = OUT_DIR / "ai-channel-banner-en-youtube.png"
    yt.save(yt_path, "PNG", optimize=True)

    print(f"wrote {wide_path}")
    print(f"wrote {yt_path}")


if __name__ == "__main__":
    main()
