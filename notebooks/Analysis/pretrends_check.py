from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "outputs" / "tables and texts"
TAB = RESULTS / "tables"
FIG = ROOT / "outputs" / "tankingfigures"

TAB.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(ROOT / "data" / "derived" / "nba_merged_analysis.csv")
df["date"] = pd.to_datetime(df["date"])
df["game_id"] = np.arange(len(df))

first_post = pd.Timestamp("2026-02-19")
df["post"] = (df["date"] >= first_post).astype(int)

TANK_MAIN = ["Sacramento Kings", "Washington Wizards",
             "New Orleans Pelicans", "Indiana Pacers", "Brooklyn Nets"]

# labelling games by month and split February at the All-Star break
ORDER = ["Oct", "Nov", "Dec", "Jan", "Feb-pre", "Feb-post", "Mar", "Apr"]

df["period"] = df["date"].dt.strftime("%b")
is_february = df["date"].dt.month == 2

df.loc[is_february & (df["post"] == 0), "period"] = "Feb-pre"
df.loc[is_february & (df["post"] == 1), "period"] = "Feb-post"

#one row per team per game, to stay consistent

home = pd.DataFrame({
    "game_id": df["game_id"], "date": df["date"], "team": df["home_team"],
    "post": df["post"], "period": df["period"],
    "won": df["home_win"], "pf": df["home_pts"], "pa": df["away_pts"],
    "ats_margin": df["margin"] + df["home_spread"],
    "star_dnp": df["home_star_dnp"].astype(int),
})
away = pd.DataFrame({
    "game_id": df["game_id"], "date": df["date"], "team": df["away_team"],
    "post": df["post"], "period": df["period"],
    "won": 1 - df["home_win"], "pf": df["away_pts"], "pa": df["home_pts"],
    "ats_margin": -(df["margin"] + df["home_spread"]),
    "star_dnp": df["away_star_dnp"].astype(int),
})
tg = pd.concat([home, away], ignore_index=True)
tg["covered"] = (tg["ats_margin"] > 0).astype(int)
tg["tanking"] = tg["team"].isin(TANK_MAIN).astype(int)
tg["period"] = pd.Categorical(tg["period"], categories=ORDER, ordered=True)

out = []

monthly = tg.groupby(["period", "tanking"], observed=True).agg(
    n=("won", "size"), ats_margin=("ats_margin", "mean"),
    cover_rate=("covered", "mean"), pa=("pa", "mean"), pf=("pf", "mean"))
out.append("Monthly means by tanking status (main spec):")
out.append(monthly.round(3).to_string())
monthly.to_csv(TAB / "tank_pretrends.csv")

#  subtract other teams' averages from tanking teams' averages
gap = monthly["ats_margin"].unstack()[1] - monthly["ats_margin"].unstack()[0]
gap_pa = monthly["pa"].unstack()[1] - monthly["pa"].unstack()[0]
out.append("\nATS-margin gap (tanking - other) by period:")
out.append(gap.round(3).to_string())
out.append("\nPoints-allowed gap (tanking - other) by period:")
out.append(gap_pa.round(3).to_string())

# Formal F-test (on pre-break months only)
pre = tg[tg["post"] == 0].copy()
pre["period"] = pre["period"].cat.remove_unused_categories()
for outcome in ["ats_margin", "pa"]:
    m = smf.ols(f"{outcome} ~ C(period) + tanking + tanking:C(period)",
                data=pre).fit(
        cov_type="cluster", cov_kwds={"groups": pre["game_id"]})
    terms = [f"tanking:C(period)[T.{p}]" for p in
             ["Nov", "Dec", "Jan", "Feb-pre"]]
    f = m.f_test(terms)
    out.append(f"\nPre-trends F-test, {outcome}: F = {float(f.fvalue):.2f}, "
               f"p = {float(f.pvalue):.3f} (null: no differential pre-trend)")
    for t in terms:
        out.append(f"  {t}: {m.params[t]:.3f} (t={m.tvalues[t]:.2f})")

results_path = ROOT / "outputs" / "tables and texts" / "pretrends_results.txt"
results_path.parent.mkdir(parents=True, exist_ok=True)

results_text = "\n".join(out)
results_path.write_text(results_text + "\n", encoding="utf-8")
print(results_text)

# figure
plt.rcParams.update({
    "font.size": 11, "axes.titlesize": 12, "axes.labelsize": 11,
    "xtick.labelsize": 10, "ytick.labelsize": 10, "legend.fontsize": 10,
    "figure.dpi": 200, "savefig.dpi": 200, "savefig.bbox": "tight",
    "axes.spines.top": False, "axes.spines.right": False,
})
fig, axes = plt.subplots(1, 2, figsize=(8.5, 4))
x = np.arange(len(ORDER))
for ax, col, title, ylabel in [
        (axes[0], "ats_margin", "(a) ATS margin (points)",
         "Mean ATS margin"),
        (axes[1], "pa", "(b) Points allowed per game",
         "Mean points allowed")]:
    piv = monthly[col].unstack()
    ax.plot(x, piv[0], "o-", color="#1f77b4", label="Other teams")
    ax.plot(x, piv[1], "o-", color="#d62728", label="Tanking teams")
    ax.axvline(4.5, color="k", ls="--", lw=1)
    ax.text(4.6, ax.get_ylim()[1], "All-Star\nbreak", fontsize=9, va="top")
    ax.set_xticks(x, ORDER)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=30)
axes[0].legend(fontsize=9)
fig.suptitle("Monthly means by tanking status, before and after "
             "the All-Star break")
fig.savefig(FIG / "tank_fig5_pretrends.png")
plt.close(fig)
print("\nwrote figures/tank_fig5_pretrends.png")
