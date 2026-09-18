# Evidence memo: AI growth comparators (5 September 2026)

> Historical research record from the 5 September 2026 pass that produced `paper/AI_COMPARATORS.md`. Where the two differ, the comparators note governs.

Prepared 2026-09-05. Five sources, all re-verified this session against fetched primary pages or PDFs. `LITREVIEW.md` §5 and `paper/references.bib` were used only as starting leads. Verification level noted per source.

## At-a-glance comparability

| Source | Outcome | Geography | Horizon | Probabilistic? | Usable for 2029–31 divergence? |
|---|---|---|---|---|---|
| Karger et al. (2026) | Annualized real GDP growth, 5-yr average | **US** | 2025–2029 and 2045–2049 | **Yes** — 10th/50th/90th + pooled tail masses, unconditional *and* scenario-conditional | **Yes — the only one** |
| Acemoglu (2024) | Cumulative TFP and GDP *level* gain vs baseline | US data | 10 years from ~2024 | No — bare point estimates | Partly: magnitude anchor only, not a density |
| Epoch AI, GATE (2025) | Gross world product growth rate | **World** | "roughly a decade"; full automation "within two decades" | No — explicit non-prediction | No — longer-horizon motivation only |
| Erdil & Besiroglu (2023/24) | GWP growth >30%/yr | **World** | by end of this century | Yes — one odds statement | No — longer-horizon motivation only |
| Davidson (2021) | GWP growth >30%/yr | **World** | this century (by 2100) | Yes — one subjective lower bound | No — longer-horizon motivation only |

---

## 1. Karger, Kuusela, Abaluck, Bryan, Halperin, Jones, Murphy, Trammell, Rosenberg, Tetlock et al. — "Forecasting the Economic Effects of AI"

- **URLs:** https://www.nber.org/papers/w35046 · https://forecastingresearch.org/research/economic-effects-of-ai
- **Publication date:** title page **March 2026**; NBER WP 35046 issue date **April 2026**; FRI page states published 31 March 2026, **revised 20 May 2026**. Survey fielded October 2025 – February 2026.
- **Verification:** full-text PDF read directly (title page, §1–3, Figures 2–10). ⚠️ The PDF read is the **31 March 2026 version**; the 20 May revision and the NBER version may differ.
- **Exact outcome:** *five-year annualized change in real GDP*. Figure 4 caption: "Forecasts for five-year annualized change in the Gross Domestic Product (GDP)." The "2030" horizon is the **2025–2029 average**; "2050" is **2045–2049**. Not endpoint annual growth.
- **Geography:** **US.** Abstract: "We elicit forecasts of how AI will affect the U.S. economy."
- **Samples (post-filter):** 69 economists (reweighted), 27 AI industry + 25 AI policy ("AI experts"), 38 superforecasters, 401 public.
- **Quantiles / probabilities:**
  - *Unconditional* medians 2025–2029: **2.4–2.5%** across all four groups; 2045–2049: 2.5% (economists) to 3.0% (AI experts).
  - *Unconditional* pooled 10th–90th, economists, 2025–2029: **0.73%–4.56%**.
  - *Rapid-conditional* 2025–2029 medians: 3.3% economists (median 10th/90th 1.2%/5.5%), 3.7% superforecasters (2.0–6.0%), 3.7% AI experts. Pooled economist 10th–90th **1.21%–6.420%** [sic].
  - *Rapid-conditional* 2045–2049: 3.5% economists (1.0–7.0%), 4.0% superforecasters (1.0–7.0%), 5.3% AI experts (2.3–9.3%), 4.5% public (2.5–7.1%).
  - **Pooled mass above 10%/yr** (read off Figure 5 labels), 2025–2029: unconditional 0.0% / 0.0% / 0.0% / 0.1% (economists / AI experts / superforecasters / public); rapid-conditional 1.5% / 3.5% / 3.4% / 2.0%. For 2045–2049: unconditional 0.9% / 1.4% / 0.4% / 0.8%; rapid-conditional 5.0% / **10.4%** / 5.6% / 7.4%.
  - Tails are **winsorized at 10%**, so above-10% masses are lower bounds.
- **Conditionality:** both forms elicited separately. "Rapid" scenario probability by 2030: economists **14.0%**, AI experts 16%, superforecasters 12.6%, public 18.1%. Do **not** rebuild an unconditional distribution by weighting the rapid one — unconditional forecasts were elicited directly and coherence-checked against the conditionals.
- **Quotation (23 words):** "economists' pooled distribution for GDP growth in 2030 under the rapid scenario spans 1.21%–6.420% (10th–90th percentile), compared to 0.73%–4.56% for the unconditional scenario."
- **Useful precedent:** Figure 6 benchmarks the economists' 2.5% against nine other 2025–2029 forecasts "which range from 1.9% to 2.1%", **including the SPF**.
- **Unresolved discrepancy:** p.17 says "the 90th percentiles of the 2030 and 2050 pooled distributions for AI experts reach the 10% winsorization cap", which doesn't obviously reconcile with Figure 5's 3.5% above-10% mass for AI experts in 2030. Check appendix Table 10 before citing either as the AI-expert upper tail.

## 2. Acemoglu — "The Simple Macroeconomics of AI" (modest-growth comparator)

- **URLs:** https://www.nber.org/papers/w32487 · https://shapingwork.mit.edu/wp-content/uploads/2024/05/Acemoglu_Macroeconomics-of-AI_May-2024.pdf
- **Publication date:** NBER WP 32487, **May 2024**; PDF dated **12 May 2024**. Journal version *Economic Policy* 40(121), 2025.
- **Verification:** PDF read directly (abstract p.1; §3.2 p.29; §3.4 pp.33–34).
- **Exact outcome:** cumulative **level** gains vs a no-AI baseline over 10 years, not a growth-rate forecast. TFP ≤0.66% over 10 years, refined to ≈0.53% for hard-to-learn tasks. GDP **1.16% over 10 years** (baseline) or **0.93%** with hard tasks; 1.4–1.56% under a large investment boom.
- **Geography:** US data (BEA industry labor shares, O\*NET tasks, US corporate-sector adoption).
- **Horizon:** 10 years from ~2024 (through ~2034) — overlaps but does not align with a single SPF forecast year.
- **Probability/conditionality:** **none.** No interval, no distribution.
- **Quotation (21 words):** "TFP will be higher by 0.66 percentage points in 10 years, or annual TFP growth will be higher by around 0.064%."
- **Trap flagged:** 1.16% is a decade **level** gain (≈0.11pp/yr), not 1.16pp/yr — and it is an *increment to* baseline growth, not a level of growth, so it is not in the same units as the 30%+ figures below.

## 3. Epoch AI — GATE integrated assessment model

- **URLs:** https://epoch.ai/blog/announcing-gate · https://arxiv.org/abs/2503.04941 · playground https://epoch.ai/gate
- **Publication date:** blog **21 March 2025**; arXiv:2503.04941 submitted 6 March 2025, v2 12 March 2025.
- **Verification:** arXiv abstract page fetched (contains no growth numbers); the numeric claims come from the blog post via fetch extraction rather than my own reading of raw HTML — one step weaker than sources 1, 2, 4.
- **Exact outcome:** growth rate of **gross world product** during the automation transition.
- **Geography:** **world.** Not US, not euro area.
- **Horizon:** elevated growth "materialize[s] over roughly a decade"; the model "consistently projects that the global economy can marshal enough effective compute to automate most tasks within two decades." No calendar anchoring of the peak-growth window in the verified material.
- **Probability/conditionality:** **none.** A parameterized scenario simulator; the authors "don't recommend interpreting the model outcomes as precise quantitative predictions."
- **Quotation (16 words):** "with rates elevated by 2-20 times compared to the recent historical average of ~3% per year."
- **Trap flagged:** 2–20× of ~3%/yr ≈ 6–60%/yr **of GWP**, over an unanchored decade, with no probability and an explicit non-prediction disclaimer. Not comparable to a 2029 US SPF density on any axis.

## 4. Erdil & Besiroglu — "Explosive growth from AI automation: A review of the arguments"

- **URL:** https://arxiv.org/abs/2309.11690 (v3 PDF read)
- **Publication date:** arXiv v1 **20 September 2023**; **v3 15 July 2024**. Epoch AI / MIT FutureTech.
- **Verification:** PDF pages 1–4 read directly.
- **Exact outcome:** "explosive growth", defined verbatim as "annual real gross world product (GWP) exceeding 130% of its maximum value over all previous years" — **>30%/yr GWP growth**, with a ratchet condition excluding crash-and-rebound episodes.
- **Geography:** **world.** **Horizon:** "by the end of this century."
- **Probability/conditionality:** one qualitative odds statement, bundling *automation happening* with *explosive growth following*. It is **not** a probability conditional on advanced AI arriving.
- **Quotation (21 words):** "We think that the odds of widespread automation and subsequent explosive growth by the end of this century are about even."
- **Correction to a downstream characterization:** Karger et al. (p.6) describe this as "roughly 50% odds of this occurring by 2100 **if** AI capable of broadly substituting for human labor is developed." The source sentence is not conditional in that way. Cite Erdil & Besiroglu directly, not via Karger.

## 5. Davidson — "Could Advanced AI Drive Explosive Economic Growth?" (Open Philanthropy, now Coefficient Giving)

- **URLs:** https://www.lesswrong.com/posts/dGWMCFkETTg8EZ2bB/could-advanced-ai-drive-explosive-economic-growth · canonical https://coefficientgiving.org/research/could-advanced-ai-drive-explosive-economic-growth/ (HTTP 403 to automated fetch)
- **Publication date:** **June 2021** (linkpost 30 June 2021).
- **Verification:** author-posted linkpost text fetched; canonical publisher page blocks fetching. One step weaker than sources 1, 2, 4.
- **Exact outcome:** "explosive growth", ">30% annual growth of gross world product (GWP)". **Geography:** world. **Horizon:** by 2100.
- **Probability/conditionality:** an explicit **unconditional lower bound** on the joint event (advanced AI arrives *and* drives explosive growth). A separate ~30%-conditional-on-advanced-AI figure is attributed to Davidson by Erdil & Besiroglu (p.2) but I could not confirm it in Davidson's own text — don't cite it without checking the full report.
- **Quotation (15 words):** "Overall, I place at least 10% probability on advanced AI driving explosive growth this century."

---

## Is there an actually comparable probability statement?

**Yes — exactly one, and only from Karger et al.**

The comparable object is the **pooled unconditional distribution of five-year annualized US real GDP growth for 2025–2029**: 10th–90th percentile 0.73%–4.56% for economists, with **0.0–0.1% pooled probability above 10%/yr** across all four groups. It matches the SPF densities on outcome variable (real GDP growth), units (percent per year), geography (US), and period (inside the US SPF's annual density horizon through 2029). Its conditional counterpart — 1.21%–6.420% pooled, 1.5–3.5% mass above 10%/yr — is explicitly conditional on the rapid scenario, which the same respondents give 12.6–18.1% probability.

Two mismatches must be stated wherever this comparison is made:

1. **Averaging window.** Karger elicits a *five-year annualized average*; the SPF density is for a *single calendar year*. A five-year average is mechanically less dispersed under transitory shocks and more dispersed under persistent regime shifts, so the spreads are not interchangeable. Either build a five-year average from the SPF annual densities, or state the direction of the bias.
2. **Winsorization.** Karger's tails are capped at 10%, so its far-right tail is a lower bound; SPF open-ended top bins are not capped the same way. Tail comparisons are conservative in Karger's direction.

**No other source here yields a comparable probability statement.** Acemoglu attaches none. GATE attaches none and disclaims prediction. Erdil & Besiroglu and Davidson attach probabilities, but to *world* GDP over a *century*, at a >30%/yr threshold the SPF bin structure does not resolve.

**Euro-area gap:** none of these five forecasts euro-area GDP. Any ECB SPF divergence claim transfers a US or world number and must say so.

## Which claims support divergence measured within 2029–31, and which only motivate a longer horizon

**Can support measured divergence inside the SPF window:**

- **Karger et al., 2025–2029, unconditional.** Directly comparable. The honest headline is that expert medians (2.4–2.5%) sit only modestly above SPF-type baselines (~1.9–2.1%, per the paper's own Figure 6) and essentially *no* pooled unconditional mass sits above 10%/yr — i.e. this supports a "unconditional divergence is small" finding, not a large one.
- **Karger et al., 2025–2029, rapid-conditional.** Supports a conditional divergence statement: pooled 90th percentile 6.42% and 1.5–3.5% mass above 10%/yr. Must always carry the 12.6–18.1% scenario weight and the word "conditional".
- **Acemoglu, weakly.** A defensible low anchor (~0.05–0.11pp/yr added to TFP/GDP growth) over a window overlapping 2029–31, but a point increment with no distribution. Brackets magnitudes; is not a density.

**Only motivate a longer elicitation horizon:**

- **GATE** — world aggregate, unanchored decade, no probability, explicit non-prediction disclaimer.
- **Erdil & Besiroglu** — world aggregate, century horizon.
- **Davidson** — world aggregate, century horizon.

These three are the right evidence for the elicitation-gap argument (distributions are most needed where no survey elicits them) and the wrong evidence for any claim about 2029–31 SPF densities. Presenting them as implying near-term forecastable divergence would be exactly the conditional-as-unconditional and world-as-US errors the rewrite is meant to avoid.

## Do not recycle the 0.1–30pp range

The 0.1–30pp band in `LITREVIEW.md` §5 concatenates, in one interval: an *increment* to US growth derived from a cumulative decade level gain (Acemoglu, ~0.1pp/yr); *levels* of world GDP growth from an uncertainty-disclaimed simulator (GATE, 6–60%/yr); and a *century-horizon threshold* on world GDP (Davidson, Erdil & Besiroglu, >30%/yr). Different aggregates, geographies, horizons, and senses of "growth". Report each in its own units or drop the aggregate range.

## Source URLs

- Karger et al. (2026), NBER WP 35046 — https://www.nber.org/papers/w35046
- Karger et al. (2026), FRI report page — https://forecastingresearch.org/research/economic-effects-of-ai
- Acemoglu (2024), NBER WP 32487 — https://www.nber.org/papers/w32487
- Acemoglu (2024), MIT-hosted PDF (12 May 2024) — https://shapingwork.mit.edu/wp-content/uploads/2024/05/Acemoglu_Macroeconomics-of-AI_May-2024.pdf
- Epoch AI (2025), GATE announcement — https://epoch.ai/blog/announcing-gate
- Erdil, Potlogea, Besiroglu et al. (2025), GATE paper — https://arxiv.org/abs/2503.04941
- Erdil & Besiroglu (2023, rev. 2024) — https://arxiv.org/abs/2309.11690
- Davidson (2021), author linkpost — https://www.lesswrong.com/posts/dGWMCFkETTg8EZ2bB/could-advanced-ai-drive-explosive-economic-growth
- Davidson (2021), canonical publisher page (403 to automated fetch) — https://coefficientgiving.org/research/could-advanced-ai-drive-explosive-economic-growth/

## Open items before these numbers go in the paper

1. Re-verify all Karger figures against the **20 May 2026** revision and the NBER April 2026 version; the PDF read here is the 31 March 2026 original.
2. Resolve the Figure 5 vs p.17 AI-expert upper-tail discrepancy against appendix Table 10.
3. Confirm Karger's exact GDP question wording in Appendix H.4.1 (I verified the outcome definition from the Figure 4 caption and §3.2 text, not from the instrument itself).
4. Confirm Davidson's conditional (~30%) figure in the full Open Philanthropy report, or drop it.
5. Re-fetch the GATE blog quotes directly if they are to appear verbatim in the manuscript.

---

**What I did and didn't do:** all five sources were fetched fresh; Karger, Acemoglu, and Erdil & Besiroglu were read from PDF page images directly, GATE and Davidson via fetch-tool extraction (flagged above as weaker). No repo files were read beyond `LITREVIEW.md` and `paper/references.bib`, and nothing was edited. The one file I was authorized to write could not be created because Write is disabled — tell me a path and re-enable writes, or copy the memo above into `report.md` yourself.
