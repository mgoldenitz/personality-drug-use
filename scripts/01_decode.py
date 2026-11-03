"""Decode the UCI Drug Consumption (quantified) file into readable columns.

Input:  data/raw/drug_consumption.data (1,885 rows, 32 columns, no header)
Output: data/processed/respondents.csv (one row per respondent, wide)
        data/processed/use_long.csv    (one row per respondent x substance)
The category codes below are the ones listed on the UCI dataset page.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
COLS = ("ID Age Gender Education Country Ethnicity Nscore Escore Oscore Ascore Cscore "
        "Impulsive SS Alcohol Amphet Amyl Benzos Caff Cannabis Choc Coke Crack Ecstasy "
        "Heroin Ketamine Legalh LSD Meth Mushrooms Nicotine Semer VSA").split()
SUBSTANCES = COLS[13:]

AGE = {-0.95197: "18-24", -0.07854: "25-34", 0.49788: "35-44", 1.09449: "45-54",
       1.82213: "55-64", 2.59171: "65+"}
GENDER = {0.48246: "Female", -0.48246: "Male"}
EDUCATION = {-2.43591: "Left school before 16", -1.7379: "Left school at 16",
             -1.43719: "Left school at 17", -1.22751: "Left school at 18",
             -0.61113: "Some college, no degree", -0.05921: "Professional certificate",
             0.45468: "University degree", 1.16365: "Master's degree", 1.98437: "Doctorate"}
COUNTRY = {-0.09765: "Australia", 0.24923: "Canada", -0.46841: "New Zealand",
           -0.28519: "Other", 0.21128: "Ireland", 0.96082: "UK", -0.57009: "USA"}
ETHNICITY = {-0.50212: "Asian", -1.10702: "Black", 1.90725: "Mixed Black/Asian",
             0.126: "Mixed White/Asian", -0.22166: "Mixed White/Black", 0.1144: "Other",
             -0.31685: "White"}
USE = {"CL0": "Never used", "CL1": "Used over a decade ago", "CL2": "Used in last decade",
       "CL3": "Used in last year", "CL4": "Used in last month", "CL5": "Used in last week",
       "CL6": "Used in last day"}
TRAITS = {"Nscore": "Neuroticism", "Escore": "Extraversion", "Oscore": "Openness",
          "Ascore": "Agreeableness", "Cscore": "Conscientiousness",
          "Impulsive": "Impulsivity", "SS": "Sensation seeking"}


def main():
    d = pd.read_csv(ROOT / "data/raw/drug_consumption.data", header=None, names=COLS)
    assert len(d) == 1885 and d["ID"].is_unique
    for col, codes in [("Age", AGE), ("Gender", GENDER), ("Education", EDUCATION),
                       ("Country", COUNTRY), ("Ethnicity", ETHNICITY)]:
        d[col] = d[col].round(5).map(codes)
        assert d[col].notna().all(), col
    d["Degree"] = d["Education"].isin(["University degree", "Master's degree", "Doctorate"])
    d = d.rename(columns=TRAITS)
    # Semeron is a fictitious drug included to detect over-claiming.
    d["Overclaimer"] = d["Semer"] != "CL0"
    for s in SUBSTANCES:
        d[s + "_level"] = d[s].str[2].astype(int)
    d.to_csv(ROOT / "data/processed/respondents.csv", index=False)

    long = d.melt(id_vars=["ID", "Overclaimer"], value_vars=SUBSTANCES,
                  var_name="Substance", value_name="Code")
    long["Level"] = long["Code"].str[2].astype(int)
    long["Use"] = long["Code"].map(USE)
    long["Last_year"] = long["Level"] >= 3
    long["Ever"] = long["Level"] >= 1
    long.to_csv(ROOT / "data/processed/use_long.csv", index=False)
    print(f"{len(d)} respondents, {d['Overclaimer'].sum()} claimed Semeron use")


if __name__ == "__main__":
    main()
