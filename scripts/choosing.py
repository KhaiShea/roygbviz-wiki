"""Figures for the Choosing a plot page. python scripts/choosing.py

One small chart per question, q{1..9}_{light,dark}.png, each the go-to answer for that question. All data is synthetic.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from plotnine import (aes, coord_flip, element_blank, element_text, geom_col, geom_density, geom_hline, geom_line,
                      geom_point, geom_pointrange, geom_segment, geom_smooth, geom_tile, ggplot, labs,
                      scale_colour_manual, scale_fill_manual, scale_y_continuous, theme)

import roygbviz as rv

OUT = Path(__file__).resolve().parent.parent / "assets" / "choosing"
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(21)

STT = ["Whisper", "Parakeet", "Conformer"]
LLM = ["Llama", "Qwen", "Gemma"]
TTS = ["Kokoro", "Piper", "XTTS"]


def head(title, sub):
    """The answer as the title (the page heading asks the question), what is plotted as the subtitle, and the
    synthetic data note."""
    return [labs(title=title, subtitle=sub, caption="Synthetic data"),
            theme(plot_subtitle=element_text(margin={"b": 10, "unit": "pt"}))]


def q1():  # compare amounts
    d = pd.DataFrame({"model": STT + LLM, "score": [91, 86, 79, 84, 88, 75]}).sort_values("score")
    d["model"] = pd.Categorical(d["model"], d["model"])
    return (ggplot(d, aes("model", "score", fill="model")) + geom_col(width=0.7, show_legend=False)
            + coord_flip() + scale_y_continuous(limits=(0, 100), expand=(0, 0))
            + scale_fill_manual(values=rv.colour_map(STT + LLM, order="rainbow"))
            + rv.theme_roygbviz(grid="x") + head("Whisper scores highest", "Score out of 100, by model") + labs(x="", y="Score"))


def q2():  # change over time
    month = np.arange(1, 13)
    d = pd.concat([pd.DataFrame({"month": month, "ms": base - drop * month + rng.normal(0, 12, 12), "cascade": c})
                   for c, base, drop in (("Cascade A", 980, 22), ("Cascade B", 900, 10), ("Cascade C", 1040, 34))])
    return (ggplot(d, aes("month", "ms", colour="cascade")) + geom_line(size=rv.stroke(1.1))
            + rv.end_labels(d, "month", "ms", "cascade", text_size=8) + rv.room(0.3, breaks=[1, 4, 7, 10])
            + rv.scale_colour_roygbviz_d() + theme(legend_position="none")
            + head("Cascade C got fastest", "Latency, month by month") + labs(x="Month", y="Latency (ms)"))


def q3():  # distribution
    d = pd.concat([pd.DataFrame({"ms": rng.normal(mu, sd, 300), "model": m})
                   for m, mu, sd in (("Kokoro", 180, 25), ("Piper", 120, 18), ("XTTS", 260, 45))])
    cols = rv.colour_map(TTS, order="rainbow")
    return (ggplot(d, aes("ms", colour="model", fill="model")) + geom_density(alpha=0.75, size=rv.stroke(0.9))
            + scale_colour_manual(values=cols) + scale_fill_manual(values=rv.shade_map(cols))
            + theme(legend_position="top", legend_title=element_blank())
            + head("Piper starts speaking first", "Time to first audio over 300 replies each") + labs(x="Time to first audio (ms)", y=""))


def q4():  # relationship
    words = rng.uniform(5, 120, 90)
    d = pd.DataFrame({"words": words, "ms": 140 + 6.5 * words + rng.normal(0, 70, words.size)})
    return (ggplot(d, aes("words", "ms")) + geom_point(colour=rv.colour("teal"), size=rv.stroke(1.6), alpha=0.85)
            + geom_smooth(method="lm", se=False, colour=rv.colour("violet"), size=rv.stroke(0.9))
            + rv.theme_roygbviz(grid="xy") + head("Longer replies take longer", "LLM time against the length of its reply")
            + labs(x="Words in the reply", y="LLM time (ms)"))


def q5():  # parts of a whole
    pipes = ["Cascade A", "Cascade B", "Cascade C", "Cascade D"]
    ms = {"STT": [180, 210, 150, 240], "LLM": [520, 410, 640, 380], "TTS": [210, 160, 260, 190]}
    d = pd.DataFrame([(p, s, v) for s, vs in ms.items() for p, v in zip(pipes, vs)], columns=["pipe", "stage", "ms"])
    d["stage"] = pd.Categorical(d["stage"], ["TTS", "LLM", "STT"])
    d["pipe"] = pd.Categorical(d["pipe"], pipes[::-1])
    return (ggplot(d, aes("pipe", "ms", fill="stage")) + geom_col(width=0.68, colour=PAL.surface, size=0.8)
            + coord_flip() + rv.scale_fill_roygbviz_groups(breaks=["STT", "LLM", "TTS"])
            + scale_y_continuous(expand=(0, 0)) + rv.theme_roygbviz(grid="x")
            + theme(legend_position="top", legend_title=element_blank())
            + head("The LLM takes most of the time", "Latency of each stage, per cascade") + labs(x="", y="Latency (ms)"))


def q6():  # difference from a baseline
    # Above zero is slower, so the hot end of the diverging palette (crimson) means worse, which reads naturally.
    pal = PAL
    cold, hot = pal.diverging(3)[0], pal.diverging(3)[-1]
    d = pd.DataFrame({"model": TTS + ["Piper fast", "XTTS small"], "change": [42, -25, 18, -61, 9]})
    d = d.sort_values("change")
    d["model"] = pd.Categorical(d["model"], d["model"])
    d["sign"] = np.where(d["change"] >= 0, "slower", "faster")
    return (ggplot(d, aes("model", "change", fill="sign")) + geom_col(width=0.65, show_legend=False)
            + geom_hline(yintercept=0, colour=pal.neutrals["rule"], size=0.8)
            + coord_flip() + scale_fill_manual(values={"slower": hot, "faster": cold})
            + rv.theme_roygbviz(grid="x") + head("Piper fast saves the most time", "Latency against the baseline voice")
            + labs(x="", y="Latency against the baseline (ms)"))


def q7():  # uncertainty
    d = pd.DataFrame({"model": STT, "wer": [6.2, 7.9, 9.4], "half": [0.9, 1.6, 0.7]})
    d["model"] = pd.Categorical(d["model"], STT[::-1])
    return (ggplot(d, aes("model", "wer", ymin="wer - half", ymax="wer + half", colour="model"))
            + geom_pointrange(size=rv.stroke(0.7), show_legend=False) + coord_flip()
            + scale_colour_manual(values=rv.colour_map(STT, order="rainbow"), guide=None)
            + scale_y_continuous(limits=(0, 12)) + rv.theme_roygbviz(grid="x")
            + head("Whisper's lead is uncertain", "Word error rate with 95% intervals, which overlap") + labs(x="", y="Word error rate (%), 95% interval"))


def q8():  # before and after
    d = pd.DataFrame({"model": STT + ["Wav2Vec", "Canary"], "clean": [5.8, 7.1, 8.9, 9.6, 6.6],
                      "noisy": [9.4, 13.8, 12.1, 17.2, 10.3]}).sort_values("noisy")
    d["model"] = pd.Categorical(d["model"], d["model"])
    long = d.melt(id_vars="model", value_vars=["clean", "noisy"], var_name="audio", value_name="wer")
    return (ggplot(d) + geom_segment(aes(x="clean", xend="noisy", y="model", yend="model"),
                                     colour=rv.colour("grey"), size=rv.stroke(1.4))
            + geom_point(aes("wer", "model", colour="audio"), data=long, size=rv.stroke(3.2))
            + scale_colour_manual(values={"clean": rv.colour("teal"), "noisy": rv.colour("red")})
            + rv.theme_roygbviz(grid="x") + theme(legend_position="top", legend_title=element_blank())
            + head("Noise hurts Wav2Vec most", "Word error rate on clean and noisy audio") + labs(x="Word error rate (%)", y=""))


def q9():  # two categories at once
    noise = ["Quiet", "Café", "Street", "Wind"]
    base = {"Whisper": 5.5, "Parakeet": 7.0, "Conformer": 8.5}
    hit = {"Quiet": 0, "Café": 2.5, "Street": 5, "Wind": 9}
    d = pd.DataFrame([(m, n, base[m] + hit[n] * (1 + 0.3 * k) + rng.normal(0, 0.4))
                      for k, m in enumerate(STT) for n in noise], columns=["model", "noise", "wer"])
    d["noise"] = pd.Categorical(d["noise"], noise)
    d["model"] = pd.Categorical(d["model"], STT[::-1])
    return (ggplot(d, aes("noise", "model", fill="wer")) + geom_tile(colour=PAL.surface, size=1.5)
            + rv.scale_fill_roygbviz_c("violet") + theme(panel_grid_major=element_blank())
            + head("Wind is hardest for every model", "Word error rate by background noise") + labs(x="", y="", fill="WER %"))


QUESTIONS = [q1, q2, q3, q4, q5, q6, q7, q8, q9]

PAL = None  # the active palette. rv.get_palette() with no mode always gives light, so keep what rv.use() returns

for mode in ("light", "dark"):
    PAL = rv.use(mode)
    for i, q in enumerate(QUESTIONS, start=1):
        q().save(OUT / f"q{i}_{mode}.png", width=4.6, height=3.4, dpi=180, verbose=False)
print("wrote", *sorted(p.name for p in OUT.iterdir()))
