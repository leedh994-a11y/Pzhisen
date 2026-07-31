# Pzhisen promo videos

## Chinese edit: Polsia → Pzhisen, founder → Bob

Edited vertical cut from the shared WeChat/Tencent source clip:

- **手机一键下载（中文剪辑 · 约48MB）：** https://github.com/leedh994-a11y/Pzhisen/raw/main/promo/versions-zh-edit/pzhisen-bob-from-polsia-vertical.mp4
- **手机一键下载（英文旁白版 · 约35MB）：** https://github.com/leedh994-a11y/Pzhisen/raw/main/promo/versions-zh-edit/pzhisen-bob-english-vertical.mp4
- English cut: English TTS + English captions; closing line includes `https://pzhisen.online`
- Outputs: `promo/versions-zh-edit/pzhisen-bob-from-polsia-vertical.mp4`, `promo/versions-zh-edit/pzhisen-bob-english-vertical.mp4`
- Download pages: `promo/download-polsia-edit.html`, `promo/download-polsia-edit-en.html`
- Rebuild ZH names: `python3 promo/scripts/edit_polsia_to_pzhisen_bob.py --src <source.mp4> --out promo/versions-zh-edit/pzhisen-bob-from-polsia-vertical.mp4`
- Rebuild EN narration: `python3 promo/scripts/make_polsia_edit_english.py --src <zh-edited.mp4> --out promo/versions-zh-edit/pzhisen-bob-english-vertical.mp4`

## NEW English 25-pack v11 — Orders 2–6 sequels (V1–V5 × 5)

Continues yesterday’s v10 personas. For **each** of V1–V5, five new vertical cuts:

| Sequel | Story beat |
|---|---|
| o2 | Today AM/PM — AI store closes the **2nd** order |
| o3 | An hour later — **3rd** order |
| o4 | Another hour later — **4th** order |
| o5 | One more hour later — **5th** order |
| o6 | Yet another hour later — **6th** order |

Same 3-act structure (money → zero-code ops → seat scarcity). Unique scripts, voice micro-shifts, color grades, motion, and pzhisen.online frames vs v10 and vs each sibling.

| Line | Persona | Quota | Files |
|---|---|---|---|
| V1 | Knox | 10/50 | `promo/versions-en-v11/pzhisen-promo-en11-v1o{2–6}-vertical.mp4` |
| V2 | Weston | 12/50 | `…-v2o{2–6}-vertical.mp4` |
| V3 | Callum | 10/50 | `…-v3o{2–6}-vertical.mp4` |
| V4 | Dorian | 12/50 | `…-v4o{2–6}-vertical.mp4` |
| V5 | Everett | 10/50 | `…-v5o{2–6}-vertical.mp4` |

- Players: `promo/promo-versions-en11.html`
- Mobile download (25 links + 5 ZIPs): `promo/download-videos-en11.html`
- Per-line ZIP (~24–28MB each): `promo/versions-en-v11/pzhisen-promo-en11-vN-orders2to6-vertical.zip`

Rebuild:

```bash
cd promo
python3 scripts/generate_assets_orders_v11.py
python3 scripts/make_narration_versions_en_v11.py
python3 scripts/build_versions_vertical_en_v11.py all j2
```

## Previous English 5-pack v10 — Results + Urgency (3-act · first order)

Brand-new vertical cuts built for Facebook/Reels duplicate avoidance. Same core claims, **different scripts, voices, locales, pacing, color systems, and per-video pzhisen.online UI shots** vs every prior pack (v1–v8).

**Structure (all 5):**
1. **Act 1 — money result:** backend earnings / first AI-store order ($47 or $87)
2. **Act 2 — minimal ops:** product name + 3 photos + payments; no code / no copy; AI ads + support at 3AM or 4AM
3. **Act 3 — urgency:** remaining seats **10/50** or **12/50**; free test CTA; next month if full

| Version | Voice | Look | Amount / quota | File |
|---|---|---|---|---|
| V1 | Knox · en-GB-Ryan | Midnight Ledger (emerald) | $47 · 10/50 | `promo/versions-en-v10/pzhisen-promo-en10-v1-vertical.mp4` |
| V2 | Weston · en-AU-William | Warm Storefront (orange) | $87 · 12/50 | `promo/versions-en-v10/pzhisen-promo-en10-v2-vertical.mp4` |
| V3 | Callum · en-CA-Liam | Ice Glass Console | $47 · 10/50 | `promo/versions-en-v10/pzhisen-promo-en10-v3-vertical.mp4` |
| V4 | Dorian · en-GB-Thomas | Graphite Signal (lime) | $87 · 12/50 | `promo/versions-en-v10/pzhisen-promo-en10-v4-vertical.mp4` |
| V5 | Everett · en-US-Roger | Editorial Alert (crimson) | $47 · 10/50 | `promo/versions-en-v10/pzhisen-promo-en10-v5-vertical.mp4` |

- Format: 1080×1920 · English burned-in subtitles · ~46–55s each
- Players: `promo/promo-versions-en10.html`
- Mobile download page: `promo/download-videos-en10.html`
- Phone ZIP (all 5, ~73MB): https://github.com/leedh994-a11y/Pzhisen/raw/main/promo/versions-en-v10/pzhisen-promo-en10-5videos-vertical.zip

Rebuild:

```bash
cd promo
python3 scripts/generate_assets_results_urgency_v10.py   # optional refresh of procedural frames
python3 scripts/make_narration_versions_en_v10.py
python3 scripts/build_versions_vertical_en_v10.py all
```

## Previous English 5-pack v8 (kept for reference)

Mason / Parker / Bennett / Quinn / Donovan — `promo/versions-en-v8/`  
Page: `promo/promo-versions-en8.html`

## Previous English 5-pack v7 (kept for reference)

Chandler / Brooks / Hayden / Reid / Nash — `promo/versions-en-v7/`  
Page: `promo/promo-versions-en7.html`

## Previous English 5-pack v6 (kept for reference)

Austin / Garrett / Wesley / Spencer / Elliot — `promo/versions-en-v6/`  
Page: `promo/promo-versions-en6.html`

## Previous English 5-pack v5 (kept for reference)

Blake / Hunter / Tristan / Miles / Connor — `promo/versions-en-v5/`  
Page: `promo/promo-versions-en5.html`

## Previous English 5-pack v4 (kept for reference)

Derek / Cole / Vincent / Grant / Logan — `promo/versions-en-v4/`  
Page: `promo/promo-versions-en4.html`

## Previous English 5-pack v3 (kept for reference)

Brandon / Trevor / Christopher / Adrian / Preston — `promo/versions-en-v3/`  
Page: `promo/promo-versions-en3.html`

## Previous English 5-pack v2 (kept for reference)

Ryan / Marcus / Ethan / Noah / Jackson — `promo/versions-en-v2/`  
Page: `promo/promo-versions-en2.html`

## Previous English 5-pack v1 (kept for reference)

Michael / David / James / Carlos / William — `promo/versions/`  
Page: `promo/promo-versions-en.html`

## Twitter / X AI Agent (`x-multi`)

Real tweet-posting agent under `x-multi-agent/` (Google Gemini + browser automation via npm `x-multi`).

```bash
cd x-multi-agent
npm install
cp .env.example .env   # set GEMINI_API_KEY
npm run setup
npm run login          # first time: manual Twitter login in browser
npm run tweet "your topic"
```

See `x-multi-agent/README.md` for full setup, HTTP API (`npm run server`), and troubleshooting.

