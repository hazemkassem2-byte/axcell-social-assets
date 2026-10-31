"""Render an Axcell social card (1080x1350 JPEG, Instagram 4:5) from a post's hook.

Usage:
  python3 render_card.py --lang ar|en --series "Rulebook" --hook "..." --out cards/2026-11/slug.jpg

Brand: navy #0A2A43 background, white type, ONE red accent (#C8102E) rule,
Tajawal for Arabic, Inter for English, white Axcell wordmark bottom-right,
mandatory footer "info@axcellservice.com · axcellservice.com" bottom-left.
Requires Pillow built with libraqm (for correct Arabic shaping).
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, features

HERE = Path(__file__).resolve().parent
B = HERE / "brand"
NAVY, RED, WHITE = (10, 42, 67), (200, 16, 46), (255, 255, 255)
W, H, M = 1080, 1350, 96  # canvas and outer margin

SERIES_AR = {
    "Rulebook": "دليل القواعد", "Owner Dashboard": "لوحة صاحب القرار",
    "Benchmark Process": "العملية النموذجية", "Automation Lab": "مختبر الأتمتة المالية",
    "CFO Teardown": "تشريح مالي", "Investor-Ready": "جاهز للمستثمر",
    "Field Case": "حالة من الميدان", "Remote Finance Team": "فريق مالي عن بُعد",
}


def font(lang, bold, size):
    if lang == "ar":
        return ImageFont.truetype(str(B / ("Tajawal-Bold.ttf" if bold else "Tajawal-Regular.ttf")), size,
                                  layout_engine=ImageFont.Layout.RAQM)
    f = ImageFont.truetype(str(B / "Inter.ttf"), size)
    try:
        f.set_variation_by_axes([14, 700 if bold else 400])  # opsz, wght
    except Exception:
        pass
    return f


def text_kwargs(lang):
    return {"direction": "rtl", "language": "ar"} if lang == "ar" else {}


def wrap(draw, text, fnt, maxw, lang):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt, **text_kwargs(lang)) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render(lang, series, hook, out):
    if lang == "ar" and not features.check("raqm"):
        raise SystemExit("Pillow lacks libraqm: Arabic would render incorrectly.")
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    kw = text_kwargs(lang)
    rtl = lang == "ar"
    x_edge = W - M if rtl else M
    anchor_l = "ra" if rtl else "la"

    # Series label + the single red accent rule
    label = SERIES_AR.get(series, series) if rtl else series.upper()
    lf = font(lang, False, 34 if rtl else 28)
    d.text((x_edge, M + 10), label, font=lf, fill=WHITE, anchor=anchor_l, **kw)
    ry = M + 76
    d.rectangle([x_edge - 96, ry, x_edge, ry + 5] if rtl else [x_edge, ry, x_edge + 96, ry + 5], fill=RED)

    # Hook: largest size that fits in at most 6 lines within the text block
    maxw, top, bottom = W - 2 * M, ry + 110, H - 330
    for size in (104, 96, 88, 80, 72, 66, 60, 54):
        hf = font(lang, True, size)
        lines = wrap(d, hook, hf, maxw, lang)
        lh = int(size * (1.38 if rtl else 1.16))
        if len(lines) <= 6 and len(lines) * lh <= bottom - top:
            break
    y = top
    for ln in lines:
        d.text((x_edge, y), ln, font=hf, fill=WHITE, anchor=anchor_l, **kw)
        y += lh

    # Byline
    bf = font(lang, False, 32 if rtl else 28)
    by = "حازم قاسم · أكسل" if rtl else "Hazem Kassem · Axcell"
    d.text((x_edge, H - 250), by, font=bf, fill=WHITE, anchor=anchor_l, **kw)

    # Wordmark bottom-right, footer bottom-left (mandatory)
    logo = Image.open(B / "axcell_wordmark_white.png")
    lw = 230
    logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    img.paste(logo, (W - M - lw, H - M - logo.height), logo)
    ff = font("en", False, 24)
    d.text((M, H - M - 6), "info@axcellservice.com  ·  axcellservice.com", font=ff, fill=WHITE, anchor="ls")

    Path(out).parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "JPEG", quality=90, optimize=True)
    return out


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--lang", required=True, choices=["ar", "en"])
    p.add_argument("--series", required=True)
    p.add_argument("--hook", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    print(render(a.lang, a.series, a.hook, a.out))
