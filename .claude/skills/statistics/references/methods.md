# Choosing the right statistical method

## 1. Describe

| Variable type | Central value | Spread | Chart |
|---|---|---|---|
| Numeric, symmetric | Mean | Standard deviation | Histogram, box plot |
| Numeric, skewed (income, sales, firm size) | **Median** | IQR, percentiles (P10/P90) | Box plot, histogram (log scale) |
| Categorical | Mode, % per category | — | Bar chart (sorted) |
| Ordinal (Likert 1–5) | Median, % top-2-box | Distribution | Stacked bar |
| Time series | Level, growth rate | Volatility | Line chart |

Useful indicators: growth rate `(x_t / x_{t-1} − 1)`, CAGR `(x_end / x_start)^(1/years) − 1`,
share, index (base = 100), coefficient of variation `sd / mean`,
concentration (Gini, Herfindahl–Hirschman, top-k share).

## 2. Compare groups / test hypotheses

| Question | Data | Parametric test | Non-parametric / robust alternative |
|---|---|---|---|
| One mean vs a target | Numeric | One-sample t-test | Wilcoxon signed-rank |
| Two independent groups | Numeric | Welch t-test (default, unequal variances) | Mann–Whitney U |
| Two paired measures (before/after) | Numeric | Paired t-test | Wilcoxon signed-rank |
| 3+ independent groups | Numeric | One-way ANOVA (Welch ANOVA if variances differ) + Tukey/Games-Howell | Kruskal–Wallis + Dunn |
| 3+ repeated measures | Numeric | Repeated-measures ANOVA / mixed model | Friedman |
| Two proportions | Binary | z-test for proportions | Fisher's exact (small counts) |
| Association of two categorical variables | Counts | Chi-square test of independence (expected ≥ 5) | Fisher's exact; report Cramér's V |
| Paired binary (before/after yes/no) | Binary | McNemar | — |
| Distribution vs expected shares | Counts | Chi-square goodness-of-fit | — |

Always report an **effect size**: mean difference with 95% CI, Cohen's d,
difference in percentage points, odds ratio, Cramér's V, η².

Assumption checks: normality (Q-Q plot; Shapiro–Wilk only for n < 50 — large
samples make it reject trivially), equal variances (Levene), independence
(design question, not a test). With n ≥ 30 per group the t-test is usually fine.

## 3. Relationships

| Question | Method |
|---|---|
| Linear association, two numeric variables | Pearson r (with CI) |
| Monotonic / ranked / outliers present | Spearman ρ |
| Explain a numeric outcome by several factors | Linear regression (OLS); robust (HC3) SEs |
| Binary outcome (bought / did not buy, firm exports / not) | Logistic regression → odds ratios / marginal effects |
| Count outcome (number of employees, visits) | Poisson / negative binomial |
| Ordinal outcome (satisfaction 1–5) | Ordered logit |
| Grouped data (firms in regions, pupils in schools) | Multilevel / mixed models or cluster-robust SEs |
| Many correlated variables → indices | PCA, factor analysis; Cronbach's α for scales |
| Segment customers / firms | k-means, hierarchical clustering (standardise first) |

Regression checklist: plot residuals, check multicollinearity (VIF > 10),
influential points (Cook's distance), report R² / pseudo-R², coefficients with
CIs, and interpret in units the reader understands.

## 4. Causal impact (programme evaluation)

Only claim impact with a credible counterfactual:
randomised controlled trial; difference-in-differences (check parallel
pre-trends); propensity score matching; regression discontinuity;
instrumental variables. Otherwise call it "association".

## 5. Time series and forecasting

1. Plot the series; identify trend, seasonality, breaks, outliers.
2. Decompose (classical or STL). Seasonal adjustment: X-13ARIMA-SEATS / TRAMO-SEATS
   for official series.
3. Forecast: naïve / seasonal naïve as benchmark → exponential smoothing (ETS,
   Holt-Winters) → ARIMA/SARIMA → regression with drivers.
4. Evaluate on a hold-out period (MAPE, MAE, RMSE) and give **prediction intervals**,
   not single numbers.
5. For SMEs: a 3-scenario forecast (low / expected / high) is often more useful
   than a complex model.

## 6. Index numbers

Laspeyres (base-period weights, standard for CPI/PPI), Paasche (current
weights), Fisher (geometric mean of both). Chain-linking for long series.
Deflate nominal values: `real = nominal / price index × 100`.

## 7. Python snippets

```python
import pandas as pd, numpy as np
from scipy import stats
import statsmodels.formula.api as smf

# Welch t-test + 95% CI for the difference
a, b = df.loc[df.g=="A","y"], df.loc[df.g=="B","y"]
t = stats.ttest_ind(a, b, equal_var=False)
diff = a.mean() - b.mean()

# Chi-square + Cramér's V
ct = pd.crosstab(df.x, df.y)
chi2, p, dof, exp = stats.chi2_contingency(ct)
v = np.sqrt(chi2 / (ct.values.sum() * (min(ct.shape) - 1)))

# OLS with robust SEs
m = smf.ols("sales ~ price + promo + C(region)", data=df).fit(cov_type="HC3")
print(m.summary())

# Logistic regression → odds ratios
lg = smf.logit("exports ~ np.log(employees) + C(sector)", data=df).fit()
print(np.exp(lg.params), np.exp(lg.conf_int()))
```

Install if missing: `pip install pandas scipy statsmodels`.
