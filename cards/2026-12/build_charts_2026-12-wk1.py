"""Charts for the week 29 Nov - 5 Dec 2026 (1080x1350, Axcell brand).

- 2026-12-02-en-chart.png: Wamda + Digital Digest, MENA startup funding, October 2026 monthly report.
- 2026-12-05-ar-chart.png: Monsha'at, National Strategy for Entrepreneurship and SMEs (2026).

Bars with matplotlib; headline/takeaway/Arabic captions with Pillow + libraqm so Arabic shapes correctly.
Every plotted value is copied from the source (see Sources in the Content Calendar rows).
Run with a Python that has Pillow (raqm) and matplotlib, e.g. python3.13.
"""
import importlib.util
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("wk4", HERE.parent / "2026-11" / "build_charts_2026-11-wk4.py")
k = importlib.util.module_from_spec(spec)
spec.loader.exec_module(k)
W, H, M = k.W, k.H, k.M


def en_chart():
    # Wamda, "MENA startup funding plunges 96% to $40 million in October 2026", 9 Nov 2026
    labels = ["Oct 2025", "Sep 2026", "Oct 2026"]
    vals = [784.9, 1100, 40]
    shown = ["$784.9m", "$1.1bn", "$40m"]
    img, d, y = k.frame("en", "INVESTOR LENS",
                        "MENA startup funding: $1.1bn in September, $40m in October",
                        "Total raised by MENA startups in the month, US$ million")
    ch_top, ch_h = y + 30, H - 330 - (y + 30) - 30
    fig = plt.figure(figsize=((W - 2 * M) / 100, ch_h / 100))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.08, 0.20, 0.84, 0.70])
    ax.bar(range(3), vals, color=[k.HMID, k.HNAVY, k.HRED], width=0.56)
    for i, (v, s) in enumerate(zip(vals, shown)):
        ax.text(i, v + 25, s, ha="center", fontproperties=k.INTER, fontsize=20, color=k.HGREY, fontweight="bold")
    ax.set_xticks(range(3))
    ax.set_xticklabels(labels, fontproperties=k.INTER, fontsize=16, color=k.HGREY)
    ax.set_ylim(0, 1300)
    ax.set_yticks([])
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(k.HLIGHT)
    ax.tick_params(length=0)
    fig.text(0.08, 0.075, "Sep 2026: 73 deals; three Saudi fintech deals = $762.5m (nearly 70%).",
             fontproperties=k.INTER, fontsize=13.5, color=k.HGREY)
    fig.text(0.08, 0.03, "Oct 2026: 32 deals; no megadeals, no later-stage rounds.",
             fontproperties=k.INTER, fontsize=13.5, color=k.HGREY)
    img.paste(k.fig_to_img(fig, W - 2 * M, ch_h), (M, ch_top))
    k.footer(img, d, "en", "So what for owners",
             "Funding windows open and close within weeks. Be diligence-ready before you need the money.",
             "Source: Wamda and Digital Digest, MENA startup funding monthly report, October 2026 "
             "(published 9 Nov 2026)")
    p = HERE / "2026-12-02-en-chart.png"
    img.save(p)
    return p


def ar_chart():
    # Monsha'at, The National Strategy for Entrepreneurship and SMEs (2026)
    vals = [1.14, 1.76]
    img, d, y = k.frame("ar", "فريق مالي عن بُعد",
                        "المنشآت في السعودية زادت 54% في ثلاث سنوات، و4.5% فقط منها سريعة النمو",
                        "عدد المنشآت الصغيرة والمتوسطة، بالمليون")
    ch_top, ch_h = y + 30, H - 330 - (y + 30) - 30
    cw = W - 2 * M
    fig = plt.figure(figsize=(cw / 100, ch_h / 100))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.06, 0.14, 0.50, 0.76])
    ax.bar(range(2), vals, color=[k.HMID, k.HNAVY], width=0.58)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.04, f"{v:.2f}", ha="center", fontproperties=k.INTER, fontsize=24, color=k.HGREY,
                fontweight="bold")
    ax.set_xticks(range(2))
    ax.set_xticklabels(["2022", "2025"], fontproperties=k.INTER, fontsize=18, color=k.HGREY)
    ax.set_ylim(0, 2.1)
    ax.set_yticks([])
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(k.HLIGHT)
    ax.tick_params(length=0)
    img.paste(k.fig_to_img(fig, cw, ch_h), (M, ch_top))
    # Stat tile on the right of the chart area (Pillow, Arabic shaped by raqm)
    tx = M + cw - 40
    ty = ch_top + int(ch_h * 0.22)
    d.text((tx, ty), "4.5%", font=k.pil_font("en", True, 120), fill=k.RED, anchor="ra")
    k.block(d, tx, ty + 150, "فقط من المنشآت سريعة النمو", k.pil_font("ar", True, 36), 360, "ar", k.GREY, 52)
    k.block(d, tx, ty + 270, "منشآت، تقييم الوضع الراهن", k.pil_font("ar", False, 26), 360, "ar", k.GREY, 40)
    k.footer(img, d, "ar", "ماذا يعني ذلك لصاحب المنشأة؟",
             "النمو يحتاج إدارة مالية تكبر معه: منهج موثق، ومراجعة لكل رقم، وتقارير في موعد ثابت.",
             "Source: Monsha'at, The National Strategy for Entrepreneurship and SMEs (2026): "
             "enterprises 2022 vs 2025; high-growth share from the current-state assessment")
    p = HERE / "2026-12-05-ar-chart.png"
    img.save(p)
    return p


if __name__ == "__main__":
    print(en_chart())
    print(ar_chart())
