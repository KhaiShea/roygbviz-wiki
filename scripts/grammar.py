"""Figures for the Grammar of graphics page. python scripts/grammar.py

step{1..6}_{light,dark}.png build one chart in six steps, one grammar part at a time, each its own image so it can
be enlarged on its own. before_after_{light,dark}.png is the finished chart with plotnine's defaults, then with
Roygbviz. All data is synthetic.
"""
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from PIL import Image
from plotnine import (aes, element_text, facet_wrap, geom_point, geom_smooth, ggplot, labs, theme, theme_gray,
                      theme_set)

import roygbviz as rv

OUT = Path(__file__).resolve().parent.parent / "assets" / "grammar"
OUT.mkdir(parents=True, exist_ok=True)

# Speech-to-text latency against clip length, for three models on two kinds of hardware.
rng = np.random.default_rng(3)
rows = []
for device, speed in (("CPU", 1.0), ("GPU", 0.35)):
    for k, model in enumerate(["Whisper", "Parakeet", "Conformer"]):
        seconds = rng.uniform(2, 30, 18)
        latency = speed * (120 + (28 + 14 * k) * seconds) + rng.normal(0, 40 * speed, seconds.size)
        rows.append(pd.DataFrame({"seconds": seconds, "latency": latency, "model": model, "device": device}))
df = pd.concat(rows, ignore_index=True)

CAPTION = "Synthetic data"


def steps():
    """The chart, one grammar part at a time. Each entry is (step name, code it adds, plot)."""
    p = ggplot(df, aes("seconds", "latency", colour="model"))
    out = [("1. Data and mapping", 'ggplot(df, aes("seconds", "latency", colour="model"))', p)]
    p = p + geom_point()
    out.append(("2. Geom", "+ geom_point()", p))
    p = p + geom_smooth(method="lm", se=False)
    out.append(("3. Stat", '+ geom_smooth(method="lm", se=False)', p))
    p = p + rv.scale_colour_roygbviz_d()
    out.append(("4. Scale", "+ rv.scale_colour_roygbviz_d()", p))
    p = p + facet_wrap("device")
    out.append(("5. Facets", '+ facet_wrap("device")', p))
    p = p + labs(x="Clip length (s)", y="Latency (ms)", colour="")
    out.append(("6. Labels", '+ labs(x="Clip length (s)", y="Latency (ms)")', p))
    return out


def tile(p, title, sub, path, dpi=130):
    # The bottom margin on the subtitle keeps the title block clear of the facet labels below it.
    g = (p + labs(title=title, subtitle=sub, caption=CAPTION)
         + theme(plot_subtitle=element_text(family="monospace", size=8, margin={"b": 14, "unit": "pt"})))
    g.save(path, width=4.6, height=3.4, dpi=dpi, verbose=False)
    return Image.open(path).convert("RGB")


def sheet(tiles, cols, bg):
    w, h = tiles[0].size
    rows = -(-len(tiles) // cols)
    out = Image.new("RGB", (cols * w, rows * h), bg)
    for i, t in enumerate(tiles):
        out.paste(t, ((i % cols) * w, (i // cols) * h))
    return out


final = None
for mode in ("light", "dark"):
    pal = rv.use(mode)
    for i, (title, code, p) in enumerate(steps(), start=1):
        tile(p, title, code, OUT / f"step{i}_{mode}.png", dpi=180)
        final = p

    after = tile(final, "With Roygbviz", "rv.use() and the Roygbviz scale", OUT / "_after.png")
    (OUT / "_after.png").unlink()

    # plotnine as it comes: its default theme, colours and fonts
    matplotlib.rcdefaults()
    theme_set(theme_gray())
    plain = (ggplot(df, aes("seconds", "latency", colour="model")) + geom_point() + geom_smooth(method="lm", se=False)
             + facet_wrap("device") + labs(x="Clip length (s)", y="Latency (ms)", colour=""))
    before = tile(plain, "plotnine defaults", "no Roygbviz", OUT / "_before.png")
    (OUT / "_before.png").unlink()
    sheet([before, after], 2, pal.neutrals["bg"]).save(OUT / f"before_after_{mode}.png")

print("wrote", *sorted(p.name for p in OUT.iterdir()))
