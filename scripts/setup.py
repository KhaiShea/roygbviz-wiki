"""Figures for the Setup page. python scripts/setup.py

first_chart_{light,dark}.png is exactly the "first chart" script on the page. modes.png puts the same chart in all
three modes side by side. All data is synthetic.
"""
from pathlib import Path

import pandas as pd
from PIL import Image
from plotnine import aes, geom_col, ggplot, labs

import roygbviz as rv

OUT = Path(__file__).resolve().parent.parent / "assets" / "setup"
OUT.mkdir(parents=True, exist_ok=True)


def first_chart(title="My first Roygbviz chart"):
    df = pd.DataFrame({
        "model": ["Whisper", "Parakeet", "Conformer"],
        "wer": [6.1, 8.4, 10.2],
    })
    return (ggplot(df, aes("model", "wer", fill="model"))
            + geom_col(show_legend=False)
            + rv.scale_fill_roygbviz_d()
            + labs(title=title, x="", y="Word error rate (%)",
                   caption="Synthetic data"))


for mode in ("light", "dark"):
    rv.use(mode)
    first_chart().save(OUT / f"first_chart_{mode}.png", width=6, height=4, dpi=150, verbose=False)

tiles = []
for mode in ("light", "dark", "cream"):
    rv.use(mode)
    f = OUT / f"_tile_{mode}.png"
    first_chart(title=f'rv.use("{mode}")').save(f, width=4, height=3.2, dpi=150, verbose=False)
    tiles.append(Image.open(f).convert("RGB"))
    f.unlink()
sheet = Image.new("RGB", (sum(t.width for t in tiles), max(t.height for t in tiles)))
x = 0
for t in tiles:
    sheet.paste(t, (x, 0))
    x += t.width
sheet.save(OUT / "modes.png")
print("wrote", *sorted(p.name for p in OUT.iterdir()))
