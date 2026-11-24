"""Build the QSS 20 final-report scaffold (.docx).

The scaffold is NOT a finished paper: it holds the full structure, every table
and figure (recomputed from the data), the formal methods, and [WRITE] prompts
that say exactly what each paragraph should cover and which numbers to use.
The prose paragraphs are for Ahaan and Siddharth to write.

Checkpoint 2 fixes applied (see the fix checklist on page 1):
  Q1  no template text anywhere; delete the "How to use" page before submitting
  Q4  Related Work is prose-only by design (no bold headers, no bullets)
  Q5  cleaning detail moved to Appendix A; every source hyperlinked;
      summary stats + plots in the Data section
  Q6  formal methods with equations in Section 4; EDA (Figure 6) before tests
"""
import csv
import os
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Inches, Pt, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "figures")
TAB = os.path.join(ROOT, "results", "tables")
OUT = os.path.join(ROOT, "report")
os.makedirs(OUT, exist_ok=True)

GREY = RGBColor(0x59, 0x59, 0x59)
doc = Document()
style = doc.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(12)
style.paragraph_format.space_after = Pt(6)

# ------------------------------------------------------------------ helpers
def h1(text):
    return doc.add_heading(text, level=1)

def h2(text):
    return doc.add_heading(text, level=2)

def p(text="", bold=False, italic=False, size=None, align=None,
      color=None):
    par = doc.add_paragraph()
    run = par.add_run(text)
    run.bold = bold
    run.italic = italic
    if size:
        run.font.size = Pt(size)
    if color:
        run.font.color.rgb = color
    if align:
        par.alignment = align
    return par

def note(text):
    """Guidance for the authors. Delete before submitting."""
    par = doc.add_paragraph()
    run = par.add_run(text)
    run.italic = True
    run.font.size = Pt(11)
    run.font.color.rgb = GREY
    return par

def write_prompt(text):
    """A [WRITE] block: what the paragraph(s) should say, with the numbers."""
    par = doc.add_paragraph()
    run = par.add_run("[WRITE] " + text)
    run.italic = True
    run.font.size = Pt(11)
    run.font.color.rgb = GREY
    return par

def equation(text):
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = par.add_run(text)
    run.italic = True
    run.font.size = Pt(12)
    return par

def hyperlink(paragraph, url, text):
    part = paragraph.part
    r_id = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
                          is_external=True)
    el = OxmlElement("w:hyperlink")
    el.set(qn("r:id"), r_id)
    run = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "0563C1")
    rpr.append(color)
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rpr.append(u)
    run.append(rpr)
    t = OxmlElement("w:t")
    t.text = text
    run.append(t)
    el.append(run)
    paragraph._p.append(el)

def link_para(label, url, text, suffix=""):
    par = doc.add_paragraph()
    par.add_run(label)
    hyperlink(par, url, text)
    if suffix:
        par.add_run(suffix)
    return par

def table_from_csv(path, caption, col_widths=None):
    with open(path, newline="") as fh:
        rows = list(csv.reader(fh))
    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = table.cell(i, j)
            cell.text = ""
            run = cell.paragraphs[0].add_run(val)
            run.font.size = Pt(10)
            if i == 0:
                run.bold = True
    p(caption, italic=True, size=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    return table

def table_manual(headers, rows, caption):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, val in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = ""
        run = cell.paragraphs[0].add_run(val)
        run.bold = True
        run.font.size = Pt(10)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = table.cell(i + 1, j)
            cell.text = ""
            run = cell.paragraphs[0].add_run(str(val))
            run.font.size = Pt(10)
    p(caption, italic=True, size=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    return table

def figure(fname, caption, width=6.0):
    doc.add_picture(os.path.join(FIG, fname), width=Inches(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    p(caption, italic=True, size=10, align=WD_ALIGN_PARAGRAPH.CENTER)

# ============================================================ HOW TO USE
doc.add_heading("How to use this file (DELETE THIS PAGE BEFORE SUBMITTING)",
                level=1)
note("This is a scaffold, not a finished paper. It has the full structure, "
     "every table and figure, the formal methods, and [WRITE] prompts telling "
     "you exactly what each paragraph should cover and which numbers to use. "
     "The prose is yours to write. Delete every grey [NOTE] and [WRITE] block "
     "and this page before submitting. Nothing in this file is template text: "
     "there is nothing left to strip out (that was the Q1 deduction last time).")
note("Loop in Siddharth before submitting. This is a joint grade.")
p("")
doc.add_heading("Checkpoint 2 fix checklist (5.2/8.0 -> what changed)",
                level=2)
table_manual(
    ["Checkpoint 2 deduction", "Fix in this report"],
    [["Q1 Overall -1.0: template instructions left on page 1",
      "No template text anywhere in this file."],
     ["Q4 Related Work -0.5: bold headers + bullets",
      "Section 2 is prose-only by design. No bold headers, no bullets."],
     ["Q5 Data -0.3: cleaning too detailed in main text",
      "Cleaning detail moved to Appendix A. Section 3 stays short."],
     ["Q5 Data -0.2: no hyperlinks to data sources",
      "Every source is hyperlinked in Section 3 and in References."],
     ["Q5 Data -0.3: no summary stats or plots",
      "Tables 1-3 and Figures 6 and 8 in Section 3."],
     ["Q6 Methodology -0.3: methods not formal",
      "Section 4 defines every measure and gives every estimating equation."],
     ["Q6 Methodology -0.2: no EDA before tests",
      "Figure 6 (EDA panel) and EDA prompts sit in Section 3, before any test."],
     ["Q2 note (not applied): README should be more than a file tree",
      "README describes the pipeline, the figures, and how to reproduce."]],
    "Table 0. How each Checkpoint 2 comment is answered in this report.")
doc.add_page_break()

# ============================================================ TITLE PAGE
p("QSS 20 \u00b7 Modern Statistical Computing \u00b7 Fall 2026",
  align=WD_ALIGN_PARAGRAPH.CENTER, size=12)
p("")
note("[NOTE \u2014 TITLE: pick one before submitting. The Checkpoint 2 title, "
     "\u201cThe Spread Doesn\u2019t Tank,\u201d does not match this analysis: "
     "nothing in the data tests tanking directly. The star-absence analysis is "
     "adjacent (rested stars) but the DNP result is noisy and does not support "
     "a tanking-blind-spot claim. Options:]")
p("Priced In: What Prediction Markets and Sportsbooks Know \u2014 and Miss "
  "\u2014 About NBA Games", bold=True, size=16,
  align=WD_ALIGN_PARAGRAPH.CENTER)
p("Polymarket vs the Sportsbook: A 1,230-Game Test on the 2025\u201326 NBA "
  "Season", size=13, align=WD_ALIGN_PARAGRAPH.CENTER)
p("What Moves the Line? Prediction Markets, Sportsbooks, and the 2025\u201326 "
  "NBA Season", size=13, align=WD_ALIGN_PARAGRAPH.CENTER)
p("")
p("Ahaan Jindal and Siddharth Singh", align=WD_ALIGN_PARAGRAPH.CENTER)
p("Dartmouth College", align=WD_ALIGN_PARAGRAPH.CENTER)
p("November 24, 2026", align=WD_ALIGN_PARAGRAPH.CENTER)
p("")
link_para("GitHub repository: ", "https://github.com/asj005/QSS20-Project",
          "github.com/asj005/QSS20-Project")
doc.add_page_break()

# ============================================================ 1 INTRODUCTION
h1("1  Introduction")
write_prompt(
    "Paragraph 1 \u2014 the question. Prediction markets have grown fast, and "
    "the natural benchmark for whether their prices mean anything is the "
    "sportsbook: bookmakers have priced NBA games for decades. This paper "
    "runs the head-to-head on the same games: every 2025\u201326 NBA "
    "regular-season game (1,230), Polymarket moneyline prices against "
    "sportsbook closing lines, scored on the actual outcomes.")
write_prompt(
    "Paragraph 2 \u2014 the three tests. (1) Calibration: which price is "
    "closer to the truth? (2) Referees: does a foul-prone officiating crew "
    "move totals, and do either market\u2019s totals account for it? "
    "(3) Stars: do the markets price a star\u2019s recent form, and does "
    "realized star performance move outcomes beyond the pregame price? "
    "State each as a question, not a claim.")
write_prompt(
    "Paragraph 3 \u2014 the answers, one sentence each. The head-to-head is "
    "a tie (Brier 0.1949 vs 0.1950). Referee foul tendency does not move "
    "totals (corr \u22120.03). Both markets fully price star recent form "
    "(t \u2248 0.7\u20130.8). Realized star performance is the one thing "
    "that moves outcomes beyond any pregame price (t = 4.2, R\u00b2 = 0.155).")
write_prompt(
    "Paragraph 4 \u2014 roadmap. One sentence per section: data, methods, "
    "results, discussion.")

# ============================================================ 2 RELATED WORK
h1("2  Related Work")
note("[NOTE \u2014 this section cost 0.5 points last time for bold headers and "
     "bullet points. Write it as continuous prose: one paragraph per paper or "
     "per strand, and blend how each paper differs from yours into the "
     "description of that paper instead of listing differences separately. "
     "No bold subheadings, no bullets. Reuse the papers from Checkpoint 2; "
     "no citations are invented here, so fill in the names from your "
     "Checkpoint 2 draft.]")
write_prompt(
    "Paragraph 1 \u2014 prediction-market accuracy. Discuss the literature "
    "on whether prediction-market prices beat other forecasts (election and "
    "sports markets), what it finds, and how your setting differs: same "
    "games, same outcomes, two prices side by side, scored with Brier and "
    "log loss rather than argued in the abstract.")
write_prompt(
    "Paragraph 2 \u2014 sports-betting market efficiency. Discuss the "
    "literature on whether sportsbook lines are efficient and where "
    "inefficiencies have been claimed (favorite-longshot bias, home bias, "
    "public-team effects). Your calibration buckets (Table 4, Figure 1) "
    "speak directly to this: note where your buckets sit relative to the "
    "diagonal and whether any favorite-longshot pattern shows up.")
write_prompt(
    "Paragraph 3 \u2014 what moves NBA outcomes beyond the line. Referee "
    "effects, star-player effects, rest and load management. For each, one "
    "or two sentences on what the literature says, then how your test is "
    "set up differently (leave-one-out crew foul rate; trailing-5 form vs "
    "realized surprise; top-3-scorer DNP flags). End the section with a "
    "sentence stating the gap your paper fills.")

# ============================================================ 3 DATA
h1("3  Data")
write_prompt(
    "Paragraph 1 \u2014 the panel in one paragraph. 1,230 games, the full "
    "2025\u201326 NBA regular season, October 21, 2025 to April 12, 2026, "
    "30 teams, 82 games each. One row per game. Scores, closing moneylines, "
    "spreads and totals; Polymarket moneyline, spread and totals prices "
    "taken as the last trade before tip-off; box scores and officials for "
    "every game. The NBA Cup final (December 16, 2025) is excluded because "
    "it does not count in the regular-season standings; playoffs and "
    "play-in games are not in the sample.")
p("Data sources", bold=True)
link_para("Scores, box scores, officials, tip-off times: ",
          "https://www.basketball-reference.com/leagues/NBA_2026_games.html",
          "Basketball-Reference, 2025\u201326 NBA schedule and box scores",
          ".")
link_para("Closing moneylines, spreads, totals: ",
          "https://www.teamrankings.com/nba/matchup/",
          "TeamRankings closing lines", ".")
link_para("Prediction-market prices: ",
          "https://gamma-api.polymarket.com/events?tag_id=745",
          "Polymarket Gamma API (NBA events, tag 745)",
          " and the Polymarket CLOB price-history endpoint, last price at or "
          "before tip-off.")
note("[NOTE \u2014 why Polymarket and not Kalshi: Kalshi publishes no public "
     "price history for event markets, so historical Kalshi odds for the "
     "2025\u201326 season do not exist. Say so in one sentence; it "
     "pre-empts the obvious question.]")
write_prompt(
    "Paragraph 2 \u2014 what each source contributes and how they join. "
    "Everything joins on date and the two teams; team names match exactly "
    "across sources. Moneyline coverage is nearly complete (Table 3); "
    "spread and totals coverage on Polymarket is thinner because those "
    "markets sometimes had no trade in the 24 hours before tip-off. "
    "Implied probabilities are vig-free: each moneyline is converted to an "
    "implied probability and the two sides are normalized to sum to one.")
table_from_csv(os.path.join(TAB, "table1_summary_stats.csv"),
               "Table 1. Summary statistics for key variables (1,230 games).")
table_from_csv(os.path.join(TAB, "table2_headline_rates.csv"),
               "Table 2. Headline rates for the 2025\u201326 season.")
table_from_csv(os.path.join(TAB, "table3_coverage.csv"),
               "Table 3. Coverage: non-missing observations per variable.")
write_prompt(
    "Paragraph 3 \u2014 read Tables 1\u20133 in words. Home teams won 55.4% "
    "of games by an average of 1.74 points; 49.1% of games went over the "
    "total and home teams covered 51.6% of spreads, so the lines look "
    "roughly right on average. The average total line was 230.7 points "
    "against an average actual total of 231.2. Polymarket moneyline "
    "coverage is 1,229 of 1,230 games; the one miss is March 1, 2026, "
    "San Antonio at New York, which had no trade in the 24 hours before "
    "tip-off.")
figure("fig6_eda.png",
       "Figure 6. Exploratory data analysis. (a) Home margin centers near "
       "zero with mean +1.74. (b) Actual totals track the sportsbook line. "
       "(c) The two markets\u2019 implied-probability distributions nearly "
       "coincide. (d) Total fouls per game average 39.7.")
write_prompt(
    "Paragraph 4 \u2014 EDA, before any test (this was the missing Q6 "
    "piece). Walk through Figure 6: the margin distribution, the tight "
    "relationship between the total line and the actual total, and the "
    "near-identical implied-probability distributions, which already hints "
    "at the head-to-head result. Note the fouls distribution as the raw "
    "material for the referee test.")
figure("fig8_coverage.png",
       "Figure 8. Form-test coverage by month. The form tests run on 581 "
       "games: 584 games have no trailing form for at least one top scorer, "
       "and 65 games have form but a star who sits out that night.")
write_prompt(
    "Paragraph 5 \u2014 the coverage caveat, stated up front. The form and "
    "surprise tests use 581 games, not 1,230, and Figure 8 shows why. A "
    "top scorer often has no box-score row at all when he is out (injured "
    "or resting, not even listed as DNP), so his trailing form is missing; "
    "and in 65 games the form exists but the star sits out that night, so "
    "realized points are undefined. Game 1 has no trailing form by "
    "definition. The Brier, referee, and DNP tests use the full 1,230 "
    "games; only the form and surprise tests use the 581-game subset.")
note("[NOTE \u2014 cleaning detail lives in Appendix A, not here. That was "
     "a 0.3-point deduction last time. Do not move it back.]")


# ============================================================ 4 METHODOLOGY
h1("4  Methodology")
note("[NOTE \u2014 this section cost 0.5 points last time: methods were "
     "stated, not explained formally, and there was no EDA before the tests. "
     "Every measure below is defined with its formula, and every regression "
     "is written out. Describe the method behind each result in prose, not "
     "just the result.]")
h2("4.1  From prices to probabilities")
write_prompt(
    "One paragraph. A moneyline converts to an implied probability, and "
    "because the bookmaker\u2019s margin makes the two sides sum to more "
    "than one, normalize: divide each side\u2019s implied probability by "
    "the sum of the two. The same normalization applies to Polymarket "
    "prices. Report the average overround (4.50%) so the reader knows how "
    "much margin was removed. All probabilities in the paper are these "
    "vig-free probabilities.")
equation("p\u2095\u2092\u2098\u2091 = (1 / odds\u2095\u2092\u2098\u2091) / "
         "(1 / odds\u2095\u2092\u2098\u2091 + 1 / odds\u2090\u2097\u2090\u2091)")
h2("4.2  Scoring the head-to-head")
write_prompt(
    "One paragraph. Two proper scoring rules. The Brier score is the mean "
    "squared error between the stated probability and the outcome; the log "
    "loss penalizes confident wrongness more heavily. Lower is better on "
    "both. A market that is better calibrated and more confident when right "
    "wins on both; a market that is only louder loses on log loss. Report "
    "both so the comparison does not hinge on one rule.")
equation("Brier = (1/N) \u03a3 (p\u1d62 \u2212 y\u1d62)\u00b2")
equation("Log loss = \u2212(1/N) \u03a3 [y\u1d62 log p\u1d62 + "
         "(1 \u2212 y\u1d62) log(1 \u2212 p\u1d62)]")
write_prompt(
    "One paragraph on calibration buckets. Group games into 10-percentage-"
    "point buckets of implied home-win probability and compare the mean "
    "implied probability to the actual home-win rate in each bucket "
    "(Figure 1, Table 4). A calibrated market sits on the diagonal; "
    "systematic deviation in a bucket is miscalibration, not noise, when "
    "the bucket is large.")
h2("4.3  Referee foul tendency")
write_prompt(
    "One paragraph. Each game has a three-person crew. A crew\u2019s foul "
    "tendency is its leave-one-out mean: the average total fouls per game "
    "across all other games that crew officiated, excluding the game in "
    "question, so the measure cannot mechanically contain the game being "
    "explained. Crews range from 38.2 to 44.1 fouls per game on this "
    "measure. The test is whether that tendency predicts the actual total, "
    "the sportsbook total line, or the Polymarket over probability, and "
    "whether games split by foul tercile differ in over-hit rates.")
equation("crew_foul\u2097 = mean total fouls in crew c\u2019s games, "
         "excluding game i")
h2("4.4  Stars: form, surprise, and absences")
write_prompt(
    "One paragraph on definitions. A team\u2019s star is one of its top "
    "three scorers by season points per game (total points divided by games "
    "played, computed from the season\u2019s own box scores); the top "
    "scorer is number one by that ranking. Trailing-5 form is a top "
    "scorer\u2019s mean points per game over his previous five games "
    "played, using however many prior games exist early in the season. "
    "Star surprise is tonight\u2019s points minus trailing-5 form. Both "
    "are differenced home minus away, so a positive value favors the home "
    "team. Note the caveat: the star label is retrospective, because it "
    "uses full-season scoring to label every game including early ones.")
equation("form_diff = trailing-5 PPG (home top scorer) \u2212 trailing-5 "
         "PPG (away top scorer)")
equation("surprise_diff = (points \u2212 trailing-5 PPG) home \u2212 "
         "(points \u2212 trailing-5 PPG) away")
write_prompt(
    "One paragraph on the regressions. Each regression is a linear "
    "probability model of the home win on the pregame price plus the "
    "variable of interest, run on the 581-game form sample. If the price "
    "already contains the information, the added variable\u2019s "
    "coefficient is zero; if it adds signal beyond the price, the "
    "coefficient is nonzero. Report t-statistics and R\u00b2 for each "
    "specification (Table 5).")
equation("home_win = \u03b2\u2080 + \u03b2\u2081 \u00b7 sb_prob + "
         "\u03b2\u2082 \u00b7 form_diff + \u03b5  (spec 1)")
equation("home_win = \u03b2\u2080 + \u03b2\u2081 \u00b7 poly_prob + "
         "\u03b2\u2082 \u00b7 form_diff + \u03b5  (spec 2)")
equation("home_win = \u03b2\u2080 + \u03b2\u2081 \u00b7 sb_prob + "
         "\u03b2\u2082 \u00b7 surprise_diff + \u03b5  (spec 3)")
equation("home_win = \u03b2\u2080 + \u03b2\u2081 \u00b7 sb_prob + "
         "\u03b5  (spec 4, baseline)")

# ============================================================ 5 RESULTS
h1("5  Results & Findings")
h2("5.1  The head-to-head is a tie")
figure("fig1_calibration.png",
       "Figure 1. Calibration: mean implied home-win probability vs actual "
       "home-win rate, in 10-percentage-point buckets. Both markets sit "
       "close to the diagonal; bucket sizes are annotated.")
table_from_csv(os.path.join(TAB, "table4_calibration_sportsbook.csv"),
               "Table 4a. Calibration buckets, sportsbook.")
table_from_csv(os.path.join(TAB, "table4_calibration_polymarket.csv"),
               "Table 4b. Calibration buckets, Polymarket.")
write_prompt(
    "Paragraph 1 \u2014 calibration. Read Figure 1 and Table 4: both "
    "markets track the diagonal closely across the full range. The "
    "largest deviations are in thin buckets (the 0\u201310% bucket has 15 "
    "sportsbook games and 22 Polymarket games, all home losses). No "
    "favorite-longshot pattern stands out: heavy favorites (90%+) won "
    "every game in both markets\u2019 top buckets.")
figure("fig2_brier.png",
       "Figure 2. Brier scores, Polymarket vs sportsbook: all games, "
       "star-DNP games, and no-DNP games. Lower is better.")
figure("fig7_poly_vs_sb.png",
       "Figure 7. Polymarket vs sportsbook implied home-win probability, "
       "one point per game (corr 0.997, mean absolute difference 0.012).")
write_prompt(
    "Paragraph 2 \u2014 the scores. Brier: Polymarket 0.1949, sportsbook "
    "0.1950, on 1,229 and 1,230 games. Log loss: 0.5706 vs 0.5716. "
    "Polymarket\u2019s price was closer to the outcome in 60.6% of games, "
    "but the average gap is tiny (mean absolute error 0.392 vs 0.395). "
    "Figure 7 explains why: the two prices correlate at 0.997 with a mean "
    "absolute difference of 1.2 percentage points. Two prices that agree "
    "this closely cannot differ much in accuracy, and they do not. State "
    "the verdict plainly: on moneylines, neither market beats the other.")
h2("5.2  Referee foul tendency does not move totals")
figure("fig3_referees.png",
       "Figure 3. Left: over-hit rate by crew foul tercile (dashed line at "
       "50%). Right: actual total vs sportsbook total line by tercile. "
       "Neither moves with the crew.")
table_from_csv(os.path.join(TAB, "table6_referee_terciles.csv"),
               "Table 6. Outcomes by crew foul tercile (410 games each).")
write_prompt(
    "One or two paragraphs. The correlation between the crew\u2019s "
    "leave-one-out foul rate and the actual total is \u22120.033; with the "
    "sportsbook total line it is \u22120.012 and with the Polymarket over "
    "probability 0.011. Split into terciles, the over-hit rate is 51.0% "
    "for low-foul crews, 48.0% mid, 48.3% high \u2014 flat. Actual totals "
    "are 232.1, 230.7, 230.8 across the terciles, against lines of 230.7, "
    "231.1, 230.4. In the regression of the actual total on the line plus "
    "the crew foul rate, the crew coefficient is \u22120.98 with t = "
    "\u22121.09: indistinguishable from zero. This is a null, and a null "
    "is a finding: foul-prone crews are not a totals signal, and neither "
    "market needs to price them.")
h2("5.3  Star absences: both markets adjust, roughly")
table_from_csv(os.path.join(TAB, "table7_dnp_brier.csv"),
               "Table 7. Brier scores split by whether a top-3 scorer sat out.")
write_prompt(
    "One or two paragraphs. 210 games had a top-3 scorer sitting out (109 "
    "home, 116 away; some games had both). In DNP games the Brier scores "
    "are Polymarket 0.1890 vs sportsbook 0.1865; in no-DNP games 0.1962 vs "
    "0.1968. Neither market breaks down when a star sits. When the home "
    "star sat, the home team won 46.8% of games against implied "
    "probabilities near 50% from both markets (n = 109, noisy); when the "
    "away star sat, the away team won 38.8% against 37.8\u201338.0% "
    "implied. The home-star gap is the largest deviation in the paper, "
    "but with 109 games the standard error is about 4.8 points, so do not "
    "oversell it: report it as suggestive, not as a blind spot.")
h2("5.4  Star form is priced; star surprise is not")
figure("fig4_form_priced.png",
       "Figure 4. Home top-scorer trailing-5 form (quintiles) vs the "
       "actual home-win rate and both markets\u2019 implied probabilities. "
       "The prices track form closely.")
figure("fig5_surprise.png",
       "Figure 5. Realized star surprise (quintiles) vs the actual "
       "home-win rate and margin. The pregame price is flat across "
       "quintiles while outcomes move sharply.")
table_manual(
    ["", "(1) form, SB", "(2) form, Poly", "(3) surprise, SB",
     "(4) baseline"],
    [["const", "0.104 (t=1.67)", "0.109 (t=1.79)", "0.064 (t=1.15)",
      "0.083 (t=1.48)"],
     ["sb_prob", "0.848 (t=8.04)", "\u2014", "0.909 (t=9.62)",
      "0.883 (t=9.24)"],
     ["poly_prob", "\u2014", "0.837 (t=8.12)", "\u2014", "\u2014"],
     ["form_diff", "0.002 (t=0.79)", "0.002 (t=0.70)", "\u2014", "\u2014"],
     ["surprise_diff", "\u2014", "\u2014", "0.008 (t=4.22)", "\u2014"],
     ["R\u00b2", "0.129", "0.131", "0.155", "0.129"],
     ["n", "581", "580", "581", "581"]],
    "Table 5. Home win on the pregame price plus form or surprise (OLS, "
    "linear probability model). Coefficients with t-statistics in "
    "parentheses. Spec (2) has 580 games: one game has no Polymarket price.")
write_prompt(
    "Paragraph 1 \u2014 form is priced. The correlation between the form "
    "difference and each market\u2019s implied probability is 0.42\u2013"
    "0.43, and Figure 4 shows the prices tracking form quintile by "
    "quintile. In the regressions, form adds nothing once the price is in: "
    "coefficient 0.002 with t = 0.79 against the sportsbook price and "
    "t = 0.70 against Polymarket. A hot star is already in the line.")
write_prompt(
    "Paragraph 2 \u2014 surprise is not, and cannot be. Realized star "
    "surprise correlates 0.218 with the home margin. In spec (3) its "
    "coefficient is 0.008 with t = 4.22, and R\u00b2 rises from 0.129 to "
    "0.155. Figure 5 shows it: across surprise quintiles the home-win "
    "rate runs from 43% to 68% and the mean margin from \u22123.8 to +6.6 "
    "points, while the pregame price sits near 55% throughout. Frame this "
    "carefully: surprise is news by construction, so this is a statement "
    "about the limits of pregame prices, not a market failure. Nobody can "
    "price tonight\u2019s performance before tonight.")

# ============================================================ 6 DISCUSSION
h1("6  Discussion & Interpretations")
write_prompt(
    "Paragraph 1 \u2014 what the tie means. Two markets built on different "
    "mechanisms (a bookmaker\u2019s line, a crowd\u2019s traded price) "
    "converge to within 1.2 points of each other and score identically. "
    "That is the efficient-market result: on the most liquid, most "
    "scrutinized NBA market, the moneyline, there is no free accuracy "
    "lying around in either place. The 60.6% figure (Polymarket closer "
    "more often) sounds like an edge until you see the average gap: "
    "0.3 points of absolute error.")
write_prompt(
    "Paragraph 2 \u2014 the two nulls. Referee foul tendency and star form "
    "are the kind of variables that sound like edges and are not: the "
    "first does not move the outcome at all, the second moves the outcome "
    "but is already in the price. Distinguish those two kinds of null "
    "explicitly, because they have opposite implications for a bettor.")
write_prompt(
    "Paragraph 3 \u2014 the one real signal, and its limits. Realized star "
    "surprise is the largest single driver of outcomes beyond the price in "
    "this data. But it is only observable after the game, so it is not a "
    "betting signal; it is a bound on how good any pregame price can be. "
    "The honest use of it is in-game: a star beating his form early is "
    "information a live market should move on, which is a future-work "
    "question, not a claim this paper can make.")
write_prompt(
    "Paragraph 4 \u2014 limitations. One season, so everything is a "
    "2025\u201326 statement. The head-to-head is moneyline-only: "
    "Polymarket spread and totals coverage is thinner (Table 3), so the "
    "spread and totals comparison is weaker. The form tests use 581 games "
    "for the reasons in Section 3. The star label is retrospective. None "
    "of this is causal: the regressions describe what is and is not in "
    "the price.")

# ============================================================ 7 CONCLUSION
h1("7  Conclusions & Future Work")
write_prompt(
    "Paragraph 1 \u2014 the findings in four sentences: the tie, the "
    "referee null, form priced, surprise as the residual driver. No new "
    "numbers here; point back to the tables and figures.")
write_prompt(
    "Paragraph 2 \u2014 future work. Three concrete directions: (1) the "
    "spread and totals head-to-head once Polymarket coverage is fuller, "
    "or with live polling during a season; (2) in-game prices, testing "
    "whether live markets move fast enough on early star surprise; "
    "(3) more seasons, to check whether the home-star-DNP gap in Section "
    "5.3 is real or noise. Each one follows from a specific limitation in "
    "Section 6.")

# ============================================================ REFERENCES
h1("References")
note("[NOTE \u2014 reuse your Checkpoint 2 references for the literature, "
     "formatted as in the example reports. The data sources below go in "
     "too, with hyperlinks (that was a 0.2-point deduction last time).]")
link_para("Basketball-Reference. 2025\u201326 NBA schedule, scores, box "
          "scores, officials. ",
          "https://www.basketball-reference.com/leagues/NBA_2026_games.html",
          "basketball-reference.com/leagues/NBA_2026_games.html", ".")
link_para("TeamRankings. NBA closing moneylines, spreads, totals. ",
          "https://www.teamrankings.com/nba/matchup/",
          "teamrankings.com/nba/matchup/", ".")
link_para("Polymarket. Gamma API (NBA events) and CLOB price history. ",
          "https://gamma-api.polymarket.com/events?tag_id=745",
          "gamma-api.polymarket.com", ".")
p("[Add the Checkpoint 2 literature references here.]", italic=True,
  color=GREY)

# ============================================================ APPENDICES
doc.add_page_break()
h1("Appendix A  Data cleaning and validation")
note("[NOTE \u2014 this is where the cleaning detail lives now. It was in "
     "the main text last time and cost 0.3 points. Keep it here.]")
p("Joins and identifiers. ", bold=True)
p("All four sources join on date and the two team names, which match "
  "exactly across Basketball-Reference, TeamRankings, and Polymarket. "
  "Tip-off times come from the Basketball-Reference schedule pages.")
p("Polymarket prices. ", bold=True)
p("Events come from the Gamma API (NBA tag 745); prices come from the "
  "CLOB price-history endpoint as the last traded price at or before "
  "tip-off. The median price is 1.0 hour before tip-off; 1.3% of prices "
  "are more than 6 hours stale. The Gamma fields clobTokenIds and "
  "outcomes are JSON-encoded strings and must be parsed before use.")
p("Box scores and DNP handling. ", bold=True)
p("Player box scores cover 32,166 player-games, including 5,515 DNP rows "
  "kept with mp = \u201cDNP\u201d and blank stats. A top scorer with no "
  "box-score row at all (out injured or resting, not even listed) has "
  "missing trailing form; that is the main reason the form sample is 581 "
  "games rather than 1,230. The DNP flag fires only when the player has a "
  "row marked DNP.")
p("Validation. ", bold=True)
p("Team points from the box scores match the scores file in all 1,230 "
  "games; player points sum to team totals in all 2,460 team-games. Five "
  "randomly chosen scores and five randomly chosen odds lines were "
  "re-checked live against the sources. Polymarket and sportsbook implied "
  "probabilities correlate at 0.997 with a mean absolute difference of "
  "0.012, which cross-validates the two price series against each other.")
p("Known quirk. ", bold=True)
p("February 11, 2026, New York at Philadelphia: TeamRankings lists a "
  "moneyline (Philadelphia \u2212140) and a spread (New York \u22122.5) "
  "that disagree about the favorite. New York won 138\u201389. The game "
  "is kept as listed; it does not affect any headline result.")
h1("Appendix B  Full regression output")
p("Table 5 in the main text reports coefficients with t-statistics. The "
  "regression CSV and the full results text are in the repository at "
  "results/tables/table5_regressions.csv and results/analysis_results.txt.")
h1("Appendix C  Repository map")
p("Notebooks 01\u201304 build the data end to end and reproduce every "
  "number in this report: 01 odds and scores, 02 box scores, 03 "
  "Polymarket prices, 04 the merge and all analysis. nba_analysis_complete.py "
  "regenerates every figure and table from the merged file and asserts "
  "the headline numbers against results/analysis_results.txt before "
  "writing anything. Raw files live in data/raw/, the merged panel in "
  "outputs/, figures in figures/, and tables in results/tables/.")

doc.save(os.path.join(OUT, "QSS20_Final_Report_scaffold.docx"))
print("saved", os.path.join(OUT, "QSS20_Final_Report_scaffold.docx"))
