"""Quick taste figure for the Start here page, in light, dark and cream. python scripts/start_here.py

All data is synthetic.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from plotnine import aes, geom_line, ggplot, labs, theme

import roygbviz as rv

OUT = Path(__file__).resolve().parent.parent / "assets" / "start-here"
OUT.mkdir(parents=True, exist_ok=True)

# Three speech-to-text models learning over 20 thousand training steps. Each settles at its own floor.
rng = np.random.default_rng(7)
step = np.arange(21)
df = pd.concat([pd.DataFrame({"step": step, "wer": floor + 14 * np.exp(-step / (3 + k)) + rng.normal(0, 0.2, step.size),
                              "model": name})
                for k, (name, floor) in enumerate([("Whisper", 6), ("Parakeet", 8), ("Conformer", 10)])])

for mode in ("light", "dark", "cream"):
    rv.use(mode)
    p = (ggplot(df, aes("step", "wer", colour="model"))
         + geom_line(size=rv.stroke(1.2))
         + rv.end_labels(df, "step", "wer", "model") + rv.room()
         + rv.scale_colour_roygbviz_d()
         + theme(legend_position="none")
         + labs(title="Word error rate", subtitle="Lower is better", x="Training step (thousands)", y="WER (%)",
                caption="Synthetic data"))
    p.save(OUT / f"taste_{mode}.png", width=6, height=3.8, dpi=160, verbose=False)
    print("wrote", OUT / f"taste_{mode}.png")
