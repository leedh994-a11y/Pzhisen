#!/usr/bin/env python3
"""Four color variants of the English AI channel banner (layout unchanged)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_ai_channel_banner_en import make_gradient, render_banner

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "promo" / "banners"

# Same layout/text as the teal original; only the gradient changes.
PALETTES: dict[str, tuple[tuple[float, tuple[int, int, int]], ...]] = {
    "sunset": (
        (0.00, (140, 28, 19)),
        (0.38, (194, 65, 12)),
        (0.70, (234, 88, 12)),
        (1.00, (245, 158, 11)),
    ),
    "magenta": (
        (0.00, (76, 5, 90)),
        (0.38, (126, 34, 206)),
        (0.70, (192, 38, 211)),
        (1.00, (219, 39, 119)),
    ),
    "forest": (
        (0.00, (6, 78, 59)),
        (0.38, (21, 128, 61)),
        (0.70, (5, 150, 105)),
        (1.00, (34, 197, 94)),
    ),
    "graphite": (
        (0.00, (15, 23, 42)),
        (0.38, (30, 41, 59)),
        (0.70, (51, 65, 85)),
        (1.00, (71, 85, 105)),
    ),
}


def write_variant(name: str, stops: tuple) -> tuple[Path, Path]:
    banner = render_banner(2560, 854, scale=1.15, stops=stops)
    wide_path = OUT_DIR / f"ai-channel-banner-en-{name}.png"
    banner.save(wide_path, "PNG", optimize=True)

    yt = make_gradient(2560, 1440, stops)
    yt.paste(banner, (0, (1440 - 854) // 2))
    yt_path = OUT_DIR / f"ai-channel-banner-en-{name}-youtube.png"
    yt.save(yt_path, "PNG", optimize=True)
    return wide_path, yt_path


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, stops in PALETTES.items():
        wide_path, yt_path = write_variant(name, stops)
        print(f"wrote {wide_path}")
        print(f"wrote {yt_path}")


if __name__ == "__main__":
    main()
