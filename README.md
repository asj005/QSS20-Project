# QSS 20 Final Project

## Do Prediction Markets Price What Sportsbooks Miss?

Evidence from the 2025-26 NBA season: Polymarket vs sportsbook closing odds

This project asks whether prediction markets or sportsbooks do a better job
pricing three things that should move NBA game outcomes: who is refereeing,
which stars are out, and how the star players have been playing lately.

We build a game-level dataset covering all 1,230 regular-season games of the
2025-26 NBA season (21 October 2025 – 12 April 2026), combining final scores,
sportsbook closing lines, Polymarket pregame prices, and player- and team-level
box scores, then test head-to-head which price better reflects each factor.

## Repository Structure

```
QSS20-Project/
│
├── data/
│   ├── raw/
│   │   ├── nba_2025_26_odds_scores.csv   # scores + sportsbook closing odds
│   │   ├── polymarket_odds.csv           # Polymarket pregame prices
│   │   ├── boxscores_player.csv          # player box scores (32,166 rows)
│   │   └── boxscores_team.csv            # team box scores + officials
│   │
│   └── interim/
│       └── boxscores_parts/              # monthly part files (during a build)
│
├── notebooks/
│   ├── 01_build_odds_scores.ipynb
│   ├── 02_build_boxscores.ipynb
│   ├── 03_build_polymarket.ipynb
│   └── 04_merge_and_analyze.ipynb
│
├── outputs/
│   └── nba_merged_analysis.csv           # merged panel, 1,230 rows x 78 cols
│
├── results/
│   ├── analysis_results.txt              # headline test results
│   ├── summary_stats.md                  # summary stats + EDA tables
│   └── tables/                           # Tables 1-7 as CSVs
│
├── figures/                              # Figures 1-8 for the final report
│
├── make_figures.py                       # regenerates figures + tables
│
├── report/
│   ├── QSS20_Final_Report_scaffold.docx  # final-report scaffold (structure,
│   │                                     # tables, figures, [WRITE] prompts)
│   └── build_scaffold.py                 # builds the scaffold from figures/
│                                          # and results/tables/
│
├── cache/
│   ├── bref/                             # Basketball-Reference schedule pages
│   ├── bref_games.json                   # game list parsed from those pages
│   └── boxscore_urls.json                # box-score URL for every game
│
└── presentation/                         # slides
```

## Key Folders

| Folder | Purpose |
| --- | --- |
| `data/raw` | Source datasets feeding the merge |
| `data/interim` | Monthly part files written during a box-score build |
| `outputs` | The merged game-level panel |
| `results` | Statistical outputs from the analysis |
| `results/tables` | Tables 1-7 (summary stats, calibration, regressions) as CSVs |
| `figures` | Figures 1-8 for the final report |
| `report` | Final-report scaffold (.docx) + the script that builds it |
| `notebooks` | The full build + analysis workflow |
| `cache` | Cached pages and lookup files the builds read |

## Methodology

### 1. Scores and sportsbook closing odds

Notebook: `notebooks/01_build_odds_scores.ipynb`

Goal: one row per game with the final score and the closing sportsbook line.

Steps:

- Parse the game list and final scores from Basketball-Reference monthly
  schedule pages (cached in `cache/bref/`).
- Keep regular-season games only (date ≤ 12 April 2026). The 16 December 2025
  NBA Cup final is excluded: it is not a regular-season game. This yields
  exactly 1,230 games (30 teams × 82 / 2).
- Pull closing lines from TeamRankings matchup pages: spread and total from the
  page header, moneyline from the money-line-movement page. Requests run with
  a 2-second delay; rows are checkpointed as fetched and failures go to a
  retry pass at the end of the notebook.

Outputs: `data/raw/nba_2025_26_odds_scores.csv`

### 2. Box scores

Notebook: `notebooks/02_build_boxscores.ipynb`

Goal: player- and team-level box scores for every game, including officials.

Steps:

- Fetch one Basketball-Reference box-score page per game (URLs in
  `cache/boxscore_urls.json`; every game matched, 1,230/1,230).
- Parse player rows (DNP rows kept with `mp="DNP"`), team totals, and the
  three officials per game.
- Write monthly part files to `data/interim/boxscores_parts/` so a re-run
  resumes from completed months, then combine into the two final files.
- A retry pass at the end of the notebook re-fetches failed games gently
  (6-second delay, up to 5 attempts). The April 2026 games were throttled
  mid-build; all were recovered on retry.

Outputs: `data/raw/boxscores_player.csv`, `data/raw/boxscores_team.csv`

Validation: team points match the final scores exactly in all 1,230 games;
player points sum to team totals in all 2,460 team-games.

### 3. Polymarket pregame prices

Notebook: `notebooks/03_build_polymarket.ipynb`

Goal: the prediction-market price for each game, as of just before tip-off.

Steps:

- Discover markets through the Polymarket Gamma API (`tag_id=745`, the NBA
  tag). Game events are titled "Away vs. Home".
- Take the last CLOB price-history point at or before tip-off (1-hour
  interval) for the moneyline, the spread line closest to the sportsbook
  spread, and the total line closest to the sportsbook total.
- Tip-off times come from the Basketball-Reference schedule pages in
  `cache/bref/`.

Outputs: `data/raw/polymarket_odds.csv`

Notes: Kalshi was not used — it publishes no price history for event markets,
so last season's Kalshi prices cannot be recovered. Polymarket coverage is
nearly complete: moneyline for 1,229 of 1,230 games (the only miss is
1 March 2026, San Antonio at New York, which had no trades in the 24 hours
before tip-off). The spread and total gaps are genuinely thin markets, not
fetch failures. Median price is 1.0 hour before tip-off.

### 4. Merge and analysis

Notebook: `notebooks/04_merge_and_analyze.ipynb`

Goal: one merged panel, then the head-to-head tests.

Steps:

- Merge the four source files on date and teams (team names match exactly).
- Derive outcomes (margin, home win, over hit, home cover) and the
  sportsbook-implied home-win probability (moneyline normalised by the
  overround).
- Build the three test variables:
  - **Crew foul tendency**: each officiating crew's foul rate in all its
    *other* games (leave-one-out, so the game's own fouls don't leak in).
  - **Star absences**: a flag for games where one of a team's top-3 scorers
    by season points per game is listed DNP. "Star" is defined from the data:
    the three highest season-PPG players per team.
  - **Top-scorer form**: the top scorer's trailing five-game points per game,
    from prior games only. Game 1 has no form by definition, and the form
    clock starts when a player first plays.
- Run the tests: Brier score and log loss for each market, the refereeing
  correlations and regressions, the DNP splits, and the form regressions
  (including realised star surprise: points scored minus trailing form).

Outputs: `outputs/nba_merged_analysis.csv`, `results/analysis_results.txt`

## Research Questions

Primary question: do prediction markets or sportsbooks price refereeing, star
absences, and individual form better?

Secondary questions:

- Do foul-prone officiating crews produce higher-scoring games, and does
  either market price that in?
- Do markets fully adjust when a star sits out?
- Does a star's recent form predict outcomes beyond the pregame price — and
  does realised star performance move outcomes beyond any pregame price?

## Key Findings

- Head-to-head it is essentially a tie: Brier score 0.1949 (Polymarket) vs
  0.1950 (sportsbook); log loss 0.5706 vs 0.5716. Polymarket is closer to the
  outcome in 60.6% of games, but mean absolute error is identical to three
  decimals.
- Refereeing does not move totals: the correlation between crew foul tendency
  and the actual total is −0.03, and the over-hit rate is flat across foul
  terciles. Neither market prices it (correlations ≈ 0).
- Star absences: 210 games have a top-3 scorer DNP. In those games the
  sportsbook is a touch better (Brier 0.1865 vs 0.1890); in no-DNP games
  Polymarket is a touch better (0.1962 vs 0.1968). A home star sitting out
  leaves the home team winning 46.8% vs ~50% implied by both markets (n=109,
  noisy).
- Recent form adds nothing beyond either price (t ≈ 0.7–0.8, n=581 games where
  both top scorers played and had prior games). But realised star surprise —
  how much the top scorer beats his recent form — moves outcomes well beyond
  any pregame price (t = 4.2).

## Data Notes

- No imputation was used anywhere. Polymarket gaps stay missing.
- One flagged quirk, kept as-is: 11 February 2026, New York at Philadelphia —
  TeamRankings' moneyline and spread favourites disagree (noted in
  `nba_2025_26_odds_scores.csv`).
- A star who sits out entirely (no box-score row at all, not even a DNP
  listing) does not trigger the DNP flag, but the game still drops out of the
  form tests because his trailing form is undefined. That is the main reason
  the form sample is 581 games rather than 1,230, not the game-1 starts.

## Requirements

Python packages used: `pandas`, `numpy`, `matplotlib`, `statsmodels`,
`tabulate` (the last three only for `make_figures.py`). Everything else is
standard library (`urllib`, `json`, `csv`, `re`). The three build notebooks
need internet access; the merge notebook runs offline from `data/raw/`.

## Running the Project

Recommended order:

| Step | Notebook |
| --- | --- |
| 1 | `01_build_odds_scores.ipynb` |
| 2 | `02_build_boxscores.ipynb` |
| 3 | `03_build_polymarket.ipynb` |
| 4 | `04_merge_and_analyze.ipynb` |

Steps 2 and 3 don't depend on each other, but everything must finish before
step 4. To reproduce the analysis only, run step 4 — it reads the four files
in `data/raw/` and writes `outputs/nba_merged_analysis.csv` and
`results/analysis_results.txt`.

Step 5 is `make_figures.py`: it reads the merged panel, re-checks the
headline numbers against `results/analysis_results.txt` (Brier scores, form
correlations, the 581-game form sample), and writes Figures 1–8 to `figures/`
plus Tables 1–7 to `results/tables/` and `results/summary_stats.md`.
`report/build_scaffold.py` then assembles those figures and tables into the
final-report scaffold.

Step 6 is the tanking paper itself: `tanking_analysis.py` runs the
difference-in-differences design (spread and totals forecast errors, the
scoring/defense/rest mechanisms, Polymarket vs sportsbook) under two tanking
definitions — worst five by pre-break win% (main spec) and the five teams
named in the Introduction (robustness) — with standard errors clustered by
game, and writes `results/tanking_results.txt` plus `results/tables/tank_*.csv`.
`make_tanking_figures.py` regenerates Figures 2–5 of the report.
`report/qss20_final_report.tex` is the Overleaf source; upload it with the
five PNGs in `figures/` (into a `figure/` folder) and the BibTeX entries in
`report/reference_bib_additions.bib`.

## Sources

- Basketball-Reference — monthly schedule pages (scores, tip-off times) and
  box-score pages (player/team stats, officials).
- TeamRankings — closing moneyline, spread, and total for each game.
- Polymarket — Gamma API (`gamma-api.polymarket.com/events`, NBA tag 745) for
  market discovery; CLOB price-history API
  (`clob.polymarket.com/prices-history`) for pregame prices.
