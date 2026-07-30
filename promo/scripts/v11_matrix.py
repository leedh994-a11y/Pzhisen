#!/usr/bin/env python3
"""Shared matrix for English promo pack v11 — V1–V5 × orders 2–6 (25 unique cuts).

Each cut keeps the matching V1–V5 persona facts from v10, but the money beat is
the Nth AI-store order (2nd…6th), with unique wording / palette / motion so
nothing fingerprints like prior packs or sibling cuts.
"""
from __future__ import annotations

ORDINAL = {2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth"}
ORDINAL_NUM = {2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th"}

# Persona locked to yesterday's V1–V5 (v10) so sequels stay linked.
BASE = {
    "v1": {
        "name": "Knox",
        "voice": "en-GB-RyanNeural",
        "owner": "solo website owner",
        "owner_alt": "a solo website owner",
        "setup_clock": "three in the afternoon",
        "setup_clock_short": "3 PM",
        "agent_clock": "three in the morning",
        "agent_clock_short": "3 AM",
        "quota": "10/50",
        "quota_words": "ten out of fifty",
        "look": "Midnight Ledger",
        "font_mode": "mono",
        "layout_family": "ledger",
        "bg": (6, 14, 22),
        "panel": (14, 28, 42),
        "accent": (16, 185, 129),
        "accent2": (250, 204, 21),
        "text": (236, 253, 245),
        "muted": (148, 163, 184),
        "danger": (248, 113, 113),
        "base_rate": "+6%",
        "base_pitch": "-2Hz",
        "gap": 0.22,
        "amounts": {2: 52, 3: 41, 4: 67, 5: 49, 6: 73},
        "order_when": {
            2: "this morning",
            3: "an hour later this morning",
            4: "another hour later",
            5: "one more hour later",
            6: "yet another hour later",
        },
    },
    "v2": {
        "name": "Weston",
        "voice": "en-AU-WilliamMultilingualNeural",
        "owner": "small-business website owner",
        "owner_alt": "a small-business owner building websites",
        "setup_clock": "four P.M.",
        "setup_clock_short": "4 PM",
        "agent_clock": "four A.M.",
        "agent_clock_short": "4 AM",
        "quota": "12/50",
        "quota_words": "twelve of fifty",
        "look": "Warm Storefront",
        "font_mode": "sans",
        "layout_family": "cards",
        "bg": (255, 244, 232),
        "panel": (255, 255, 255),
        "accent": (234, 88, 12),
        "accent2": (14, 116, 144),
        "text": (67, 20, 7),
        "muted": (120, 113, 108),
        "danger": (185, 28, 28),
        "base_rate": "-2%",
        "base_pitch": "+2Hz",
        "gap": 0.28,
        "amounts": {2: 87, 3: 94, 4: 76, 5: 103, 6: 88},
        "order_when": {
            2: "this afternoon",
            3: "an hour later this afternoon",
            4: "another hour later",
            5: "one more hour later",
            6: "yet another hour later",
        },
    },
    "v3": {
        "name": "Callum",
        "voice": "en-CA-LiamNeural",
        "owner": "agency website founder",
        "owner_alt": "an agency founder who builds sites",
        "setup_clock": "three yesterday afternoon",
        "setup_clock_short": "3 PM",
        "agent_clock": "three A.M.",
        "agent_clock_short": "3 AM",
        "quota": "10/50",
        "quota_words": "ten slash fifty",
        "look": "Ice Glass Console",
        "font_mode": "sans",
        "layout_family": "glass",
        "bg": (236, 242, 250),
        "panel": (255, 255, 255),
        "accent": (2, 132, 199),
        "accent2": (15, 23, 42),
        "text": (15, 23, 42),
        "muted": (100, 116, 139),
        "danger": (220, 38, 38),
        "base_rate": "+4%",
        "base_pitch": "+0Hz",
        "gap": 0.24,
        "amounts": {2: 47, 3: 58, 4: 44, 5: 69, 6: 53},
        "order_when": {
            2: "this afternoon",
            3: "an hour later this afternoon",
            4: "another hour later",
            5: "one more hour later",
            6: "yet another hour later",
        },
    },
    "v4": {
        "name": "Dorian",
        "voice": "en-GB-ThomasNeural",
        "owner": "enterprise website operator",
        "owner_alt": "an enterprise website operator",
        "setup_clock": "four o'clock yesterday afternoon",
        "setup_clock_short": "4 PM",
        "agent_clock": "four in the morning",
        "agent_clock_short": "4 AM",
        "quota": "12/50",
        "quota_words": "twelve remaining of fifty",
        "look": "Graphite Signal",
        "font_mode": "mono",
        "layout_family": "signal",
        "bg": (8, 8, 10),
        "panel": (22, 22, 26),
        "accent": (163, 230, 53),
        "accent2": (244, 244, 245),
        "text": (250, 250, 250),
        "muted": (161, 161, 170),
        "danger": (251, 113, 133),
        "base_rate": "-5%",
        "base_pitch": "-4Hz",
        "gap": 0.32,
        "amounts": {2: 87, 3: 112, 4: 79, 5: 95, 6: 121},
        "order_when": {
            2: "this morning",
            3: "an hour later this morning",
            4: "another hour later",
            5: "one more hour later",
            6: "yet another hour later",
        },
    },
    "v5": {
        "name": "Everett",
        "voice": "en-US-RogerNeural",
        "owner": "independent web-shop owner",
        "owner_alt": "an independent web-shop owner",
        "setup_clock": "three P.M.",
        "setup_clock_short": "3 PM",
        "agent_clock": "three A.M.",
        "agent_clock_short": "3 AM",
        "quota": "10/50",
        "quota_words": "ten of fifty",
        "look": "Editorial Alert",
        "font_mode": "serif",
        "layout_family": "editorial",
        "bg": (254, 240, 240),
        "panel": (255, 255, 255),
        "accent": (185, 28, 28),
        "accent2": (28, 25, 23),
        "text": (28, 25, 23),
        "muted": (87, 83, 78),
        "danger": (153, 27, 27),
        "base_rate": "+9%",
        "base_pitch": "-6Hz",
        "gap": 0.18,
        "amounts": {2: 47, 3: 55, 4: 62, 5: 48, 6: 74},
        "order_when": {
            2: "this morning",
            3: "an hour later this morning",
            4: "another hour later",
            5: "one more hour later",
            6: "yet another hour later",
        },
    },
}

# Per-order voice micro-shifts (audio fingerprint diversity within same persona).
RATE_SHIFT = {2: 0, 3: -2, 4: +3, 5: -4, 6: +5}
PITCH_SHIFT = {2: 0, 3: +2, 4: -3, 5: +4, 6: -2}

# Unique scene order templates (anti-dupe motion fingerprints).
BEAT_TEMPLATES = {
    2: [
        ("title", 0.00, 0.05),
        ("revenue", 0.05, 0.20),
        ("site", 0.20, 0.30),
        ("setup", 0.30, 0.44),
        ("agents", 0.44, 0.56),
        ("ops", 0.56, 0.68),
        ("urgency", 0.68, 0.90),
        ("success", 0.90, 1.00),
    ],
    3: [
        ("revenue", 0.00, 0.16),
        ("site", 0.16, 0.26),
        ("setup", 0.26, 0.40),
        ("ops", 0.40, 0.52),
        ("agents", 0.52, 0.64),
        ("title", 0.64, 0.70),
        ("urgency", 0.70, 0.90),
        ("success", 0.90, 1.00),
    ],
    4: [
        ("site", 0.00, 0.08),
        ("revenue", 0.08, 0.22),
        ("agents", 0.22, 0.36),
        ("setup", 0.36, 0.48),
        ("ops", 0.48, 0.60),
        ("urgency", 0.60, 0.84),
        ("title", 0.84, 0.90),
        ("success", 0.90, 1.00),
    ],
    5: [
        ("title", 0.00, 0.06),
        ("revenue", 0.06, 0.18),
        ("ops", 0.18, 0.30),
        ("site", 0.30, 0.40),
        ("setup", 0.40, 0.54),
        ("agents", 0.54, 0.66),
        ("urgency", 0.66, 0.88),
        ("success", 0.88, 1.00),
    ],
    6: [
        ("revenue", 0.00, 0.14),
        ("setup", 0.14, 0.28),
        ("agents", 0.28, 0.40),
        ("site", 0.40, 0.50),
        ("ops", 0.50, 0.62),
        ("urgency", 0.62, 0.86),
        ("success", 0.86, 0.94),
        ("title", 0.94, 1.00),
    ],
}

SUBTITLE = {
    "v1": {2: ("&H00D1FAE5", 36, 150), 3: ("&H00A7F3D0", 35, 158), 4: ("&H00FEF08A", 37, 142), 5: ("&H00BBF7D0", 34, 165), 6: ("&H00E0F2FE", 38, 148)},
    "v2": {2: ("&H00FFF7ED", 35, 168), 3: ("&H00FFEDD5", 36, 155), 4: ("&H00FEF3C7", 34, 172), 5: ("&H00ECFEFF", 37, 145), 6: ("&H00FFE4E6", 35, 160)},
    "v3": {2: ("&H00E0F2FE", 37, 140), 3: ("&H00DBEAFE", 36, 152), 4: ("&H00F0F9FF", 35, 166), 5: ("&H00ECFDF5", 38, 138), 6: ("&H00FDF4FF", 34, 170)},
    "v4": {2: ("&H00ECFCCB", 34, 132), 3: ("&H00D9F99D", 36, 148), 4: ("&H00F7FEE7", 35, 160), 5: ("&H00E0E7FF", 37, 144), 6: ("&H00FEF9C3", 38, 156)},
    "v5": {2: ("&H00FEE2E2", 38, 175), 3: ("&H00FECACA", 36, 160), 4: ("&H00FEF2F2", 35, 148), 5: ("&H00FFEDD5", 37, 168), 6: ("&H00E0F2FE", 34, 152)},
}

DRIFT = {
    2: ["center", "up", "right", "center", "left", "up", "center", "right"],
    3: ["up", "left", "center", "right", "up", "center", "left", "up"],
    4: ["left", "center", "up", "right", "center", "up", "left", "center"],
    5: ["right", "up", "center", "left", "up", "right", "center", "up"],
    6: ["center", "right", "up", "left", "center", "up", "right", "center"],
}


def _shift_rate(base: str, delta: int) -> str:
    sign = 1 if base.startswith("+") else -1
    val = int(base.strip("+%").strip("-%").rstrip("%") or "0") * (1 if "+" in base[:1] or base.startswith("+") else -1)
    if base.startswith("+"):
        val = int(base[1:-1])
    elif base.startswith("-"):
        val = -int(base[1:-1])
    else:
        val = 0
    val += delta
    return f"{val:+d}%"


def _shift_pitch(base: str, delta: int) -> str:
    if base.startswith("+"):
        val = int(base[1:].replace("Hz", ""))
    elif base.startswith("-"):
        val = -int(base[1:].replace("Hz", ""))
    else:
        val = 0
    val += delta
    return f"{val:+d}Hz"


def money_words(n: int) -> str:
    # keep TTS natural for common amounts (supports up to 199)
    ones = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    teens = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
    if n < 10:
        return ones[n]
    if n < 20:
        return teens[n - 10]
    if n < 100:
        t, o = divmod(n, 10)
        return tens[t] + (f"-{ones[o]}" if o else "")
    # 100–199
    rest = n - 100
    if rest == 0:
        return "one hundred"
    return "one hundred " + money_words(rest)


def build_cues(vid: str, order: int) -> list[str]:
    b = BASE[vid]
    amt = b["amounts"][order]
    when = b["order_when"][order]
    ord_w = ORDINAL[order]
    ord_n = ORDINAL_NUM[order]
    dollars = money_words(amt)

    # Five persona-specific phrasings so sibling order cuts don't share templates.
    if vid == "v1":
        a1 = f"Yesterday at {b['setup_clock']}, {b['owner_alt']} used Pzhisen to do just three things: enter a product name, upload three photos, and connect payments."
        a1b = f"{when.capitalize()}, his AI store automatically closed the {ord_w} order — {dollars} dollars."
        if order >= 3:
            a1b = f"Then {when}, the AI store closed the {ord_w} order for {dollars} dollars — still fully automatic."
        a2 = "Across the whole process, he never touched a single line of code, and he never wrote a single line of marketing copy."
        a2b = f"Every ad placement and every customer-service reply was handled by Pzhisen AI agents at {b['agent_clock']} — fully automatic."
        a2c = "That is the point of pzhisen.online: you set it up once, then the agents keep selling while you sleep."
        a3 = f"Today's remaining free seats: {b['quota_words']}."
        a3b = "This AI agent can onboard only fifty new stores per day. If you want to wake up to orders, tap the link below and claim today's free test."
        a3c = "When the seats are gone, you wait until next month."
    elif vid == "v2":
        a1 = f"Yesterday at {b['setup_clock']}, {b['owner_alt']} ran Pzhisen through three steps only: type the product name, upload three images, and bind payment."
        a1b = f"{when.capitalize()}, the AI shop rang up the {ord_w} order for {dollars} dollars — no manual push."
        if order >= 3:
            a1b = f"{when.capitalize()}, order number {order} hit for {dollars} dollars — still no manual push."
        a2 = "He did not edit code. He did not draft ad copy. Not once."
        a2b = f"Ads and customer replies were completed by Pzhisen AI agents at {b['agent_clock']} on autopilot."
        a2c = "Open pzhisen.online and you get the same hands-off loop: store up, agents selling overnight."
        a3 = f"Seats left today: {b['quota_words']}."
        a3b = "The agent can serve fifty new stores daily. Want orders waiting when you wake? Hit the link below for today's free test slot."
        a3c = "Miss it, and the next window opens next month."
    elif vid == "v3":
        a1 = f"At {b['setup_clock']}, {b['owner_alt']} used Pzhisen for three actions: product name in, three photos up, payment linked."
        a1b = f"By {when}, the AI storefront booked its {ord_w} paid order at {dollars} dollars."
        if order >= 3:
            a1b = f"{when.capitalize()}, paid order {ord_n} landed at {dollars} dollars on the AI storefront."
        a2 = "Zero code from him. Zero sales copy from him."
        a2b = f"Pzhisen AI agents ran ads and answered buyers at {b['agent_clock']} without anyone watching the screen."
        a2c = "That workflow is live on pzhisen.online — launch light, let agents work the night shift."
        a3 = f"Free tests remaining today: {b['quota_words']}."
        a3b = "Hard cap: fifty new stores a day. If you want to sleep and still see orders, tap below and grab today's free trial seat."
        a3c = "Once filled, new seats wait until next month."
    elif vid == "v4":
        a1 = f"{b['setup_clock'].capitalize()}: {b['owner_alt']} used Pzhisen to complete three moves — name the product, upload three pictures, bind checkout."
        a1b = f"{when.capitalize()} the AI store recorded the {ord_w} sale: {dollars} U.S. dollars, closed automatically."
        if order >= 3:
            a1b = f"{when.capitalize()} sale {order} posted: {dollars} U.S. dollars, closed automatically."
        a2 = "No code was written. No marketing text was authored by a human."
        a2b = f"Advertising and support replies were executed by Pzhisen AI agents at {b['agent_clock']}, unsupervised."
        a2c = "Visit pzhisen.online for the same minimal setup and overnight AI selling."
        a3 = f"Quota on the board today: {b['quota_words']}."
        a3b = "Only fifty new shops can be onboarded each day. Tap the link under this video for today's free test before it disappears."
        a3c = "After the quota resets next month is your next chance."
    else:  # v5
        a1 = f"Yesterday, {b['setup_clock']}: {b['owner_alt']} used Pzhisen for three steps only — product name, three image uploads, payment binding."
        a1b = f"{when.capitalize()} the AI store auto-printed the {ord_w} order for {dollars} dollars."
        if order >= 3:
            a1b = f"{when.capitalize()} the AI store auto-printed order {order} for {dollars} dollars."
        a2 = "He never coded. He never wrote copy."
        a2b = f"All ads and all customer replies were finished by Pzhisen AI agents at {b['agent_clock']} while he slept."
        a2c = "That is exactly what pzhisen.online is built to do: tiny setup, nonstop AI selling."
        a3 = f"Today left: {b['quota_words']} free seats."
        a3b = "Daily hard limit — fifty new stores. Want to wake up to orders? Tap the link below and lock today's free test."
        a3c = "Seats gone means waiting until next month."

    return [a1, a1b, a2, a2b, a2c, a3, a3b, a3c]


def palette_for(vid: str, order: int) -> dict:
    """Slight hue/value shifts per order so sibling cuts don't share identical grades."""
    b = BASE[vid]
    shift = (order - 2) * 8
    def nudge(rgb, s):
        return tuple(max(0, min(255, c + (s if i == order % 3 else -s // 2))) for i, c in enumerate(rgb))
    return {
        "bg": nudge(b["bg"], shift // 2),
        "panel": nudge(b["panel"], shift // 3),
        "accent": nudge(b["accent"], shift),
        "accent2": nudge(b["accent2"], -shift // 2),
        "text": b["text"],
        "muted": b["muted"],
        "danger": nudge(b["danger"], shift // 4),
    }


def all_cuts() -> list[dict]:
    cuts = []
    for vid in ("v1", "v2", "v3", "v4", "v5"):
        b = BASE[vid]
        for order in (2, 3, 4, 5, 6):
            cid = f"{vid}o{order}"
            primary, fs, mv = SUBTITLE[vid][order]
            cuts.append(
                {
                    "id": cid,
                    "vid": vid,
                    "order": order,
                    "name": b["name"],
                    "title": f"{b['name']} · {b['look']} · Order {ORDINAL_NUM[order]}",
                    "voice": b["voice"],
                    "rate": _shift_rate(b["base_rate"], RATE_SHIFT[order]),
                    "pitch": _shift_pitch(b["base_pitch"], PITCH_SHIFT[order]),
                    "gap": b["gap"] + (order - 2) * 0.02,
                    "cues": build_cues(vid, order),
                    "amount": b["amounts"][order],
                    "amount_str": f"${b['amounts'][order]}",
                    "quota": b["quota"],
                    "order_when": b["order_when"][order],
                    "ordinal": ORDINAL[order],
                    "ordinal_num": ORDINAL_NUM[order],
                    "owner": b["owner"],
                    "setup_clock_short": b["setup_clock_short"],
                    "agent_clock_short": b["agent_clock_short"],
                    "look": b["look"],
                    "font_mode": b["font_mode"],
                    "layout_family": b["layout_family"],
                    "colors": palette_for(vid, order),
                    "beats": BEAT_TEMPLATES[order],
                    "subtitle_fs": fs,
                    "subtitle_margin_v": mv,
                    "subtitle_primary": primary,
                    "drift_cycle": DRIFT[order],
                    "zoom_alt": order % 2 == 0,
                    "zoom_speed": 0.0009 + order * 0.00007 + (hash(vid) % 5) * 0.00002,
                    "layout_variant": order,  # 2..6 drives unique UI chrome
                }
            )
    return cuts


if __name__ == "__main__":
    cuts = all_cuts()
    print(f"{len(cuts)} cuts")
    for c in cuts:
        print(c["id"], c["name"], c["amount_str"], c["quota"], c["rate"], c["pitch"])
