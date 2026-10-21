"""Annotated figure for the Anatomy page. python scripts/anatomy.py

Draws an ordinary Roygbviz chart with plotnine, then numbers its parts with matplotlib. The numbers match the table
on the page. Idea after matplotlib's "Anatomy of a figure" example
(https://matplotlib.org/stable/gallery/showcase/anatomy.html). All data is synthetic.
"""
from pathlib import Path

import matplotlib
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
import pandas as pd
from plotnine import aes, element_blank, geom_line, geom_point, ggplot, labs, theme

import roygbviz as rv

matplotlib.use("Agg")  # draw off-screen, so text sizes can be measured

OUT = Path(__file__).resolve().parent.parent / "assets" / "anatomy"
OUT.mkdir(parents=True, exist_ok=True)
DPI = 150

rng = np.random.default_rng(11)
step = np.arange(0, 21, 2)
df = pd.concat([pd.DataFrame({"step": step, "wer": floor + 12 * np.exp(-step / scale) + rng.normal(0, 0.15, step.size),
                              "model": name})
                for name, floor, scale in (("Whisper", 6, 4), ("Parakeet", 9, 6))])


def chart():
    # Both a legend and end labels, so both can be pointed at. A real figure would use one or the other.
    return (ggplot(df, aes("step", "wer", colour="model"))
            + geom_line(size=rv.stroke(1.2))
            + geom_point(size=rv.stroke(2.2))
            + rv.end_labels(df, "step", "wer", "model", dot=False) + rv.room(0.2)
            + rv.scale_colour_roygbviz_d()
            + theme(legend_position="top", legend_title=element_blank(), figure_size=(9, 6), plot_margin=0.06)
            + labs(title="Word error rate", subtitle="Lower is better", x="Training step (thousands)", y="WER (%)",
                   caption="Synthetic data"))


def draw(mode):
    pal = rv.use(mode)
    ink, bg = pal.neutrals["text"], pal.neutrals["bg"]
    fig = chart().draw()
    FigureCanvasAgg(fig)
    fig.set_dpi(DPI)  # measure text at the resolution it's saved at, or big text comes out wider than measured
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    ax = fig.axes[0]
    to_fig = fig.transFigure.inverted()

    def box(artist):
        """An artist's bounding box in figure fractions."""
        return artist.get_window_extent(renderer).transformed(to_fig)

    def text(s, which=max):
        """The figure's text with this content; ``which`` picks by height when there are several."""
        from matplotlib.text import Text
        hits = [t for t in fig.findobj(Text) if t.get_text() == s and t.get_visible()]
        return which(hits, key=lambda t: box(t).y0)

    def data(x, y):
        return to_fig.transform(ax.transData.transform((x, y)))

    def axes(x, y):
        return to_fig.transform(ax.transAxes.transform((x, y)))

    overlay = fig.add_axes((0, 0, 1, 1), zorder=100)
    overlay.set_axis_off()
    overlay.set_xlim(0, 1)
    overlay.set_ylim(0, 1)

    # Every pointer is built the same way, measured in points so it looks the same across and up: a dot GAP points
    # from the edge of the part (0 when it sits on a line or marker), then a leader LEAD points long to the number.
    GAP, LEAD = 5, 32
    w_in, h_in = fig.get_size_inches()
    r = 2 ** -0.5
    ways = {"right": (1, 0), "up": (0, 1), "down": (0, -1), "up-right": (r, r)}

    def step(xy, way, pts):
        ux, uy = ways[way]
        return xy[0] + ux * pts / 72 / w_in, xy[1] + uy * pts / 72 / h_in

    def edge(artist, side):
        """The middle of one side of an artist's box."""
        b = box(artist)
        return {"right": (b.x1, (b.y0 + b.y1) / 2), "top": ((b.x0 + b.x1) / 2, b.y1),
                "bottom": ((b.x0 + b.x1) / 2, b.y0)}[side]

    style = dict(ha="center", va="center", color=bg, fontsize=10, fontweight="bold",
                 bbox=dict(boxstyle="circle,pad=0.28", fc=ink, ec="none"))

    def badge(n, at, way=None, gap=GAP):
        """Number ``n`` at ``at``, or pointing back at it from direction ``way``."""
        if way is None:
            overlay.text(*at, str(n), **style)
            return
        dot = step(at, way, gap)
        overlay.plot(*dot, "o", ms=3.5, color=ink)
        overlay.annotate(str(n), xy=dot, xytext=step(dot, way, LEAD),
                         arrowprops=dict(arrowstyle="-", color=ink, lw=0.9, shrinkA=0, shrinkB=0), **style)

    whisper = df[df.model == "Whisper"].set_index("step")["wer"]
    parakeet = df[df.model == "Parakeet"].set_index("step")["wer"]
    title, sub, cap = text("Word error rate"), text("Lower is better"), text("Synthetic data")
    xlab, ylab = text("Training step (thousands)"), text("WER (%)")
    legend_key, end_label = text("Whisper", max), text("Parakeet", min)
    tick = next(t for t in ax.get_xticklabels() if t.get_text() == "5")

    badge(1, (0.975, 0.955))                                             # figure: the whole image
    badge(2, data(22.5, 17.5))                                           # panel: an empty patch of it
    badge(3, edge(title, "right"), "right")
    badge(4, edge(sub, "right"), "right")
    badge(5, data(3, (whisper[2] + whisper[4]) / 2), "up-right", gap=0)  # on the line
    badge(6, data(8, parakeet[8]), "up-right", gap=0)                    # on a marker
    badge(7, data(17, ax.get_yticks()[-2]), "up", gap=0)                 # on a gridline
    badge(8, edge(legend_key, "right"), "right")
    badge(9, edge(xlab, "right"), "right")
    badge(10, edge(ylab, "top"), "up")
    badge(11, edge(tick, "bottom"), "down")
    badge(12, axes(0.86, 0), "down", gap=0)                              # on the axis line
    badge(13, edge(end_label, "right"), "right")
    badge(14, edge(cap, "right"), "right")

    fig.savefig(OUT / f"anatomy_{mode}.png", dpi=DPI, facecolor=bg)


for m in ("light", "dark"):
    draw(m)
print("wrote", *sorted(p.name for p in OUT.iterdir()))
