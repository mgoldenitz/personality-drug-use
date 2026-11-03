"""Heatmap of odds ratios (traits x substances) and Tableau-ready exports."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

ROOT = Path(__file__).resolve().parents[1]
SUBS = ["Alcohol", "Nicotine", "Cannabis", "Benzos", "Amphet", "Coke",
        "Ecstasy", "Mushrooms", "LSD"]
LABEL = {"Benzos": "Benzodiazepines", "Amphet": "Amphetamines", "Coke": "Cocaine"}
TRAITS = ["Sensation seeking", "Openness", "Impulsivity", "Neuroticism",
          "Extraversion", "Agreeableness", "Conscientiousness"]

r = pd.read_csv(ROOT / "results/logit_odds_ratios.csv")
or_ = r.pivot(index="Trait", columns="Substance", values="OR").loc[TRAITS, SUBS]
sig = r.pivot(index="Trait", columns="Substance", values="p_holm").loc[TRAITS, SUBS] < 0.05

fig, ax = plt.subplots(figsize=(10, 4.8))
im = ax.imshow(np.log2(or_.values), cmap="RdBu_r", norm=TwoSlopeNorm(0, -1.2, 1.2), aspect="auto")
for i in range(len(TRAITS)):
    for j in range(len(SUBS)):
        v = or_.iloc[i, j]
        ax.text(j, i, f"{v:.2f}" + ("*" if sig.iloc[i, j] else ""), ha="center", va="center",
                fontsize=9, color="white" if abs(np.log2(v)) > 0.8 else "#222")
ax.set_xticks(range(len(SUBS)), [LABEL.get(s, s) for s in SUBS], rotation=30, ha="right")
ax.set_yticks(range(len(TRAITS)), TRAITS)
ax.set_title("Odds of last-year use per 1 SD higher trait score\n"
             "(adjusted for the other traits, age, gender and degree; * Holm p < 0.05)",
             fontsize=11, loc="left")
ax.tick_params(length=0)
for s in ax.spines.values():
    s.set_visible(False)
fig.tight_layout()
fig.savefig(ROOT / "images/odds_ratio_heatmap.png", dpi=200)

# Tableau exports
r.assign(Substance_label=r["Substance"].map(lambda s: LABEL.get(s, s)),
         Significant=r["p_holm"] < 0.05).to_csv(ROOT / "tableau/odds_ratios.csv", index=False)
d = pd.read_csv(ROOT / "data/processed/respondents.csv")
d = d[~d["Overclaimer"]]
keep = ["ID", "Age", "Gender", "Education", "Country"] + TRAITS + [s + "_level" for s in SUBS]
d[keep].to_csv(ROOT / "tableau/respondents.csv", index=False)
long = pd.read_csv(ROOT / "data/processed/use_long.csv")
long = long[~long["Overclaimer"] & long["Substance"].isin(SUBS)]
long.assign(Substance_label=long["Substance"].map(lambda s: LABEL.get(s, s))).drop(
    columns="Overclaimer").to_csv(ROOT / "tableau/use_long.csv", index=False)
print("done")
