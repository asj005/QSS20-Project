"""Figures for the tanking paper. Reads results/tables/tank_*_main.csv
(main spec: worst five by pre-break win%) and the merged panel for RQ3.
Writes figures/tank_fig1_spread.png ... tank_fig4_brier.png.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(ROOT, "figures")
TAB = os.path.join(ROOT, "results", "tables")

plt.rcParams.update({
    "font.size": 11, "axes.titlesize": 12, "axes.labelsize": 11,
    "xtick.labelsize": 10, "ytick.labelsize": 10, "legend.fontsize": 10,
    "figure.dpi": 200, "savefig.dpi": 200, "savefig.bbox": "tight",
    "axes.spines.top": False, "axes.spines.right": False,
})
TANK, OTHER = "#d62728", "#1f77b4"

spread = pd.read_csv(os.path.join(TAB, "tank_spread_cells_main.csv"),
                     index_col=[0, 1])
totals = pd.read_csv(os.path.join(TAB, "tank_totals_cells_main.csv"),
                     index_col=[0, 1])
mech = pd.read_csv(os.path.join(TAB, "tank_mechanism_main.csv"),
                   index_col=[0, 1])

# ------------------------------------------------- FIG 1: spread DID (null)
fig, axes = plt.subplots(1, 2, figsize=(8.5, 4))
x = np.arange(2); w = 0.36
for ax, col, title, ylim in [
        (axes[0], "cover_rate", "(a) Cover rate", (0.35, 0.60)),
        (axes[1], "ats_margin", "(b) ATS margin (points)", (-2.5, 1.5))]:
    ax.bar(x - w / 2, [spread.loc[(0, 0), col], spread.loc[(0, 1), col]],
           w, color=OTHER, label="Other teams")
    ax.bar(x + w / 2, [spread.loc[(1, 0), col], spread.loc[(1, 1), col]],
           w, color=TANK, label="Tanking teams")
    ax.set_xticks(x, ["Pre-break", "Post-break"])
    ax.set_title(title)
    ax.set_ylim(*ylim)
    if col == "cover_rate":
        ax.axhline(0.5, color="k", ls="--", lw=1)
    else:
        ax.axhline(0, color="k", lw=1)
    for i, (a, b) in enumerate([(spread.loc[(0, 0), col],
                                spread.loc[(1, 0), col]),
                               (spread.loc[(0, 1), col],
                                spread.loc[(1, 1), col])]):
        ax.text(i - w / 2, a + 0.02 if col == "cover_rate" else a + 0.1,
                f"{a:.3f}" if col == "cover_rate" else f"{a:.2f}",
                ha="center", fontsize=9)
        ax.text(i + w / 2, b + 0.02 if col == "cover_rate" else b + 0.1,
                f"{b:.3f}" if col == "cover_rate" else f"{b:.2f}",
                ha="center", fontsize=9)
axes[0].legend(fontsize=9)
fig.suptitle("The spread DID is a null: tanking teams cover no "
             "worse after the break")
plt.savefig(os.path.join(FIG, "tank_fig1_spread.png")); plt.close()

# ------------------------------------------------- FIG 2: totals DID
fig, axes = plt.subplots(1, 2, figsize=(8.5, 4))
for ax, col, title, ylim in [
        (axes[0], "over_hit", "(a) Over-hit rate", (0.35, 0.65)),
        (axes[1], "total_err", "(b) Total forecast error (points)",
         (-1.5, 5.0))]:
    ax.bar(x - w / 2, [totals.loc[(0, 0), col], totals.loc[(0, 1), col]],
           w, color=OTHER, label="Other games")
    ax.bar(x + w / 2, [totals.loc[(1, 0), col], totals.loc[(1, 1), col]],
           w, color=TANK, label="Games with a tanking team")
    ax.set_xticks(x, ["Pre-break", "Post-break"])
    ax.set_title(title)
    ax.set_ylim(*ylim)
    if col == "over_hit":
        ax.axhline(0.5, color="k", ls="--", lw=1)
    else:
        ax.axhline(0, color="k", lw=1)
    for i, (a, b) in enumerate([(totals.loc[(0, 0), col],
                                totals.loc[(1, 0), col]),
                               (totals.loc[(0, 1), col],
                                totals.loc[(1, 1), col])]):
        off = 0.02 if col == "over_hit" else 0.15
        ax.text(i - w / 2, a + off, f"{a:.3f}" if col == "over_hit"
                else f"{a:.2f}", ha="center", fontsize=9)
        ax.text(i + w / 2, b + off, f"{b:.3f}" if col == "over_hit"
                else f"{b:.2f}", ha="center", fontsize=9)
axes[0].legend(fontsize=9)
fig.suptitle("Totals lean the other way: tanking games go over "
             "more after the break")
plt.savefig(os.path.join(FIG, "tank_fig2_totals.png")); plt.close()

# ------------------------------------------------- FIG 3: mechanism (defense)
fig, axes = plt.subplots(1, 2, figsize=(8.5, 4))
for ax, col, title, ylim in [
        (axes[0], "pa", "(a) Points allowed per game", (110, 126)),
        (axes[1], "dnp_rate", "(b) Star DNP rate", (0, 0.16))]:
    ax.bar(x - w / 2, [mech.loc[(0, 0), col], mech.loc[(0, 1), col]],
           w, color=OTHER, label="Other teams")
    ax.bar(x + w / 2, [mech.loc[(1, 0), col], mech.loc[(1, 1), col]],
           w, color=TANK, label="Tanking teams")
    ax.set_xticks(x, ["Pre-break", "Post-break"])
    ax.set_title(title)
    ax.set_ylim(*ylim)
    for i, (a, b) in enumerate([(mech.loc[(0, 0), col],
                                mech.loc[(1, 0), col]),
                               (mech.loc[(0, 1), col],
                                mech.loc[(1, 1), col])]):
        off = 0.3 if col == "pa" else 0.006
        ax.text(i - w / 2, a + off, f"{a:.1f}" if col == "pa" else f"{a:.3f}",
                ha="center", fontsize=9)
        ax.text(i + w / 2, b + off, f"{b:.1f}" if col == "pa" else f"{b:.3f}",
                ha="center", fontsize=9)
axes[0].legend(fontsize=9)
fig.suptitle("The mechanism is defense: tanking teams allow "
             "+3.0 points after the break")
plt.savefig(os.path.join(FIG, "tank_fig3_mechanism.png")); plt.close()

# ------------------------------------------------- FIG 4: RQ3 Brier
df = pd.read_csv(os.path.join(ROOT, "outputs", "nba_merged_analysis.csv"),
                 parse_dates=["date"])
df["post"] = (df["date"] >= "2026-02-19").astype(int)
tank_main = ["Sacramento Kings", "Washington Wizards",
             "New Orleans Pelicans", "Indiana Pacers", "Brooklyn Nets"]
df["tank_game"] = (df["home_team"].isin(tank_main)
                   | df["away_team"].isin(tank_main)).astype(int)

def brier(p, y):
    m = p.notna() & y.notna()
    return float(np.mean((p[m] - y[m]) ** 2))

labels, bp, bs, ns = [], [], [], []
for lab, sub in [("Tanking games\npre-break",
                  df[(df["tank_game"] == 1) & (df["post"] == 0)]),
                 ("Tanking games\npost-break",
                  df[(df["tank_game"] == 1) & (df["post"] == 1)]),
                 ("Other games\npre-break",
                  df[(df["tank_game"] == 0) & (df["post"] == 0)]),
                 ("Other games\npost-break",
                  df[(df["tank_game"] == 0) & (df["post"] == 1)])]:
    labels.append(f"{lab}\n(n={len(sub)})")
    bp.append(brier(sub["poly_home_prob"], sub["home_win"]))
    bs.append(brier(sub["sb_home_prob"], sub["home_win"]))
fig, ax = plt.subplots(figsize=(7.5, 4.2))
x = np.arange(4)
ax.bar(x - w / 2, bp, w, color="#1f77b4", label="Polymarket")
ax.bar(x + w / 2, bs, w, color="#e67e22", label="Sportsbook")
for i in range(4):
    ax.text(i - w / 2, bp[i] + 0.005, f"{bp[i]:.4f}", ha="center",
            fontsize=9)
    ax.text(i + w / 2, bs[i] + 0.005, f"{bs[i]:.4f}", ha="center",
            fontsize=9)
ax.set_xticks(x, labels)
ax.set_ylabel("Brier score (lower is better)")
ax.set_title("Polymarket is no better than the sportsbook on "
             "tanking games")
ax.set_ylim(0, 0.27)
ax.legend()
plt.savefig(os.path.join(FIG, "tank_fig4_brier.png")); plt.close()
print("wrote tank_fig1-4")
