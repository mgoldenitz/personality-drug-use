"""Descriptives and logistic regressions for last-year use of nine substances.

Analysis set: all respondents except the 8 who claimed to have used Semeron.
Outcome: used in the last year (CL3 or more recent) vs not.
Predictors: seven trait scores (already standardized in the UCI file, so odds
ratios are per 1 SD), plus age group, gender and holding a university degree.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.outliers_influence import variance_inflation_factor

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
TRAITS = ["Neuroticism", "Extraversion", "Openness", "Agreeableness",
          "Conscientiousness", "Impulsivity", "Sensation seeking"]
SUBS = ["Alcohol", "Nicotine", "Cannabis", "Benzos", "Amphet", "Coke",
        "Ecstasy", "Mushrooms", "LSD"]
GROUP = {"Alcohol": "Legal", "Nicotine": "Legal", "Cannabis": "Cannabis",
         "Benzos": "Depressant", "Amphet": "Stimulant", "Coke": "Stimulant",
         "Ecstasy": "Stimulant", "Mushrooms": "Hallucinogen", "LSD": "Hallucinogen"}


def safe(name):
    return name.replace(" ", "_")


def main():
    d = pd.read_csv(ROOT / "data/processed/respondents.csv")
    d = d[~d["Overclaimer"]].copy()
    d = d.rename(columns={t: safe(t) for t in TRAITS})
    # 45+ is one band: the 55-64 and 65+ groups (111 people) have almost no
    # last-year users of some substances, which stops the models converging.
    d["Age"] = pd.Categorical(d["Age"].replace({"45-54": "45+", "55-64": "45+", "65+": "45+"}),
                              ["18-24", "25-34", "35-44", "45+"])
    print(f"Analysis set: {len(d)} respondents")

    # Prevalence of last-year use
    prev = pd.DataFrame({"Substance": SUBS,
                         "Group": [GROUP[s] for s in SUBS],
                         "Last_year_n": [(d[s + "_level"] >= 3).sum() for s in SUBS],
                         "Never_n": [(d[s + "_level"] == 0).sum() for s in SUBS]})
    prev["Last_year_pct"] = (100 * prev["Last_year_n"] / len(d)).round(1)
    prev.to_csv(RES / "prevalence.csv", index=False)
    print(prev.to_string(index=False))

    # Trait means and standardized differences: last-year users vs never users
    rows = []
    for s in SUBS:
        users = d[d[s + "_level"] >= 3]
        never = d[d[s + "_level"] == 0]
        for t in TRAITS:
            a, b = users[safe(t)], never[safe(t)]
            sp = np.sqrt(((len(a) - 1) * a.var() + (len(b) - 1) * b.var()) / (len(a) + len(b) - 2))
            rows.append({"Substance": s, "Trait": t, "Users_mean": a.mean(),
                         "Never_mean": b.mean(), "Users_n": len(a), "Never_n": len(b),
                         "Cohens_d": (a.mean() - b.mean()) / sp})
    prof = pd.DataFrame(rows).round(3)
    prof.to_csv(RES / "trait_profiles.csv", index=False)

    # Collinearity among traits
    X = d[[safe(t) for t in TRAITS]].assign(const=1.0)
    vif = pd.DataFrame({"Trait": TRAITS,
                        "VIF": [variance_inflation_factor(X.values, i) for i in range(len(TRAITS))]}).round(2)
    vif.to_csv(RES / "vif.csv", index=False)
    print(vif.to_string(index=False))
    print("r(Impulsivity, Sensation seeking) =",
          round(d["Impulsivity"].corr(d["Sensation_seeking"]), 2))

    # Logistic regression per substance
    rhs = " + ".join(safe(t) for t in TRAITS) + " + C(Age) + C(Gender) + Degree"
    out = []
    for s in SUBS:
        d["y"] = (d[s + "_level"] >= 3).astype(int)
        m = smf.logit(f"y ~ {rhs}", data=d).fit(disp=0, maxiter=200)
        assert m.mle_retvals["converged"], s
        ci = m.conf_int()
        for t in TRAITS:
            k = safe(t)
            out.append({"Substance": s, "Group": GROUP[s], "Trait": t,
                        "OR": np.exp(m.params[k]), "CI_low": np.exp(ci.loc[k, 0]),
                        "CI_high": np.exp(ci.loc[k, 1]), "p": m.pvalues[k],
                        "n": int(m.nobs), "Pseudo_R2": m.prsquared})
    res = pd.DataFrame(out)
    res["p_holm"] = multipletests(res["p"], method="holm")[1]
    res = res.round(4)
    res.to_csv(RES / "logit_odds_ratios.csv", index=False)
    show = res.pivot(index="Trait", columns="Substance", values="OR")[SUBS].round(2)
    print(show.to_string())
    print(res.groupby("Substance")["Pseudo_R2"].first().round(3)[SUBS].to_string())
    print("Significant after Holm:", (res["p_holm"] < 0.05).sum(), "of", len(res))


if __name__ == "__main__":
    main()
