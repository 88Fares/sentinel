# Portfolio Sentinel — program repository

A free, unattended paper-trading engine for a Bogle-style portfolio. GitHub Actions pulls delayed prices every 30 minutes during US market hours (and twice daily otherwise), settles pending paper orders at verified session opens, recomputes four virtual portfolios, and publishes a dashboard on GitHub Pages. Claude's scheduled sessions read and write the same ledgers through the GitHub API.

Nothing in this repository places real orders. It is a simulation and a record.

## What is in here

| Path | Purpose |
|---|---|
| `ledger/01–09` | The canonical records (mandate, positions, paper transactions, watchlist, decision/forecast/data-quality/alert logs, runbook). Append-only by convention. |
| `config.json` | Cost assumptions, strategic targets, instrument metadata (exchange, timezone, open time, slippage). |
| `scripts/fetch_data.py` | Pulls daily OHLC (Yahoo, stooq fallback), delayed quotes, US Treasury curve, optional FRED series → `data/`. |
| `scripts/settle_orders.py` | Fills `PENDING` `MARKET_NEXT_OPEN` orders at the first session open after the recommendation timestamp (+ slippage, commission, FX). Cancels if the open exceeds the max-price guard. Logs every fill to `data/settlements.csv`. |
| `scripts/compute_state.py` | Deterministic accounting → `docs/state.json` (values, weights, history, pending orders, freshness). |
| `docs/index.html` | The dashboard (GitHub Pages serves `docs/`). |
| `.github/workflows/sentinel.yml` | The schedule. |

## Set-up — about 15 minutes, once

1. **Create the repository.** On github.com: New repository → name `sentinel` → **Public** (simplest; the ledgers contain no personal data beyond the simulation) or Private (then step 5 is required for reads too). Do not initialise with a README.
2. **Upload this package** keeping the folder structure (drag-and-drop "Add file → Upload files" works; include the hidden `.github` folder — if the web uploader drops it, create `.github/workflows/sentinel.yml` by hand with "Add file → Create new file" and paste the content).
3. **Allow the workflow to commit.** Settings → Actions → General → Workflow permissions → *Read and write permissions* → Save.
4. **Turn on the dashboard.** Settings → Pages → Source: *Deploy from a branch* → Branch `main`, folder `/docs` → Save. The URL will be `https://<your-username>.github.io/sentinel/`.
5. **Give Claude write access** (so its scheduled sessions can commit ledger updates and new paper orders). GitHub → your profile photo → Settings → Developer settings → Personal access tokens → **Fine-grained tokens** → Generate new token:
   - Token name: `claude-sentinel`; Expiration: 90 days (renew when it expires — Claude will remind you in the daily brief a week before).
   - Repository access: *Only select repositories* → `sentinel`.
   - Repository permissions: **Contents: Read and write**. Nothing else.
   - Generate, copy the token (starts with `github_pat_`).
   Paste the token and the repository URL into the Claude conversation. Claude stores it in the Project doc `sentinel/github_access.md` so the scheduled runs can use it; that doc is visible only inside your Claude account, and you can revoke the token at any time from the same GitHub page.
6. **Run once and check.** Actions → sentinel → Run workflow. After ~2 minutes `data/prices_daily.csv`, `data/latest_quotes.json` and `docs/state.json` should update and the Pages URL should show live values. Optional: a free FRED API key as the repository secret `FRED_API_KEY` adds Fed-funds, CPI and yield series.

## How the pieces cooperate

- **The workflow** is the clock and the accountant: prices in, orders settled, state recomputed, committed. It never decides anything.
- **Claude's scheduled sessions** (daily 07:00, weekly Saturday 18:00, monthly 1st 18:00, pilot-end 31 Oct — Riyadh time) are the analyst: they read `ledger/` and `data/`, write briefs, add contributions and new paper orders (status `PENDING`), audit the automated fills, and record decisions. They commit through the GitHub API with the token from step 5.
- **You** read the dashboard or the briefs, and make policy decisions (the mandate lists the pending ones).

## Integrity rules enforced in code

Fills only at a dated session open that occurred *after* the recommendation timestamp; never a close, a low, or a prior price. Costs (commission, VAT, FX spread, slippage) always applied. Cancelled and unsuccessful orders stay in the ledger. `settlements.csv` records the exact price row used for every fill. History is valued with only the fills that had occurred by each date.

## Known limits

Yahoo data are delayed (~15 min) and occasionally revised; Saudi symbols may be missing on Yahoo (they are only needed if the active sleeve ever holds a Saudi name). GitHub's cron can drift by several minutes. If a fetch fails the run still completes and the failure is logged in `data/fetch_log.csv`; pending orders simply wait for the next run.
