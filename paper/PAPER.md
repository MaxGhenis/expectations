> Historical development document. Superseded for current findings and methods by the September 2026 growth-beliefs revision: see `RESEARCH_REVISION.md`, `paper/index.qmd`, and regenerated `outputs/`. Numbers below may use the former midpoint/sample-variance convention and approximate annual outcomes.

# What do forecasters say they don't know?

Elicited macroeconomic uncertainty across two surveys, six decades, and the
horizons where it stops.

Working title. Alternatives for Max:

1. What do forecasters say they don't know? (question form, the seed)
2. What forecasters say they don't know (statement form)
3. Stated uncertainty: the macroeconomic distributions forecasters report,
   1968–2026
4. The uncertainty forecasters report
5. Elicited uncertainty and the horizons where elicitation stops

Authors: Max Ghenis [+ TBD]. Target venue open — Review of Income and Wealth
fits the measurement framing (IARIW's journal); alternatives: International
Journal of Forecasting (the natural home for SPF density work), Journal of
Economic Perspectives (if the panorama framing dominates the methods).

---

## Abstract (draft)

Professional forecasters state their own uncertainty four times a year.
Since 1968 the US Survey of Professional Forecasters has collected
probability distributions — not just point forecasts — for output growth
and inflation, and the ECB's survey has done the same for the euro area
since 1999. We pool every reported histogram by the law of total variance,
decomposing total uncertainty into the average forecaster's stated
uncertainty and the disagreement between forecasters, for every variable,
horizon, and survey round — 3,695 round-target distributions. Five findings
organize the panorama. Stated growth uncertainty is stable: its pandemic
spike decayed by 2026 on both continents, while euro-area inflation
uncertainty remains a third above its pre-2021 level. Disagreement — the
only uncertainty visible in point-forecast data — is the minority share
everywhere: a sixth of total variance for growth, at most a third for any
variable. Stated uncertainty stops rising with horizon by year two, and the
ten-year US point forecasts invert the term structure outright: forecasters
put a tighter interquartile range on the next decade's growth (0.2pp) than
on next year's (0.4pp). The US distributions are roughly calibrated on
average (69.7% one-sigma coverage over 33 years); the euro area's are
overconfident (49–57%); both fail in clusters at regime shifts, in the
tail the regime moved toward — and scored properly, the densities beat
climatology everywhere but beat a consensus-plus-historical-error Gaussian
only for growth and the euro area. And the
euro area's unique long-horizon density — four to five years out — sits at
its series high after 2021, exactly where the US elicits nothing. Density
elicitation stops there. Published estimates of AI's growth effects span
roughly 0.1 to 30 percentage points a year (Shenk 2026; Cunningham 2025)
at the horizons no survey asks about, and we show what asking would take.
A live interactive tracks every series.

---

## 1. Introduction

Job: the elicitation-gap hook, then the contribution list. Open with the
2026 fact pair (computed): forecasters put a 0.40-point interquartile range
on next year's US growth and a 0.20-point IQR on the next decade's — the
ten-year answer is tighter than the one-year answer, and no one asked the
ten-year question as a distribution. Then the AI contrast: the published
range of decade-scale growth effects runs from under 0.1pp a year (Acemoglu
2024; CBO per Cunningham 2025) through ~1.5pp (Briggs and Kodnani 2023) and
0.07–1.24pp within one framework (Aghion and Bunel 2024) to above 30pp
(Davidson 2021; Erdil and Besiroglu 2023) — compiled at 0.1–30pp/yr by
Shenk (2026) and Cunningham (2025), almost entirely as point estimates — a
debate conducted outside the instruments that measure stated uncertainty.
The one large elicitation, Karger et al. (2026, FRI + Chicago Fed), is a
one-off collecting medians and two quantiles, and it confirms the pattern:
the disagreement is about economic impact, not capability arrival.

Contributions (draft list, confirm against LITREVIEW verdict):
1. The panorama: every density variable, horizon, and round of both
   surveys, one construction, 1968–2026.
2. The 2020s update: the inflation surge, the bin-scheme changes, and what
   they did to measured uncertainty.
3. Cross-Atlantic comparison on identical measures, including the ECB's
   longer-term (4–5 year) densities, which have no US counterpart.
4. Calibration of the pooled distributions against realizations, and where
   the misses cluster.
5. The elicitation gap: a documented inventory of where density elicitation
   stops, against where the growth debate now lives.
6. A live interactive publishing every series.

Positioning (from LITREVIEW.md, all citations verified): the decomposition
is Wallis (2005) and Boero, Smith and Wallis (2008), first posed on these
histograms by Zarnowitz and Lambros (1987); the histogram machinery follows
Engelberg, Manski and Williams (2009); the fixed-event conversion is Ganics,
Rossi and Sekhposyan (2024); the calibration template runs from Diebold,
Tay and Wallis (1999) through Clements (2014). Nearest antecedents:
D'Amico and Orphanides (2008) — the US long series, inflation only, ending
2008; Clements, Rich and Tracy (2022) — both surveys, in prose, no new
series; Allayioti et al. (2024) — the ECB's own 25-year retrospective, one
survey. The paper is the assembled object none of them built: every density
variable, both surveys, decomposed and calibration-checked through 2026,
with a live interactive — and the elicitation-gap argument, which the
corpus shows unmade.

## 2. The elicitation landscape

Job: the inventory table — who asks forecasters for distributions, about
what, how far out. Draftable now from FACTS.md (survey structure blocks):

| Survey | Density variables | Density horizons | Since |
|---|---|---|---|
| US SPF (Philadelphia Fed) | output growth | current + next year (to 2009Q1); current…+3 (2009Q2–) | 1968Q4 (nominal GNP era; real GNP 1981Q3; real GDP 1992Q1) |
| US SPF | GDP price inflation | current + next year (Table 6: two blocks throughout) | 1968Q4 (deflator concept changes in step) |
| US SPF | core CPI, core PCE (Q4/Q4) | current + next year | 2007Q1 |
| US SPF | unemployment rate | current…+3 | 2009Q2 |
| US SPF | recession probability (decline in real GDP) | current + 4 quarters | 1968Q4 |
| US SPF | 10-year growth, CPI, PCE | POINT only — no density (RGDP10 Q1-only since 1992Q1; CPI10 quarterly since 1991Q4; PCE10 since 2007Q1) | 1991–2007 |
| ECB SPF | HICP, real GDP growth, unemployment | current/next calendar year (+ year after next); rolling 1y + 2y; longer-term (4y in Q1/Q2 rounds, 5y in Q3/Q4; Q1-only in early years) | 1999Q1 |
| ECB SPF | core HICP (ex energy and food) | same structure | 2017Q1 |

Prose to carry: the asymmetry. The US survey is longer; the euro-area survey
asks further out. Nobody asks beyond five years, and the US stops at three.
The rest of the landscape (verified in LITREVIEW.md §5): the NY Fed's SCE
elicits household densities to three years (a five-year inflation question
since 2022); Consensus Economics elicits by-range probabilities at one year
and publishes its 5–10 year forecasts as points; Livingston (since 1946),
Blue Chip, and the FOMC's SEP are point products — the SEP's fans come from
historical errors, not elicited beliefs. The two partial precedents at long
horizons are one-offs: Christensen, Gillingham and Nordhaus (2018, expert
quantiles on growth to 2100) and Karger et al. (2026). The claim the
inventory supports: no survey anywhere regularly elicits probability
distributions over ten-year-ahead growth. Bin history for the US densities
(SPF documentation): 15 bins at the 1968Q4 origin, 6 from 1981Q3, 10 from
1992Q1, 11 from 2009Q2, with changes in 2020Q2 and 2024Q2.

## 3. Measures

Job: the construction, stated once, used everywhere. Draft (evidence in
hand):

Each forecaster attaches probabilities to bins. We place each bin's mass at
its midpoint, give open tails the width of the adjacent bin, keep responses
whose probabilities sum to within two points of 100, and renormalize. For
forecaster i, the histogram yields a mean m_i and a variance v_i. The law
of total variance splits the pooled mixture:

    total variance = E[v_i] + Var(m_i)

The first term is the average uncertainty forecasters state individually;
the second is disagreement, the only term visible in point-forecast data.
We report the square roots, the between share, and quantiles of the pooled
mixture. The interquartile range of the mixture doubles as a robustness
measure: bin-scheme changes move midpoint-based SDs mechanically, and the
2020Q2 US bin widening is the worked example [PENDING-SOL: magnitude].

Fixed-event structure: targets are calendar years, so a "next year"
forecast made in Q1 and one made in Q4 differ in horizon by three quarters.
We treat (round, target) pairs explicitly and show within-year shrinkage
rather than averaging over it (computed: current-year uncertainty falls
24–41% from Q1 to Q4, by variable).

Scoring: coverage rates test the density at two thresholds; proper scores
evaluate all of it. The pooled CDF is piecewise linear, so the CRPS has an
exact closed form, and pinball losses at the published quantile levels
decompose it by tail. We score every calibrated round against two
no-lookahead benchmarks — expanding-window climatology and a Gaussian
centered on the consensus with historical-error SD — and report skill, plus
the pooled mixture against the average individual forecaster (does the
disagreement variance earn its keep?). PITs complete the standard
diagnostics. Scoring rules on these densities go back to Boero, Smith and
Wallis (2011, IJF); the scoring-rule theory is Gneiting and Raftery (2007,
JASA 102(477), 359–378 — verified from the paper). One structural note the
text must carry: the pooled CDF is the mean of individual CDFs and CRPS is
convex in the CDF, so the pool beats the average individual on every
observation by construction — the empirical content is the size of that
gain (3.5–18.7% by cell) and where it thins (the long ECB horizons, where
disagreement is smallest).

## 4. Five stylized facts

Each fact gets a figure from the pipeline and a paragraph. All numbers
below are computed (FACTS.md, full-pipeline block).

1. **Stated uncertainty is stable in growth — and its pandemic spike
   decayed on both continents, while euro-area inflation uncertainty has
   not come home.** US next-year growth: 1.25pp average total SD 2010–19,
   1.74 in 2020–24, 1.36 by 2026. ECB growth: 0.73 → 1.58 (peak 2.62 in
   2020) → 0.79 in 2026. ECB HICP one-year uncertainty went 0.68 → 0.97
   and still stands at 0.91 in 2026, a third above its pre-2021 level. One
   counterpoint the panorama surfaces: US GDP-price uncertainty declined
   through the pandemic era.
2. **Disagreement is the minority share of stated uncertainty —
   everywhere, but not uniformly.** The median between share is a sixth
   for growth (US 17%, EA 16%) and EA prices (14%), and a quarter to a
   third for unemployment and the US inflation densities (26–33%). No
   variable's median reaches a third: the spread visible in point
   forecasts understates stated uncertainty two-to-threefold across the
   whole panorama.
3. **Stated uncertainty rises with horizon only until year two — then
   plateaus, and for growth it even inverts.** US growth within-SD climbs
   1.14 → 1.29 → 1.37 from the current year to two years out, then gains
   one point in the hundredths place at three (1.38). In the euro area,
   total growth uncertainty is mildly higher at the one-year rolling
   horizon (0.86) than at the four-to-five-year horizon (0.81). Only
   unemployment keeps steepening. And the term structure of the US
   10-year point forecasts inverts outright: IQR 0.20 for the decade vs
   0.40 for next year in 2026. Forecasters do not state growing
   uncertainty at the horizons where growth uncertainty should compound.
   (Within-year, the fixed-event effect is strong and mechanical:
   current-year uncertainty falls 24–41% from Q1 to Q4.)
4. **The US distributions are roughly calibrated on average; the euro
   area's are overconfident; both fail in clusters.** ±1σ coverage across
   all horizons: US 64–83% by variable (growth 75%, the Q1 next-year
   series exactly 69.7% over 33 years); ECB 49–57%. Misses are not
   spread — they cluster in regime shifts: every forecast of the 1996–99
   outcomes missed; every US core-inflation forecast of 2021 and 2022
   missed both the ±1σ and the 90% band; all 16 ECB calendar-year HICP
   forecasts of 2022 missed both bands. Scored properly, the densities
   beat climatology everywhere (variable-level CRPS skill +15% to +57%) —
   but beat the harder benchmark, a Gaussian around the consensus with
   historical-error RMSE, only for US growth (+6%) and the euro area: for
   US inflation and unemployment, the elicited shape adds nothing beyond
   the point forecast wrapped in its own track record. And the pinball
   decomposition shows the clusters live in tails: 2008–09 growth losses
   sit in the lower tail (ECB 05-loss 2.29 vs 95-loss 0.22), 2020–22
   inflation losses in the upper tail by factors of five to nine.
5. **The euro area asks the question the US doesn't — and after 2021 the
   long answer moved less than the short one, but it moved.** The ECB
   longer-term (4–5 year) density: total SD 0.70 before 2021, 0.91 after
   (+31%), against +59% at one year; longer-term consensus inflation
   1.82% → 2.00% against 1.58% → 2.29% at one year. Stated long-run
   uncertainty is now at its series high exactly where the US elicits
   nothing.

Cross-era caveat carried by the figures: the 2020Q2–2024Q1 US wide-bin
era inflates SD-based measures mechanically (+59% within-SD vs +40%
pooled IQR; at the clean 2024Q2 scheme change, SD fell 22% while IQR fell
4%). Cross-era statements use the pooled IQR.

## 5. The elicitation gap

Job: put the AI growth debate against the inventory. Beats, citations
verified (LITREVIEW.md §5): the 0.1–30pp/yr published range and its
anchors (Acemoglu low, Goldman mid, Aghion–Bunel spread-within-framework,
Davidson/Erdil–Besiroglu high, Epoch's GATE model whose own authors
disclaim quantitative reliability); Karger et al. (2026) as the flagship
elicitation — medians and two quantiles, once; Chow, Halperin and Mazlish
(2026) extracting long-horizon growth beliefs from asset prices precisely
because no survey elicits them; Cunningham (2025) independently noting the
missing distributions. The observation the paper owns: the instruments that
would discipline this debate exist, run quarterly, have 50 years of
calibration record — and stop at year three (US) or five (EA). Tone check:
state the gap; do not scold the surveys.

## 6. What better elicitation would look like

Job: constructive close. Candidate beats (design, not advocacy): extend one
existing survey block to a 10-year density on growth — the ECB's
longer-term question shows a panel will answer it, and its 2023 special
survey already asked whether ten-year expectations would differ (Allayioti
et al. 2024); bins wide enough to be honest about tails (the 2020 US
widening as precedent — and fact 3 says the current instruments would
likely elicit a plateau, which is itself the test); score and publish
the record the way section 4 does — CRPS with pinball components, so a
long-horizon density question ships with the scoring rule that disciplines
it, and the record shows where stated densities break (regime shifts)
exactly because the AI question is a regime-shift question; pair each long-horizon density with the respondent's AI-adoption
assumption so the 0.1–30pp range becomes decomposable into capability and
diffusion beliefs.

## 7. Conclusion

One page. The 2026 pair again — 0.40 next year, 0.20 for the decade — now
with the whole panorama behind it.

---

## Figures (planned, all from `outputs/`)

1. Total pooled uncertainty over time, all variables, both surveys (fact 1)
2. Decomposition: within vs between shares (fact 2)
3. Term structure: stated uncertainty by horizon, US and EA (fact 3)
4. Calibration: consensus ± total band vs realizations, misses flagged
   (fact 4)
5. ECB longer-term series 1999–2026 (fact 5)
6. The elicitation gap: horizons with densities vs the AI-estimate range
   (the one original diagram; design in the interactive first)
