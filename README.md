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

## NEW English 5-pack v9 (unique — not prior versions)

Brand-new vertical cuts with **different presenters, scripts, voices, pacing, and per-video website UI screenshots** from every previous pack (v1–v8).

| Version | Presenter | Look | UI style | File |
|---|---|---|---|---|
| V1 | Fletcher | Chicago river loft | Indigo-amber | `promo/versions-en-v9/pzhisen-promo-en9-v1-vertical.mp4` |
| V2 | Camden | Austin creative studio | Cactus-terracotta | `promo/versions-en-v9/pzhisen-promo-en9-v2-vertical.mp4` |
| V3 | Sterling | NYC Midtown penthouse | Platinum-crimson | `promo/versions-en-v9/pzhisen-promo-en9-v3-vertical.mp4` |
| V4 | Beckett | Portland glass atrium | Forest-mint | `promo/versions-en-v9/pzhisen-promo-en9-v4-vertical.mp4` |
| V5 | Harlan | Phoenix desert modern | Sand-turquoise | `promo/versions-en-v9/pzhisen-promo-en9-v5-vertical.mp4` |

- Format: 1080×1920 · English burned-in subtitles · ~1:45–2:20 each
- Players: `promo/promo-versions-en9.html`
- Mobile download page: `promo/download-videos-en9.html`
- Phone ZIP (all 5, ~83MB): https://github.com/leedh994-a11y/Pzhisen/raw/main/promo/versions-en-v9/pzhisen-promo-en9-5videos-vertical.zip

Rebuild:

```bash
cd promo
python3 scripts/make_narration_versions_en_v9.py
python3 scripts/build_versions_vertical_en_v9.py all
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
