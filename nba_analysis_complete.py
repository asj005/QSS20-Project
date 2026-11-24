"""Generate all figures and summary-statistics tables for the QSS 20 final report.

Reads outputs/nba_merged_analysis.csv (1,230 games, 2025-26 NBA regular season),
writes PNG figures to figures/ and tables to results/summary_stats.md + results/tables/.

Every headline number is re-computed from the CSV and checked against
results/analysis_results.txt. If a check fails the script raises.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.api as sm

ROOT = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(ROOT, "figures")
TAB = os.path.join(ROOT, "results", "tables")
os.makedirs(FIG, exist_ok=True)
os.makedirs(TAB, exist_ok=True)

plt.rcParams.update({
    "font.size": 11, "axes.titlesize": 12, "axes.labelsize": 11,
    "xtick.labelsize": 10, "ytick.labelsize": 10, "legend.fontsize": 10,
    "figure.dpi": 200, "savefig.dpi": 200, "savefig.bbox": "tight",
    "axes.spines.top": False, "axes.spines.right": False,
})
POLY, SB = "#1f77b4", "#e67e22"  # blue = Polymarket, orange = sportsbook

df = pd.read_csv(os.path.join(ROOT, "outputs", "nba_merged_analysis.csv"))
df["date"] = pd.to_datetime(df["date"])
df["surprise_diff"] = ((df["home_top_pts"] - df["home_top1_trail5"])
                       - (df["away_top_pts"] - df["away_top1_trail5"]))
df["month"] = df["date"].dt.strftime("%b")
assert len(df) == 1230, len(df)

# ---------------------------------------------------------------- verification
def brier(p, y):
    m = p.notna() & y.notna()
    return float(np.mean((p[m] - y[m]) ** 2))

bp = brier(df["poly_home_prob"], df["home_win"])
bs = brier(df["sb_home_prob"], df["home_win"])
assert abs(bp - 0.1949) < 0.001, bp
assert abs(bs - 0.1950) < 0.001, bs
# Form-test subset (the merge script's definition): trailing form exists for
# BOTH top scorers AND neither star is DNP tonight. That is n=581, not the
# 646 games where form_diff alone is non-missing: 65 games have pregame form
# for a star who then sits out, and realized points are undefined for them.
f = df.dropna(subset=["form_diff"])
f = f[(f["home_star_dnp"] == 0) & (f["away_star_dnp"] == 0)]
assert len(f) == 581, len(f)
assert abs(np.corrcoef(f["form_diff"], f["sb_home_prob"])[0, 1] - 0.422) < 0.005
fp = f.dropna(subset=["poly_home_prob"])  # one game has no Poly price
assert abs(np.corrcoef(fp["form_diff"], fp["poly_home_prob"])[0, 1] - 0.426) < 0.005
assert abs(np.corrcoef(f["surprise_diff"], f["margin"])[0, 1] - 0.218) < 0.005
assert abs(np.corrcoef(df["crew_foul_loo"], df["actual_total"])[0, 1] - (-0.033)) < 0.005
print(f"checks passed: Brier Poly {bp:.4f} / SB {bs:.4f}; form sample n={len(f)}")

# ---------------------------------------------------------------- helpers
def calib_table(prob_col):
    """10pp-bucket calibration: mean implied prob vs actual home-win rate."""
    d = df.dropna(subset=[prob_col]).copy()
    d["bin"] = pd.cut(d[prob_col], bins=np.arange(0, 1.01, 0.1),
                      include_lowest=True)
    g = d.groupby("bin", observed=True).agg(
        n=("home_win", "size"), implied=(prob_col, "mean"),
        actual=("home_win", "mean"))
    g["mid"] = [iv.mid for iv in g.index]
    return g.reset_index(drop=True)

def ols(y, X, names):
    Xd = sm.add_constant(X)
    r = sm.OLS(y, Xd, missing="drop").fit()
    out = {n: (round(r.params.iloc[i], 4), round(r.tvalues.iloc[i], 2))
           for i, n in enumerate(["const"] + names)}
    return out, round(r.rsquared, 4), int(r.nobs)

# ================================================================ FIGURE 1
# Calibration curves: implied home-win prob (binned) vs actual win rate.
fig, ax = plt.subplots(figsize=(7, 5))
for col, c, lab, off in [("poly_home_prob", POLY, "Polymarket", (5, 6)),
                         ("sb_home_prob", SB, "Sportsbook", (5, -15))]:
    g = calib_table(col)
    ax.plot(g["implied"], g["actual"], "o-", color=c, label=lab)
    for _, r in g.iterrows():
        ax.annotate(f"n={int(r['n'])}", (r["implied"], r["actual"]),
                    textcoords="offset points", xytext=off, fontsize=8,
                    color=c)
ax.plot([0, 1], [0, 1], "k--", lw=1, label="Perfect calibration")
ax.set_xlabel("Mean implied home-win probability (10pp buckets)")
ax.set_ylabel("Actual home-win rate")
ax.set_title("Figure 1. Calibration: implied probability vs outcomes")
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.legend(loc="upper left")
plt.savefig(os.path.join(FIG, "fig1_calibration.png")); plt.close()

# ================================================================ FIGURE 2
# Brier scores: overall, star-DNP games, no-DNP games.
rows = []
for label, sub in [("All games", df), ("Star DNP", df[df["any_star_dnp"] == 1]),
                   ("No star DNP", df[df["any_star_dnp"] == 0])]:
    rows.append((label, len(sub), brier(sub["poly_home_prob"], sub["home_win"]),
                 brier(sub["sb_home_prob"], sub["home_win"])))
fig, ax = plt.subplots(figsize=(7, 4.2))
x = np.arange(3); w = 0.36
ax.bar(x - w / 2, [r[2] for r in rows], w, color=POLY, label="Polymarket")
ax.bar(x + w / 2, [r[3] for r in rows], w, color=SB, label="Sportsbook")
for i, r in enumerate(rows):
    ax.text(i - w / 2, r[2] + 0.004, f"{r[2]:.4f}", ha="center", fontsize=9)
    ax.text(i + w / 2, r[3] + 0.004, f"{r[3]:.4f}", ha="center", fontsize=9)
ax.set_xticks(x, [f"{r[0]}\n(n={r[1]:,})" for r in rows])
ax.set_ylabel("Brier score (lower is better)")
ax.set_title("Figure 2. Brier scores: Polymarket vs sportsbook")
ax.set_ylim(0, 0.24); ax.legend()
plt.savefig(os.path.join(FIG, "fig2_brier.png")); plt.close()

# ================================================================ FIGURE 3
# Refereeing null: over-hit rate and actual total by crew foul tercile.
df["foul_tercile"] = pd.qcut(df["crew_foul_loo"], 3,
                             labels=["Low foul crew", "Mid foul crew",
                                     "High foul crew"])
t = df.groupby("foul_tercile", observed=True).agg(
    n=("home_win", "size"), over_hit=("over_hit", "mean"),
    actual_total=("actual_total", "mean"), sb_total=("total", "mean"),
    poly_over=("poly_over_prob", "mean"))
fig, axes = plt.subplots(1, 2, figsize=(8.5, 4))
axes[0].bar(t.index, t["over_hit"], color="#2ca02c")
axes[0].axhline(0.5, color="k", ls="--", lw=1)
axes[0].set_ylabel("Share of games going over the total")
axes[0].set_title("Over-hit rate by crew")
axes[0].set_ylim(0.40, 0.58)
for i, v in enumerate(t["over_hit"]):
    axes[0].text(i, v + 0.008, f"{v:.3f}", ha="center", fontsize=9)
axes[1].plot(t.index, t["actual_total"], "o-", label="Actual total")
axes[1].plot(t.index, t["sb_total"], "s--", label="Sportsbook total line")
axes[1].set_ylabel("Points")
axes[1].set_title("Total points by crew")
axes[1].legend()
fig.suptitle("Figure 3. Referee foul tendency does not move totals")
plt.savefig(os.path.join(FIG, "fig3_referees.png")); plt.close()

# ================================================================ FIGURE 4
# Star form is priced: form_diff quintiles vs win rate and implied prob.
f = f.copy()  # the 581-game form-test subset defined above
f["form_q"] = pd.qcut(f["form_diff"], 5, labels=["Q1\n(cold)", "Q2", "Q3",
                                                 "Q4", "Q5\n(hot)"])
g = f.groupby("form_q", observed=True).agg(
    n=("home_win", "size"), win_rate=("home_win", "mean"),
    sb=("sb_home_prob", "mean"), poly=("poly_home_prob", "mean"))
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(g.index, g["win_rate"], "ko-", label="Actual home-win rate")
ax.plot(g.index, g["sb"], "o--", color=SB, label="Sportsbook implied prob")
ax.plot(g.index, g["poly"], "o--", color=POLY, label="Polymarket implied prob")
ax.set_xlabel("Home top scorer trailing-5 form, minus away (quintiles)")
ax.set_ylabel("Home-win probability")
ax.set_title("Figure 4. Star recent form is fully priced by both markets")
ax.set_ylim(0.35, 0.75); ax.legend()
plt.savefig(os.path.join(FIG, "fig4_form_priced.png")); plt.close()

# ================================================================ FIGURE 5
# Star surprise is NOT priced: surprise_diff quintiles vs win rate and margin.
f["surp_q"] = pd.qcut(f["surprise_diff"], 5, labels=["Q1\n(big miss)", "Q2",
                                                     "Q3", "Q4",
                                                     "Q5\n(big beat)"])
g = f.groupby("surp_q", observed=True).agg(
    n=("home_win", "size"), win_rate=("home_win", "mean"),
    margin=("margin", "mean"), sb=("sb_home_prob", "mean"))
fig, axes = plt.subplots(1, 2, figsize=(8.5, 4))
axes[0].plot(g.index, g["win_rate"], "ko-", label="Actual home-win rate")
axes[0].plot(g.index, g["sb"], "o--", color=SB,
             label="Sportsbook implied prob")
axes[0].set_xlabel("Realized star surprise (quintiles)")
axes[0].set_ylabel("Home-win probability")
axes[0].set_title("Win rate vs pregame price")
axes[0].legend(fontsize=9)
axes[1].bar(g.index, g["margin"], color="#9467bd")
axes[1].axhline(0, color="k", lw=1)
axes[1].set_xlabel("Realized star surprise (quintiles)")
axes[1].set_ylabel("Mean home margin (points)")
axes[1].set_title("Margin moves with surprise")
fig.suptitle("Figure 5. Realized star performance moves outcomes beyond the line")
plt.savefig(os.path.join(FIG, "fig5_surprise.png")); plt.close()

# ================================================================ FIGURE 6
# EDA panel: margin, total vs line, implied-prob distributions, fouls.
fig, axes = plt.subplots(2, 2, figsize=(9, 7))
fig.subplots_adjust(hspace=0.55, wspace=0.3)
axes[0, 0].hist(df["margin"], bins=30, color="#7f7f7f")
axes[0, 0].axvline(df["margin"].mean(), color="r", ls="--",
                   label=f"Mean +{df['margin'].mean():.2f}")
axes[0, 0].set_xlabel("Home margin (points)")
axes[0, 0].set_title("(a) Distribution of home margin")
axes[0, 0].legend()
axes[0, 1].scatter(df["total"], df["actual_total"], s=6, alpha=0.35)
lo = min(df["total"].min(), df["actual_total"].min())
hi = max(df["total"].max(), df["actual_total"].max())
axes[0, 1].plot([lo, hi], [lo, hi], "r--", lw=1)
axes[0, 1].set_xlabel("Sportsbook total line")
axes[0, 1].set_ylabel("Actual total points")
axes[0, 1].set_title("(b) Actual total vs the line")
axes[1, 0].hist(df["sb_home_prob"].dropna(), bins=30, alpha=0.6, color=SB,
                label="Sportsbook")
axes[1, 0].hist(df["poly_home_prob"].dropna(), bins=30, alpha=0.6, color=POLY,
                label="Polymarket")
axes[1, 0].set_xlabel("Implied home-win probability")
axes[1, 0].set_title("(c) Implied-probability distributions")
axes[1, 0].legend()
axes[1, 1].hist(df["total_pf"], bins=25, color="#2ca02c")
axes[1, 1].set_xlabel("Total fouls per game")
axes[1, 1].set_title("(d) Distribution of total fouls")
fig.suptitle("Figure 6. Exploratory data analysis: the 1,230-game panel")
plt.savefig(os.path.join(FIG, "fig6_eda.png")); plt.close()

# ================================================================ FIGURE 7
# Polymarket vs sportsbook implied probs (near-identical).
d = df.dropna(subset=["poly_home_prob", "sb_home_prob"])
fig, ax = plt.subplots(figsize=(6, 5.5))
ax.scatter(d["sb_home_prob"], d["poly_home_prob"], s=8, alpha=0.4)
ax.plot([0, 1], [0, 1], "r--", lw=1)
ax.set_xlabel("Sportsbook implied home-win probability")
ax.set_ylabel("Polymarket implied home-win probability")
corr = np.corrcoef(d["sb_home_prob"], d["poly_home_prob"])[0, 1]
mad = np.mean(np.abs(d["sb_home_prob"] - d["poly_home_prob"]))
ax.set_title(f"Figure 7. The two prices are nearly the same\n"
             f"(corr {corr:.3f}, mean |difference| {mad:.3f}, n={len(d):,})")
plt.savefig(os.path.join(FIG, "fig7_poly_vs_sb.png")); plt.close()

# ================================================================ FIGURE 8
# Form-sample coverage by month (the 581-game caveat, shown not hidden).
# Three-way split: in the form sample (form exists, no star DNP); form exists
# but a star is DNP tonight; form missing entirely.
df["form_status"] = np.where(df["form_diff"].isna(), "form missing",
                     np.where((df["home_star_dnp"] == 1)
                              | (df["away_star_dnp"] == 1),
                              "form exists, star DNP", "in form sample"))
cov = df.groupby(["month", "form_status"]).size().unstack(fill_value=0)
order = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr"]
cov = cov.reindex([m for m in order if m in cov.index])
for c in ["in form sample", "form exists, star DNP", "form missing"]:
    if c not in cov.columns:
        cov[c] = 0
fig, ax = plt.subplots(figsize=(7.5, 4.2))
ax.bar(cov.index, cov["in form sample"], color=POLY,
       label="In form sample (581)")
ax.bar(cov.index, cov["form exists, star DNP"],
       bottom=cov["in form sample"], color="#ffbf00",
       label="Form exists, star DNP tonight (65)")
ax.bar(cov.index, cov["form missing"],
       bottom=cov["in form sample"] + cov["form exists, star DNP"],
       color="#d62728", label="Form missing (584)")
for i, m in enumerate(cov.index):
    tot = cov.loc[m].sum()
    ax.text(i, tot + 4, f"{int(cov.loc[m, 'in form sample'])}/{int(tot)}",
            ha="center", fontsize=9)
ax.set_ylabel("Games")
ax.set_title("Figure 8. Form-test coverage by month (581 of 1,230 games)")
ax.legend(fontsize=9)
plt.savefig(os.path.join(FIG, "fig8_coverage.png")); plt.close()

# ================================================================ TABLES
lines = []
lines.append("# Summary statistics and EDA tables (recomputed from "
             "outputs/nba_merged_analysis.csv)\n")
lines.append(f"Games: {len(df):,}; dates {df['date'].min().date()} to "
             f"{df['date'].max().date()}; teams: "
             f"{df['home_team'].nunique()}.\n")

# Table 1: dataset summary stats
desc = df[["margin", "actual_total", "total", "sb_home_prob",
           "poly_home_prob", "crew_foul_loo", "total_pf", "form_diff",
           "surprise_diff"]].describe().T[["count", "mean", "std", "min",
                                           "max"]].round(3)
desc.to_csv(os.path.join(TAB, "table1_summary_stats.csv"))
lines.append("## Table 1. Summary statistics (key variables)\n")
lines.append(desc.to_markdown() + "\n")

# Table 2: headline rates
rates = {
    "Home win rate": df["home_win"].mean(),
    "Mean home margin (pts)": df["margin"].mean(),
    "Over rate (actual total > line)": df["over_hit"].mean(),
    "Home ATS cover rate": df["home_cover"].mean(),
    "Mean sportsbook total line": df["total"].mean(),
    "Mean actual total": df["actual_total"].mean(),
    "Mean total fouls per game": df["total_pf"].mean(),
    "Games with a top-3 scorer DNP": df["any_star_dnp"].mean(),
}
rt = pd.Series(rates).round(4)
rt.to_csv(os.path.join(TAB, "table2_headline_rates.csv"),
          header=["value"])
lines.append("## Table 2. Headline rates\n")
lines.append(rt.to_markdown() + "\n")

# Table 3: coverage
cov_rows = {
    "Sportsbook moneyline (all games)": (1230, 1230),
    "Polymarket moneyline": (int(df["poly_home_prob"].notna().sum()), 1230),
    "Polymarket spread line": (int(df["poly_spread_line"].notna().sum()), 1230),
    "Polymarket spread prob": (int(df["poly_spread_home_prob"].notna().sum()), 1230),
    "Polymarket total line": (int(df["poly_total_line"].notna().sum()), 1230),
    "Polymarket over prob": (int(df["poly_over_prob"].notna().sum()), 1230),
    "Both top scorers trailing form": (int(df["form_diff"].notna().sum()), 1230),
    "Form-test sample (form + no star DNP)": (581, 1230),
    "Crew foul LOO rate": (int(df["crew_foul_loo"].notna().sum()), 1230),
}
ct = pd.DataFrame([(k, v[0], v[1], round(v[0] / v[1], 4))
                   for k, v in cov_rows.items()],
                  columns=["variable", "n", "games", "share"])
ct.to_csv(os.path.join(TAB, "table3_coverage.csv"), index=False)
lines.append("## Table 3. Coverage (non-missing / 1,230 games)\n")
lines.append(ct.to_markdown(index=False) + "\n")

# Table 4: calibration buckets (sportsbook)
for col, name in [("sb_home_prob", "sportsbook"),
                  ("poly_home_prob", "polymarket")]:
    g = calib_table(col)[["mid", "n", "implied", "actual"]].round(3)
    g.to_csv(os.path.join(TAB, f"table4_calibration_{name}.csv"),
             index=False)
    lines.append(f"## Table 4{'' if name == 'sportsbook' else 'b'}. "
                 f"Calibration buckets ({name})\n")
    lines.append(g.to_markdown(index=False) + "\n")

# Table 5: regression table (4 specs, OLS; each spec drops its own missing,
# so spec (2) is n=580: the one game with no Polymarket price)
f581 = df.dropna(subset=["form_diff", "surprise_diff", "home_win"])
f581 = f581[(f581["home_star_dnp"] == 0) & (f581["away_star_dnp"] == 0)]
assert len(f581) == 581, len(f581)
specs = {}
specs["(1) home_win ~ sb_prob + form_diff"], r2a, na = ols(
    f581["home_win"], f581[["sb_home_prob", "form_diff"]],
    ["sb_prob", "form_diff"])
specs["(2) home_win ~ poly_prob + form_diff"], r2b, nb = ols(
    f581["home_win"], f581[["poly_home_prob", "form_diff"]],
    ["poly_prob", "form_diff"])
specs["(3) home_win ~ sb_prob + surprise_diff"], r2c, nc = ols(
    f581["home_win"], f581[["sb_home_prob", "surprise_diff"]],
    ["sb_prob", "surprise_diff"])
specs["(4) home_win ~ sb_prob"], r2d, nd = ols(
    f581["home_win"], f581[["sb_home_prob"]], ["sb_prob"])
reg = pd.DataFrame({
    k: {f"{kk} (coef)": vv[0] for kk, vv in v.items()} for k, v in specs.items()
})
reg.loc["R-squared"] = [r2a, r2b, r2c, r2d]
reg.loc["n"] = [na, nb, nc, nd]
reg.to_csv(os.path.join(TAB, "table5_regressions.csv"))
lines.append("## Table 5. Headline regressions (OLS, coefficients; "
             "t-stats in parentheses below in the docx)\n")
lines.append(reg.to_markdown() + "\n")
lines.append("t-statistics:\n")
for k, v in specs.items():
    lines.append(f"- {k}: " + ", ".join(
        f"{kk} t={vv[1]}" for kk, vv in v.items()) + "\n")

# Table 6: referee terciles + DNP splits
t.to_csv(os.path.join(TAB, "table6_referee_terciles.csv"))
lines.append("\n## Table 6. Referee foul terciles\n")
lines.append(t.round(3).to_markdown() + "\n")
dnp_rows = []
for label, sub in [("Star DNP games", df[df["any_star_dnp"] == 1]),
                   ("No star DNP", df[df["any_star_dnp"] == 0])]:
    dnp_rows.append((label, len(sub),
                     round(brier(sub["poly_home_prob"], sub["home_win"]), 4),
                     round(brier(sub["sb_home_prob"], sub["home_win"]), 4)))
dt = pd.DataFrame(dnp_rows, columns=["sample", "n", "brier_poly",
                                     "brier_sb"])
dt.to_csv(os.path.join(TAB, "table7_dnp_brier.csv"), index=False)
lines.append("## Table 7. Brier scores by star-DNP status\n")
lines.append(dt.to_markdown(index=False) + "\n")

# Correlations worth quoting
lines.append("## Correlations (for the text)\n")
lines.append(f"- corr(form_diff, sb_home_prob) = "
             f"{np.corrcoef(f581['form_diff'], f581['sb_home_prob'])[0, 1]:.3f}\n")
fp581 = f581.dropna(subset=["poly_home_prob"])
lines.append(f"- corr(form_diff, poly_home_prob) = "
             f"{np.corrcoef(fp581['form_diff'], fp581['poly_home_prob'])[0, 1]:.3f}\n")
lines.append(f"- corr(surprise_diff, margin) = "
             f"{np.corrcoef(f581['surprise_diff'], f581['margin'])[0, 1]:.3f}\n")
lines.append(f"- corr(crew_foul_loo, actual_total) = "
             f"{np.corrcoef(df['crew_foul_loo'], df['actual_total'])[0, 1]:.3f}\n")
lines.append(f"- corr(crew_foul_loo, sb total line) = "
             f"{np.corrcoef(df['crew_foul_loo'], df['total'])[0, 1]:.3f}\n")
lines.append(f"- corr(poly_home_prob, sb_home_prob) = {corr:.3f}; "
             f"mean |Poly - SB| = {mad:.3f}\n")
lines.append(f"- Poly closer to outcome in "
             f"{100 * np.mean(np.abs(d['poly_home_prob'] - d['home_win']) < np.abs(d['sb_home_prob'] - d['home_win'])):.1f}% "
             f"of games\n")

with open(os.path.join(ROOT, "results", "summary_stats.md"), "w") as fh:
    fh.write("\n".join(lines))
print("wrote figures + results/summary_stats.md + results/tables/")
print("headline R2 (spec 3):", r2c, "| n:", nc)
