# 00 — Sentinel Runbook (read first in every scheduled or new session)

System: Bogle-Plus Portfolio Sentinel — Saudi and US markets. SIMULATION ONLY. Never execute, submit, or represent a real transaction. The full master operating prompt is stored as `09_Master_Operating_Prompt.md` in this Project; this runbook is the operational digest.

## Where state lives
All canonical records are Project docs (they persist across sessions; the workspace does not):
`01_Investment_Mandate.md`, `02_Pilot_Portfolios.csv`, `03_Paper_Transactions.csv`, `04_Watchlist_and_Theses.csv`, `05_Decision_Log.csv`, `06_Forecast_Log.csv`, `07_Data_Quality_Log.csv`, `08_Alert_Log.csv`, plus dated reports under `reports/`.
Ledgers 03, 05, 06, 07, 08 are APPEND-ONLY: read the doc, append rows, write the full doc back. Never delete or rewrite historical rows; corrections are new rows that reference the original ID. 02 is a snapshot table: append a new as-of block, keep prior blocks.

## Session start checklist
1. `project_read` this runbook, then 01, 02, 03 (and 04–08 as needed). Record the session's information cutoff (exact time, Asia/Riyadh).
2. Check `03_Paper_Transactions.csv` for PENDING orders and try to verify fills (procedure below).
3. Do the task for this schedule (daily / weekly / monthly / pilot-end). Produce NO ACTION when nothing material changed.
4. Append to the ledgers; write the report to `reports/YYYY-MM-DD_<type>.md`; update `02_Pilot_Portfolios.csv` with a new as-of block if any position or price changed.

## Fill-verification procedure (no hindsight)
- MARKET_NEXT_OPEN orders fill at the first regular-session OPEN after the recommendation timestamp, plus slippage (US ETFs 0.05%; Saudi ETFs 0.50%), plus commissions and FX per 01. The open price must come from a dated source (Investing.com historical, stockanalysis.com history, Yahoo history, fund-provider page, saudiexchange.sa). Record source and timestamp in 07.
- If the open exceeds the order's max-price guard, mark CANCELLED and re-issue at the next session with a new timestamp and reference price.
- If no verifiable open price can be obtained, the order stays PENDING. Never fill from a daily low, a prior close, or an undated quote.
- Fill FX at 3.7550 unless a dated USD/SAR quote for the fill day is found; apply 0.25% conversion cost.

## Data retrieval (capability limits)
- Direct API calls from the workspace shell are blocked (403). Use WebFetch/WebSearch on: stockanalysis.com (US closes/history), Investing.com historical pages (US, Saudi ETFs, TASI, FX, oil), iShares/SSGA/Vanguard factsheets, saudiexchange.sa ETF market watch (intraday delayed; profile pages often render empty), Argaam (prices undated — lower confidence), US Treasury daily rates, BLS, Federal Reserve, SAMA, GASTAT.
- Classify every price: LIVE/NEAR-LIVE, RECENT DELAYED, OFFICIAL CLOSE, STALE, UNKNOWN. Only OFFICIAL CLOSE or a dated open is acceptable for fills.
- GitHub program (package delivered 2026-09-08; AWAITING investor set-up — repository URL and token not yet provided): repository `sentinel` with `ledger/` (canonical copies of 01–09), `data/prices_daily.csv`, `data/latest_quotes.json`, `data/settlements.csv`, `docs/state.json` (dashboard state). A GitHub Action runs every 30 min in US hours plus 03:15 and 12:45 UTC: fetch → auto-settle PENDING MARKET_NEXT_OPEN orders at the first session open after the recommendation timestamp → recompute state → commit. ONCE `sentinel/github_access.md` exists in this Project (repo URL + fine-grained token, Contents read/write), the repository's `ledger/` becomes canonical: read it via `https://api.github.com/repos/<owner>/sentinel/contents/<path>` (base64 content), write via PUT to the same endpoint with the file's current `sha`, and mirror changes to the Project docs. Audit automated fills (price source/date in `data/settlements.csv`) rather than re-filling them. Until then, retrieval is manual-by-agent and fills are verified by the session.

## Schedules (as created 2026-09-08)
- Mandate v1.1 (AM-001, 2026-09-08): core is US-only (VTI + SGOV); Saudi only as an exceptional active idea in Portfolio D. Core-alert scan covers VTI and SGOV; Saudi ETFs 9412/9413 are benchmark references only.
- Daily brief 07:00 Asia/Riyadh (04:00 UTC), Sun–Fri (covers previous US session and Saudi session).
- Weekly outlook Saturday 18:00 Asia/Riyadh (15:00 UTC).
- Monthly contribution & optimization: 1st of month 18:00 Asia/Riyadh (15:00 UTC); first run 2026-10-01: add SAR 20,000 to A, B, C, D; Portfolio C tranche 2 due ≈2026-10-08.
- Pilot-end review 2026-10-31 18:00 Asia/Riyadh.
- Hourly urgent monitor: NOT created by default (cost/value: no active positions; passive core alerts are structural, not intraday). Enable only when Portfolio D holds an active position or the investor requests it.

## Output formats
Use the ACTION-CARD, DAILY-BRIEF and WEEKLY-MEMO formats from 09_Master_Operating_Prompt.md. Lead with the conclusion. State timestamps and data freshness. "NO ACTION" is a complete answer.

## Integrity rules (absolute)
No backdating; no future information; no advantageous historical fills; no removal of unsuccessful recommendations; no unrecorded corrections; no leverage; no use of unavailable virtual cash; costs always included; never claim skill from a short favorable outcome.
