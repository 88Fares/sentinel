#!/usr/bin/env python3
"""Auto-settle PENDING MARKET_NEXT_OPEN paper orders in ledger/03_Paper_Transactions.csv.

Rule (from the mandate's fill conventions): an order fills at the OPEN of the first regular
session that starts AFTER the recommendation timestamp, plus adverse slippage, commissions and FX.
The open comes from data/prices_daily.csv (dated rows written by fetch_data.py, source recorded).
If the open exceeds the max-price guard the order is CANCELLED. If no qualifying session row
exists yet, the order stays PENDING. Nothing is ever filled from a close, a low, or a prior price.
Every settlement is also appended to data/settlements.csv with the price row it used.
"""
import csv, json, re, os, sys, datetime as dt
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "ledger", "03_Paper_Transactions.csv")
PRICES = os.path.join(ROOT, "data", "prices_daily.csv")
SETTLE = os.path.join(ROOT, "data", "settlements.csv")
CFG = json.load(open(os.path.join(ROOT, "config.json")))
NOW = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

def num(s):
    m = re.search(r"-?\d+(\.\d+)?", str(s).replace(",", ""))
    return float(m.group()) if m else None

def load_prices():
    px = {}
    if not os.path.exists(PRICES): return px
    for r in csv.DictReader(open(PRICES)):
        px.setdefault(r["ticker"], {})[r["date"]] = r
    return px

def fx_on(px, d):
    rows = px.get("SAR=X", {})
    if d in rows and rows[d].get("close"): return float(rows[d]["close"]), "yahoo SAR=X close " + d
    return CFG["fx_ref"], "config fx_ref"

def commission(ccy, qty, gross):
    f = CFG["fees"][ccy]
    if ccy == "USD":
        c = max(qty * f["per_share"], f["min"]) + max(qty * f["clearing_per_share"], f["clearing_min"])
        return round(c * (1 + f["vat"]), 2)
    return round(gross * f["pct"], 2)

def main():
    px = load_prices()
    rows = list(csv.DictReader(open(LEDGER)))
    fields = list(rows[0].keys())
    changed = 0; log = []
    for r in rows:
        if not r["status"].startswith("PENDING") or r["order_type"] != "MARKET_NEXT_OPEN": continue
        tk = CFG["ticker_aliases"].get(r["ticker"], r["ticker"])
        inst = CFG["instruments"].get(tk)
        if not inst: log.append((r["transaction_id"], "SKIP", "no instrument config")); continue
        tz = ZoneInfo(inst["tz"])
        rec = dt.datetime.fromisoformat(r["recommendation_timestamp"]).astimezone(tz)
        open_t = dt.time(*map(int, inst["open"].split(":")))
        # first session whose open is after the recommendation
        cands = sorted(d for d in px.get(tk, {}) if px[tk][d].get("open"))
        fill_date = None
        for d in cands:
            dd = dt.date.fromisoformat(d)
            if dd > rec.date() or (dd == rec.date() and rec.time() < open_t):
                fill_date = d; break
        if not fill_date: log.append((r["transaction_id"], "PENDING", "no session row after recommendation yet")); continue
        prow = px[tk][fill_date]
        open_px = float(prow["open"]); qty = float(r["quantity"])
        guard = num(r["limit_price"])
        fill_ts = dt.datetime.combine(dt.date.fromisoformat(fill_date), open_t, tzinfo=tz).isoformat()
        if guard and open_px > guard:
            r["status"] = f"CANCELLED {NOW} (open {open_px} > max price {guard}; auto)"
            r["fill_timestamp"] = fill_ts
            log.append((r["transaction_id"], "CANCELLED", f"open {open_px} > guard {guard}")); changed += 1
            continue
        slip = inst["slippage"]
        fill_px = round(open_px * (1 + slip), 4)
        gross = qty * fill_px
        comm = commission(inst["ccy"], qty, gross)
        if inst["ccy"] == "USD":
            fx, fx_src = fx_on(px, fill_date)
            usd_total = gross + comm
            fx_cost = round(usd_total * fx * CFG["fx_cost"], 2)
            sar = round(usd_total * fx + fx_cost, 2)
            r["fx_rate"] = f"{fx:.4f} ({fx_src}; +{CFG['fx_cost']*100:.2f}% cost = SAR {fx_cost})"
            r["commission"] = f"{comm} USD"
        else:
            fx = 1.0; sar = round(gross + comm, 2)
            r["fx_rate"] = "1.0000"; r["commission"] = f"{comm} SAR"
        sign = -1 if r["action"] == "BUY" else 1
        r["fill_timestamp"] = fill_ts
        r["fill_price"] = f"{fill_px}"
        r["slippage"] = f"{slip*100:.2f}% applied to open {open_px}"
        r["total_sar_cash_effect"] = f"{sign*sar:.2f}"
        r["status"] = f"FILLED (auto-settled {NOW}; source {prow['source']} open {fill_date})"
        log.append((r["transaction_id"], "FILLED", f"{qty} @ {fill_px} ({inst['ccy']}) = SAR {sign*sar:.2f}")); changed += 1
        new = not os.path.exists(SETTLE)
        with open(SETTLE, "a", newline="") as f:
            w = csv.writer(f)
            if new: w.writerow(["settled_at_utc", "transaction_id", "portfolio_id", "ticker", "quantity", "fill_date", "open_used", "fill_price", "fx_rate", "commission", "total_sar_cash_effect", "price_source", "price_fetched_at_utc"])
            w.writerow([NOW, r["transaction_id"], r["portfolio_id"], tk, qty, fill_date, open_px, fill_px, fx, comm, f"{sign*sar:.2f}", prow["source"], prow["fetched_at_utc"]])
    if changed:
        with open(LEDGER, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    for l in log: print(*l)
    print(f"settled/cancelled {changed} orders")

if __name__ == "__main__":
    main()
