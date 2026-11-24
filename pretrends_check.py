"""Pre-trends check for the tanking DID.

The DID assumes tanking and non-tanking teams would have trended together
without the All-Star break (parallel trends). This script checks it two ways:

  1. Monthly means: ATS margin and points allowed by tanking status, in
     eight periods (Oct, Nov, Dec, Jan, Feb-pre, Feb-post, Mar, Apr).
     If the two groups move together before the break, the assumption holds.
  2. Formal F-test (pre-break only): ATS margin (and points allowed) on
     month dummies + tanking + tanking x month. The null is that all
     tanking x month interactions are zero, i.e. no differential pre-trend.

Writes results/pretrends_results.txt, results/tables/tank_pretrends.csv,
and figures/tank_fig5_pretrends.png.
"""
import os
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.abspath(__file__))
TAB = os.path.join(ROOT, "results", "tables")
FIG = os.path.join(ROOT, "figures")
os.makedirs(TAB, exist_ok=True)

df = pd.read_csv(os.path.join(ROOT, "outputs", "nba_merged_analysis.csv"))
df["date"] = pd.to_datetime(df["date"])
df["game_id"] = np.arange(len(df))
df["post"] = (df["date"] >= "2026-02-19").astype(int)

TANK_MAIN = ["Sacramento Kings", "Washington Wizards",
             "New Orleans Pelicans", "Indiana Pacers", "Brooklyn Nets"]

# Period bins; February is split at the All-Star break.
def period(d):
    if d < pd.Timestamp("2025-11-01"):
        return "Oct"
    if d < pd.Timestamp("2025-12-01"):
        return "Nov"
    if d < pd.Timestamp("2026-01-01"):
        return "Dec"
    if d < pd.Timestamp("2026-02-01"):
        return "Jan"
    if d < pd.Timestamp("2026-02-13"):
        return "Feb-pre"
    if d < pd.Timestamp("2026-03-01"):
        return "Feb-post"
    if d < pd.Timestamp("2026-04-01"):
        return "Mar"
    return "Apr"

ORDER = ["Oct", "Nov", "Dec", "Jan", "Feb-pre", "Feb-post", "Mar", "Apr"]
df["period"] = df["date"].apply(period)

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
monthly.to_csv(os.path.join(TAB, "tank_pretrends.csv"))

# Gap series: tanking minus other, per period.
gap = monthly["ats_margin"].unstack()[1] - monthly["ats_margin"].unstack()[0]
gap_pa = monthly["pa"].unstack()[1] - monthly["pa"].unstack()[0]
out.append("\nATS-margin gap (tanking - other) by period:")
out.append(gap.round(3).to_string())
out.append("\nPoints-allowed gap (tanking - other) by period:")
out.append(gap_pa.round(3).to_string())

# Formal F-test on pre-break months only (Oct is the reference month).
# Drop the unused post-break categories first, or the design is rank-deficient.
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

with open(os.path.join(ROOT, "results", "pretrends_results.txt"), "w") as fh:
    fh.write("\n".join(out) + "\n")
print("\n".join(out))

# ------------------------------------------------------------- figure
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
plt.savefig(os.path.join(FIG, "tank_fig5_pretrends.png"))
plt.close()
print("\nwrote figures/tank_fig5_pretrends.png")
