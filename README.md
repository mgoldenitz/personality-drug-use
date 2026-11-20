# Personality and Drug Use

This project examines whether Big Five personality traits, impulsivity and sensation seeking predict use of hallucinogens (LSD, mushrooms) differently from use of alcohol, nicotine, stimulants or benzodiazepines.

Interactive dashboard: [Personality and Drug Use on Tableau Public](https://public.tableau.com/app/profile/michael.goldenitz/viz/PersonalityandDrugUse/Dashboard)

![Tableau dashboard](images/tableau_dashboard.png)

![Odds ratio heatmap](images/odds_ratio_heatmap.png)

## Key findings

- Sensation seeking is linked with last-year use of every substance studied. A person one standard deviation higher on sensation seeking than another has 1.39 to 2.00 times the odds of having used the substance in the last year, after adjusting for the other traits, age, gender and education. The alcohol result (1.46) does not stay significant after the Holm correction.
- Openness to experience separates hallucinogens and cannabis from the rest. The odds ratio is 1.97 for LSD, 1.85 for mushrooms and 2.27 for cannabis, against 1.05 for cocaine and 0.86 for alcohol.
- Neuroticism is linked with one substance: benzodiazepines (odds ratio 1.57), which are prescription sedatives used for anxiety.
- Impulsivity adds little once sensation seeking is in the model. The two scores correlate at r = 0.62, and amphetamines are the only substance where impulsivity's odds ratio is above 1.1 (1.28, not significant after correction). In other words, most of what impulsivity predicts is already carried by sensation seeking.
- 20 of the 63 trait effects (7 traits x 9 substances) stay significant after a Holm correction, which adjusts the p-values for the number of tests run.

## Data

The data is the [Drug Consumption (Quantified)](https://archive.ics.uci.edu/dataset/373/drug+consumption+quantified) file from the UCI Machine Learning Repository, DOI 10.24432/C5TC7S, licensed CC BY 4.0. Elaine Fehrman, Vincent Egan and Evgeny Mirkes collected it through an anonymous online survey. The file has 1,885 adult respondents (1,044 UK, 551 USA) with:

- Personality scores from the NEO-FFI-R (NEO Five-Factor Inventory, revised), which measures neuroticism, extraversion, openness, agreeableness and conscientiousness; the BIS-11 (Barratt Impulsiveness Scale), which measures impulsivity; and the ImpSS (Impulsive Sensation Seeking scale), which measures sensation seeking. The scores come already standardized, so odds ratios are per 1 SD.
- Age group, gender, education, country and ethnicity, stored as numeric codes that `scripts/01_decode.py` converts back to labels.
- Use of 18 substances on a 7-level scale, from never used to used in the last day.

The survey includes Semeron, a drug that does not exist, to catch over-claiming. 8 respondents said they had used it. They are excluded, which leaves 1,877.

## Method

- Outcome: used in the last year or more recently (CL3 to CL6) against not used, for nine substances: alcohol, nicotine, cannabis, benzodiazepines, amphetamines, cocaine, ecstasy, mushrooms and LSD.
- Model: one logistic regression per substance with all seven traits together, plus age group (18-24, 25-34, 35-44, 45+), gender and holding a university degree. The 45+ band combines three groups because the 55-64 and 65+ groups (111 people) had insufficient data on some drugs for the models to converge.
- Checks: variance inflation factors, which measure how much the traits overlap with each other, are all under 2 (largest 1.91, sensation seeking). The R script refits every model with `glm()` and matches all 63 Python odds ratios to three decimals.
- Descriptives: last-year prevalence per substance and, for each trait, the standardized difference (Cohen's d) between people who used the substance last-year and people who never used the substance.

## Limitations

- The sample is a convenience sample recruited online, mostly in the UK and USA. Its rates of drug use are far higher than in national surveys (20% used LSD in the last year). As such, the results do not generalize to any population.
- The data is cross-sectional. A trait being linked with use does not show that the trait causes use.
- Use is self-reported. The Semeron check catches only the most obvious over-claiming, so some reported use may be inflated.
- "Used in the last year" mixes one-time use with heavy use. The models cannot separate traits linked with trying a drug from traits linked with using it often.

## Files

- `data/raw/drug_consumption.data`: the UCI file, unchanged
- `scripts/01_decode.py`: decodes the numeric codes and writes `data/processed/respondents.csv` and `use_long.csv`
- `scripts/02_analysis.py`: prevalence, trait profiles, collinearity check and the logistic regressions
- `scripts/03_models.R`: R replication of the regressions
- `scripts/04_charts.py`: the heatmap and the Tableau exports
- `results/`: `prevalence.csv`, `trait_profiles.csv`, `vif.csv`, `logit_odds_ratios.csv`, `r_logit_odds_ratios.csv`
- `tableau/`: `respondents.csv`, `use_long.csv` and `odds_ratios.csv` for the Tableau dashboard

## How to run

```
pip install pandas numpy statsmodels matplotlib
python scripts/01_decode.py
python scripts/02_analysis.py
Rscript scripts/03_models.R
python scripts/04_charts.py
```

## Tools

Python (pandas, statsmodels, matplotlib), R (base `glm`), Tableau.

## Author

Michael Goldenitz. [LinkedIn](https://www.linkedin.com/in/michael-goldenitz/) · [GitHub](https://github.com/mgoldenitz)
