# Tanking and the Spread: Do Betting Markets Price Late-Season Losing?

## Group A2

Sid Singh and Ahaan Jindal · Dartmouth College · QSS 20

## Introduction

The NBA draft lottery gives teams near the bottom of the standings an incentive to finish with a worse record. We ask whether betting markets anticipated changes in those teams’ performance after the All-Star break in the 2025–26 season.

1. Did teams in potential tanking position perform worse against the spread, and did games involving those teams finish further above the posted total?
2. Did changes in points scored, points allowed, or recorded star-player absences accompany those patterns?
3. How did Polymarket and sportsbooks compare at predicting winners in games involving these teams?

## Data

The merged dataset contains **1,230 games**, with one row per regular-season game from October 21, 2025, through April 12, 2026. We match sources by game date, home team, and away team. The NBA Cup final, play-in games, and playoffs are outside the sample.

| Source | Data used |
| --- | --- |
| [Basketball-Reference](https://www.basketball-reference.com/leagues/NBA_2026_games.html) | Game dates, tip-off times, final scores, and box scores |
| [TeamRankings](https://www.teamrankings.com/nba/matchup/) | Closing sportsbook moneylines, spreads, and totals |
| [Polymarket Gamma API](https://gamma-api.polymarket.com/events?tag_id=745) and [CLOB price history](https://clob.polymarket.com/prices-history) | NBA market listings and the last available price at or before tip-off within a 24-hour window |

We normalize the two sportsbook moneyline probabilities to remove the bookmaker’s margin. Sportsbook moneylines cover all 1,230 games, and Polymarket moneyline prices cover 1,229.

## Directory

| Path | Contents |
| --- | --- |
| `cache/` | Cached files from data collection |
| `data/raw/` | Saved odds, scores, box scores, and Polymarket prices |
| `data/interim/` | Intermediate files produced during data preparation |
| `data/derived/` | `nba_merged_analysis.csv`, the final game-level dataset |
| `notebooks/` | Notebooks 01–04 for building and merging the datasets |
| `notebooks/Analysis/` | Scripts for the report analysis, figures, and pre-trends check |
| `outputs/tables and texts/` | Analysis logs and a `tables/` subfolder with CSV results |
| `outputs/tankingfigures/` | Figures generated for the tanking analysis |
| `docs/` | Project report and supporting documents |

## How to run

From the repository root, activate your Python environment and install the analysis dependencies:

```bash
python -m pip install pandas numpy matplotlib statsmodels
```

The report analysis uses the saved dataset at `data/derived/nba_merged_analysis.csv`. Run the following commands from the repository root:

```bash
python notebooks/Analysis/tanking_analysis.py
python notebooks/Analysis/make_tanking_figures.py
python notebooks/Analysis/pretrends_check.py
```

You can also run the same sequence from a Jupyter notebook at the repository root:

```python
%run notebooks/Analysis/tanking_analysis.py
%run notebooks/Analysis/make_tanking_figures.py
%run notebooks/Analysis/pretrends_check.py
```

Run `tanking_analysis.py` first because `make_tanking_figures.py` reads the tables it generates. To rebuild the merged dataset, run notebooks 01–04 in order using the saved inputs in `data/raw/`.

## Results

We use a **difference-in-differences** design around the All-Star break. The main group is the five teams with the lowest pre-break winning percentages: Sacramento, Washington, New Orleans, Indiana, and Brooklyn. We compare their pre-to-post changes with those of other teams. The report also includes an exploratory comparison using five teams selected for low post-break winning percentages.

| Outcome | Main finding |
| --- | --- |
| Point spread | The estimated change in against-the-spread margin for the main group was **−0.04 points** relative to other teams (*p* = 0.98). |
| Game totals | After the break, **57.5%** of games involving a team in the main group went over, compared with **48.6%** of other games. The estimated relative increase in total forecast error was **3.28 points** (*p* = 0.17). |
| Team performance | Teams in the main group allowed **3.00 more points per game** after the break relative to other teams (*p* = 0.031). Changes in points scored and recorded star absences were less precisely estimated. |
| Moneyline accuracy | In post-break games involving the main group, Brier scores were **0.1190** for Polymarket and **0.1198** for sportsbooks. Lower Brier scores indicate more accurate probability forecasts. |

The [tanking figures](outputs/tankingfigures/) show the spread, totals, team performance, and moneyline comparisons, along with the pre-trends diagnostic.

## Discussion

The study covers one season and uses poor pre-break records as a proxy for tanking incentives. Higher points allowed could reflect changes in pace, opponents, or lineups. The pre-trends diagnostic also warrants caution when interpreting the spread estimate, and the recorded absence measure can miss players without a box-score entry.

Future work could compare multiple seasons and lottery rules, use pace-adjusted defensive measures, and track how odds move from opening to tip-off.

## References

- Levitt, Steven D. 2004. “Why Are Gambling Markets Organised So Differently from Financial Markets?” *Economic Journal* 114(495), 223–246.
- Price, Joseph, Brian P. Soebbing, David Berri, and Brad R. Humphreys. 2010. “Tournament Incentives, League Policy, and NBA Team Performance Revisited.” *Journal of Sports Economics* 11(2), 117–135.
- Taylor, Beck A., and Justin G. Trogdon. 2002. “Losing to Win: Tournament Incentives in the National Basketball Association.” *Journal of Labor Economics* 20(1), 23–41.

See the [full report](docs/) for additional references and analysis details.
