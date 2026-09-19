# Literature review: elicited macroeconomic forecast uncertainty

> Historical literature compilation, superseded in scope and AI-comparator interpretation by [the research revision](history/RESEARCH_REVISION.md) and [primary-source audit](../paper/AI_COMPARATORS.md). In particular, the heterogeneous 0.1–30 pp range below is not a commensurable distribution of annual GDP forecasts. Use the revised manuscript for current numerical claims.

Prepared for the working paper on the panorama of elicited macroeconomic forecast uncertainty (US SPF 1968/1992–2026 and ECB SPF 1999–2026): the law-of-total-variance decomposition of pooled survey densities into within-forecaster uncertainty and disagreement, applied to every density variable and horizon of both surveys, checked against realized errors, delivered with a live cross-survey interactive, and framed by the elicitation gap between where stated densities stop (3–5 years out) and where the AI growth debate (published scenarios that differ in outcome, horizon and conditioning, so no single range spans them) needs distributions.

Every entry below survived an adversarial verification pass (verdicts CONFIRMED or CORRECTED against fetched pages). Items that could not be verified are quarantined in the appendix — do not cite them without independent verification. Entries appearing in more than one dimension get a full annotation at first appearance and a cross-reference with a dimension-specific note afterward.

Contents:

1. Uncertainty vs disagreement in the US SPF (22 entries)
2. Calibration of survey densities against realized outcomes (21 entries)
3. The ECB SPF (22 entries)
4. Interactives, dashboards, and the live-tracker landscape (19 entries)
5. AI growth forecasts and the elicitation gap (19 entries)
6. Novelty verdict
7. Positioning
8. Appendix: could not verify

---

## 1. Uncertainty vs disagreement in the US SPF

The decomposition literature: within-forecaster uncertainty, between-forecaster disagreement, and the pooled mixture that adds them.

**Zarnowitz, Victor and Louis A. Lambros (1987). "Consensus and Uncertainty in Economic Prediction." Journal of Political Economy 95(3), 591–621.**
https://www.nber.org/papers/w1171
The original paper distinguishing consensus (agreement among point predictions) from uncertainty (the diffuseness of each forecaster's predictive distribution), using the NBER-ASA quarterly outlook surveys 1969–1981, which collected probability distributions for GNP growth and the deflator alongside point forecasts. Comparing matched point and probability forecasts from the same respondents, it finds mean point predictions align closely with the means of the probability distributions, but the standard deviation of point forecasts (disagreement) is generally smaller than the mean standard deviation of the predictive distributions (average individual uncertainty) — so disagreement understates uncertainty, particularly at shorter horizons.
Covers: the paper's core distinction and its baseline stylized fact, established on the very histograms the panorama tracks back to 1968.

**Diebold, Francis X., Anthony S. Tay and Kenneth F. Wallis (1999). "Evaluating Density Forecasts of Inflation: The Survey of Professional Forecasters." In Cointegration, Causality and Forecasting: A Festschrift in Honour of Clive W. J. Granger, Oxford University Press, 76–90 (NBER WP 6228, 1997).**
https://www.nber.org/papers/w6228
First systematic calibration evaluation of the SPF's aggregate inflation density forecasts, collected since 1968, applying the probability integral transform framework to the survey densities against realized inflation. Finds the probability of a large negative inflation shock is generally overestimated, and in later years the probability of large shocks of either sign is overpredicted; inflation surprises are serially correlated; lower expected inflation is associated with lower uncertainty.
Covers: the direct ancestor of the calibration exercise — ex-ante densities vs ex-post outcomes on the same US series.

**Giordani, Paolo and Paul Söderlind (2003). "Inflation forecast uncertainty." European Economic Review 47(6), 1037–1059.**
https://ideas.repec.org/a/eee/eecrev/v47y2003i6p1037-1059.html
Studies inflation uncertainty as reported by individual US SPF forecasters 1969–2001, analyzing the three survey-based measures the panorama pools (average individual variance, disagreement, aggregate/mixture variance) and proposing improved histogram-fitting methods. Finds disagreement is a better uncertainty proxy than earlier literature suggested, that forecasters underestimate inflation uncertainty (densities too narrow ex post), and similar results for output growth.
Covers: canonical treatment of exactly the three quantities in the decomposition, plus the overconfidence benchmark for the calibration panel.

**Wallis, Kenneth F. (2005). "Combining Density and Interval Forecasts: A Modest Proposal." Oxford Bulletin of Economics and Statistics 67(s1), 983–994.**
https://econpapers.repec.org/article/blaobuest/v_3a67_3ay_3a2005_3ai_3as1_3ap_3a983-994.htm
Proposes the finite mixture distribution as the statistical model for a combined density forecast built from individual survey densities, spelling out that the mixture variance decomposes into average individual variance plus the variance of individual means, with implications for uncertainty and disagreement measures; applied to the US SPF.
Covers: the methodological core of the paper — the total mixture SD is precisely Wallis's combined-density object, and the law-of-total-variance split is his identity.

**Lahiri, Kajal and Fushang Liu (2006). "Modelling multi-period inflation uncertainty using a panel of density forecasts." Journal of Applied Econometrics 21(8), 1199–1219.**
https://ideas.repec.org/a/wly/japmet/v21y2006i8p1199-1219.html
Estimates a dynamic heterogeneous panel model with ARCH-style specifications on the SPF density panel to study the determinants of individual inflation forecast uncertainty. Finds persistence in uncertainty much lower than aggregate series suggest, a weakened link between past errors and current uncertainty in multi-period settings, and that the inflation level predicts uncertainty while disagreement and macro volatility do not.
Covers: panel modeling of the within-forecaster component, and a warning about overstating persistence when reading aggregate uncertainty series.

**Boero, Gianna, Jeremy Smith and Kenneth F. Wallis (2008). "Uncertainty and Disagreement in Economic Prediction: The Bank of England Survey of External Forecasters." Economic Journal 118(530), 1107–1127.**
https://ideas.repec.org/a/ecj/econjl/v118y2008i530p1107-1127.html
Introduces the Bank of England Survey of External Forecasters (UK inflation and GDP point and density forecasts) and presents the clean statistical framework interrelating uncertainty and disagreement — the mixture-variance decomposition — with cross-survey comparisons. Finds a significant, sustained reduction in inflation uncertainty after the Bank's 1997 independence.
Covers: the framework the paper applies wholesale (aggregate variance = average individual variance + disagreement) and a precedent for cross-survey comparison.

**D'Amico, Stefania and Athanasios Orphanides (2008). "Uncertainty and Disagreement in Economic Forecasting." Federal Reserve Board Finance and Economics Discussion Series 2008-56.**
https://www.federalreserve.gov/econres/feds/uncertainty-and-disagreement-in-economic-forecasting.htm
Uses SPF probabilistic responses to build one of the longest histogram-based series constructed: quarterly estimates since 1968 of average individual inflation uncertainty, disagreement about the mean, and disagreement about uncertainty itself, comparing parametric characterizations of the individual distributions and relating the measures to term premia. Finds higher expected inflation associated with both higher uncertainty and greater disagreement, and that disagreement is an imperfect proxy for uncertainty.
Covers: the closest existing exercise to the paper's US long time series — which the panorama extends to all variables, horizons and rounds, adds the ECB SPF, and updates through 2026.

**Engelberg, Joseph, Charles F. Manski and Jared Williams (2009). "Comparing the Point Predictions and Subjective Probability Distributions of Professional Forecasters." Journal of Business & Economic Statistics 27(1), 30–41.**
https://www.nber.org/papers/w11978
Compares SPF point forecasts of GDP growth and inflation with the same respondents' reported histograms. Finds forecasters summarize their distributions inconsistently, point forecasts are favorable relative to the central tendency of the histograms, and the optimism is persistent; concludes point forecasts reveal nothing about felt uncertainty and surveys should elicit probabilistic expectations.
Covers: the elicitation-side justification for the paper's premise — only density elicitation reveals stated uncertainty — which underwrites the elicitation-gap framing.

**Rich, Robert W. and Joseph S. Tracy (2010). "The Relationships among Expected Inflation, Disagreement, and Uncertainty: Evidence from Matched Point and Density Forecasts." Review of Economics and Statistics 92(1), 200–207.**
https://ideas.repec.org/a/tpr/restat/v92y2010i1p200-207.html
Tests the relationships among expected inflation, disagreement, and uncertainty in matched US SPF point and density forecasts, deriving uncertainty via the Wallis mixture decomposition and entropy in an SUR framework. Finds little evidence disagreement is a useful uncertainty proxy, mixed evidence that higher expected inflation raises uncertainty, and a significant positive disagreement–expected-inflation association.
Covers: central US measurement of both decomposition components; its negative verdict on disagreement-as-proxy motivates tracking elicited uncertainty directly.

**Lahiri, Kajal and Xuguang Simon Sheng (2010). "Measuring forecast uncertainty by disagreement: The missing link." Journal of Applied Econometrics 25(4), 514–538.**
https://ideas.repec.org/a/jae/japmet/v25y2010i4p514-538.html
The theoretical decomposition linking disagreement and uncertainty: splitting forecast errors into common and idiosyncratic shocks, aggregate uncertainty equals disagreement plus the perceived variability of future common shocks, so disagreement's reliability as a proxy depends on regime stability and horizon. SPF density data support the framework; GARCH-type estimates of common-shock variability are recommended over squared consensus errors.
Covers: the theory behind the law-of-total-variance decomposition and the sharpest statement of when disagreement tracks total uncertainty — the missing common-shock term is what the paper's 50-year series makes visible.

**Clements, Michael P. (2014). "Forecast Uncertainty—Ex Ante and Ex Post: U.S. Inflation and Output Growth." Journal of Business & Economic Statistics 32(2), 206–216.**
https://ideas.repec.org/a/taf/jnlbes/v32y2014i2p206-216.html
Compares SPF forecasters' histogram-implied ex-ante uncertainty with their ex-post error performance for US inflation and output growth. Finds overconfidence at horizons of a year or more but overestimated uncertainty at short horizons (ex-ante uncertainty stays high as the horizon shortens), and little link between individuals' ex-post accuracy and ex-ante assessments.
Covers: the template for the calibration dimension — elicited SD vs realized errors by horizon; its over/underconfidence profile is a stylized fact the 2020s update tests.

**Boero, Gianna, Jeremy Smith and Kenneth F. Wallis (2015). "The Measurement and Characteristics of Professional Forecasters' Uncertainty." Journal of Applied Econometrics 30(7), 1029–1046.**
https://ideas.repec.org/a/wly/japmet/v30y2015i7p1029-1046.html
Follow-up to their 2008 paper addressing the statistical issues in constructing and interpreting survey uncertainty measures, applied to the Bank of England Survey of External Forecasters. Documents substantial heterogeneity in individual uncertainty with significant persistence in relative uncertainty, alongside established persistence in relative optimism; whether disagreement proxies uncertainty depends on the macro environment.
Covers: methodological guidance for the histogram-to-moments choices (fitting, bin handling) the panorama makes at scale.

**Abel, Joshua, Robert Rich, Joseph Song and Joseph Tracy (2016). "The Measurement and Behavior of Uncertainty: Evidence from the ECB Survey of Professional Forecasters." Journal of Applied Econometrics 31(3), 533–550.**
https://ideas.repec.org/a/wly/japmet/v31y2016i3p533-550.html
Constructs uncertainty measures from individual ECB SPF histograms for output growth, inflation and unemployment across horizons. Uncertainty is countercyclical and rose across all horizons after 2007; dispersion and accuracy are not reliable proxies for uncertainty; results are robust to panel composition changes.
Covers: the benchmark ECB-SPF measurement paper for the euro-area leg of the decomposition.

**Shoja, Mehdi and Ehsan S. Soofi (2017). "Uncertainty, information, and disagreement of economic forecasters." Econometric Reviews 36(6–9), 796–817.**
https://ideas.repec.org/a/taf/emetrv/v36y2017i6-9p796-817.html
Develops the information-theoretic analog of the mixture decomposition: Jensen–Shannon divergence of the mixture plays disagreement's role and entropy plays individual uncertainty's, applied to US SPF inflation. Notably, it uses a normalized entropy index that corrects distortions caused by changes in the SPF's bin design over time, with Bayesian hierarchical models relating uncertainty, expected inflation, and dispersion.
Covers: the entropy counterpart of the paper's pooling, and an explicit treatment of the bin-change data problem the panorama must handle.

**Clements, Michael P. (2018). "Are macroeconomic density forecasts informative?" International Journal of Forecasting 34(2), 181–198.**
https://ideas.repec.org/a/eee/intfor/v34y2018i2p181-198.html
Tests whether US SPF inflation and output-growth histograms beat unconditional density forecasts that simply project past average uncertainty forward, at aggregate and individual level. The surveys do not systematically outperform unconditional densities at short horizons, implying forecasters do not meaningfully adapt stated uncertainty to current conditions.
Covers: a sobering benchmark for the time-variation analysis — the informational content of the within-forecaster component over time is itself something the panorama can quantify.

**Glas, Alexander (2020). "Five dimensions of the uncertainty–disagreement linkage." International Journal of Forecasting 36(2), 607–627.**
https://econpapers.repec.org/article/eeeintfor/v_3a36_3ay_3a2020_3ai_3a2_3ap_3a607-627.htm
Maps the disagreement–uncertainty relationship in the ECB SPF 1999Q1–2018Q4 along five dimensions: dispersion statistic, point- vs histogram-mean disagreement, variable, horizon, and period. Disagreement is generally a poor proxy, the link weakening around 2008; survey-based uncertainty co-moves with policy uncertainty while disagreement tracks expected financial volatility.
Covers: a systematic map of when the two decomposition components diverge — the grid the cross-survey interactive lets users explore.

**Rich, Robert W. and Joseph S. Tracy (2021). "A Closer Look at the Behavior of Uncertainty and Disagreement: Micro Evidence from the Euro Area." Journal of Money, Credit and Banking 53(1), 233–253.**
https://ideas.repec.org/a/wly/jmoncb/v53y2021i1p233-253.html
Examines individual ECB SPF point and density forecasts, introducing individual disagreement measures alongside individual uncertainty. Both are heterogeneous and persistent, but uncertainty is dominated by respondent fixed effects while disagreement is dominated by time effects; their relationship is economically insignificant and robust to volatility changes, challenging information-friction models.
Covers: the sharpest modern statement of why the two components have different natures — uncertainty as a forecaster trait, disagreement as a state of the world.

**Glas, Alexander and Matthias Hartmann (2022). "Uncertainty measures from partially rounded probabilistic forecast surveys." Quantitative Economics 13(3), 979–1022.**
https://ideas.repec.org/a/wly/quante/v13y2022i3p979-1022.html
Shows the well-known misalignment between low ex-ante variances and larger ex-post squared errors is related to respondents' rounding of reported probabilities, and uses the distinct numerical accuracy of reported probabilities in US SPF and ECB SPF data (inflation, output growth, unemployment) to propose real-time corrections. Corrected uncertainty is higher for all three variables in both areas, and the growing share of non-rounders reinterprets uncertainty trends since the financial crisis.
Covers: a first-order measurement correction affecting both the level and trend of the within-forecaster component the paper tracks, in both surveys.

**Clements, Michael P., Robert W. Rich and Joseph S. Tracy (2022). "Surveys of Professionals." Federal Reserve Bank of Cleveland Working Paper 22-13; chapter in the Handbook of Economic Expectations (Elsevier/Academic Press, 2023), 71–106.**
https://ideas.repec.org/p/fip/fedcwq/94166.html
A comprehensive survey of professional-forecaster surveys focused on the US SPF and ECB SPF, whose distinguishing feature is publicly available matched point and density forecasts: survey structure, data-use issues, construction of disagreement and uncertainty measures, point-vs-density alignment, density coverage and rounding, comparative accuracy, and persistent heterogeneity.
Covers: the state-of-the-art synthesis the paper positions against — it catalogs the same surveys and measures; what it lacks (a computed all-variable, all-horizon pooled series with a 2020s update and a live interactive) is the panorama's claimed contribution.

**Krüger, Fabian and Lora Pavlova (2024). "Quantifying subjective uncertainty in survey expectations." International Journal of Forecasting 40(2), 796–810.**
https://ideas.repec.org/a/eee/intfor/v40y2024i2p796-810.html
Proposes a measure of the uncertainty implicit in histogram-type survey probabilities based on expected ranked probability scores: robust, trivial to implement, assumption-free, and well defined for all probability vectors including spiky single-bin responses that break moment fitting. Demonstrated on NY Fed Survey of Consumer Expectations inflation microdata.
Covers: a 2020s non-parametric alternative for extracting within-forecaster uncertainty — a needed robustness check where SPF respondents put all mass in one or two bins.

**Ganics, Gergely, Barbara Rossi and Tatevik Sekhposyan (2024). "From Fixed-Event to Fixed-Horizon Density Forecasts: Obtaining Measures of Multihorizon Uncertainty from Survey Density Forecasts." Journal of Money, Credit and Banking 56(7), 1675–1704.**
https://ideas.repec.org/a/wly/jmoncb/v56y2024i7p1675-1704.html
Addresses the fixed-event structure of US SPF densities — each quarter panelists forecast calendar-year outcomes, so the effective horizon changes with the round — by proposing a density combination that weights fixed-event densities into correctly calibrated fixed-horizon densities for output growth and inflation, competitive with standard alternatives.
Covers: the standard fix for the mechanical within-year decline in stated uncertainty that the paper's across-rounds design must confront.

**Clements, Michael P., Robert W. Rich and Joseph Tracy (2025). "An Investigation into the Uncertainty Revision Process of Professional Forecasters." Journal of Economic Dynamics and Control 173.**
https://ideas.repec.org/a/eee/dyncon/v173y2025ics0165188925000260.html
Studies how forecasters revise fixed-event variance forecasts as the horizon shortens, applying Patton–Timmermann monotonicity tests to second moments (a first). Finds strong evidence that variance forecasts decline monotonically toward the event, consistent with Bayesian learning.
Covers: the newest word on within-round dynamics of stated uncertainty — evidence the round-by-round decline the panorama plots is rational updating, not noise.

---

## 2. Calibration of survey densities against realized outcomes

The ex-ante vs ex-post literature: does stated uncertainty match realized errors?

**Diebold, Tay and Wallis (1999).** See section 1. https://www.nber.org/papers/w6228
For this dimension: the founding PIT-based calibration study of the exact US SPF density series the paper evaluates; its finding of overstated tail probabilities is the benchmark any 2020s coverage update revisits.

**Giordani and Söderlind (2003).** See section 1. https://ideas.repec.org/a/eee/eecrev/v47y2003i6p1037-1059.html
For this dimension: an early ex-ante-vs-ex-post comparison (densities too narrow) and the pioneer of fitting normal distributions to SPF histograms.

**Engelberg, Manski and Williams (2009).** See section 1. https://www.nber.org/papers/w11978
For this dimension: introduced the now-standard generalized-beta fits for histograms spanning three or more bins (triangular for one or two) — the methodology backbone any moment extraction must adopt or argue against. (Verification note: the NBER page lists pages 146–158 while other indexes list 30–41; the page range is not load-bearing.)

**Stark, Tom (2010). "Realistic evaluation of real-time forecasts in the Survey of Professional Forecasters." Federal Reserve Bank of Philadelphia, Research Rap Special Report (May 2010).**
https://ideas.repec.org/s/fip/fedprr.html
The Philadelphia Fed's in-house accuracy evaluation underlying the SPF error-statistics documentation: measures SPF point-forecast accuracy against alternative realization vintages from the real-time data set and benchmarks against no-change and AR models estimated on real-time data. Finds sharp accuracy decline at longer horizons, significant influence of vintage choice, and that the SPF generally beats naive benchmarks at short horizons.
Covers: the authoritative treatment of the realization-vintage choice the paper's realized-error calibration must make.

**Boero, Gianna, Jeremy Smith and Kenneth F. Wallis (2011). "Scoring rules and survey density forecasts." International Journal of Forecasting 27(2), 379–393.**
https://ideas.repec.org/a/eee/intfor/v27yi2p379-393.html
Practical evaluation of density scoring rules in the survey context, using UK histogram forecasts from the BoE Survey of External Forecasters. Shows the ranked probability score has clear advantages for histogram forecasts and introduces RPS*, a Yates-decomposition adjustment for differential non-response across a panel.
Covers: which scoring rule to use when evaluating bin-format densities against outcomes across an unbalanced panel.

**Patton, Andrew J. and Allan Timmermann (2012). "Forecast Rationality Tests Based on Multi-Horizon Bounds." Journal of Business & Economic Statistics 30(1), 1–17.**
https://ideas.repec.org/a/taf/jnlbes/v30y2011i1p1-17.html
Develops rationality tests from the bounds squared-error rationality imposes across horizons — MSE weakly increasing in horizon, mean squared forecast weakly decreasing — via inequality-constraint regressions, plus revision-based tests needing no realization data, applied to Greenbook forecasts.
Covers: the theoretical discipline for the term-structure panel — how measured uncertainty and errors should behave as horizon shrinks across rounds.

**Kenny, Geoff, Thomas Kostka and Federico Masera (2014). "How informative are the subjective density forecasts of macroeconomists?" Journal of Forecasting 33(3) (ECB Working Paper 1446, 2012).**
https://ideas.repec.org/p/ecb/ecbwps/20121446.html
Evaluates entire predictive densities from euro-area SPF micro data, decomposing density performance into location, spread, skew and tail-risk contributions against simple benchmarks. Finds considerable heterogeneity, performance somewhat better for GDP growth than inflation but diminishing substantially with horizon, frequent realizations of events assigned zero probability (overconfidence), and little contribution from higher moments.
Covers: the core calibration study for the ECB half of the cross-survey design; the zero-probability-events finding is the sharpest evidence that elicited densities understate uncertainty.

**Clements (2014).** See section 1. https://ideas.repec.org/a/taf/jnlbes/v32y2014i2p206-216.html
For this dimension: the direct template — horizon-dependent overconfidence (year-plus) and underconfidence (short horizons) is the main stylized fact the paper's all-variable, all-round calibration panel replicates or overturns.

**Kenny, Geoff, Thomas Kostka and Federico Masera (2015). "Can Macroeconomists Forecast Risk? Event-Based Evidence from the Euro-Area SPF." International Journal of Central Banking 11(4).**
https://www.ijcb.org/journal/v11n4/can-macroeconomists-forecast-risk-event-based-evidence-euro-area-spf
Event-based evaluation of ECB SPF densities: direction-of-change and high/low-outcome predictions located in the density tails. Densities have predictive value for directional change in inflation and GDP growth; usefulness is strongest for GDP-growth extremes at shorter horizons, while inflation tail regions show limited forecasting power.
Covers: whether the tails of elicited distributions carry information — complementary to variance-based calibration.

**Rossi, Barbara and Tatevik Sekhposyan (2015). "Macroeconomic Uncertainty Indices Based on Nowcast and Forecast Error Distributions." American Economic Review (Papers & Proceedings) 105(5), 650–655.**
https://www.aeaweb.org/articles?id=10.1257/aer.p20151124
Proposes uncertainty indices measuring how unexpected a realization is relative to the unconditional forecast error distribution, built from SPF nowcasts and forecasts, and compares them with existing uncertainty measures.
Covers: the main error-based (ex-post) alternative to elicited-density uncertainty — the other side of the paper's said-vs-shown contrast.

**Clements, Michael P. (2015). "Are Professional Macroeconomic Forecasters Able To Do Better Than Forecasting Trends?" Journal of Money, Credit and Banking 47(2–3), 349–382.**
https://onlinelibrary.wiley.com/doi/abs/10.1111/jmcb.12179
Asks whether SPF forecasters beat a naive benchmark in which variables move monotonically to long-run expected values. Consensus forecasts beat the trend benchmark to varying degrees, but the advantage is largely confined to current-quarter forecasts.
Covers: calibrates how little information professional forecasts add at exactly the horizons where stated uncertainty matters most — sharpening the case that beyond short horizons the honest answer is the unconditional distribution.

**Abel, Rich, Song and Tracy (2016).** See section 1. https://ideas.repec.org/a/wly/japmet/v31y2016i3p533-550.html
For this dimension: methodological reference for individual-histogram uncertainty in the ECB SPF and evidence that neither dispersion nor accuracy proxies uncertainty.

**Clements (2018).** See section 1. https://ideas.repec.org/a/eee/intfor/v34y2018i2p181-198.html
For this dimension: the single most direct antecedent of the calibration claim — it operationalizes "could you do better than the historical range?" for SPF densities and answers no at short horizons; the all-variable, 2020s-inclusive update is what the panorama adds.

**Glas and Hartmann (2022).** See section 1. https://ideas.repec.org/a/wly/quante/v13y2022i3p979-1022.html
For this dimension: part of the apparent overconfidence in elicited densities is a rounding artifact; the correction machinery changes both level and trend of measured stated uncertainty.

**Knüppel, Malte and Fabian Krüger (2022). "Forecast uncertainty, disagreement, and the linear pool." Journal of Applied Econometrics 37(1), 23–41.**
https://onlinelibrary.wiley.com/doi/full/10.1002/jae.2834
Analyzes the linear pool — whose variance equals average individual variance plus disagreement, i.e. exactly the paper's mixture — in a mean-variance framework. If individual variance predictions are unbiased, the disagreement component makes the pool's variance prediction upward biased (by twice expected disagreement), and under empirically relevant conditions disagreement has no predictive content for ex-post squared errors; a centered linear pool stripping disagreement outperforms in simulations and SPF-based US inflation applications.
Covers: directly interrogates the paper's headline object — when the disagreement component of the pooled mixture SD helps or hurts as a statement of uncertainty.

**Clements, Rich and Tracy (2022).** See section 1. https://ideas.repec.org/p/fip/fedcwq/94166.html
For this dimension: the catalog of histogram data pitfalls (bins, rounding, coverage) for both surveys that the calibration pipeline must survive.

**Krüger and Pavlova (2024).** See section 1. https://ideas.repec.org/a/eee/intfor/v40y2024i2p796-810.html
For this dimension: the leading non-parametric (ERPS-entropy) alternative to beta-fit variance extraction, well-defined for one-bin responses where variance fits are not.

**Ganics, Rossi and Sekhposyan (2024).** See section 1. https://ideas.repec.org/a/wly/jmoncb/v56y2024i7p1675-1704.html
For this dimension: the standard fix for the fixed-event vs fixed-horizon distortion when plotting the term structure of elicited uncertainty.

**Bassetti, Federico, Roberto Casarin and Marco Del Negro (2024). "A Bayesian Approach for Inference on Probabilistic Surveys." CEPR Discussion Paper 19426 (also FRB of New York Staff Report 1025, 2022, rev. 2024).**
https://ideas.repec.org/p/cpr/ceprdp/19426.html
Nonparametric Bayesian mixture approach treating reported histograms as data, delivering smooth posterior estimates of subjective distributions and moments; applied to US SPF output growth and inflation densities 1982–2022 to test noisy rational expectations. At horizons near two years there is no relationship between subjective uncertainty and forecast accuracy for output growth, weak relationships for inflation at long horizons, and stronger theory-consistent relationships at short horizons.
Covers: the most recent econometric machinery for histogram-to-distribution conversion over roughly the paper's US span, and a modern subjective-uncertainty-vs-accuracy benchmark.

**Knüppel, Malte and Lora Pavlova (2026). "Survey Design and Professional Forecasters: The Case of Uncertainty in the US SPF." ZEW Discussion Paper 26-017.**
https://www.zew.de/en/publications/survey-design-and-professional-forecasters-the-case-of-uncertainty-in-the-us-spf
The bin-change paper: structural breaks in measured US SPF uncertainty arise mechanically from changes in histogram bin widths. Exploiting the 2014 redesign — when bin widths and hence measured inflation uncertainty shifted significantly while true uncertainty was virtually constant — the authors construct break adjustments and propose horizon-specific bin widths aligning measured with underlying uncertainty.
Covers: the closest existing work to the panorama's bin-change problem, including an adjustment methodology to apply or contrast for the 2020Q2 and 2024Q2 changes.

**European Central Bank (2020). "The ECB Survey of Professional Forecasters — Second quarter of 2020." ECB website, SPF quarterly report.**
https://www.ecb.europa.eu/stats/ecb_surveys/survey_of_professional_forecasters/html/ecb.spf2020q2~b83bc3700f.en.html
The official Q2 2020 report, fielded at the COVID outbreak, documenting that the questionnaire was adjusted to allow a significantly wider range of probability distributions — 2-percentage-point bins around the regular bins — and the resulting record widening of reported distributions.
Covers: primary-source documentation of the COVID-era bin widening on the ECB side, whose mechanical effect on measured density spread the paper must adjust for (the parallel US 2020Q2 change is documented in the Philly Fed SPF documentation, section 5 entry).

---

**Gneiting, Tilmann and Adrian E. Raftery (2007). "Strictly Proper Scoring Rules, Prediction, and Estimation." Journal of the American Statistical Association 102(477), 359–378.**
https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf
The canonical theory of proper scoring rules: propriety, the Savage representation, and the standard scores for predictive densities and CDFs, including the continuous ranked probability score (CRPS) and quantile/interval scores. (Added after the workflow pass; verified from the fetched paper itself, DOI 10.1198/016214506000001437.)
Covers: the theoretical foundation for the paper's CRPS/pinball scoring layer.

**Clements, Michael P. (2014). "Probability distributions or point predictions? Survey forecasts of US output growth and inflation." International Journal of Forecasting 30(1), 99–117.**
https://ideas.repec.org/a/eee/intfor/v30y2014i1p99-117.html
Asks whether SPF respondents' reported histograms deliver dependable point predictions under a Bayesian learning framework, and concludes a role remains for directly elicited point predictions alongside the histograms. (Promoted from the unverified appendix after in-session verification via IDEAS; DOI 10.1016/j.ijforecast.2013.07.010.)
Covers: the point-vs-density comparison inside one survey — background for both the calibration section and the elicitation-design discussion.

## 3. The ECB SPF

The euro-area survey: design, measurement, official retrospectives, and the unique longer-horizon densities.

**García, Juan Angel (2003). "An introduction to the ECB's Survey of Professional Forecasters." ECB Occasional Paper Series No. 8.**
https://ideas.repec.org/p/ecb/ecbops/20038.html
The founding methodological reference for the ECB SPF, run quarterly since 1999: point forecasts and probability distributions for HICP inflation, real GDP growth and unemployment at rolling one- and two-year horizons plus longer-term (five-year-ahead) expectations, with documentation of histogram bins and round timing.
Covers: primary documentation of the elicitation design, including the five-year-ahead densities no other survey elicits.

**Bowles, Carlos, Roberta Friz, Véronique Genre, Geoff Kenny, Aidan Meyler and Tuomas Rautanen (2007). "The ECB Survey of Professional Forecasters (SPF) — A review after eight years' experience." ECB Occasional Paper Series No. 59.**
https://ideas.repec.org/p/ecb/ecbops/200759.html
First official review, 1999–2007: the SPF systematically underestimated inflation at one- and two-year horizons in line with other private forecasters, while GDP and unemployment forecasts showed fewer biases; also evaluates individual performance and reports PIT-based evidence that respondents did not fully capture overall macro uncertainty.
Covers: the first official calibration assessment of ECB densities, the early-sample baseline later retrospectives update.

**García, Juan Angel and Andrés Manzanares (2007). "Reporting biases and survey results: evidence from European professional forecasters." ECB Working Paper Series No. 836.**
https://www.ecb.europa.eu/pub/pdf/scpwps/ecbwp836.pdf
Compares ECB SPF point predictions with the mean/median/mode of respondents' own distributions, fitting skew-normal densities. Point predictions are biased toward favourable outcomes (too-high growth, too-low inflation) relative to the forecasters' own densities, and aggregates of point predictions inherit the bias every round; density-based results are more reliable.
Covers: direct support for building the panorama from densities rather than points, and an early parametric-fitting template.

**Conflitti, Cristina (2011). "Measuring Uncertainty and Disagreement in the European Survey of Professional Forecasters." OECD Journal: Journal of Business Cycle Measurement and Analysis 2011/2, 69–103 (issued 2012).**
https://econpapers.repec.org/RePEc:oec:stdkab:5kg0p9zzp26k
Constructs uncertainty and disagreement measures from the ECB SPF at aggregate and individual level for GDP, inflation and unemployment across horizons, using a piecewise-linear histogram approximation avoiding distributional assumptions. Uncertainty and disagreement are higher for GDP and unemployment than inflation, and the measures move independently across variables.
Covers: an early explicit implementation of the aggregate = individual + disagreement decomposition on ECB data.

**Andrade, Philippe, Eric Ghysels and Julien Idier (2012). "Tails of Inflation Forecasts and Tales of Monetary Policy." Banque de France Working Paper No. 407.**
https://econpapers.repec.org/RePEc:bfr:banfra:407
Introduces Inflation-at-Risk, a VaR-style tail-risk measure estimated from survey densities in both the US and European SPF (beta fits following Engelberg–Manski–Williams), plus the realized p-value of ex-post inflation against ex-ante distributions. Tail risk contains information not captured by standard uncertainty or disagreement indicators; risk asymmetry varies over time and affects inflation and policy rates; extreme events (1970s, 2008–09) were not foreseen.
Covers: what density tails add beyond mean and variance in both surveys, plus realized-p-value machinery for the calibration comparison.

**Kenny, Kostka and Masera (2014).** See section 2. Journal version: https://ideas.repec.org/a/wly/jforec/v33y2014i3p163-185.html
For this dimension: the core ECB density-evaluation paper — overconfidence, horizon-degrading performance, and zero-probability events bear directly on the framing about ranges no forecaster entertains.

**Kenny, Kostka and Masera (2015, IJCB).** See section 2. https://www.ijcb.org/journal/v11n4/can-macroeconomists-forecast-risk-event-based-evidence-euro-area-spf
For this dimension: event-based tests of whether ECB SPF tail probabilities have predictive content.

**Kenny, Geoff, Thomas Kostka and Federico Masera (2015). "Density characteristics and density forecast performance: a panel analysis." Empirical Economics 48(3), 1203–1231 (ECB Working Paper 1679, 2014).**
https://ideas.repec.org/a/spr/empeco/v48y2015i3p1203-1231.html
Panel regressions on ECB SPF micro data linking density characteristics (location, spread, skewness, tail risk) to density performance. Headline finding: many experts could systematically improve their density performance by correcting a downward bias in their variances — forecasters state too little uncertainty — while higher moments contribute little.
Covers: direct quantitative evidence that ECB stated uncertainty is biased low relative to good calibration — the central benchmark for the elicited-SD-vs-realized-error comparison.

**Abel, Rich, Song and Tracy (2016).** See section 1. https://ideas.repec.org/a/wly/japmet/v31y2016i3p533-550.html
For this dimension: benchmark construction of individual-histogram uncertainty in the ECB SPF, with the post-2007 step-up the 2020s update extends.

**Glas, Alexander and Matthias Hartmann (2016). "Inflation uncertainty, disagreement and monetary policy: Evidence from the ECB Survey of Professional Forecasters." Journal of Empirical Finance 39(B), 215–228.**
https://ideas.repec.org/a/eee/empfin/v39y2016ipbp215-228.html
Examines determinants of average individual inflation uncertainty and disagreement in the ECB SPF: individual uncertainty is higher during expansionary monetary policy, disagreement rises during contractionary periods, so using disagreement alone as an uncertainty indicator yields incomplete or misleading conclusions.
Covers: euro-area evidence that the two decomposition components respond to different forces, motivating reporting both everywhere.

**López-Pérez, Víctor (2016). "Does uncertainty affect non-response to the European Central Bank's survey of professional forecasters?" Economics: The Open-Access, Open-Assessment E-Journal 10, 1–47.**
https://ideas.repec.org/a/zbw/ifweej/201625.html
Tests whether uncertainty affects ECB SPF participation: higher uncertainty significantly reduces participation, and forecasters reporting higher personal uncertainty are less likely to respond, implying survey-derived uncertainty measures may be biased downward precisely when uncertainty spikes.
Covers: a selection-effect caveat for interpreting the paper's time series of pooled mixture SDs.

**Krüger, Fabian (2017). "Survey-based forecast distributions for Euro Area growth and inflation: ensembles versus histograms." Empirical Economics 53(1), 235–246.**
https://ideas.repec.org/a/spr/empeco/v53y2017i1d10.1007_s00181-017-1228-3.html
Real-time comparison of forecast distributions built from the cross-section of ECB SPF point forecasts (ensembles) versus the elicited histograms. Ensembles perform very similarly to histograms while being simpler to handle.
Covers: how aggregate distributions built from SPF micro data behave, and whether elicited densities add information over the point cross-section.

**de Vincent-Humphreys, Rupert, Ivelina Dimitrova, Elisabeth Falck, Lukas Henkel and Aidan Meyler (2019). "Twenty years of the ECB Survey of Professional Forecasters." ECB Economic Bulletin, Issue 1/2019.**
https://www.ecb.europa.eu/press/economic-bulletin/articles/2019/html/ecb.ebart201901_01~8300a24082.en.html
Official 20-year retrospective. Documents a permanent step increase in perceived uncertainty from 2009 across all variables and horizons — with the widened distributions still underestimating actual volatility — and explicitly notes the aggregate distribution's width reflects both individual uncertainty and disagreement. Five-year-ahead inflation expectations stayed anchored at 1.8–2.0%, densities acquired negative skew post-crisis, and longer-term unemployment expectations showed cyclicality suggesting perceived hysteresis. (Note: the ECB page's main byline names four authors; RePEc additionally credits Meyler, whose contribution is Box 4.)
Covers: the closest official antecedent — two decades of stated uncertainty with the same decomposition of aggregate width, including the five-year densities; the panorama's extension and cross-survey generalization start here.

**Glas (2020).** See section 1. https://econpapers.repec.org/article/eeeintfor/v_3a36_3ay_3a2020_3ai_3a2_3ap_3a607-627.htm
For this dimension: the five-dimensional map of the uncertainty–disagreement linkage estimated on ECB SPF data 1999–2018.

**Rich and Tracy (2021).** See section 1. https://ideas.repec.org/a/wly/jmoncb/v53y2021i1p233-253.html
For this dimension: respondent effects dominate uncertainty and time effects dominate disagreement in the ECB panel — structure the panorama's interpretation should reflect.

**Baumann, Ursel, Elena Bobeica, Matthieu Darracq Pariès, Aidan Meyler, Marianna Riggi, Thomas Westermann and ~44 co-authors (2021). "Inflation expectations and their role in Eurosystem forecasting." ECB Occasional Paper Series No. 264.**
https://ideas.repec.org/p/ecb/ecbops/2021264.html
The strategy-review Occasional Paper on inflation expectations: metrics for assessing anchoring, including the degree of uncertainty, showing that different metrics can give conflicting signals about potential unanchoring; the SPF is a core input.
Covers: the official framework connecting SPF-based uncertainty metrics to the anchoring question — the policy use-case for the longer-horizon density panorama.

**Górnicka, Lucyna and Aidan Meyler (2022). "Does the tail wag the dog? A closer look at recent movements in the distributions of professional forecasters' inflation expectations." ECB Economic Bulletin, Issue 6/2022 (box).**
https://www.ecb.europa.eu/press/economic-bulletin/focus/2022/html/ecb.ebbox202206_03~bba52a0a2a.en.html
Examines the post-2021 shift in longer-term ECB SPF inflation distributions: re-centred around 2% but with a new upper tail (17% of respondents at 2.5%+ by Q3 2022). Tail respondents extrapolate recent inflation and do not lead broader expectation shifts.
Covers: flagship official analysis of the 2021–22 surge episode in the five-year-ahead densities the 2020s update documents.

**Glas and Hartmann (2022).** See section 1. https://ideas.repec.org/a/wly/quante/v13y2022i3p979-1022.html
For this dimension: rounding corrections applicable to the ECB histograms alongside the US ones.

**Clements, Rich and Tracy (2022).** See section 1. https://ideas.repec.org/p/fip/fedcwq/94166.html
For this dimension: the definitive cross-survey methodological reference for exactly the two surveys the paper spans.

**Allayioti, Anastasia, Rodolfo Arioli, Colm Bates, Vasco Botelho, Bruno Fagandini, Luís Fonseca, Peter Healy, Aidan Meyler, Ryan Minasian and Octavia Zahrt (2024). "A look back at 25 years of the ECB SPF." ECB Occasional Paper Series No. 364.**
https://ideas.repec.org/p/ecb/ecbops/2024364.html
The official 25-year retrospective (1999Q1–2024) covering the pandemic, the Ukraine invasion and the inflation surge: SPF performance broadly comparable to Eurosystem staff projections, technical assumptions accounting for the lion's share of inflation error variance, and uncertainty shown to have increased considerably relative to 1999–2008. A 2023 special survey explored respondents' forecasting processes.
Covers: the paper's main official benchmark for the 2020s — the ratchet-up in stated uncertainty is precisely the time-variation the pooled mixture SDs quantify.

**European Central Bank (2024). "The ECB Survey of Professional Forecasters — Fourth quarter of 2024." ECB website, quarterly SPF report (18 October 2024).**
https://www.ecb.europa.eu/stats/ecb_surveys/survey_of_professional_forecasters/html/ecb.spf2024q4~ee6e2cd847.en.html
Exemplar of the ECB's own published quarterly uncertainty statistics: aggregate probability distributions for inflation, GDP growth and unemployment for the current year, next two years and longer term (2029), with aggregate-distribution SDs, separate individual-uncertainty and disagreement metrics, and balance-of-risk indicators; this round notes disagreement had fallen substantially while individual uncertainty remained elevated.
Covers: proof the ECB operationally publishes the exact decomposition the paper generalizes — including at the five-year horizon — making these reports both a data source and the institutional precedent for the live tracker.

**Bates, Colm, Aidan Meyler, Giovanni Trebbi and Zivile Zekaite (2026). "Capturing inflation expectations (de-)anchoring and what survey-based metrics are telling us." ECB Economic Bulletin, Issue 5/2026 (box).**
https://www.ecb.europa.eu/press/economic-bulletin/focus/2026/html/ecb.ebbox202605_06~06d555dcf1.en.html
Assesses anchoring after the Middle East energy shock using higher-moment metrics from survey distributions: disagreement stable and below long-term averages, uncertainty initially up then receding, high-inflation shares modestly up but below 2022–23 levels; short/long co-movement weakened.
Covers: the most recent official use of density-based uncertainty, disagreement and tail metrics as de-anchoring monitors — a 2026 data point for the post-surge narrative.

---

## 4. Interactives, dashboards, and the live-tracker landscape

What is (and is not) published as a live surface for forecast uncertainty. The core verified verdict: no one publishes a live cross-survey, cross-variable, cross-horizon tracker of elicited forecast uncertainty.

**Federal Reserve Bank of Philadelphia (Real-Time Data Research Center). "Survey of Professional Forecasters — main data page." 1968–2026 (files last updated August 14, 2026).**
https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/survey-of-professional-forecasters
Distributes the US SPF as static files: mean/median/individual forecasts; three cross-sectional dispersion measures (D1–D3) for horizons T to T+4 since 1968Q4; and a single Mean Probability Data Excel file of the density variables since 1968Q4, plus 62-page documentation. Quarterly release pages embed static round-over-round aggregate histogram bar charts for real GDP growth and unemployment.
Covers: the primary US data source — and the gap: no interactive dashboard, no aggregate density-SD time series, no within/between decomposition.

**Federal Reserve Bank of Philadelphia. "The Anxious Index." 1968Q4–2026Q3.**
https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/anxious-index
The one SPF probability series the Philly Fed charts on the web: the probability of a decline in real GDP in the quarter after the survey (20.0% in Q3 2026), charted since 1968Q4 with a data download.
Covers: the closest the survey's owner comes to a live visualization of elicited probabilities — one derived event probability, one variable, one horizon.

**Federal Reserve Bank of Philadelphia. "Forecast Error Statistics for the Survey of Professional Forecasters." (checked 26 Aug 2026).**
https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/error-statistics
The designated home for SPF accuracy statistics currently serves an empty content region in both raw HTML and a rendered browser; realized-error material lives in downloadable files and a 2010 summary paper. No error-vs-stated-uncertainty comparison is presented on the web.
Covers: nobody, including the survey's owner, currently publishes a working web presentation of SPF forecast errors, let alone errors set against elicited densities.

**European Central Bank. "ECB Survey of Professional Forecasters — 'Analyse the results' dashboard." 1999–2026.**
https://www.ecb.europa.eu/stats/ecb_surveys/survey_of_professional_forecasters/html/ecb.spf_dashboard_inflation_content.en.html
The ECB's interactive per-variable dashboard (R-Markdown-knitted, embedded via iframes): point-forecast term structures for the last two rounds, aggregate probability distributions for the next three calendar years and the longer term overlaying the last three rounds, a time series of longer-term expectation measures back to 2000, and the cross-respondent point-forecast distribution, plus comparison tables.
Covers: the most advanced official interactive surface for elicited densities anywhere — but latest-three-rounds only, no uncertainty time series, no disagreement series, no decomposition, no calibration, one survey. The strongest existing comparator for the proposed interactive.

**European Central Bank. "The ECB Survey of Professional Forecasters — Third quarter of 2026" (released 24 July 2026).**
https://www.ecb.europa.eu/stats/ecb_surveys/survey_of_professional_forecasters/html/ecb.spf2026q3.en.html
Each round's report carries static charts plus an annex of aggregate probability distribution charts (A1–A7), including longer-term inflation (65% of respondents at exactly 2.0% in Q3 2026) and longer-term GDP densities, with one-standard-deviation bands and Excel downloads.
Covers: round-by-round density snapshots including five-year-ahead densities — a static quarterly publication, not a tracker of stated uncertainty over time.

**European Central Bank. "Survey of Professional Forecasters (SPF) dataset — ECB Data Portal." 1999–2026.**
https://data.ecb.europa.eu/methodology/survey-professional-forecasters-spf
Documents the full SPF dataset (point forecasts and probability distributions, with rolling horizons designed to "support a more robust analysis of uncertainty") as SDMX 2.1/CSV bulk downloads; the portal offers generic series charting only.
Covers: the machine-readable feed a live cross-survey tracker can sit on; itself a data catalog with no uncertainty visualization.

**Federal Reserve Bank of St. Louis. "FRED and ALFRED — no SPF density or uncertainty series" (checked 26 Aug 2026).**
https://fred.stlouisfed.org/searchresults/?st=survey+of+professional+forecasters
Documented absence: neither FRED nor ALFRED carries any Philadelphia Fed SPF series — no points, no dispersion, no probability variables, no anxious index. FRED's uncertainty-adjacent holdings are market- and text-based (VIX, EPU).
Covers: the most-used economic-data dashboard ecosystem offers no way to plot elicited forecast uncertainty at all.

**Board of Governors of the Federal Reserve System. "Summary of Economic Projections (SEP) — uncertainty and risk assessments" (guide, quarterly, ongoing).**
https://www.federalreserve.gov/monetarypolicy/guide-to-the-summary-of-economic-projections.htm
The SEP elicits each FOMC participant's qualitative uncertainty judgment (Higher/Lower relative to the past 20 years) and risk weighting, publishing fan charts whose widths come from historical forecast errors, diffusion indexes of the answers, and historical error ranges — as static HTML/PDF.
Covers: a genuine elicited-uncertainty product from policymakers, but qualitative and historical-error-based, static — an institutional contrast for the framing.

**Federal Reserve Bank of New York. "Survey of Consumer Expectations (SCE) — interactive chart." 2013–2026 (monthly).**
https://www.newyorkfed.org/microeconomics/sce
Monthly rotating-panel survey of ~1,300 US household heads eliciting subjective probability distributions and explicitly collecting individual forecast uncertainty, with an interactive chart covering inflation expectations at one-, three- and now five-year horizons, outcome probabilities, and Excel downloads.
Covers: the closest existing thing to a live tracker of elicited forecast uncertainty — but households, not professionals, US-only, horizons capped at five years; a design precedent and contrast.

**Federal Reserve Bank of New York (Adrian, Boyarchenko, Giannone and co-authors). "Outlook-at-Risk: Real GDP Growth, Unemployment, and Inflation" (monthly interactive).**
https://www.newyorkfed.org/research/policy/outlook-at-risk
Monthly interactive publishing conditional and unconditional distributions of future GDP growth, unemployment and CPI inflation estimated from financial conditions (Vulnerable Growth lineage), with percentile headline objects.
Covers: proof that a Fed publishes live macro density trackers — but the densities are econometric estimates, not elicited from anyone.

**Federal Reserve Bank of Atlanta (CenFIS). "Market Probability Tracker" (daily).**
https://www.atlantafed.org/cenfis/market-probability-tracker
Estimates probability distributions for three-month average SOFR implied by CME options prices, updated daily, with comparisons across the prior six weeks, percentile regions, and FOMC target-range probabilities.
Covers: live, interactive, full-distribution tracking — extracted from option prices, single variable, sub-year horizons.

**CME Group. "CME FedWatch" (live).**
https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html
Live tool tracking probabilities of Fed rate moves implied by 30-Day Fed Funds futures prices, with methodology page and API.
Covers: the best-known live probability tracker in macro — market-implied, single variable, meeting-by-meeting — underlining that no elicited-survey counterpart exists at comparable liveness.

**Bank of England (MPC). "Monetary Policy Report fan charts" (May 2025 MPR; fan charts since 1996).**
https://www.bankofengland.co.uk/monetary-policy-report/2025/may-2025
The original central-bank predictive-density communication: probability distributions for CPI inflation, GDP growth and unemployment whose location, width and skew are set by the MPC's own judgment, with 30% central bands and ~90% total coverage, as static charts in the quarterly report.
Covers: confirms fan charts are committee model-plus-judgment densities, not uncertainty elicited from an external forecaster panel — a categorically different object from SPF histograms.

**Baker, Scott R., Nicholas Bloom and Steven J. Davis. "Economic Policy Uncertainty Index" (policyuncertainty.com); "Measuring Economic Policy Uncertainty," Quarterly Journal of Economics 131(4), 1593–1636 (2016).**
https://www.policyuncertainty.com/methodology.html
Monthly newspaper-text-based uncertainty indices for 50+ countries; the US index combines newspaper counts, tax-code expirations, and professional forecaster disagreement from the Philadelphia Fed. Downloadable data and charts, no interactive dashboard.
Covers: flagship of the non-elicited tracker landscape; its use of SPF disagreement as an input highlights that the within-forecaster density component is exactly what such trackers omit.

**Jurado, Kyle, Sydney C. Ludvigson and Serena Ng. "Macro and Financial Uncertainty Indexes" (site, updated through June 2026); "Measuring Uncertainty," American Economic Review 105(3), 1177–1216 (2015).**
https://www.sydneyludvigson.com/macro-and-financial-uncertainty-indexes
The JLN indexes — econometric estimates of the common time-varying volatility of forecast errors across hundreds of series — updated twice annually with data, vintages and replication code; static charts.
Covers: the canonical statistical (non-elicited) macro uncertainty tracker; semiannual static updates contrast with a live elicited panorama.

**Ahir, Hites, Nicholas Bloom and Davide Furceri. "World Uncertainty Index" (worlduncertaintyindex.com; data January 2008–July 2026 shown).**
https://worlduncertaintyindex.com/
Text-count uncertainty indices built from EIU country reports (WUI, WPUI, sentiment), GDP-weighted global aggregates, chart and Excel export.
Covers: completes the text-based wing — global coverage, regularly updated, measuring word frequencies rather than what forecasters say they do not know.

**Metaculus. "Community distribution forecasts on macro questions (e.g. 'US Inflation In 2022')" (platform 2015–present).**
https://www.metaculus.com/questions/8901/us-inflation-in-2022/
Elicits full probability distributions over numeric outcomes from a forecaster crowd and displays the aggregated community distribution interactively (the fetched inflation question drew 276 forecasters), with log-score resolution feedback.
Covers: a live, interactive elicited-density platform — but an ad-hoc crowd on one-off questions, not a standing professional panel with fixed variables, horizons, and a 50-year archive; the AI-era forecasting-culture contrast.

**MacroMicro. "US — Philly Fed Recession Probability Index (Anxious Index) live chart."**
https://en.macromicro.me/charts/62344/philly-fed-anxious-index
Third-party commercial charting site maintaining a continuously updated interactive chart of the SPF recession probabilities on a freemium platform.
Covers: the only third-party live tracker of any SPF-elicited probability found — one event-probability series, no densities, no uncertainty measures.

**Consensus Economics. "Consensus Forecasts" (subscription survey publications).**
https://www.consensuseconomics.com/
Commercial monthly survey polling 1,000+ economists across 100+ countries, publishing individual and consensus point forecasts with mean/high/low ranges; no probability or density forecasts, no uncertainty measures, subscription-only.
Covers: the largest cross-country forecaster operation elicits no densities at all — its high-low range is a disagreement proxy — reinforcing that the two SPFs are essentially the only long-running density panels.

---

## 5. AI growth forecasts and the elicitation gap

The published AI-growth range, and the inventory establishing that no survey regularly elicits decade-scale growth densities.

**Karger, Ezra, Otto Kuusela, Jason Abaluck, Kevin A. Bryan, Basil Halperin, Todd R. Jones, Connacher Murphy, Philip Trammell, Josh Rosenberg, Philip E. Tetlock, and coauthors (2026). "Forecasting the Economic Effects of AI." NBER Working Paper 35046 (April 2026); also a Forecasting Research Institute report.**
https://www.nber.org/papers/w35046
Large forecasting exercise (fielded October 2025–February 2026; FRI with the Chicago Fed) tracking 69 academic economists, 52 AI industry and policy experts, 38 superforecasters, and 401 members of the public on AI's economic effects, eliciting medians, 10th/90th percentiles for selected questions, and probabilities over three AI-progress scenarios for 2030 and 2050. Medians expect substantial capability advances but only ~2.5% annual GDP growth by 2030; under the rapid scenario experts forecast roughly 4% annualized growth by 2050. Disagreement centered on whether capabilities will have economic impact, not whether they will arrive.
Covers: the flagship long-horizon expert elicitation — and still a one-off that stops at two quantiles plus scenario weights, not the regular density histograms the panorama tracks; it anchors both the AI framing and the gap claim.

**Acemoglu, Daron (2024). "The Simple Macroeconomics of AI." NBER Working Paper 32487; journal version in Economic Policy.**
https://www.nber.org/papers/w32487
Task-based (Hulten-style) model predicting modest AI gains: no more than ~0.66% total TFP over 10 years, revised to under ~0.53% — roughly 0.05–0.07pp per year — with no confidence intervals or probability distributions attached.
Covers: the canonical low anchor of the published range, and an example of a decade-scale forecast published as a bare point estimate.

**Briggs, Joseph and Devesh Kodnani (2023). "The Potentially Large Effects of Artificial Intelligence on Economic Growth." Goldman Sachs Global Economics Analyst (March 2023).**
https://www.ai-cio.com/news/goldman-artificial-intelligence-will-boost-global-gdp-by-7/
Estimates generative AI could raise global GDP by 7% (~$7 trillion) and lift annual labor productivity growth by ~1.5pp over the decade following widespread adoption, based on occupational task exposure. Point/scenario estimates without an elicited distribution. (URL is verified secondary coverage; Goldman's own pages block fetching — the canonical GS Publishing URL is noted in the verification record.)
Covers: the most-cited mid-range anchor (~1.5pp/yr) in the published range.

**Aghion, Philippe and Simon Bunel (2024). "AI and Growth: Where Do We Stand?" Working paper, June 2024, hosted by the Federal Reserve Bank of San Francisco.**
https://www.frbsf.org/wp-content/uploads/AI-and-Growth-Aghion-Bunel.pdf
Two approaches to AI's decade-scale productivity impact: parallels with past technological revolutions give 0.8–1.3pp/yr; re-implementing Acemoglu's formula with their own reading of the evidence gives 0.07–1.24pp with a median of 0.68pp/yr.
Covers: shows published decade-scale point estimates span an order of magnitude even within one framework — the within-methodology version of the range contrasted with elicited densities.

**Davidson, Tom (2021). "Could Advanced AI Drive Explosive Economic Growth?" Open Philanthropy report (June 2021; Open Philanthropy since renamed Coefficient Giving).**
https://www.lesswrong.com/posts/dGWMCFkETTg8EZ2bB/could-advanced-ai-drive-explosive-economic-growth
Defines explosive growth as gross world product growth above 30%/yr and argues sufficiently capable AI substituting for labor could restore the increasing-returns regime; places at least ~10% probability on explosive growth this century. (URL is the verified linkpost; the canonical Open Phil URL now redirects and blocks fetching.)
Covers: the canonical high anchor (>30pp/yr) — and one of the few entries attaching any explicit probability, via one analyst's judgment rather than a survey density.

**Erdil, Ege and Tamay Besiroglu (2023). "Explosive growth from AI automation: A review of the arguments." arXiv:2309.11690 (rev. July 2024); Epoch AI.**
https://arxiv.org/abs/2309.11690
Reviews whether substantial AI automation could accelerate growth by roughly an order of magnitude, evaluating nine counterarguments; concludes explosive growth is plausible conditional on broadly labor-substituting AI, but high confidence is unwarranted. No formal probability distribution.
Covers: the systematic argument-level review behind the top of the range — even careful explosive-growth advocates stop short of calibrated distributions.

**Erdil, Ege, Andrei Potlogea, Tamay Besiroglu, Edu Roldan, Anson Ho, Jaime Sevilla, Matthew Barnett, Matej Vrzla and Robert Sandler (2025). "GATE: An Integrated Assessment Model for AI Automation." arXiv:2503.04941; Epoch AI, with interactive playground.**
https://epoch.ai/blog/announcing-gate
Integrated assessment model combining compute-based AI development, an automation framework, and semi-endogenous growth; under significant automation it projects growth 2–20x the recent ~3%/yr average, with compute investment potentially exceeding 10% of world GDP. The authors explicitly warn against reading outcomes as quantitative predictions.
Covers: the model-generated top end of the range, whose own authors disclaim quantitative reliability — underlining that no elicited density exists at these horizons.

**Korinek, Anton and Donghyun Suh (2024). "Scenarios for the Transition to AGI." NBER Working Paper 32255.**
https://www.nber.org/papers/w32255
Models output and wage trajectories under different paths to AGI as automation expands over a task-complexity distribution; outcomes hinge on the race between automation and capital accumulation, with scenarios (transformative AI in 5 or 20 years) producing starkly different growth and wage paths.
Covers: the leading academic scenario analysis bridging the low and explosive camps — scenarios again carry no elicited probability weights.

**Chow, Trevor, Basil Halperin and J. Zachary Mazlish (2026). "Transformative AI, existential risk, and real interest rates." Working paper, June 2026 version (first posted January 2023).**
https://basilhalperin.com/papers/agi_emh.pdf
Shows either transformative AI or existential risk predicts a large rise in long-term real rates via consumption smoothing; the June 2026 version finds higher long-term growth expectations associated with higher long-term real rates, and concludes current low rates imply markets are not pricing near-term transformative AI.
Covers: the market-price counterpart to survey elicitation at long horizons — extracting implicit growth beliefs from asset prices precisely because no survey elicits them.

**Shenk, Anton (2026). "The Quadrillion-Dollar Disagreement on AI and the Economy." AI Frontiers (May 11, 2026).**
https://ai-frontiers.org/articles/the-quadrillion-dollar-disagreement-on-ai-and-the-economy
Compiles published decade-scale AI growth forecasts spanning 0.1% to 30% added annual growth — a gap worth nearly a quadrillion dollars of cumulative output by 2035 — with all estimates presented as points or ranges with no probabilistic weighting.
Covers: the 0.1–30pp/yr compilation the framing points to, which itself notes the absence of distributions.

**Cunningham, Tom (2025). "Forecasts of AI & Economic Growth." Personal research blog (October 19, 2025, since updated).**
https://tecunningham.github.io/posts/2025-10-19-forecasts-of-AI-growth.html
Compiles 33 quantitative published forecasts of AI's excess growth effect over ~2025–2035, spanning +0.07% to +30%/yr, with economists clustering at 0.1–1.5%/yr and AI insiders at 3–30%/yr. Explicitly observes the forecasts lack probability distributions — most are single estimates without confidence intervals, the FRI/Chicago Fed percentile bands being the main exception.
Covers: the most complete itemized inventory of the range, independently making the paper's key framing observation.

**Federal Reserve Bank of Philadelphia (2026). "Survey of Professional Forecasters: Documentation" (last updated 2026).**
https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/survey-of-professional-forecasters/spf-documentation.pdf
The official US SPF documentation. Lists exactly six probability variables (PRGDP, PRPGDP, PRCCPI, PRCPCE, PRUNEMP, RECESS) and the density history: 1968Q4 origin (15 bins), 1981Q3 switch to real GNP (6 bins), 1992Q1 to GDP (10 bins), 2009Q2 to 11 bins with current + following three years, bin changes in 2020Q2 and 2024Q2. All 10-year variables (RGDP10, INFCPI10YR, PROD10, STOCK10, BILL10, BOND10) are point forecasts with no density counterpart.
Covers: primary-source confirmation of the inventory facts — US densities extend only ~3 years out, and every 10-year SPF variable is a point forecast.

**Allayioti et al. (2024). "A look back at 25 years of the ECB SPF."** See section 3. PDF: https://www.ecb.europa.eu/pub/pdf/scpops/ecb.op364~8a27dcb996.en.pdf
For this dimension: primary-source confirmation that ECB SPF densities reach four calendar years ahead in Q1/Q2 rounds and five in Q3/Q4 rounds — the longest-horizon regularly collected macro density anywhere — bounding the "nothing beyond ~5 years" gap claim; a 2023 special survey even asked whether respondents' expectations would differ at ten-year horizons.

**Federal Reserve Bank of New York. "Survey of Consumer Expectations (SCE)."** See section 4. https://www.newyorkfed.org/microeconomics/sce
For this dimension: the household-side density benchmark — consumer densities reach three years (a five-year inflation question added January 2022, first published July 2022), so even the household frontier stops far short of decade-scale growth densities. (Whether the five-year measure is published with a density-based uncertainty measure was not confirmed by a fetched page — treat that detail as unconfirmed.)

**Christensen, Peter, Kenneth Gillingham and William Nordhaus (2018). "Uncertainty in forecasts of long-run economic growth." Proceedings of the National Academy of Sciences 115(21), 5409–5414.**
https://phys.org/news/2018-05-uncertainty-long-run-economic-growth-greater.html
Estimates uncertainty in per-capita GDP growth to 2100 via an expert survey (the Yale Long Run Growth Survey, quantiles for six world regions over 2010–2050 and 2010–2100, ~16 experts) and low-frequency econometrics: median global growth ~2.03%/yr with an SD of roughly 1.1pp/yr — far more uncertainty than climate-impact studies assume. (URL is verified press coverage; the canonical PNAS URL blocks fetching and is noted in the verification record. The survey-design details are search-corroborated, not page-verified.)
Covers: the main partial precedent for the gap claim — a genuine long-horizon growth-uncertainty elicitation, but a one-off quantile survey, not a regular density panel; it sharpens rather than refutes the claim.

**Consensus Economics Inc. "Consensus Forecasts — Economic Forecast Probabilities and Long-Term (5–10 Year) Forecasts" (surveys since 1989).**
https://www.consensuseconomics.com/forecast-surveys/economic-forecast-probabilities/
The Economic Forecast Probabilities product elicits probabilities that year-ahead GDP growth and inflation fall in specified ranges; the long-term (5–10 year, April/October) forecasts are point forecasts only — no probability distributions at those horizons.
Covers: closes a key cell of the inventory — the one commercial survey with by-range probability elicitation confines it to the one-year horizon.

**Federal Open Market Committee (2025). "Summary of Economic Projections, September 16–17, 2025."**
https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20250917.htm
Individual point projections for GDP growth, unemployment, inflation and the funds rate through 2028 and the longer run, reported as medians, central tendencies and ranges, with fan charts built from historical errors and qualitative uncertainty diffusion indexes — not elicited subjective densities.
Covers: the Fed's own longer-run projections are policymaker points with historical-error fans — a needed row in the who-elicits-what-at-which-horizon table.

**Federal Reserve Bank of Philadelphia. "Livingston Survey" (since 1946).**
https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/livingston-survey
The oldest continuous survey of economists' expectations (started by Joseph Livingston in 1946; at the Philadelphia Fed since 1990), twice yearly, publishing mean/median and individual point forecasts. No probability distributions are collected.
Covers: the longest-running expectations survey is entirely point-based, including its long-horizon inflation questions — the SPF densities are the exception, not the rule.

**Wolters Kluwer. "Blue Chip Economic Indicators" (monthly since 1976).**
https://en.wikipedia.org/wiki/Blue_Chip_Economic_Indicators
Monthly survey of ~50 US business economists publishing individual point forecasts and consensus averages for ~15 variables; search-level evidence indicates twice-yearly long-range supplements extend consensus point forecasts 5–10 years ahead (the long-range cadence is search-confirmed only, not page-verified). No probability distributions.
Covers: another points-only row at the 5–10 year horizon, supporting the claim that no regular survey elicits decade-scale growth densities.

---

## 6. Novelty verdict

Component by component, against the verified corpus.

### (a) The uncertainty-vs-disagreement decomposition itself

**DONE.** Zarnowitz and Lambros (1987) posed the distinction on these very histograms; Wallis (2005) formalized the finite-mixture identity (total variance = average individual variance + disagreement); Boero, Smith and Wallis (2008) supplied the working framework; Lahiri and Sheng (2010) gave it a common-shock theory; and the ECB publishes the decomposition operationally every quarter (Q4 2024 report, section 3). Knüppel and Krüger (2022) have even litigated when the disagreement component should be excluded from the pooled variance. The paper contributes nothing methodological here and should not pretend to; the decomposition is the vehicle. The seed finding that disagreement is only ~10–20% of total variance is the modern quantification of Zarnowitz–Lambros's original direction (disagreement understates uncertainty) and of Lahiri–Sheng's prediction that the common-shock term dominates in most regimes.

### (b) Long-sample US time series, 2020s update, bin-change handling

**PARTIALLY DONE.** D'Amico and Orphanides (2008) built quarterly average-uncertainty and disagreement series from the histograms back to 1968 — for inflation, ending 2008. Giordani and Söderlind (2003) cover 1969–2001; Bassetti, Casarin and Del Negro (2024) process 1982–2022 with modern machinery. On bin changes, Shoja and Soofi (2017) built an entropy index explicitly correcting for bin-design changes, and Knüppel and Pavlova (2026) is a whole paper on the 2014 redesign with break adjustments; the 2020Q2 widenings are documented on both sides (SPF documentation; ECB Q2 2020 report). What remains genuinely undone: a published all-density-variable US series with the full decomposition running through 2026 — no verified item covers the 2021–22 surge, the 2024Q2 bin change, and the current level of stated uncertainty in one consistent series. The remaining work is real but incremental: extension and consolidation, not invention.

### (c) Cross-Atlantic US + euro-area joint treatment

**PARTIALLY DONE.** Glas and Hartmann (2022) pool US SPF and ECB SPF microdata — but for a rounding correction, not a decomposition panorama. Andrade, Ghysels and Idier (2012) used both surveys for tail-risk measures. Clements, Rich and Tracy (2022) survey both surveys' literatures side by side in prose. Nobody computes harmonized within/between decompositions across both surveys' full histories with comparable methods and presents them jointly. The joint computed treatment is open; the idea of comparing the two surveys is not.

### (d) All-variables, all-horizons panorama including the term structure of stated uncertainty

**OPEN — as an assembly.** Every ingredient exists separately: Abel et al. (2016) span variables and horizons for the ECB; Ganics, Rossi and Sekhposyan (2024) solve the fixed-event-to-fixed-horizon conversion; Clements, Rich and Tracy (2025) characterize the within-round variance revision path; the ECB's own reports show per-round term structures. But no verified item computes the complete grid — every density variable, every horizon, every round, both surveys — and no item reports anything like the seed finding that the US 10-year point-forecast IQR (0.2pp) is tighter than the next-year IQR (0.4pp); that term-structure inversion between stated short-horizon densities and long-horizon point dispersion appears nowhere in the corpus. Honesty requires saying this component is new as an assembly of standard pieces, and the assembly (plus the facts it surfaces) is the contribution.

### (e) Calibration against realized errors

**DONE in method, PARTIALLY DONE for this paper's version.** The ex-ante-vs-ex-post exercise is one of the most worked seams in the corpus: Diebold, Tay and Wallis (1999), Giordani and Söderlind (2003), Clements (2014), Kenny, Kostka and Masera (2014, 2015), Clements (2018), Knüppel and Krüger (2022), Glas and Hartmann (2022), Bassetti et al. (2024). The stylized facts are established: overconfidence at year-plus horizons, zero-probability events realized, part of the miss a rounding artifact. What no verified item provides: a uniform coverage-rate panel (like the seed pipeline's 70% one-sigma coverage over 33 years with misses clustered in regime shifts) across all variables and both surveys through the 2020s — i.e., including the one episode (2020–22) that most tests stated densities. The update is worth doing; the method section should cite rather than reinvent.

### (f) A live interactive

**OPEN.** The interactives dimension verified an absence: no live cross-survey, cross-variable, cross-horizon tracker of elicited forecast uncertainty exists anywhere. The ECB's dashboard is the high-water mark and shows only the latest three rounds' densities with no uncertainty time series, no decomposition, no calibration, one survey. The Philly Fed publishes static files, one charted event-probability series, and an error-statistics page that currently renders empty. FRED carries no SPF series at all. Every live full-distribution tracker found (Outlook-at-Risk, Atlanta Market Probability Tracker, CME FedWatch) is estimated or market-implied, not elicited; the SCE interactive is households; Metaculus is an ad-hoc crowd. A live pooled-density panorama across both SPFs would be the first of its kind.

### (g) The elicitation-gap-vs-AI-debate framing

**OPEN.** The two halves exist separately and no one has joined them. Half one: the survey inventory (SPF documentation; ECB OP 364; Consensus, Livingston, Blue Chip, SEP entries) establishes that professional density elicitation stops at roughly 3 years (US) to 5 years (ECB), with all decade-horizon products points only. Half two: the AI-growth compilation (Shenk 2026; Cunningham 2025) establishes a published range of roughly 0.1–30pp/yr, presented almost entirely without distributions — and Cunningham independently remarks on the missing distributions. The two partial precedents — Christensen, Gillingham and Nordhaus (2018) and Karger et al. (2026) — are one-off quantile elicitations, which sharpens the correct claim: no survey anywhere regularly elicits probability distributions over ten-year-ahead growth. Connecting the 50-year density record's horizon boundary to the decade-scale question where distributions are most needed is, on this corpus, an unmade argument.

### Bottom line

The paper is worth writing, with eyes open about what it is. Every methodological ingredient is standard and decades old: the decomposition is Wallis (2005), the histogram machinery is Engelberg, Manski and Williams (2009) with Glas-Hartmann (2022) and Krüger-Pavlova (2024) refinements, the fixed-event fix is Ganics, Rossi and Sekhposyan (2024), the bin adjustments are Knüppel-Pavlova (2026), and the calibration template runs from Diebold, Tay and Wallis (1999) through Clements (2014). What does not exist anywhere is the assembled object: a complete, current, decomposed, calibration-checked account of every elicited density in both long-running professional surveys, through 2026, in one consistent pipeline with a live interactive — and no one has pointed out that the stated-density record stops three to five years out exactly where the AI growth debate, whose published range spans roughly 0.1 to 30 percentage points a year, needs decade-scale distributions. The sharpest novelty claim is the elicitation gap: fifty-plus years of professional density forecasting, systematically panoramized for the first time, ends precisely at the horizon where today's biggest growth question begins. That framing, plus the panorama's completeness and currency, is the paper; the decomposition is the vehicle, not the contribution.

---

## 7. Positioning

Nearest three papers and how this differs:

1. **D'Amico and Orphanides (2008), FEDS 2008-56.** The closest single antecedent for the US long series: quarterly uncertainty and disagreement from the histograms back to 1968. Differs: inflation only, ends 2008, no calibration panel, no euro area, no interactive. The panorama is that exercise done for every density variable in two surveys, 18 years later, with the errors attached.
2. **Clements, Rich and Tracy (2022), "Surveys of Professionals."** Covers the same two surveys, the same measures, and the same pitfalls — as a prose synthesis. Differs: it computes no new series and presents no panorama; the paper is, in effect, the empirical companion the handbook chapter's agenda calls for, extended through the 2020s.
3. **Allayioti et al. (2024), "A look back at 25 years of the ECB SPF," ECB OP 364.** The official single-survey panorama, including an uncertainty section and the 2020s episodes. Differs: euro area only, retrospective format, no US counterpart, no systematic decomposition-by-horizon grid, no live surface. The paper does for both surveys, symmetrically and reproducibly, what the ECB did for its own.

Plausible venues. The measurement framing — what do our instruments for stated macroeconomic uncertainty actually record, over the full history, and where do they stop — fits IARIW's **Review of Income and Wealth** well, and the IARIW connection is live. The **International Journal of Forecasting** is the natural disciplinary home (it published Glas 2020, Clements 2018, Boero et al. 2011, Krüger-Pavlova 2024 from this corpus) and would referee the decomposition and calibration components hardest. **Journal of Applied Econometrics** or **JMCB** fit if the econometric contribution is deepened (e.g., adopting the Ganics et al. fixed-horizon machinery formally). A central-bank working paper series (Philadelphia Fed, ECB) is a sensible preprint route given both institutions own the underlying data. The AI-framing section travels furthest in a general-interest outlet, but the paper's referee-proof core is the measurement panorama, so venue choice should follow that.

---

## 8. Appendix: could not verify

Do not cite any of the following without fresh independent verification. These are items the search passes hinted at, generated, or encountered but could not confirm — listed so nobody re-invents them.

**NOT_FOUND verdicts:**
- "PLACEHOLDER - IGNORE" (dimension 1): a self-declared placeholder row accidentally emitted by the producing agent, not a real citation; its URL duplicates Lahiri-Sheng (2010). Dropped.

**Hinted papers that do not exist as hinted:**
- "Christensen, Kenny, Meyler" density evaluation: no paper by that trio exists; the actual ECB density-evaluation work is Kenny, Kostka and Masera (three papers, all verified above).
- "Abel/Meyler on aggregation": no such paper found; the hint likely conflates Abel, Rich, Song and Tracy (2016) with Genre, Kenny, Meyler and Timmermann (2013, IJF 29(1), 108–121, point-forecast combination — verified via IDEAS but out of scope here).
- "Rieth/Glas on euro area uncertainty": no Rieth paper on ECB SPF uncertainty found; Glas's SPF coauthor is Hartmann.
- No Clements paper literally titled "Are professional macroeconomic forecasters able to do better than forecasting that inflation/output will be within its historical range?": the hint maps to Clements (2018, IJF) and Clements (2015, JMCB), both verified above.
- A search for "law of total variance forecast pooling" as a named method found no dedicated paper — the decomposition enters the literature via Wallis (2005) and Boero, Smith and Wallis (2008).

**Real but unverified (verification bar not met — confirm before citing):**
- "Uncertain and Asymmetric Forecasts" (arXiv 2411.05938, 2024): ECB-SPF histogram-moment corrections; author name could not be confirmed from fetched pages.
- Bassetti, Casarin and Del Negro's Handbook of Economic Expectations chapter (COVID-era SPF uncertainty application): appears in ScienceDirect listings; chapter page could not be fetched. Cite the verified CEPR DP 19426 instead.
- Oinonen and Paloviita, "How informative are aggregated inflation expectations?": surfaced in search; bibliographic details not confirmed.
- "Uncertainty in long-term macroeconomic forecasts: Ex post evaluation of forecasts by economics researchers": exists per search listing; unverified.
- CBO's ~0.1pp/yr generative-AI productivity assumption (February 2026 outlook): confirmed only via search snippets and Cunningham's compilation; no CBO page fetched — cite via Cunningham or fetch CBO directly.
- IMF (+0.1–0.8pp) and OECD (+0.25–1.3pp) decade-scale figures: present in the verified Shenk and Cunningham compilations; no primary IMF/OECD page fetched.
- Amodei's "Machines of Loving Grace" and Aschenbrenner's "Situational Awareness" (+30%): neither primary essay fetched; Aschenbrenner appears via Cunningham's table.
- Anthropic Economic Index: a usage-measurement program; not verified as containing any growth forecast — do not cite as a growth-estimate source.
- Michigan Surveys of Consumers probabilistic questions and the IGM/Kent Clark qualitative panels: not fetched this session; verify before adding to the elicitation inventory.
- Norges Bank and Riksbank fan-chart/forecast-evaluation pages: content could not be read (navigation-only or JS-walled); excluded from the dashboard inventory.
- Blue Chip long-range (5–10 year) supplement cadence and the SCE five-year question's density format: search-corroborated only, flagged inline above.
- Clements, Rich and Tracy (2022) Handbook chapter pagination (pp. 71–106): search-corroborated (ScienceDirect/CentAUR listings), not page-verified; the Cleveland Fed WP 22-13 version is fully verified.
