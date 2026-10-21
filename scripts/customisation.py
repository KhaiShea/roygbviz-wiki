"""Figures for the Customisation page. python scripts/customisation.py

One chart on each of the three papers, the four gridline settings, a chart before and after a few theme() tweaks, and
a plain matplotlib chart. Everything but the papers comes in light and dark. All data is synthetic.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from plotnine import (aes, element_blank, element_text, geom_col, geom_line, geom_point, ggplot, labs,  # noqa: E402
                      position_dodge, theme)

import roygbviz as rv  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "assets" / "customisation"
OUT.mkdir(parents=True, exist_ok=True)
CAPTION = "Synthetic data"


def latency():
    """The same noise every call, so every mode shows the same data."""
    rng, month = np.random.default_rng(5), np.arange(1, 13)
    return pd.concat([pd.DataFrame({"month": month, "ms": base - drop * month + rng.normal(0, 10, 12), "cascade": c})
                      for c, base, drop in (("Cascade A", 900, 14), ("Cascade B", 760, 8), ("Cascade C", 980, 30))])


def lines(title, sub):
    d = latency()
    return (ggplot(d, aes("month", "ms", colour="cascade")) + geom_line(size=rv.stroke(1.1))
            + rv.end_labels(d, "month", "ms", "cascade", text_size=8.5) + rv.room(0.3, breaks=[1, 4, 7, 10])
            + rv.scale_colour_roygbviz_d() + theme(legend_position="none")
            + labs(title=title, subtitle=sub, caption=CAPTION, x="Month", y="Latency (ms)"))


def points(grid):
    rng = np.random.default_rng(9)
    words = rng.uniform(5, 120, 70)
    d = pd.DataFrame({"words": words, "ms": 140 + 6.5 * words + rng.normal(0, 70, words.size)})
    return (ggplot(d, aes("words", "ms")) + geom_point(colour=rv.colour("teal"), size=rv.stroke(1.6), alpha=0.85)
            + rv.theme_roygbviz(grid=grid)
            + labs(title=f'grid="{grid}"', subtitle="LLM time against reply length", caption=CAPTION,
                   x="Words in the reply", y="LLM time (ms)"))


def scores():
    d = pd.DataFrame([(m, n, v) for m, vals in (("Whisper", (94, 88, 79)), ("Parakeet", (92, 84, 70)),
                                                 ("Conformer", (90, 81, 74)))
                      for n, v in zip(("Quiet", "Café", "Street"), vals)], columns=["model", "noise", "score"])
    d["noise"] = pd.Categorical(d["noise"], ["Quiet", "Café", "Street"])
    d["model"] = pd.Categorical(d["model"], ["Whisper", "Parakeet", "Conformer"])
    return (ggplot(d, aes("noise", "score", fill="model")) + geom_col(position=position_dodge(0.8), width=0.75)
            + rv.scale_fill_roygbviz_d())


def tweaks():
    before = scores() + labs(title="As it comes", subtitle="Score out of 100, by background noise",
                             caption=CAPTION, x="", y="Score")
    after = (scores() + labs(title="Street noise costs every model", subtitle="Score out of 100, by background noise",
                             caption=CAPTION, x="", y="Score")
             + theme(legend_position="top", legend_title=element_blank(),
                     plot_subtitle=element_text(margin={"b": 10, "unit": "pt"})))
    return before, after


def mpl_fig(path, pal):
    d = latency()
    fig, ax = plt.subplots(figsize=(6.4, 4), dpi=160, layout="constrained")
    fig.get_layout_engine().set(w_pad=0.15, h_pad=0.2)  # room round the edge, and for the caption at the bottom
    for name, g in d.groupby("cascade"):
        ax.plot(g["month"], g["ms"], label=name)
    ax.set_title("Cascade C got fastest", loc="left")
    ax.set_xlabel("Month")
    ax.set_ylabel("Latency (ms)")
    ax.set_xticks([1, 4, 7, 10])
    ax.legend(loc="upper right")
    fig.text(0.02, 0.025, CAPTION, size=7.7, color=pal.neutrals["muted"])
    fig.savefig(path)
    plt.close(fig)


for mode in ("light", "cream", "dark"):
    rv.use(mode)
    lines(f"{mode.capitalize()} paper", f'rv.use("{mode}")').save(OUT / f"mode_{mode}.png", width=4.6, height=3.4,
                                                               dpi=180, verbose=False)

for mode in ("light", "dark"):
    pal = rv.use(mode)
    for grid in ("y", "x", "xy", "none"):
        points(grid).save(OUT / f"grid_{grid}_{mode}.png", width=4.6, height=3.4, dpi=180, verbose=False)
    for name, p in zip(("before", "after"), tweaks()):
        p.save(OUT / f"tweak_{name}_{mode}.png", width=4.6, height=3.4, dpi=180, verbose=False)
    mpl_fig(OUT / f"matplotlib_{mode}.png", pal)
rv.use("light")
print("wrote", *sorted(p.name for p in OUT.iterdir()))
