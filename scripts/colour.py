"""Figures for the Colour page. python scripts/colour.py

Seven figures, each in light and dark: the twelve colours, their levels, shading, the magnitude ramps, a diverging
heatmap, contrast against each paper, and the nine model colours under simulated colour blindness. All data is
synthetic.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from plotnine import (aes, coord_flip, element_blank, element_text, facet_wrap, geom_col, geom_hline, geom_line,
                      geom_ribbon, geom_text, geom_tile, ggplot, labs, scale_colour_identity, scale_colour_manual,
                      scale_fill_identity, scale_fill_manual, scale_x_continuous, scale_x_discrete, scale_y_continuous,
                      scale_y_discrete, theme)

import roygbviz as rv
from roygbviz import _colour as C  # private, but it's the library's own maths for contrast and colour blindness

OUT = Path(__file__).resolve().parent.parent / "assets" / "colour"
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(8)

FAMILIES = [("STT", ["red", "orange", "yellow"]), ("LLM", ["green", "teal", "blue"]), ("TTS", ["indigo", "violet", "pink"])]
TWELVE = [c for stage, models in FAMILIES for c in [stage] + models]
PAL = None  # the active palette; rv.get_palette() with no mode always gives light, so keep what rv.use() returns


def hex_of(name):
    return PAL.roles.get(name) or PAL.groups[name]


def readable_on(fill):
    """Ink or white, whichever reads better on this fill."""
    ink = "#1B2A41"
    return ink if C.contrast(ink, fill) >= C.contrast("#FFFFFF", fill) else "#FFFFFF"


def head(title, sub, caption="Synthetic data"):
    return [labs(title=title, subtitle=sub, caption=caption),
            theme(plot_subtitle=element_text(margin={"b": 10, "unit": "pt"}))]


def bare():
    """No gridlines or axis line, for swatches."""
    return theme(panel_grid_major=element_blank(), axis_line_x=element_blank())


def palette_fig():
    rows = []
    for r, (stage, models) in enumerate(FAMILIES):
        for c, name in enumerate([stage] + models):
            h = hex_of(name)
            label = f"{name} stage" if name == stage else name
            rows.append((c, -r, f"{label}\n{h}", h, readable_on(h)))
    d = pd.DataFrame(rows, columns=["x", "y", "label", "fill", "ink"])
    return (ggplot(d, aes("x", "y")) + geom_tile(aes(fill="fill"), width=0.94, height=0.9)
            + geom_text(aes(label="label", colour="ink"), size=8.5, lineheight=1.4)
            + scale_fill_identity() + scale_colour_identity()
            + scale_x_continuous(breaks=[], expand=(0, 0.02)) + scale_y_continuous(breaks=[], expand=(0, 0.02))
            + bare() + head("Twelve colours, three families", "Each stage colour leads its own three model colours",
                            caption=f"Hex codes for {PAL.mode} mode") + labs(x="", y=""))


def levels_fig():
    names = ["deeper 2", "deeper 1", "default", "softer 1", "softer 2"]
    rows = [(name, k, h) for name in TWELVE for k, h in enumerate(PAL.levels(name, 5))]
    d = pd.DataFrame(rows, columns=["colour", "level", "fill"])
    d["colour"] = pd.Categorical(d["colour"], TWELVE[::-1])
    return (ggplot(d, aes("level", "colour", fill="fill")) + geom_tile(colour=PAL.surface, size=1.2)
            + scale_fill_identity() + scale_x_continuous(breaks=range(5), labels=names, expand=(0, 0))
            + bare() + head("Five levels of every colour", "The default sits in the middle",
                            caption=f"Colours for {PAL.mode} mode") + labs(x="", y=""))


def shading_fig():
    month = np.arange(1, 13)
    cols = {"Cascade A": rv.colour("teal"), "Cascade B": rv.colour("violet")}
    d = pd.concat([pd.DataFrame({"month": month, "ms": base - drop * month + rng.normal(0, 8, 12), "cascade": c,
                                 "spread": spread})
                   for c, base, drop, spread in (("Cascade A", 900, 18, 45), ("Cascade B", 640, 6, 30))])
    d["low"], d["high"] = d.ms - d.spread, d.ms + d.spread
    return (ggplot(d, aes("month", "ms", colour="cascade", fill="cascade"))
            + geom_ribbon(aes(ymin="low", ymax="high"), colour="none", alpha=0.45)  # see-through, so the line shows
            + geom_line(size=rv.stroke(1.2))
            + rv.end_labels(d, "month", "ms", "cascade", text_size=8.5) + rv.room(0.22, breaks=[1, 4, 7, 10])
            + scale_colour_manual(values=cols) + scale_fill_manual(values=rv.shade_map(cols))
            + theme(legend_position="none")
            + head("Lines in the colour, bands in its shade", "Latency with its typical range, month by month")
            + labs(x="Month", y="Latency (ms)"))


def ramps_fig():
    hues = ["red", "orange", "yellow", "green", "teal", "blue", "indigo", "violet", "pink", "spectrum"]
    rows = [(h, k, c) for h in hues for k, c in enumerate(PAL.sequential(h, 9))]
    d = pd.DataFrame(rows, columns=["hue", "step", "fill"])
    d["hue"] = pd.Categorical(d["hue"], hues[::-1])
    return (ggplot(d, aes("step", "hue", fill="fill")) + geom_tile(colour=PAL.surface, size=1)
            + scale_fill_identity() + scale_x_continuous(breaks=[0, 8], labels=["low", "high"], expand=(0, 0))
            + bare() + head("A ramp for every hue", "Low values blend into the paper, high values stand out",
                            caption=f"Colours for {PAL.mode} mode") + labs(x="", y=""))


def diverging_fig():
    stt, llm = ["Whisper", "Parakeet", "Conformer"], ["Llama", "Qwen", "Gemma"]
    change = [[0, -45, 60], [-80, -120, -20], [95, 40, 150]]
    d = pd.DataFrame([(s, l, change[i][j]) for i, s in enumerate(stt) for j, l in enumerate(llm)],
                     columns=["stt", "llm", "change"])
    d["stt"] = pd.Categorical(d["stt"], stt[::-1])
    d["llm"] = pd.Categorical(d["llm"], llm)
    d["label"] = [f"{v:+d}" if v else "0" for v in d.change]
    # The tile's own colour, worked out the way the scale does it, then whichever text reads better on it.
    cold, mid, hot = PAL.diverging(3)  # returned cold to hot
    d["ink"] = [readable_on(C.mix(mid, hot if v > 0 else cold, abs(v) / 150)) for v in d.change]
    return (ggplot(d, aes("llm", "stt", fill="change")) + geom_tile(colour=PAL.surface, size=2)
            + geom_text(aes(label="label", colour="ink"), size=10)
            + rv.scale_fill_roygbviz_div(limits=(-150, 150))
            + scale_colour_identity()
            + bare() + head("Hot is slower, cold is faster", "Latency against Whisper with Llama (ms), for each pairing")
            + labs(x="Language model", y="Speech to text", fill="ms"))


def contrast_fig():
    papers = [("light", "White paper"), ("cream", "Cream paper"), ("dark", "Navy paper")]
    rows = []
    for mode, label in papers:
        p = rv.get_palette(mode)
        for name in TWELVE:
            h = p.roles.get(name) or p.groups[name]
            rows.append((label, name, h, C.contrast(h, p.surface)))
    d = pd.DataFrame(rows, columns=["paper", "colour", "fill", "ratio"])
    d["paper"] = pd.Categorical(d["paper"], [l for _, l in papers])
    d["colour"] = pd.Categorical(d["colour"], TWELVE[::-1])
    return (ggplot(d, aes("colour", "ratio", fill="fill")) + geom_col(width=0.75)
            + geom_hline(yintercept=3, colour=PAL.neutrals["muted"], linetype="dashed", size=0.6)  # 3:1, the guide
            + scale_fill_identity() + coord_flip() + facet_wrap("paper")
            + scale_y_continuous(breaks=[1, 3, 5, 7, 9, 11, 13], expand=(0, 0, 0.05, 0))
            + rv.theme_roygbviz(grid="x")
            + head("How much each colour stands out", "Contrast with the paper. The usual guide for chart marks is 3:1",
                   caption="Measured with the WCAG contrast formula") + labs(x="", y="Contrast ratio"))


def simulate(hex_, cvd):
    """How a colour looks with a strong red-weak (protan) or green-weak (deutan) colour vision, after Machado et al."""
    r, g, b = C.hex_to_linear(hex_)
    m = C._MACHADO[cvd]
    return C.linear_to_hex(tuple(max(0.0, min(1.0, m[k][0] * r + m[k][1] * g + m[k][2] * b)) for k in range(3)))


def colourblind_fig():
    order = list(rv.palettes._SERIES_ORDER)
    views = [("Typical vision", None), ("Red-weak (protan)", "protan"), ("Green-weak (deutan)", "deutan")]
    rows = []
    for view, cvd in views:
        for k, name in enumerate(order, start=1):
            h = PAL.roles[name]
            rows.append((view, f"{k}\n{name}", simulate(h, cvd) if cvd else h))
    d = pd.DataFrame(rows, columns=["view", "colour", "fill"])
    d["view"] = pd.Categorical(d["view"], [v for v, _ in views][::-1])
    d["colour"] = pd.Categorical(d["colour"], [f"{k}\n{n}" for k, n in enumerate(order, start=1)])
    return (ggplot(d, aes("colour", "view", fill="fill")) + geom_tile(colour=PAL.surface, size=2)
            + scale_fill_identity() + scale_x_discrete(expand=(0, 0)) + scale_y_discrete(expand=(0, 0))
            + bare() + head("The model colours, as colour-blind readers see them",
                            "In the order they're handed out. Colours 6 and 7 (pink and blue) are the weak pair",
                            caption="Simulated after Machado, Oliveira and Fernandes (2009), full strength")
            + labs(x="", y=""))


FIGS = {"palette": (palette_fig, 7, 3.9), "levels": (levels_fig, 6, 6.2), "shading": (shading_fig, 6.4, 4),
        "ramps": (ramps_fig, 6.4, 5.2), "diverging": (diverging_fig, 6, 4.4), "contrast": (contrast_fig, 9, 5),
        "colourblind": (colourblind_fig, 8, 3.6)}

for mode in ("light", "dark"):
    PAL = rv.use(mode)
    for name, (fn, w, h) in FIGS.items():
        fn().save(OUT / f"{name}_{mode}.png", width=w, height=h, dpi=160, verbose=False)
print("wrote", *sorted(p.name for p in OUT.iterdir()))
