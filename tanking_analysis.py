"""Tanking analysis for the QSS 20 final report ("The Spread Doesn't Tank").

Runs the difference-in-differences design from the paper's Introduction on the
merged 1,230-game panel (outputs/nba_merged_analysis.csv):

  RQ1  Do tanking-position teams underperform the spread and the total line
       after the All-Star break, vs their own pre-break performance and vs
       other teams?
  RQ2  Mechanism: do they stop scoring, stop defending, or rest their stars?
  RQ3  Does Polymarket price tanking any better than sportsbooks?

Two tanking definitions are run:
  MAIN  worst five teams by PRE-BREAK win% (Sacramento, Washington, New
        Orleans, Indiana, Brooklyn). Treatment is defined from information
        available before each game, as the Introduction promises.
  NAMED the five teams the Introduction names (Washington, Indiana, Memphis,
        Brooklyn, Utah), selected on POST-break win% < 18%. Reported as a
        robustness check; the selection uses post-break outcomes.

Standard errors in the team-game regressions are clustered by game: each game
contributes two rows (home + away) whose ATS margins sum to zero by
construction, so unclustered SEs would be too small.

Writes results/tanking_results.txt and results/tables/tank_*.csv.
"""
import os
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = os.path.dirname(os.path.abspath(__file__))
TAB = os.path.join(ROOT, "results", "tables")
os.makedirs(TAB, exist_ok=True)

df = pd.read_csv(os.path.join(ROOT, "outputs", "nba_merged_analysis.csv"))
df["date"] = pd.to_datetime(df["date"])
df["game_id"] = np.arange(len(df))
out = []

# ------------------------------------------------------------------ break date
dates = sorted(df["date"].unique())
gaps = [(pd.Timestamp(dates[i + 1]) - pd.Timestamp(dates[i])).days
        for i in range(len(dates) - 1)]
gi = int(np.argmax(gaps))
last_pre = pd.Timestamp(dates[gi])
first_post = pd.Timestamp(dates[gi + 1])
out.append(f"Longest gap with no games: {gaps[gi]} days, "
           f"{last_pre.date()} -> {first_post.date()}")
out.append(f"Pre-break: games on/before {last_pre.date()}; "
           f"post-break: games on/after {first_post.date()}")
df["post"] = (df["date"] >= first_post).astype(int)

# ------------------------------------------------------------------ team panel
home = pd.DataFrame({
    "game_id": df["game_id"], "date": df["date"], "team": df["home_team"],
    "opp": df["away_team"], "is_home": 1, "post": df["post"],
    "won": df["home_win"], "pf": df["home_pts"], "pa": df["away_pts"],
    "ats_margin": df["margin"] + df["home_spread"],
    "star_dnp": df["home_star_dnp"].astype(int),
    "top_pts": df["home_top_pts"], "top_trail5": df["home_top1_trail5"],
})
away = pd.DataFrame({
    "game_id": df["game_id"], "date": df["date"], "team": df["away_team"],
    "opp": df["home_team"], "is_home": 0, "post": df["post"],
    "won": 1 - df["home_win"], "pf": df["away_pts"], "pa": df["home_pts"],
    "ats_margin": -(df["margin"] + df["home_spread"]),
    "star_dnp": df["away_star_dnp"].astype(int),
    "top_pts": df["away_top_pts"], "top_trail5": df["away_top1_trail5"],
})
tg = pd.concat([home, away], ignore_index=True)
tg["covered"] = (tg["ats_margin"] > 0).astype(int)
tg["push"] = (tg["ats_margin"] == 0).astype(int)
out.append(f"\nTeam-game rows: {len(tg)} (pushes: {int(tg['push'].sum())})")

# Pre-break win% for every team.
pre = tg[tg["post"] == 0].groupby("team").agg(
    pre_games=("won", "size"), pre_wins=("won", "sum"))
pre["pre_winpct"] = pre["pre_wins"] / pre["pre_games"]
pre = pre.sort_values("pre_winpct")
out.append("\nPre-break win% (worst 8):")
out.append(pre.head(8).round(3).to_string())
tank_main = list(pre.head(5).index)
tank_named = ["Washington Wizards", "Indiana Pacers", "Memphis Grizzlies",
              "Brooklyn Nets", "Utah Jazz"]
out.append(f"\nMAIN tanking set (worst 5 pre-break): {tank_main}")
out.append(f"NAMED tanking set (Introduction's five): {tank_named}")

# Verify the Introduction's "<18% post-break" claim for the named five.
post = tg[tg["post"] == 1].groupby("team").agg(
    post_games=("won", "size"), post_wins=("won", "sum"))
post["post_winpct"] = post["post_wins"] / post["post_games"]
chk = post.loc[tank_named]
out.append("\nPost-break win% for the five named teams (Introduction claims "
           "all < 18%):")
out.append(chk.round(3).to_string())
out.append(f"Claim verified: {bool((chk['post_winpct'] < 0.18).all())}")
out.append("Pre-break win% of the named five (Memphis 0.377 and Utah 0.321 "
           "were NOT bottom-5 at the break):")
out.append(pre.loc[tank_named].round(3).to_string())


def brier(p, y):
    m = p.notna() & y.notna()
    return float(np.mean((p[m] - y[m]) ** 2))


def run_pass(tank_teams, label, tag):
    out.append(f"\n{'=' * 70}\n{label}\n{'=' * 70}")
    tg["tanking"] = tg["team"].isin(tank_teams).astype(int)
    df["tank_game"] = (df["home_team"].isin(tank_teams)
                       | df["away_team"].isin(tank_teams)).astype(int)

    # ---- RQ1a: spread DID (team-game level, SEs clustered by game)
    cells = tg.groupby(["tanking", "post"]).agg(
        n=("won", "size"), cover_rate=("covered", "mean"),
        ats_margin=("ats_margin", "mean"),
        ats_margin_se=("ats_margin",
                       lambda s: s.std(ddof=1) / np.sqrt(len(s))),
        win_rate=("won", "mean"))
    out.append("\n--- RQ1a. SPREAD: cover rate / ATS margin ---")
    out.append(cells.round(4).to_string())
    cells.to_csv(os.path.join(TAB, f"tank_spread_cells_{tag}.csv"))
    m1 = smf.ols("ats_margin ~ tanking * post", data=tg).fit(
        cov_type="cluster", cov_kwds={"groups": tg["game_id"]})
    m2 = smf.ols("ats_margin ~ post + tanking:post + C(team) + is_home",
                 data=tg).fit(
        cov_type="cluster", cov_kwds={"groups": tg["game_id"]})
    out.append(f"DID, ATS margin (no FE, clustered SE): "
               f"tanking x post = {m1.params['tanking:post']:.3f} "
               f"(t={m1.tvalues['tanking:post']:.2f}, "
               f"p={m1.pvalues['tanking:post']:.3f}); "
               f"tanking = {m1.params['tanking']:.3f}, "
               f"post = {m1.params['post']:.3f}, R2 = {m1.rsquared:.4f}")
    out.append(f"DID, ATS margin (team FE + home, clustered SE): "
               f"tanking x post = {m2.params['tanking:post']:.3f} "
               f"(t={m2.tvalues['tanking:post']:.2f}, "
               f"p={m2.pvalues['tanking:post']:.3f}); R2 = {m2.rsquared:.4f}")
    c2 = smf.ols("covered ~ post + tanking:post + C(team) + is_home",
                 data=tg).fit(
        cov_type="cluster", cov_kwds={"groups": tg["game_id"]})
    out.append(f"DID, cover indicator LPM (team FE + home, clustered SE): "
               f"tanking x post = {c2.params['tanking:post']:.4f} "
               f"(t={c2.tvalues['tanking:post']:.2f}, "
               f"p={c2.pvalues['tanking:post']:.3f})")

    # ---- RQ1b: totals DID (game level)
    df["total_err"] = df["actual_total"] - df["total"]
    tcells = df.groupby(["tank_game", "post"]).agg(
        n=("home_win", "size"), over_hit=("over_hit", "mean"),
        total_err=("total_err", "mean"),
        total_err_se=("total_err",
                      lambda s: s.std(ddof=1) / np.sqrt(len(s))),
        actual_total=("actual_total", "mean"), line=("total", "mean"))
    out.append("\n--- RQ1b. TOTALS: over-hit / total error ---")
    out.append(tcells.round(4).to_string())
    tcells.to_csv(os.path.join(TAB, f"tank_totals_cells_{tag}.csv"))
    t1 = smf.ols("total_err ~ tank_game * post", data=df).fit()
    o1 = smf.ols("over_hit ~ tank_game * post", data=df).fit()
    out.append(f"DID, total forecast error: tank_game x post = "
               f"{t1.params['tank_game:post']:.3f} "
               f"(t={t1.tvalues['tank_game:post']:.2f}, "
               f"p={t1.pvalues['tank_game:post']:.3f})")
    out.append(f"DID, over-hit indicator: tank_game x post = "
               f"{o1.params['tank_game:post']:.4f} "
               f"(t={o1.tvalues['tank_game:post']:.2f}, "
               f"p={o1.pvalues['tank_game:post']:.3f})")

    # ---- RQ2: mechanism (team-game level, clustered SEs)
    mech = tg.groupby(["tanking", "post"]).agg(
        n=("won", "size"), pf=("pf", "mean"), pa=("pa", "mean"),
        dnp_rate=("star_dnp", "mean"), top_pts=("top_pts", "mean"))
    mech["net"] = mech["pf"] - mech["pa"]
    out.append("\n--- RQ2. MECHANISM: scoring / defense / star rest ---")
    out.append(mech.round(3).to_string())
    mech.to_csv(os.path.join(TAB, f"tank_mechanism_{tag}.csv"))
    for col, label2 in [("pf", "points scored"), ("pa", "points allowed"),
                        ("star_dnp", "star DNP rate")]:
        r = smf.ols(f"{col} ~ tanking * post", data=tg).fit(
            cov_type="cluster", cov_kwds={"groups": tg["game_id"]})
        out.append(f"DID, {label2}: tanking x post = "
                   f"{r.params['tanking:post']:.3f} "
                   f"(t={r.tvalues['tanking:post']:.2f}, "
                   f"p={r.pvalues['tanking:post']:.3f})")

    # ---- RQ3: Polymarket vs sportsbook
    out.append("\n--- RQ3. POLYMARKET vs SPORTSBOOK (Brier, moneyline) ---")
    for lab2, sub in [("tanking-team games, pre-break",
                       df[(df["tank_game"] == 1) & (df["post"] == 0)]),
                      ("tanking-team games, post-break",
                       df[(df["tank_game"] == 1) & (df["post"] == 1)]),
                      ("other games, pre-break",
                       df[(df["tank_game"] == 0) & (df["post"] == 0)]),
                      ("other games, post-break",
                       df[(df["tank_game"] == 0) & (df["post"] == 1)])]:
        out.append(f"{lab2} (n={len(sub)}): Poly "
                   f"{brier(sub['poly_home_prob'], sub['home_win']):.4f} vs SB "
                   f"{brier(sub['sb_home_prob'], sub['home_win']):.4f}")
    sp = df[(df["tank_game"] == 1) & (df["post"] == 1)].dropna(
        subset=["poly_spread_home_prob"])
    out.append(f"\nTanking games post-break with a Poly spread price: "
               f"n={len(sp)}")
    if len(sp):
        out.append(f"  Poly implied home-cover prob (mean): "
                   f"{sp['poly_spread_home_prob'].mean():.3f}; actual "
                   f"home-cover rate: {sp['home_cover'].mean():.3f}")
        d = df.dropna(subset=["poly_spread_line"])
        out.append(f"  Poly spread line vs SB spread line (all games): "
                   f"mean |diff| "
                   f"{np.mean(np.abs(d['poly_spread_line'] - d['home_spread'])):.2f} pts, "
                   f"corr "
                   f"{np.corrcoef(d['poly_spread_line'], d['home_spread'])[0, 1]:.3f}")


run_pass(tank_main, "MAIN SPEC: worst five by PRE-BREAK win%", "main")
run_pass(tank_named, "ROBUSTNESS: the five NAMED teams (post-break <18%)",
         "named")

with open(os.path.join(ROOT, "results", "tanking_results.txt"), "w") as fh:
    fh.write("\n".join(out) + "\n")
print("\n".join(out))
print("\nwrote results/tanking_results.txt + results/tables/tank_*.csv")
