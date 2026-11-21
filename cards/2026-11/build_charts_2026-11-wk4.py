"""Charts for the week 22-28 Nov 2026 (1080x1350, Axcell brand).

- 2026-11-25-en-chart.png: PwC Global Investor Survey 2025, Middle East findings, figure 9.
- 2026-11-28-ar-chart.png: MISA monthly indicators (July 2026), SME credit facilities (source SAMA).

Bars are drawn with matplotlib; headline/takeaway text with Pillow + libraqm so Arabic shapes correctly.
Every plotted value is copied from the source (see Sources in the Content Calendar rows).
"""
import io
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[2]
B = REPO / "brand"
OUT = Path(__file__).resolve().parent
NAVY, RED, WHITE, GREY = (10, 42, 67), (200, 16, 46), (255, 255, 255), (44, 44, 44)
HNAVY, HRED, HGREY, HMID, HLIGHT = "#0A2A43", "#C8102E", "#2C2C2C", "#8A97A6", "#E6EAEF"
W, H, M = 1080, 1350, 80
INTER = FontProperties(fname=str(B / "Inter.ttf"))


def pil_font(lang, bold, size):
    if lang == "ar":
        return ImageFont.truetype(str(B / ("Tajawal-Bold.ttf" if bold else "Tajawal-Regular.ttf")), size,
                                  layout_engine=ImageFont.Layout.RAQM)
    f = ImageFont.truetype(str(B / "Inter.ttf"), size)
    try:
        f.set_variation_by_axes([14, 700 if bold else 400])
    except Exception:
        pass
    return f


def kw(lang):
    return {"direction": "rtl", "language": "ar"} if lang == "ar" else {}


def wrap(d, text, f, maxw, lang):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f, **kw(lang)) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def block(d, x, y, text, f, maxw, lang, fill, lh):
    rtl = lang == "ar"
    for ln in wrap(d, text, f, maxw, lang):
        d.text((x, y), ln, font=f, fill=fill, anchor="ra" if rtl else "la", **kw(lang))
        y += lh
    return y


def fig_to_img(fig, w, h):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGB").resize((w, h), Image.LANCZOS)


def frame(lang, label, headline, sub):
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    rtl = lang == "ar"
    x = W - M if rtl else M
    d.text((x, M), label, font=pil_font(lang, False, 30 if rtl else 26), fill=WHITE,
           anchor="ra" if rtl else "la", **kw(lang))
    d.rectangle([x - 96, M + 52, x, M + 57] if rtl else [x, M + 52, x + 96, M + 57], fill=RED)
    y = block(d, x, M + 90, headline, pil_font(lang, True, 58 if rtl else 54), W - 2 * M, lang, WHITE,
              82 if rtl else 66)
    y = block(d, x, y + 10, sub, pil_font(lang, False, 30 if rtl else 28), W - 2 * M, lang, WHITE,
              44 if rtl else 38)
    return img, d, y


def footer(img, d, lang, sowhat_label, sowhat, source):
    rtl = lang == "ar"
    x = W - M if rtl else M
    y0 = H - 330
    d.rectangle([M, y0, W - M, y0 + 2], fill=WHITE)
    y = y0 + 22
    y = block(d, x, y, sowhat_label, pil_font(lang, True, 30 if rtl else 26), W - 2 * M, lang, WHITE, 44)
    block(d, x, y, sowhat, pil_font(lang, False, 30 if rtl else 27), W - 2 * M, lang, WHITE, 44 if rtl else 38)
    sf = pil_font("en", False, 20)
    src = wrap(d, source, sf, W - 2 * M - 250, "en")
    yy = H - 90 - 26 * len(src)
    for ln in src:
        d.text((M, yy), ln, font=sf, fill=WHITE, anchor="la")
        yy += 26
    d.text((M, H - 52), "axcellservice.com", font=pil_font("en", True, 22), fill=WHITE, anchor="ls")
    logo = Image.open(B / "axcell_wordmark_white.png")
    lw = 200
    logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    img.paste(logo, (W - M - lw, H - M - logo.height + 18), logo)


def en_chart():
    # PwC GIS 2025 ME findings, figure 9 (NET "to a very large/large extent")
    cats = ["Financial statements\nand notes", "Investor-focused\ncommunications", "Dialogue with\nthe company",
            "Narrative reporting\n(non-sustainability)", "Press releases /\ncompany news"]
    me = [73, 68, 54, 53, 37]
    gl = [69, 64, 53, 47, 37]
    img, d, y = frame("en", "INVESTOR LENS",
                      "Investors in the Middle East lean on your financial statements first",
                      "Share of investors using each source to a large or very large extent")
    ch_top, ch_h = y + 30, H - 330 - (y + 30) - 30
    fig = plt.figure(figsize=((W - 2 * M) / 100, ch_h / 100))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.30, 0.13, 0.66, 0.84])
    ys = list(range(len(cats)))[::-1]
    h = 0.36
    for i, (a, b) in enumerate(zip(me, gl)):
        yy = ys[i]
        ax.barh(yy + h / 2, a, height=h, color=HRED if i == 0 else HNAVY)
        ax.barh(yy - h / 2, b, height=h, color=HMID)
        ax.text(a + 1, yy + h / 2, f"{a}%", va="center", fontproperties=INTER, fontsize=15, color=HGREY,
                fontweight="bold")
        ax.text(b + 1, yy - h / 2, f"{b}%", va="center", fontproperties=INTER, fontsize=13, color=HGREY)
    ax.set_yticks(ys)
    ax.set_yticklabels(cats, fontproperties=INTER, fontsize=14, color=HGREY)
    ax.set_xlim(0, 85)
    ax.set_xticks([])
    for s in ("top", "right", "bottom"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(HLIGHT)
    ax.tick_params(length=0)
    ax.text(0, -0.95, "■ Investing in the Middle East (n=322)", color=HNAVY, fontproperties=INTER, fontsize=13)
    ax.text(48, -0.95, "■ Global (n=1,074)", color=HMID, fontproperties=INTER, fontsize=13)
    ax.set_ylim(-1.1, len(cats) - 0.5)
    img.paste(fig_to_img(fig, W - 2 * M, ch_h), (M, ch_top))
    footer(img, d, "en", "So what for owners",
           "Investors lean on your notes to the accounts more than on your story. Make sure they reconcile and explain.",
           "Source: PwC, Global Investor Survey 2025: Middle East findings (fig. 9), survey fielded Sep-Oct 2025, "
           "published 2026")
    p = OUT / "2026-11-25-en-chart.png"
    img.save(p)
    return p


def ar_chart():
    # MISA, Performance of Key Economic and Investment Indicators in Saudi Arabia, July 2026 (source: SAMA)
    q = ["Q1\n23", "Q2", "Q3", "Q4", "Q1\n24", "Q2", "Q3", "Q4", "Q1\n25", "Q2", "Q3", "Q4", "Q1\n26"]
    v = [252, 263, 269, 276, 293, 307, 329, 352, 383, 421, 447, 469, 489]
    img, d, y = frame("ar", "فريق مالي عن بُعد",
                      "تمويل المنشآت الصغيرة والمتوسطة في السعودية تضاعف تقريبًا في 3 سنوات",
                      "تسهيلات المنشآت متناهية الصغر والصغيرة والمتوسطة، بالمليار ريال")
    ch_top, ch_h = y + 30, H - 330 - (y + 30) - 30
    fig = plt.figure(figsize=((W - 2 * M) / 100, ch_h / 100))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.04, 0.16, 0.92, 0.78])
    cols = [HNAVY] * (len(v) - 1) + [HRED]
    ax.bar(range(len(v)), v, color=cols, width=0.68)
    for i, val in enumerate(v):
        ax.text(i, val + 8, str(val), ha="center", fontproperties=INTER, fontsize=13 if i in (0, len(v) - 1) else 11,
                color=HGREY, fontweight="bold" if i in (0, len(v) - 1) else "normal")
    ax.set_xticks(range(len(v)))
    ax.set_xticklabels(q, fontproperties=INTER, fontsize=11, color=HGREY)
    ax.set_ylim(0, 560)
    ax.set_yticks([])
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(HLIGHT)
    ax.tick_params(length=0)
    ax.text(0, 530, "SAR bn, end of quarter. Share of total credit: 8.7% (Q1 2023) to 11.8% (Q1 2026)",
            fontproperties=INTER, fontsize=12, color=HGREY)
    img.paste(fig_to_img(fig, W - 2 * M, ch_h), (M, ch_top))
    footer(img, d, "ar", "ماذا يعني ذلك لصاحب المنشأة؟",
           "التمويل متاح أكثر من قبل، والبنك يبدأ بسؤال واحد: أين أرقامك المراجَعة؟",
           "Source: Ministry of Investment (MISA), Performance of Key Economic and Investment Indicators in "
           "Saudi Arabia, July 2026 (data: SAMA), Q1 2023 - Q1 2026")
    p = OUT / "2026-11-28-ar-chart.png"
    img.save(p)
    return p


if __name__ == "__main__":
    print(en_chart())
    print(ar_chart())
