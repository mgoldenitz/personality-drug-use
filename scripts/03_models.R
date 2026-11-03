# R replication of the logistic regressions in 02_analysis.py (base R only).
# Run from the repo root after scripts/01_decode.py:  Rscript scripts/03_models.R
d <- read.csv("data/processed/respondents.csv", check.names = FALSE)
d <- d[d$Overclaimer == "False", ]
names(d)[names(d) == "Sensation seeking"] <- "Sensation_seeking"
d$Age <- factor(ifelse(d$Age %in% c("45-54", "55-64", "65+"), "45+", d$Age),
                levels = c("18-24", "25-34", "35-44", "45+"))
d$Degree <- d$Degree == "True"
traits <- c("Neuroticism", "Extraversion", "Openness", "Agreeableness",
            "Conscientiousness", "Impulsivity", "Sensation_seeking")
subs <- c("Alcohol", "Nicotine", "Cannabis", "Benzos", "Amphet", "Coke",
          "Ecstasy", "Mushrooms", "LSD")
f <- as.formula(paste("y ~", paste(traits, collapse = " + "), "+ Age + Gender + Degree"))
out <- do.call(rbind, lapply(subs, function(s) {
  d$y <- as.integer(d[[paste0(s, "_level")]] >= 3)
  m <- glm(f, data = d, family = binomial)
  est <- coef(summary(m))[traits, ]
  ci <- confint.default(m)[traits, ]
  data.frame(Substance = s, Trait = traits, OR = exp(est[, 1]),
             CI_low = exp(ci[, 1]), CI_high = exp(ci[, 2]), p = est[, 4])
}))
out$p_holm <- p.adjust(out$p, method = "holm")
write.csv(out, "results/r_logit_odds_ratios.csv", row.names = FALSE)
py <- read.csv("results/logit_odds_ratios.csv")
py$Trait <- sub(" ", "_", py$Trait)
chk <- merge(out, py, by = c("Substance", "Trait"), suffixes = c("_r", "_py"))
cat(sprintf("%d of %d odds ratios match Python to 3 decimals; Holm-significant in R: %d\n",
            sum(abs(chk$OR_r - chk$OR_py) < 0.001), nrow(chk), sum(out$p_holm < 0.05)))
