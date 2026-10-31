# Surveys and studies

## 1. Plan

1. Objectives → list of indicators → questions (every question must serve an
   indicator; drop the rest).
2. Target population and **sampling frame** (business register, census
   enumeration areas, customer list). Note frame coverage gaps (informal firms!).
3. Unit of observation (enterprise, establishment, household, individual).
4. Reference period and data collection mode (CAPI/KoboToolbox/ODK/CSPro,
   phone, web, paper).
5. Domains of estimation (country, region, sector, sex of owner) — sample size
   must be sufficient **in each domain** you want to publish.

## 2. Sampling designs

| Design | When to use | Note |
|---|---|---|
| Simple random sampling | Small, complete frame | Benchmark design |
| Systematic | List frame, field simplicity | Order the list to get implicit stratification |
| Stratified | Heterogeneous population (size class, sector, region) | Allocation: proportional, Neyman, or equal per domain; take-all stratum for large firms |
| Cluster / multi-stage | No list frame, dispersed population (households) | Increases variance → design effect |
| PPS | Clusters of unequal size | Self-weighting two-stage designs |
| Quota / purposive | Quick market studies, qualitative | **Non-probability**: no valid margin of error; say so |

## 3. Sample size

Proportion (worst case p = 0.5):

```
n0 = z² · p(1−p) / e²
n  = n0 / (1 + (n0 − 1)/N)          # finite population correction
n_final = n · deff / response_rate
```

Mean: `n0 = (z · σ / e)²`.

Rule-of-thumb values: z = 1.96 (95%); e = 0.05 → n0 ≈ 385; e = 0.03 → ≈ 1 068.
Typical design effect for cluster household surveys: 1.5–2.5. Enterprise
surveys: response rate often 60–80%.

Use `scripts/sample_size.py`, e.g.

```
python3 scripts/sample_size.py --margin 0.05 --population 12000 --deff 1.5 --response 0.8
python3 scripts/sample_size.py --mean --sd 250000 --margin 50000
```

Comparing two groups (detect a difference of d percentage points with 80% power):
`n per group ≈ (1.96 + 0.84)² · [p1(1−p1) + p2(1−p2)] / (p1 − p2)²`.

## 4. Questionnaire quality checklist

- One idea per question; no double-barrelled or leading questions.
- Exhaustive and mutually exclusive answer categories; include "Don't know" /
  "Refused" codes distinct from missing.
- Consistent reference periods and units (monthly vs annual, FCFA vs '000 FCFA).
- Skip logic and validation rules (ranges, consistency checks) in CAPI.
- Translate and back-translate (French, English, Portuguese, local languages).
- Pre-test (pilot) and cognitive testing before fieldwork.
- Use international standard classifications (ISIC Rev.4, CPC, ISCO-08, ISO country codes).

## 5. Data processing

1. Merge and de-duplicate; check IDs.
2. Range and consistency checks; outlier review (interviewer- or respondent-level).
3. Code open answers; harmonise categories.
4. Treat non-response: unit non-response → weight adjustment; item
   non-response → imputation (hot-deck, regression, multiple imputation) and flag
   imputed values.
5. Document everything in a data-processing log.

## 6. Weighting

1. Design weight = 1 / inclusion probability (e.g. `N_h / n_h` per stratum).
2. Non-response adjustment = design weight × (selected / responded) within
   adjustment cells.
3. Calibration / post-stratification to known totals (raking) — e.g. number of
   firms by sector and region from the business register.
4. Trim extreme weights if they dominate; check the sum of weights ≈ population.

## 7. Analysis of complex samples

- Use weights for all estimates of levels, totals, means and proportions.
- Use design-based variance (strata + PSU): Python `samplics`, R `survey`/`srvyr`,
  Stata `svy`, SPSS Complex Samples. Ordinary formulas understate errors.
- Publish estimates with CI and coefficient of variation; suppress or flag
  cells with CV > 30% or n < 30 (common NSO rule; confirm the local rule).
- Respect statistical confidentiality: no cells that identify a single firm
  (dominance rule, minimum 3 units).

## 8. Market study specifics (SMEs)

Market size (top-down from official data and bottom-up from survey: number of
buyers × purchase frequency × average basket), market shares, price
sensitivity (Van Westendorp), willingness to pay, satisfaction (NPS = % 9–10
minus % 0–6; CSAT), segmentation by clustering. Always triangulate with a
second source.
