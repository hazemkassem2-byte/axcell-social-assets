"""Build the Axcell Insight Brief, November 2026 (English).

Outputs (relative to this folder):
  axcell-insight-brief-2026-11-en.pdf   A4 portrait, 8 pages
  pages/en-01.png ... en-08.png         1080x1350 (A4 page centred on a 4:5 canvas)

Every number below was read on the cited source page on 19 Nov 2026 (see SOURCES).
Run with: /usr/bin/python3 build_brief.py   (needs matplotlib, Pillow, fontTools)
"""
import io
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Rectangle, FancyBboxPatch
from matplotlib.textpath import TextPath
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
FONTS = Path("/tmp/claude-0/fonts")  # static instances of brand/Inter.ttf (made with fontTools.instancer)
NAVY, RED, GREY, WHITE = "#0A2A43", "#C8102E", "#2C2C2C", "#FFFFFF"
MID, LIGHT, PALE = "#8A97A6", "#E6EAEF", "#F3F5F8"
W_IN, H_IN = 8.27, 11.69  # A4
M = 0.62  # side margin, inches

FP = {k: FontProperties(fname=str(FONTS / f"AxInter-{v}.ttf"))
      for k, v in {"r": "Regular", "s": "SemiBold", "b": "ExtraBold"}.items()}
plt.rcParams["pdf.fonttype"] = 42

LOGO_COLOR = Image.open(REPO / "brand/logo/axcell-logo-color.png")
LOGO_WHITE = Image.open(REPO / "brand/logo/axcell-lockup-name-white.png")


# ---------- helpers ----------
def tw(s, fp, size):
    """Text width in inches."""
    return TextPath((0, 0), s, prop=fp, size=size).get_extents().width / 72.0


def wrap(s, fp, size, width_in):
    out = []
    for para in s.split("\n"):
        cur = ""
        for w in para.split():
            trial = (cur + " " + w).strip()
            if tw(trial, fp, size) <= width_in or not cur:
                cur = trial
            else:
                out.append(cur)
                cur = w
        out.append(cur)
    return out


def X(x):  # inches -> figure fraction
    return x / W_IN


def Y(y_from_top):
    return 1 - y_from_top / H_IN


def text(fig, x, y, s, fp="r", size=10, color=GREY, ha="left", va="top", **kw):
    return fig.text(X(x), Y(y), s, fontproperties=FP[fp], fontsize=size, color=color, ha=ha, va=va, **kw)


def para(fig, x, y, s, width, fp="r", size=10, color=GREY, lh=1.45):
    """Draw wrapped paragraph; return y (inches from top) after it."""
    lines = wrap(s, FP[fp], size, width)
    step = size * lh / 72.0
    for i, ln in enumerate(lines):
        text(fig, x, y + i * step, ln, fp, size, color)
    return y + len(lines) * step


def rect(fig, x, y, w, h, color, **kw):
    fig.add_artist(Rectangle((X(x), Y(y + h)), w / W_IN, h / H_IN, transform=fig.transFigure,
                             facecolor=color, edgecolor="none", **kw))


def logo(fig, img, x, y, w):
    h = w * img.height / img.width
    ax = fig.add_axes([X(x), Y(y + h), w / W_IN, h / H_IN])
    ax.imshow(img)
    ax.axis("off")


def page_frame(fig, n, kicker, headline, sub=None):
    rect(fig, 0, 0, W_IN, 0.46, NAVY)
    text(fig, M, 0.17, "AXCELL INSIGHT BRIEF  ·  NOVEMBER 2026", "s", 8, WHITE)
    text(fig, W_IN - M, 0.17, f"{n:02d} / 08", "s", 8, WHITE, ha="right")
    rect(fig, M, 0.82, 0.5, 0.045, RED)
    text(fig, M, 0.98, kicker.upper(), "s", 9, RED)
    y = para(fig, M, 1.28, headline, W_IN - 2 * M, "b", 21, NAVY, lh=1.2)
    if sub:
        y = para(fig, M, y + 0.1, sub, W_IN - 2 * M, "r", 10.5, GREY, lh=1.45)
    return y


def footer(fig, source):
    rect(fig, M, H_IN - 0.78, W_IN - 2 * M, 0.01, LIGHT)
    para(fig, M, H_IN - 0.68, "Source: " + source, W_IN - 2 * M - 1.6, "r", 7, MID, lh=1.35)
    text(fig, W_IN - M, H_IN - 0.68, "axcellservice.com", "s", 7.5, NAVY, ha="right")
    logo(fig, LOGO_COLOR, W_IN - M - 0.85, H_IN - 0.5, 0.85)


def owner_box(fig, y, title, body, h=None):
    width = W_IN - 2 * M
    lines = wrap(body, FP["r"], 10, width - 0.5)
    h = h or 0.62 + len(lines) * 10 * 1.45 / 72
    fig.add_artist(FancyBboxPatch((X(M), Y(y + h)), width / W_IN, h / H_IN, transform=fig.transFigure,
                                  boxstyle="round,pad=0,rounding_size=0.008", facecolor=PALE, edgecolor="none"))
    rect(fig, M, y, 0.07, h, NAVY)
    text(fig, M + 0.25, y + 0.2, title.upper(), "s", 8.5, NAVY)
    para(fig, M + 0.25, y + 0.45, body, width - 0.5, "r", 10, GREY)
    return y + h


def tile(fig, x, y, w, h, big, label, note):
    rect(fig, x, y, w, h, PALE)
    text(fig, x + 0.15, y + 0.15, label.upper(), "s", 7.5, MID)
    text(fig, x + 0.15, y + 0.4, big, "b", 24, NAVY)
    para(fig, x + 0.15, y + 0.95, note, w - 0.3, "r", 8, GREY, lh=1.35)


def chart_axes(fig, x, y, w, h):
    ax = fig.add_axes([X(x), Y(y + h), w / W_IN, h / H_IN])
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(LIGHT)
    ax.tick_params(colors=GREY, labelsize=8, length=0)
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontproperties(FP["r"])
    return ax


def style_ticks(ax, size=8):
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontproperties(FP["r"])
        lab.set_fontsize(size)
        lab.set_color(GREY)


# ---------- pages ----------
def p1_cover():
    fig = plt.figure(figsize=(W_IN, H_IN))
    fig.patch.set_facecolor(NAVY)
    logo(fig, LOGO_WHITE, M, 0.75, 2.1)
    rect(fig, M, 3.55, 0.7, 0.06, RED)
    text(fig, M, 3.85, "AXCELL INSIGHT BRIEF", "s", 13, WHITE)
    text(fig, M, 4.3, "November 2026", "b", 40, WHITE)
    y = para(fig, M, 5.25, "Egypt's rates, prices, credit and capital: what the latest data means "
             "for an owner's cash, pricing and financing decisions this month.", 6.2, "r", 14, WHITE, lh=1.45)
    items = ["Egypt macro snapshot", "Cash and pricing", "Credit and financing",
             "Venture and private capital in MENA", "What investors check in due diligence",
             "5 numbers to check this month", "Sources"]
    y = 7.0
    text(fig, M, y, "INSIDE", "s", 9, "#9FB3C8")
    for i, it in enumerate(items):
        text(fig, M, y + 0.35 + i * 0.3, f"{i + 2:02d}", "s", 10, "#9FB3C8")
        text(fig, M + 0.5, y + 0.35 + i * 0.3, it, "r", 10.5, WHITE)
    text(fig, M, H_IN - 1.25, "Hazem Kassem", "s", 11, WHITE)
    text(fig, M, H_IN - 1.0, "Managing Director, Axcell Financial Consulting  ·  25+ years as CFO", "r", 9, "#C9D4E0")
    text(fig, M, H_IN - 0.62, "Your CFO partner: Clear Decisions, Strong Growth.", "r", 9, "#C9D4E0")
    text(fig, W_IN - M, H_IN - 0.62, "axcellservice.com", "s", 9, WHITE, ha="right")
    return fig


MONTHS = ["Dec\n25", "Jan\n26", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct"]
INFL = [12.3, 11.9, 13.4, 15.2, 14.9, None, 14.3, 14.9, 14.5, 13.9, 12.7]   # CBE, annual urban headline
DEPO = [20.0, 20.0, 19.0, 19.0, 19.0, 19.0, 19.0, 19.0, 19.0, 19.0, 20.0]   # CBE overnight deposit rate, month-end


def p2_macro():
    fig = plt.figure(figsize=(W_IN, H_IN))
    y = page_frame(fig, 2, "Egypt macro snapshot",
                   "Inflation fell to 12.7%, and the CBE still raised rates. Borrowing just got dearer in real terms.")
    y += 0.25
    tw_ = (W_IN - 2 * M - 0.45) / 4
    tiles = [("20.0%", "CBE deposit rate", "Raised 100 bps on 29 Oct 2026, the first hike since March 2024. Lending rate 21.0%."),
             ("12.7%", "Urban inflation", "Annual, October 2026, down from 13.9% in September. Core: 13.1%."),
             ("53.78", "EGP per USD", "CBE average market sell rate, 17 Nov 2026."),
             ("47.2", "Egypt PMI", "October 2026. Below 50 for the tenth month running.")]
    for i, (b, l, n) in enumerate(tiles):
        tile(fig, M + i * (tw_ + 0.15), y, tw_, 1.75, b, l, n)
    y += 2.05
    text(fig, M, y, "CBE overnight deposit rate vs annual urban headline inflation, %", "s", 10, NAVY)
    ax = chart_axes(fig, M + 0.1, y + 0.35, W_IN - 2 * M - 0.6, 3.3)
    xs = list(range(len(MONTHS)))
    ax.step(xs, DEPO, where="post", color=NAVY, lw=2.4)
    seg = [(i, v) for i, v in enumerate(INFL) if v is not None]
    a = [p for p in seg if p[0] < 5]; b = [p for p in seg if p[0] > 5]
    for part in (a, b):
        ax.plot([p[0] for p in part], [p[1] for p in part], color=RED, lw=2.0, marker="o", ms=4)
    for i, v in seg:
        ax.annotate(f"{v:.1f}", (i, v), xytext=(0, -14), textcoords="offset points", ha="center",
                    fontproperties=FP["r"], fontsize=7.5, color=RED)
    for i in (0, 1, 5, 10):
        ax.annotate(f"{DEPO[i]:.1f}", (i, DEPO[i]), xytext=(0, 6), textcoords="offset points", ha="center",
                    fontproperties=FP["s"], fontsize=7.5, color=NAVY)
    ax.text(5, 16.0, "May: not shown\n(source page\nunavailable)", ha="center", fontproperties=FP["r"], fontsize=6.5, color=MID)
    ax.text(10.15, 20.0, "Deposit rate", va="center", fontproperties=FP["s"], fontsize=8, color=NAVY)
    ax.text(10.15, 12.7, "Inflation", va="center", fontproperties=FP["s"], fontsize=8, color=RED)
    ax.set_xticks(xs)
    ax.set_xticklabels(MONTHS)
    ax.set_ylim(0, 23)
    ax.set_xlim(-0.4, 11.2)
    ax.yaxis.grid(True, color=LIGHT, lw=0.6)
    ax.set_axisbelow(True)
    style_ticks(ax)
    y += 3.95
    owner_box(fig, y, "What this means for owners",
              "The gap between the deposit rate and inflation widened from 5.1 points in September to 7.3 points "
              "in October. Money in the bank now beats inflation by a wide margin, and money you borrow costs you "
              "more in real terms. Any project financed with debt has to clear that bar before it adds value.")
    footer(fig, "Central Bank of Egypt, MPC press releases (25 Dec 2025 to 29 Oct 2026), CPI press releases and exchange-rate "
                "page; S&P Global Egypt PMI, 3 Nov 2026. Rate shown at month-end. Accessed 19 Nov 2026.")
    return fig


def p3_pricing():
    fig = plt.figure(figsize=(W_IN, H_IN))
    y = page_frame(fig, 3, "Cash and pricing",
                   "Costs are climbing faster again. The firms that wait to reprice pay for it in margin.")
    y += 0.2
    y = para(fig, M, y, "What about 400 Egyptian non-oil private firms told S&P Global in October 2026:", W_IN - 2 * M, "s", 10.5, NAVY)
    pts = ["Input cost inflation rose to its highest since May, driven by imported inputs, energy, shipping and a weaker pound.",
           "Firms raised selling prices at the fastest rate since June.",
           "Output and new orders fell at the fastest rates in four months; business confidence hit a seven-month low.",
           "Delivery times lengthened the most since June, and firms built stocks for the first time since June."]
    y += 0.08
    for p in pts:
        rect(fig, M, y + 0.07, 0.06, 0.06, RED)
        y = para(fig, M + 0.22, y, p, W_IN - 2 * M - 0.22, "r", 10, GREY) + 0.06
    y += 0.1
    y = para(fig, M, y, "The World Bank's 2025 Enterprise Survey of Egypt found that 30.8% of firms use inputs of foreign "
             "origin, so the pound feeds straight into their cost base.", W_IN - 2 * M, "r", 10, GREY)
    y += 0.25
    text(fig, M, y, "Example: what an 8% cost rise does to a 25% gross margin", "s", 10, NAVY)
    text(fig, M, y + 0.22, "Illustrative only. Assumptions: price 100, cost 75; costs then rise 8% to 81.", "r", 8, MID)
    ax = chart_axes(fig, M + 0.1, y + 0.6, W_IN - 2 * M - 0.2, 2.4)
    labels = ["Before the\ncost rise", "Price\nunchanged", "Price\n+6%", "Price\n+8%"]
    vals = [25.0, 19.0, 23.6, 25.0]   # 25/100, 19/100, 25/106, 27/108
    cols = [MID, RED, NAVY, NAVY]
    bars = ax.bar(labels, vals, color=cols, width=0.55)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.6, f"{v:.1f}%", ha="center",
                fontproperties=FP["s"], fontsize=9, color=GREY)
    ax.set_ylim(0, 30)
    ax.set_yticks([0, 10, 20, 30])
    ax.yaxis.grid(True, color=LIGHT, lw=0.6)
    ax.set_axisbelow(True)
    style_ticks(ax)
    y += 3.75
    owner_box(fig, y, "What this means for owners",
              "Holding price while costs rise 8% takes a 25% margin down to 19%. A 6% increase only gets you back to "
              "23.6%; you need the full 8% to stand still. Re-cost your top ten products every month while input "
              "inflation is accelerating, and reprice by product, not with one blanket increase.")
    footer(fig, "S&P Global Egypt PMI news release, 3 Nov 2026 (data collected 12-22 Oct 2026, panel of about 400 firms); "
                "World Bank Enterprise Surveys, Egypt 2025 Country Profile. Example computed by Axcell. Accessed 19 Nov 2026.")
    return fig


ES = [  # (label, Egypt 2025, MENAAP region) from the World Bank Enterprise Surveys Egypt 2025 country profile
    ("Share of investment\nfinanced internally", 88.0, 71.4),
    ("Firms using supplier/customer\ncredit for working capital", 36.8, 21.1),
    ("Firms using banks to\nfinance investment", 8.9, 28.2),
    ("Share of investment\nfinanced by banks", 2.9, 15.1),
]


def p4_credit():
    fig = plt.figure(figsize=(W_IN, H_IN))
    y = page_frame(fig, 4, "Credit and financing",
                   "Egyptian firms fund 88% of their investment themselves. Banks fund 2.9%.",
                   "World Bank Enterprise Survey of 1,024 Egyptian firms, interviewed September 2025 to January 2026, "
                   "compared with the Middle East, North Africa, Afghanistan & Pakistan average.")
    y += 0.3
    text(fig, M, y, "% (Egypt 2025 vs regional average)", "s", 10, NAVY)
    text(fig, W_IN - M - 1.55, y, "■ Egypt 2025", "s", 9, NAVY, ha="right")
    text(fig, W_IN - M, y, "■ Regional average", "s", 9, MID, ha="right")
    ax = chart_axes(fig, M + 2.05, y + 0.35, W_IN - 2 * M - 2.5, 3.9)
    n = len(ES)
    ys = list(range(n))[::-1]
    h = 0.34
    ax.barh([v + h / 2 for v in ys], [e[1] for e in ES], height=h, color=NAVY)
    ax.barh([v - h / 2 for v in ys], [e[2] for e in ES], height=h, color=MID)
    for yy, e in zip(ys, ES):
        ax.text(e[1] + 1.2, yy + h / 2, f"{e[1]:.1f}", va="center", fontproperties=FP["s"], fontsize=9, color=NAVY)
        ax.text(e[2] + 1.2, yy - h / 2, f"{e[2]:.1f}", va="center", fontproperties=FP["r"], fontsize=9, color=GREY)
    ax.set_yticks(ys)
    ax.set_yticklabels([e[0] for e in ES])
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.xaxis.grid(True, color=LIGHT, lw=0.6)
    ax.set_axisbelow(True)
    style_ticks(ax, 8.5)
    y += 4.55
    y = para(fig, M, y, "Add the price of bank money: the CBE lending rate is 21.0% against 12.7% inflation, "
             "a real cost of 8.3 points. The survey shows most firms grow on their own cash and their suppliers' patience.",
             W_IN - 2 * M, "r", 10.5, GREY)
    y += 0.2
    owner_box(fig, y, "What this means for owners",
              "If growth is paid for by your own cash and your suppliers' credit, then collections, stock and payment "
              "terms are your real financing. Every day you take off receivables is a loan you did not need. "
              "And when you do go to a bank, lenders ask for the same thing investors ask for: numbers they can trust.")
    footer(fig, "World Bank Enterprise Surveys, Egypt 2025 Country Profile (1,024 firms, Sep 2025-Jan 2026), appendix table; "
                "Central Bank of Egypt MPC press release 29 Oct 2026 and CPI press release Oct 2026. Accessed 19 Nov 2026.")
    return fig


VC = [("Funding\nH1 2026", -22), ("Deals\nH1 2026", -41), ("Funding\n9M 2026", -7), ("Deals\n9M 2026", -33)]


def p5_capital():
    fig = plt.figure(figsize=(W_IN, H_IN))
    y = page_frame(fig, 5, "Venture and private capital in MENA",
                   "Money is still there. It is going to fewer companies, in bigger cheques.")
    y += 0.25
    tw_ = (W_IN - 2 * M - 0.45) / 4
    tiles = [("$2.98B", "MENA VC, 9M 2026", "Raised by MENA startups in the first nine months of 2026 (MAGNiTT)."),
             ("81%", "Regional capital", "Estimated share of H1 2026 capital supplied by MENA-based investors."),
             ("35%", "Egypt's M&A share", "Egypt's share of MENA venture M&A (exit) activity in 9M 2026."),
             ("$304M", "Egypt VC, 2025", "Across 69 deals in 2025 (ITIDA / Startup Genome, 2026 report).")]
    for i, (b, l, n) in enumerate(tiles):
        tile(fig, M + i * (tw_ + 0.15), y, tw_, 1.75, b, l, n)
    y += 2.05
    text(fig, M, y, "MENA venture capital, change vs the same period of 2025, %", "s", 10, NAVY)
    ax = chart_axes(fig, M + 0.1, y + 0.8, W_IN - 2 * M - 0.2, 2.7)
    labels = [v[0] for v in VC]
    vals = [v[1] for v in VC]
    bars = ax.bar(labels, vals, color=[MID, NAVY, MID, NAVY], width=0.55)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v - 2.5, f"{v}%", ha="center", va="top",
                fontproperties=FP["s"], fontsize=9.5, color=GREY)
    ax.axhline(0, color=GREY, lw=0.8)
    ax.set_ylim(-50, 5)
    ax.set_yticks([0, -10, -20, -30, -40, -50])
    ax.yaxis.grid(True, color=LIGHT, lw=0.6)
    ax.set_axisbelow(True)
    ax.xaxis.tick_top()
    style_ticks(ax)
    y += 3.75
    y = para(fig, M, y, "Deal count fell almost twice as fast as funding. In H1 2026 the ten largest deals took 58% "
             "of capital and international investor participation fell 48%. Early-stage deals were 82% of 9M 2026 "
             "activity, yet at their lowest level in a decade (MAGNiTT).", W_IN - 2 * M, "r", 10, GREY)
    y += 0.2
    owner_box(fig, y, "What this means for owners",
              "When investors write fewer cheques, they choose the companies that are easiest to underwrite: "
              "clean monthly numbers, audited accounts, clear unit economics and a data room ready on day one. "
              "If you plan to raise or sell in 2027, the preparation starts with this year's close.")
    footer(fig, "MAGNiTT, MENA Venture Capital: The H1 2026 Review and The Q3 2026 Update (magnitt.com; $2.98B from MAGNiTT's "
                "Q3 2026 announcement); ITIDA & Startup Genome, Egypt Startup Ecosystem Report 2026. Accessed 19 Nov 2026.")
    return fig


DD = [
    ("Trading trends and KPIs", "Monthly management accounts by product, service, division and territory, with the KPIs that drive value.",
     "24 months of monthly P&L that ties to the audited accounts."),
    ("Current cost base", "What the business really costs to run today.",
     "Costs mapped by function; owner and related-party costs shown separately."),
    ("Quality of earnings", "Underlying earnings, excluding one-off items and policy changes.",
     "A list of one-offs with documents behind each one."),
    ("Cash, capex and working capital", "Cash generation, capital spending and the 'normal' level of working capital.",
     "Monthly receivables, payables and stock, aged, for two years."),
    ("Net debt and liabilities", "Balance-sheet items a buyer would have to fund, which move the price.",
     "All loans, leases, tax exposures and overdue payables in one schedule."),
    ("Accounting judgements", "Policies in judgement areas and any recent changes.",
     "A one-page note on revenue recognition, provisions and stock valuation."),
    ("Material contracts", "Pricing, payment terms and duration of key agreements.",
     "Top customer and supplier contracts filed and summarised."),
    ("Budget accuracy", "How close past budgets came to actual results.",
     "Last two years' budget vs actual, with the reasons for the gaps."),
]


def p6_dd():
    fig = plt.figure(figsize=(W_IN, H_IN))
    y = page_frame(fig, 6, "What investors check in due diligence",
                   "Due diligence tests whether your profit is real, repeatable and turns into cash.",
                   "Core areas from the ICAEW Corporate Finance Faculty best-practice guideline on financial due diligence "
                   "(authors: PwC UK). Right-hand column: Axcell's view of what to prepare.")
    y += 0.3
    c1, c2, c3 = M, M + 1.95, M + 4.55
    w1, w2, w3 = 1.8, 2.45, W_IN - M - c3
    rect(fig, M, y, W_IN - 2 * M, 0.34, NAVY)
    for cx, s in ((c1, "AREA"), (c2, "WHAT THE INVESTOR TESTS"), (c3, "PREPARE NOW (AXCELL VIEW)")):
        text(fig, cx + 0.1, y + 0.11, s, "s", 7.5, WHITE)
    y += 0.42
    for i, (a, b, c) in enumerate(DD):
        la = wrap(a, FP["s"], 9, w1 - 0.15)
        lb = wrap(b, FP["r"], 8.5, w2 - 0.2)
        lc = wrap(c, FP["r"], 8.5, w3 - 0.2)
        rows = max(len(la), len(lb), len(lc))
        h = rows * 8.8 * 1.4 / 72 + 0.22
        if i % 2 == 0:
            rect(fig, M, y - 0.06, W_IN - 2 * M, h, PALE)
        para(fig, c1 + 0.1, y + 0.04, a, w1 - 0.15, "s", 9, NAVY, lh=1.4)
        para(fig, c2 + 0.1, y + 0.04, b, w2 - 0.2, "r", 8.5, GREY, lh=1.4)
        para(fig, c3 + 0.1, y + 0.04, c, w3 - 0.2, "r", 8.5, GREY, lh=1.4)
        y += h
    y += 0.25
    owner_box(fig, y, "What this means for owners",
              "The guideline notes that due diligence typically focuses on management information, which is often "
              "more detailed than the audited statements. If your monthly accounts are late or don't reconcile, the "
              "investor learns that in week one, and it shows up in the price or the terms.")
    footer(fig, "ICAEW Corporate Finance Faculty, Best-Practice Guideline 71: Financial Due Diligence (authors: PricewaterhouseCoopers "
                "LLP, UK), icaew.com. 'Prepare now' column is Axcell's practitioner view. Accessed 19 Nov 2026.")
    return fig


FIVE = [
    ("Your real cost of borrowing", "Loan rate minus inflation. At the CBE's 21.0% lending rate and 12.7% inflation, that is 8.3 points.",
     "If a project financed with debt cannot beat this after inflation, fund it from cash or delay it."),
    ("Your cost pass-through gap", "Percentage rise in your input costs over the last three months minus your price rise.",
     "A positive gap is margin leaving the business every month. PMI firms report input costs at a five-month high."),
    ("Your dollar share of costs", "Share of cost of sales priced in or linked to USD. The CBE rate was 53.78 EGP per USD on 17 Nov.",
     "Know how much a one-pound move costs you before your supplier tells you."),
    ("Your days of receivables", "Receivables divided by the month's sales, times 30, measured every month.",
     "With bank money at 21%, each day you collect sooner is financing you don't need to borrow."),
    ("Your budget accuracy", "This year's actual results vs the budget, line by line. December is budget season.",
     "Investors check past budget accuracy. Build 2027 on what actually happened in 2026."),
]


def p7_five():
    fig = plt.figure(figsize=(W_IN, H_IN))
    y = page_frame(fig, 7, "Your checklist for this month", "5 numbers every owner should check this month")
    y += 0.3
    for i, (t, how, why) in enumerate(FIVE):
        text(fig, M, y, f"{i + 1}", "b", 30, RED if i == 0 else NAVY)
        y0 = y + 0.02
        text(fig, M + 0.62, y0, t, "b", 13, NAVY)
        y1 = para(fig, M + 0.62, y0 + 0.32, how, W_IN - 2 * M - 0.62, "r", 10, GREY)
        y1 = para(fig, M + 0.62, y1 + 0.03, why, W_IN - 2 * M - 0.62, "s", 10, NAVY)
        y = y1 + 0.22
        if i < len(FIVE) - 1:
            rect(fig, M + 0.62, y - 0.1, W_IN - 2 * M - 0.62, 0.01, LIGHT)
            y += 0.08
    y += 0.1
    owner_box(fig, y, "Want a second pair of eyes?",
              "If any of these five numbers surprises you, or you can't get it from your accounts within a day, "
              "that is the first thing to fix. Message Hazem Kassem on LinkedIn or write to info@axcellservice.com.")
    footer(fig, "Central Bank of Egypt (rates 29 Oct 2026; CPI Oct 2026; exchange rate 17 Nov 2026); S&P Global Egypt PMI, 3 Nov 2026; "
                "ICAEW Guideline 71. Ratios and rules are Axcell's practitioner view. Accessed 19 Nov 2026.")
    return fig


SOURCES = [
    ("Central Bank of Egypt", "MPC Press Release 29 October 2026 (rates raised 100 bps; deposit 20.0%, lending 21.0%)",
     "cbe.org.eg/en/news-publications/news/2026/10/29/13/08/mpc-press-release-29-october-2026"),
    ("Central Bank of Egypt", "MPC Press Releases 25 Dec 2025, 2 Apr, 21 May, 9 Jul, 20 Aug, 24 Sep 2026 (rate path; inflation for "
     "Dec 2025, Jan, Feb, Jun, Jul, Aug 2026); 12 Feb 2026 release (cut to 19.0%; CBE copy via amwalalghad.com)",
     "cbe.org.eg/en/news-publications/news/2026/08/20/15/17/mpc-press-release-20-august-2026 (and same path for other dates)"),
    ("Central Bank of Egypt", "CPI Press Releases March and April 2026; CPI Press Release October 2026 (12.7% headline, 13.1% core)",
     "cbe.org.eg/en/news-publications/news/2026/05/06/15/18/cpi-press-release-april-2026; October via publicnow.com CBE feed"),
    ("Central Bank of Egypt", "Exchange Rates, average market rate 17 Nov 2026 (USD sell 53.7753)",
     "cbe.org.eg/en/economic-research/statistics/exchange-rates"),
    ("S&P Global", "S&P Global Egypt PMI news release, 3 November 2026 (October data, PMI 47.2)",
     "pmi.spglobal.com/Public/Home/PressRelease/4a9da20d16624d459b5402c66d1ccd22"),
    ("World Bank", "Enterprise Surveys, Egypt 2025 Country Profile (1,024 firms, Sep 2025-Jan 2026)",
     "enterprisesurveys.org/content/dam/enterprisesurveys/documents/country/Egypt-2025.pdf"),
    ("MAGNiTT", "MENA Venture Capital: The H1 2026 Review", "magnitt.com/research/mena-venture-capital-the-h1-2026-review-51047"),
    ("MAGNiTT", "MENA Venture Capital: The Q3 2026 Update (9M 2026 funding $2.98B per MAGNiTT announcement, 13 Oct 2026)",
     "magnitt.com/research/Q3-2026-MENA-VC-Update-51060"),
    ("ITIDA & Startup Genome", "Egypt Startup Ecosystem Report 2026 (2025: ~$304M across 69 VC deals)",
     "itida.gov.eg/English/MediaCenter/Announcements/Documents/egypt-startup-ecosystem-report-2026.pdf"),
    ("ICAEW Corporate Finance Faculty", "Best-Practice Guideline 71: Financial Due Diligence (authors: PwC UK)",
     "icaew.com/-/media/corporate/files/technical/corporate-finance/guidelines/financial-due-diligence-guideline-71.ashx"),
]


def p8_sources():
    fig = plt.figure(figsize=(W_IN, H_IN))
    y = page_frame(fig, 8, "Sources and notes", "Every figure, where it came from",
                   "All sources opened on 19 November 2026. Figures are as published; percentages are rounded as in the source.")
    y += 0.3
    for pub, title, url in SOURCES:
        text(fig, M, y, pub.upper(), "s", 7.5, RED)
        y = para(fig, M, y + 0.2, title, W_IN - 2 * M, "r", 9, GREY, lh=1.35)
        y = para(fig, M, y + 0.01, url, W_IN - 2 * M, "r", 7.5, MID, lh=1.3) + 0.14
    y += 0.05
    owner_box(fig, y, "Notes",
              "Chart on page 2 shows the deposit rate at month-end; May 2026 inflation is omitted because the CBE "
              "release could not be opened. Page 3 margin example is illustrative, with its assumptions stated. "
              "This brief is general information, not investment advice.")
    footer(fig, "Compiled by Axcell Financial Consulting, November 2026.")
    return fig


PAGES = [p1_cover, p2_macro, p3_pricing, p4_credit, p5_capital, p6_dd, p7_five, p8_sources]


def main():
    out_pdf = HERE / "axcell-insight-brief-2026-11-en.pdf"
    (HERE / "pages").mkdir(exist_ok=True)
    with PdfPages(out_pdf) as pdf:
        info = pdf.infodict()
        info["Title"] = "Axcell Insight Brief, November 2026"
        info["Author"] = "Axcell Financial Consulting"
        for i, fn in enumerate(PAGES, 1):
            fig = fn()
            pdf.savefig(fig)
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=2 * 1350 / H_IN)
            plt.close(fig)
            im = Image.open(buf).convert("RGB")
            im = im.resize((round(1350 * W_IN / H_IN), 1350), Image.LANCZOS)
            bg = NAVY if i == 1 else WHITE
            canvas = Image.new("RGB", (1080, 1350), bg)
            canvas.paste(im, ((1080 - im.width) // 2, 0))
            if i > 1:  # extend the navy header band to the full canvas width
                band = round(0.46 / H_IN * 1350)
                canvas.paste(Image.new("RGB", ((1080 - im.width) // 2 + 1, band), NAVY), (0, 0))
                canvas.paste(Image.new("RGB", ((1080 - im.width) // 2 + 1, band), NAVY), (1080 - (1080 - im.width) // 2 - 1, 0))
            canvas.save(HERE / "pages" / f"en-{i:02d}.png", optimize=True)
    print(out_pdf)


if __name__ == "__main__":
    main()
