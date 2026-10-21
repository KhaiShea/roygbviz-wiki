"""Figures for the Fonts and text page. python scripts/fonts.py

Four figures, each in light and dark: the type scale, the same chart in three font pairs, the same chart saved at two
sizes, and text inside a chart. All data is synthetic.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from plotnine import (aes, annotate, coord_flip, element_text, geom_col, geom_line, geom_vline, ggplot, labs,  # noqa: E402
                      scale_colour_manual, scale_fill_manual, scale_y_continuous, theme)

import roygbviz as rv  # noqa: E402
from roygbviz.config import pick_font, pick_serif  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "assets" / "fonts"
OUT.mkdir(parents=True, exist_ok=True)
PAL = None  # the active palette; rv.get_palette() with no mode always gives light, so keep what rv.use() returns

# Every text role in the theme, as (name, what it's for, share of base_size, serif?, bold?, neutral colour).
# These are copied from theme_roygbviz, so check them against roygbviz/theme.py if the library changes.
ROLES = [
    ("Title", "Latency fell by a third", 1.6, True, True, "text"),
    ("Facet label", "GPU", 0.95, True, True, "text"),
    ("Subtitle", "Median latency per reply, month by month", 0.95, False, False, "text_2"),
    ("Axis title", "Latency (ms)", 0.85, False, False, "text_2"),
    ("Legend text", "Cascade A", 0.8, False, False, "text_2"),
    ("Axis numbers", "200  400  600  800", 0.8, False, False, "muted"),
    ("Caption", "Synthetic data", 0.7, False, False, "muted"),
]


def head(title, sub, caption="Synthetic data"):
    return [labs(title=title, subtitle=sub, caption=caption),
            theme(plot_subtitle=element_text(margin={"b": 10, "unit": "pt"}))]


def scale_fig(path, dpi=160):
    """A type specimen: each role written in its own font, size and colour."""
    n = PAL.neutrals
    fig = plt.figure(figsize=(6.4, 3.7), dpi=dpi)
    fig.patch.set_facecolor(n["bg"])
    top, step = 0.85, 0.125
    fig.text(0.04, 0.955, "ROLE", size=7, color=n["muted"], weight="bold", va="center")
    fig.text(0.27, 0.955, "HOW IT LOOKS", size=7, color=n["muted"], weight="bold", va="center")
    fig.text(0.96, 0.955, "SIZE AT BASE 11", size=7, color=n["muted"], weight="bold", va="center", ha="right")
    for k, (name, sample, share, serif, bold, ink) in enumerate(ROLES):
        y = top - k * step
        fig.add_artist(plt.Line2D([0.04, 0.96], [y - step / 2] * 2, color=n["grid"], lw=0.8))
        fig.text(0.04, y, name, size=8.5, color=n["text_2"], va="center")
        fig.text(0.27, y, sample, size=11 * share, color=n[ink], va="center",
                 family=pick_serif() if serif else pick_font(), weight="bold" if bold else "normal")
        fig.text(0.96, y, f"{11 * share:g} pt", size=8.5, color=n["muted"], va="center", ha="right")
    fig.savefig(path, dpi=dpi)
    plt.close(fig)


def bars(d):
    return (ggplot(d, aes("model", "score", fill="model")) + geom_col(width=0.7, show_legend=False)
            + coord_flip() + scale_y_continuous(limits=(0, 100), expand=(0, 0))
            + scale_fill_manual(values=rv.colour_map(list(d["model"])[::-1], order="rainbow")))


def pairs_tiles(mode):
    """The same chart in three font pairs, all installed on the machine that made this wiki."""
    d = pd.DataFrame({"model": ["Conformer", "Parakeet", "Whisper"], "score": [79, 86, 91]})
    d["model"] = pd.Categorical(d["model"], d["model"])
    pairs = [("Arial", "Georgia"), ("Liberation Sans", "Liberation Serif"), ("DejaVu Sans", "DejaVu Serif")]
    for k, (body, serif) in enumerate(pairs, start=1):
        p = (bars(d) + rv.theme_roygbviz(base_family=body, title_family=serif, grid="x")
             + head(f"{serif} for titles", f"{body} for everything else") + labs(x="", y="Score out of 100"))
        p.save(OUT / f"pair{k}_{mode}.png", width=4.2, height=3, dpi=180, verbose=False)


def latency():
    """The same noise every call, so light and dark show the same data."""
    rng, month = np.random.default_rng(14), np.arange(1, 13)
    return pd.concat([pd.DataFrame({"month": month, "ms": base - drop * month + rng.normal(0, 10, 12), "cascade": c})
                      for c, base, drop in (("Cascade A", 900, 14), ("Cascade B", 760, 8), ("Cascade C", 980, 30))])


def size_tiles(mode):
    """One chart saved 5 and 10 inches wide, and 10 wide with the base size doubled. Every PNG comes out 1000 pixels
    wide, so on the page they're shown at the same width, the way a reader would see them in a document."""
    d = latency()
    setups = [(1, 5, 11, "Saved 5 inches wide", "base_size=11"),
              (2, 10, 11, "Saved 10 inches wide", "base_size=11, so the text looks half the size"),
              (3, 10, 22, "Saved 10 inches wide", "base_size=22, and the lines scaled with rv.stroke()")]
    for k, width, base, title, sub in setups:
        rv.use(mode, base_size=base)
        p = (ggplot(d, aes("month", "ms", colour="cascade")) + geom_line(size=rv.stroke(1.1))
             + rv.end_labels(d, "month", "ms", "cascade", size=rv.stroke(3.4), text_size=rv.stroke(9))
             + rv.room(0.3, breaks=[1, 4, 7, 10]) + rv.scale_colour_roygbviz_d()
             + theme(legend_position="none") + labs(title=title, subtitle=sub, caption="Synthetic data",
                                                    x="Month", y="Latency (ms)"))
        p.save(OUT / f"size{k}_{mode}.png", width=width, height=width * 0.68, dpi=1000 / width, verbose=False)
    rv.use(mode)


def labels_fig():
    """Text inside the chart: names at the line ends, and a note at the moment something changed."""
    d = latency()
    after = d.cascade.eq("Cascade C") & d.month.ge(7)
    d.loc[after, "ms"] -= 160  # Cascade C moves to a GPU in July
    ink, soft = PAL.neutrals["text"], PAL.neutrals["text_2"]
    return (ggplot(d, aes("month", "ms", colour="cascade"))
            + geom_vline(xintercept=6.5, colour=PAL.neutrals["rule"], linetype="dashed", size=0.6)
            + annotate("text", x=6.7, y=1000, label="Cascade C moves\nto a GPU", ha="left", va="top", size=8.5,
                       colour=soft, lineheight=1.3)
            + geom_line(size=rv.stroke(1.1))
            + rv.end_labels(d, "month", "ms", "cascade", text_size=8.5)
            + rv.room(0.3, breaks=[1, 4, 7, 10])
            + scale_colour_manual(values=rv.colour_map(["Cascade A", "Cascade B", "Cascade C"]))
            + theme(legend_position="none", plot_title=element_text(color=ink))
            + head("Cascade C overtook the others in July", "Latency per reply, month by month")
            + labs(x="Month", y="Latency (ms)"))


for mode in ("light", "dark"):
    PAL = rv.use(mode)
    scale_fig(OUT / f"scale_{mode}.png")
    pairs_tiles(mode)
    size_tiles(mode)
    labels_fig().save(OUT / f"labels_{mode}.png", width=6.4, height=4, dpi=160, verbose=False)
print("wrote", *sorted(p.name for p in OUT.iterdir()))
