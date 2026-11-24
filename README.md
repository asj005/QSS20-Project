# Tanking and the Spread: Do Betting Markets Price Late-Season Losing?

**Sid Singh and Ahaan Jindal · Dartmouth College · QSS 20**

**Keywords:** NBA, draft lottery, tanking, point spreads, prediction markets, difference-in-differences

## Introduction

The NBA draft lottery gives teams near the bottom of the standings a reason to value a worse record. We study whether betting markets accounted for changes in those teams’ performance late in the 2025–26 regular season. Sportsbook spreads and totals provide pregame benchmarks for the margin and combined score. Polymarket prices provide a second set of forecasts for who wins.

We ask three questions:

1. Did teams in tanking position perform worse against the spread after the All-Star break, and did games involving those teams go over the posted total more often?
2. Did changes in scoring, points allowed, or star-player absences help explain the pattern?
3. Did Polymarket predict game winners more accurately than sportsbooks in games involving potential tanking teams?

## Data

The dataset covers all **1,230 games** of the 2025–26 NBA regular season, from October 21, 2025, through April 12, 2026. The NBA Cup final, play-in games, and playoffs are excluded. We match sources on game date and the home and away teams to build `nba_merged_analysis.csv`, with one row per game.

| Source | What we collected | Input file |
| --- | --- | --- |
| [Basketball-Reference](https://www.basketball-reference.com/leagues/NBA_2026_games.html) | Game dates, tip-off times, scores, box scores, and officials | `nba_2025_26_odds_scores.csv`, `boxscores_player.csv`, `boxscores_team.csv` |
| [TeamRankings](https://www.teamrankings.com/nba/matchup/) | Closing sportsbook moneylines, spreads, and totals | `nba_2025_26_odds_scores.csv` |
| [Polymarket Gamma API](https://gamma-api.polymarket.com/events?tag_id=745) and [CLOB price history](https://clob.polymarket.com/prices-history) | NBA market listings and the last available pregame prices | `polymarket_odds.csv` |

We convert sportsbook moneylines into implied probabilities and normalize the two sides to remove the sportsbook margin. Polymarket moneyline probabilities are available for 1,229 games. Polymarket spread and totals probabilities have lower coverage.

## Methods

The main analysis uses a **difference-in-differences** design around the All-Star break. The potential tanking group is the five teams with the lowest **pre-break** win percentages. We compare the change for those teams with the change for other teams. A robustness check uses the five teams with the lowest post-break winning percentages identified in the report. That grouping uses outcomes observed after the break.

- **Spreads and team performance.** At the team-game level, we examine margin against the spread, whether a team covered, points scored, points allowed, and absences among each team’s top three scorers. The main spread model includes team fixed effects, and team-game regressions cluster standard errors by game.
- **Totals.** At the game level, we compare actual combined scoring with the sportsbook total and examine how often games finish above the line.
- **Forecast accuracy.** We compare the two markets on games with both home-win probabilities, using the Brier score, or average squared probability error. We report scores separately by period and by whether the game involves a potential tanking team.

## Results

| Outcome | Main finding |
| --- | --- |
| Spread | The estimated post-break change in margin against the spread for potential tanking teams was **−0.04 points** relative to other teams (p = 0.98). |
| Totals | After the break, **57.5%** of games involving potential tanking teams went over, compared with **48.6%** of other games. The difference-in-differences estimate was **+3.28 points** relative to the posted total (p = 0.17). |
| Team performance | Potential tanking teams allowed **3.00 more points per game** after the break relative to other teams (p = 0.031). Changes in scoring and star absences were less clearly estimated. |
| Forecast accuracy | In post-break games involving potential tanking teams, Brier scores were **0.1190** for Polymarket and **0.1198** for sportsbooks. |

The estimates describe one season. Poor records proxy for lottery incentives, and changes in points allowed can also reflect factors such as opponents, pace, and lineup changes.

## Repository organization

| Location | Contents |
| --- | --- |
| `data/raw/` | Saved inputs: odds and scores, box scores, and Polymarket prices. |
| `notebooks/` | 01–04: build the odds/scores, box-score, and Polymarket files, then merge them and run the calibration analysis. |
| `outputs/` | `nba_merged_analysis.csv`, the merged 1,230-game dataset the analyses run on. |
| `nba_analysis_complete.py` | Checkpoint analysis: market comparison and calibration figures and summary tables. |
| `tanking_analysis.py` | The report's difference-in-differences analysis and Brier comparisons. |
| `make_tanking_figures.py` | Figures for the tanking paper. |
| `pretrends_check.py` | Parallel-trends check for the tanking DID. |
| `figures/` | PNG figures used in the report. |
| `results/` and `results/tables/` | Analysis output logs and CSV tables. |
| `report/` | The LaTeX report source, Overleaf upload zip, and bibliography additions. |
| `cache/` | Scraping cache from data collection. |

## Reproducing the analysis

Run from the repository root. Install the Python dependencies first.

```bash
python -m pip install pandas numpy matplotlib statsmodels
```

- **Checkpoint analysis** (market comparison and calibration): `python nba_analysis_complete.py`. Reads `outputs/nba_merged_analysis.csv` and writes figures to `figures/` and tables to `results/tables/`. It covers Brier scores and log loss, calibration by probability bucket, referee crew foul rates vs totals, pricing of star recent form, realized star surprise, and star absences. It re-computes every headline number and checks it against `results/analysis_results.txt` before writing.
- **The report's tanking analysis**: `python tanking_analysis.py`, then `python make_tanking_figures.py` for the figures. Results go to `results/tanking_results.txt` and `results/tables/tank_*.csv`.
- **Parallel-trends check**: `python pretrends_check.py`.
- **Rebuilding the merged dataset**: run notebooks 01–04 in order, starting from the files in `data/raw/`.
