# Summary statistics and EDA tables (recomputed from outputs/nba_merged_analysis.csv)

Games: 1,230; dates 2025-10-21 to 2026-04-12; teams: 30.

## Table 1. Summary statistics (key variables)

|                |   count |    mean |    std |     min |     max |
|:---------------|--------:|--------:|-------:|--------:|--------:|
| margin         |    1230 |   1.737 | 16.413 | -55     |  54     |
| actual_total   |    1230 | 231.215 | 19.876 | 169     | 302     |
| total          |    1230 | 230.73  |  7.667 | 206.5   | 254.5   |
| sb_home_prob   |    1230 |   0.55  |  0.219 |   0.066 |   0.952 |
| poly_home_prob |    1229 |   0.552 |  0.225 |   0.045 |   0.977 |
| crew_foul_loo  |    1230 |  39.732 |  0.581 |  38.192 |  44.15  |
| total_pf       |    1230 |  39.732 |  6.846 |  14     |  70     |
| form_diff      |     646 |  -0.3   |  7.533 | -27     |  21.55  |
| surprise_diff  |     646 |   0.545 |  9.726 | -38.4   |  32.6   |

## Table 2. Headline rates

|                                 |        0 |
|:--------------------------------|---------:|
| Home win rate                   |   0.5545 |
| Mean home margin (pts)          |   1.7374 |
| Over rate (actual total > line) |   0.4911 |
| Home ATS cover rate             |   0.5163 |
| Mean sportsbook total line      | 230.73   |
| Mean actual total               | 231.215  |
| Mean total fouls per game       |  39.7317 |
| Games with a top-3 scorer DNP   |   0.1707 |

## Table 3. Coverage (non-missing / 1,230 games)

| variable                              |    n |   games |   share |
|:--------------------------------------|-----:|--------:|--------:|
| Sportsbook moneyline (all games)      | 1230 |    1230 |  1      |
| Polymarket moneyline                  | 1229 |    1230 |  0.9992 |
| Polymarket spread line                | 1221 |    1230 |  0.9927 |
| Polymarket spread prob                | 1119 |    1230 |  0.9098 |
| Polymarket total line                 | 1221 |    1230 |  0.9927 |
| Polymarket over prob                  | 1063 |    1230 |  0.8642 |
| Both top scorers trailing form        |  646 |    1230 |  0.5252 |
| Form-test sample (form + no star DNP) |  581 |    1230 |  0.4724 |
| Crew foul LOO rate                    | 1230 |    1230 |  1      |

## Table 4. Calibration buckets (sportsbook)

|   mid |   n |   implied |   actual |
|------:|----:|----------:|---------:|
|  0.05 |  15 |     0.084 |    0     |
|  0.15 |  67 |     0.152 |    0.119 |
|  0.25 | 111 |     0.251 |    0.234 |
|  0.35 | 140 |     0.355 |    0.371 |
|  0.45 | 177 |     0.448 |    0.48  |
|  0.55 | 170 |     0.553 |    0.529 |
|  0.65 | 175 |     0.646 |    0.68  |
|  0.75 | 196 |     0.748 |    0.76  |
|  0.85 | 151 |     0.852 |    0.828 |
|  0.95 |  28 |     0.92  |    1     |

## Table 4b. Calibration buckets (polymarket)

|   mid |   n |   implied |   actual |
|------:|----:|----------:|---------:|
|  0.05 |  22 |     0.075 |    0     |
|  0.15 |  75 |     0.156 |    0.133 |
|  0.25 |  91 |     0.249 |    0.253 |
|  0.35 | 145 |     0.351 |    0.345 |
|  0.45 | 175 |     0.447 |    0.497 |
|  0.55 | 166 |     0.553 |    0.524 |
|  0.65 | 185 |     0.651 |    0.686 |
|  0.75 | 172 |     0.75  |    0.756 |
|  0.85 | 156 |     0.85  |    0.801 |
|  0.95 |  42 |     0.928 |    1     |

## Table 5. Headline regressions (OLS, coefficients; t-stats in parentheses below in the docx)

|                      |   (1) home_win ~ sb_prob + form_diff |   (2) home_win ~ poly_prob + form_diff |   (3) home_win ~ sb_prob + surprise_diff |   (4) home_win ~ sb_prob |
|:---------------------|-------------------------------------:|---------------------------------------:|-----------------------------------------:|-------------------------:|
| const (coef)         |                               0.1037 |                                 0.1087 |                                   0.064  |                   0.0832 |
| sb_prob (coef)       |                               0.848  |                               nan      |                                   0.909  |                   0.8834 |
| form_diff (coef)     |                               0.0022 |                                 0.0019 |                                 nan      |                 nan      |
| poly_prob (coef)     |                             nan      |                                 0.8366 |                                 nan      |                 nan      |
| surprise_diff (coef) |                             nan      |                               nan      |                                   0.0081 |                 nan      |
| R-squared            |                               0.1294 |                                 0.1312 |                                   0.1546 |                   0.1285 |
| n                    |                             581      |                               580      |                                 581      |                 581      |

t-statistics:

- (1) home_win ~ sb_prob + form_diff: const t=1.67, sb_prob t=8.04, form_diff t=0.79

- (2) home_win ~ poly_prob + form_diff: const t=1.79, poly_prob t=8.12, form_diff t=0.7

- (3) home_win ~ sb_prob + surprise_diff: const t=1.15, sb_prob t=9.62, surprise_diff t=4.22

- (4) home_win ~ sb_prob: const t=1.48, sb_prob t=9.24


## Table 6. Referee foul terciles

| foul_tercile   |   n |   over_hit |   actual_total |   sb_total |   poly_over |
|:---------------|----:|-----------:|---------------:|-----------:|------------:|
| Low foul crew  | 410 |      0.51  |        232.124 |    230.665 |       0.496 |
| Mid foul crew  | 410 |      0.48  |        230.739 |    231.088 |       0.497 |
| High foul crew | 410 |      0.483 |        230.783 |    230.437 |       0.495 |

## Table 7. Brier scores by star-DNP status

| sample         |    n |   brier_poly |   brier_sb |
|:---------------|-----:|-------------:|-----------:|
| Star DNP games |  210 |       0.189  |     0.1865 |
| No star DNP    | 1020 |       0.1962 |     0.1968 |

## Correlations (for the text)

- corr(form_diff, sb_home_prob) = 0.422

- corr(form_diff, poly_home_prob) = 0.426

- corr(surprise_diff, margin) = 0.218

- corr(crew_foul_loo, actual_total) = -0.033

- corr(crew_foul_loo, sb total line) = -0.012

- corr(poly_home_prob, sb_home_prob) = 0.997; mean |Poly - SB| = 0.012

- Poly closer to outcome in 60.6% of games
