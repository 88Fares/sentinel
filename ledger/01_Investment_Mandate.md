# 01 — Investment Mandate (Bogle-Plus Portfolio Sentinel)

Version 1.1 — created 2026-09-08 14:47 Asia/Riyadh; amended 2026-09-08 15:06 Asia/Riyadh (AM-001). SIMULATION ONLY. No real transactions are executed, submitted, or represented as executed under this mandate.

## Investor profile (as stated by the investor, 2026-09-08)
Saudi national, age 23–26, stable income, no debt, base currency SAR. Approximately SAR 200,000 investable cash plus approximately SAR 20,000 per month. Emergency reserve is outside scope. No near-term cash need. Long-term, open-ended horizon. Comfortable with meaningful temporary declines when the thesis is sound. Priorities: long-term growth and inflation protection. Distributions reinvested. Investments should generally be realizable within about one month. No ESG or Sharia restriction specified. Not a US citizen. Likely broker: Sahm (no integration; not authorized).

## Objective
Increase expected long-term real wealth after inflation, fees, FX costs, taxes and avoidable mistakes. Success is measured by decision quality and process discipline, not activity or short-term outperformance.

## Approved markets and instruments
Listing venues: Saudi Exchange (main market) and major regulated US exchanges. Excluded: OTC/pink sheets, unregulated products, private placements, crypto, CFDs, anything not available through the approved broker. Leverage, margin, derivatives, short selling and leveraged funds are DISABLED. Global ex-US exposure via a US-listed diversified fund may be researched but not bought without an explicit pending-policy-decision note or user approval.

## Strategic allocation (v1.1, AM-001)
| Sleeve | Portfolio B (Bogle Immediate) | Portfolio C (Bogle Phased) | Portfolio D (Bogle-Plus Agent) |
|---|---|---|---|
| Broad US equity | 90% | 90% | 80% |
| Broad Saudi equity | 0% (removed by AM-001) | 0% | 0% in core; Saudi allowed only in the active sleeve |
| Defensive & liquid | 10% | 10% | 10% |
| Active satellite | 0% | 0% | 10% (starts in virtual SAR cash) |

Superseded v1.0 allocation (for the record): B and C 70/20/10; D 60/20/10/10.

Portfolio A is a SAR cash baseline (0% nominal; a SAR money-market comparator line is reported alongside).
Portfolio C deploys 50% of target positions at initial deployment, 25% ≈30 days later (target 2026-10-08), 25% ≈60 days later (target 2026-11-08, after pilot end — tracked as a pending commitment). The schedule is not altered on market predictions.
Rebalancing band: ±5 percentage points on any major sleeve triggers analysis (not automatic trading). Cash flows first; sell only for material breach, thesis deterioration, risk reduction or clearly superior replacement.
Monthly contribution: SAR 20,000 to every portfolio on the first of each month (first: 2026-10-01), allocated by the contribution hierarchy (confirm contribution → fix material underweights → fund core at target weights → approved active idea only if all gates pass → otherwise defensive sleeve).

## Selected core instruments (v1.1 — see 05_Decision_Log D0002, D0004, D0008)
- US equity: VTI — Vanguard Morningstar Total Stock Market ETF, NYSE Arca, US-domiciled, 0.03% ER.
- Defensive & liquid: SGOV — iShares 0-3 Month Treasury Bond ETF, NYSE Arca, USD, 0.09% ER, effective duration 0.10y.
- Saudi equity (removed from core by AM-001): 9412 Albilad MSCI Saudi Equity ETF and 9413 Al Rajhi MSCI Saudi Equity ETF remain the reference Saudi passive instruments for benchmarking the active sleeve's Saudi ideas (D0003 records the original selection and its liquidity and Shariah-screen caveats).

## Saudi exception rule (AM-001)
Saudi securities may enter Portfolio D's active sleeve only when the agent documents that the asset is exceptionally undervalued and an outstanding opportunity, and it passes all seven gates and the concentration rules. The core never holds Saudi equity. Saudi opportunities are judged against both VTI and the Saudi passive reference ETFs.

## Industry rules (active sleeve, Portfolio D only)
Provisional research whitelist — Saudi: banks & financial infrastructure; telecom & digital infrastructure; healthcare services & established manufacturers; consumer staples & selected high-quality consumer; logistics & high-quality industrials; selected energy & materials. US: semiconductors & computing infrastructure; enterprise software & cloud; healthcare equipment & established healthcare; industrial automation & infrastructure; high-quality consumer platforms; selected profitable financial & financial-infrastructure businesses. No absolute exclusions. Positions outside the whitelist require a documented special-situations justification.

## Concentration rules (active sleeve)
Active sleeve target 10% of Portfolio D, hard max 10% during pilot. Max 5 names. Starting position 1–2%; normal max 4% per company; hard max 5%; max 5% of total portfolio in one industry. No averaging down without a full thesis refresh. All seven gates (eligibility, business quality, valuation, passive alternative, differentiated view, portfolio fit, red team) must pass before any active paper order. NO ACTIVE INVESTMENT is the default.

## Cost and tax assumptions used in the simulation (provisional; disclosed)
- US commission (Sahm published schedule as of 2026-01-27): USD 0.015/share, min USD 1.99, plus clearing USD 0.003/share; 15% VAT applied to Saudi-resident clients.
- Saudi commission: 0.105% broker + 0.020% Tadawul Group fees (both +15% VAT) + 0.030% CMA fee = 0.174% of value. Sahm's current 0% promotional commission is ignored (conservative).
- FX: USD/SAR mid 3.7550 at reference; 0.25% conversion cost assumed (Sahm spread NOT FOUND — assumption).
- Slippage on next-open fills: 0.05% adverse for US ETFs; 0.50% adverse for Saudi ETFs (thin books).
- US dividend withholding: 30% (no US–Saudi income-tax treaty). Applied to VTI distributions. Applied to SGOV distributions as a conservative assumption even though SGOV distributions have been designated 100% qualified interest income (potentially exempt under IRC §871(k)) — broker application unverified.
- US estate tax: NOT modelled in returns, but flagged as a material live-stage risk (US-situs assets above USD 60,000; no estate-tax treaty).
- Saudi personal income/capital-gains tax: none. Zakat: personal obligation not modelled.

## Pending policy decisions (require investor input before live stage; simulation proceeds on stated defaults)
1. US-domiciled ETFs expose a non-resident alien to US estate tax above USD 60,000 of US-situs assets and 30% dividend withholding. Alternatives (Irish-domiciled UCITS ETFs on LSE/Xetra; Saudi-listed 9406 Albilad MSCI US Equity ETF) are outside the current venue rule or carry higher fees/Islamic screens. Default: proceed with VTI in simulation; professional tax/estate advice recommended before live use.
2. (Closed by AM-001.) Saudi core removed; the Shariah-screen and liquidity issues no longer affect the core. Consequence to note: the portfolio is now ~90% US-domiciled, so pending decision 1 (estate tax and withholding) applies to nearly all assets, and home-country diversification is gone (SAR peg makes currency a tail risk only).
3. Defensive sleeve currency: SGOV is USD (peg risk only) vs SAR sukuk ETF 9404 (has duration) vs SAR money-market funds (best fit if Sahm offers them — unverified). Default: SGOV.
4. Global ex-US scenario (50/15/15/10/10): researched only; not implemented.
5. Hourly monitoring cadence and cost (see 00_Runbook).

## Simulation status
ACTIVE — paper trading only. Transition to live recommendations requires explicit, unambiguous written authorization from the investor and a completed pilot-end review (2026-10-31).

## Approved amendments
- AM-001 — 2026-09-08 15:06 Asia/Riyadh — Investor instruction: prioritise US securities/ETFs under the Bogle method; remove Saudi equity from the strategic core; Saudi permitted only as an exceptional, gate-passing active idea. New targets B/C 90/10, D 80/10/10. Six pending Saudi paper orders cancelled unfilled; replacement VTI orders T0013–T0015 issued before the 8 Sep US open. Decision D0008.
