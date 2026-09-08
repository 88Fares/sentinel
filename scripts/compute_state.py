#!/usr/bin/env python3
"""Rebuild docs/state.json (what the dashboard renders) from the ledgers and price files.
Deterministic accounting only: cash = start capital + contributions + cash effects of FILLED rows;
holdings = filled quantities; values = holdings x latest price x FX. History is valued day by day
using only fills that had occurred by each date (no look-ahead)."""
import csv, json, os, re, datetime as dt
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(ROOT, "config.json")))
L = lambda n: os.path.join(ROOT, "ledger", n)
D = lambda n: os.path.join(ROOT, "data", n)
NOW = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
START_DATE = "2026-09-08"

def num(s):
    m = re.search(r"-?\d+(\.\d+)?", str(s).replace(",", "")); return float(m.group()) if m else 0.0

def rd(path):
    return list(csv.DictReader(open(path))) if os.path.exists(path) else []

def alias(t): return CFG["ticker_aliases"].get(t, t)

def main():
    tx = rd(L("03_Paper_Transactions.csv"))
    prices = defaultdict(dict)
    for r in rd(D("prices_daily.csv")):
        if r.get("close"): prices[r["ticker"]][r["date"]] = r
    quotes = {}
    if os.path.exists(D("latest_quotes.json")):
        quotes = json.load(open(D("latest_quotes.json"))).get("quotes", {})

    def price_on(tk, d):  # last close on or before d
        ds = [x for x in prices.get(tk, {}) if x <= d]
        return (float(prices[tk][max(ds)]["close"]), max(ds)) if ds else (None, None)

    def latest_price(tk):
        q = quotes.get(tk)
        c, d = price_on(tk, "9999-12-31")
        if q and q.get("price") and (not d or q.get("as_of_utc", "") >= d):
            return float(q["price"]), q.get("as_of_utc"), "delayed quote (" + q.get("source", "yahoo") + ")"
        return c, d, "official close (" + (prices[tk][d]["source"] if d else "n/a") + ")"

    fx_now, fx_asof, fx_src = latest_price("SAR=X")
    if not fx_now: fx_now, fx_asof, fx_src = CFG["fx_ref"], None, "config fx_ref"

    pids = ["A", "B", "C", "D"]
    events = defaultdict(list)  # pid -> (date, kind, tk, qty, cash_effect)
    pending = []
    for r in tx:
        pid = r["portfolio_id"]; st = r["status"]
        if r["action"] == "CONTRIBUTION":
            events[pid].append((r["fill_timestamp"][:10] or r["recommendation_timestamp"][:10], "CASH", None, 0, num(r["total_sar_cash_effect"])))
        elif st.startswith("FILLED"):
            q = num(r["quantity"]) * (1 if r["action"] == "BUY" else -1)
            events[pid].append((r["fill_timestamp"][:10], "FILL", alias(r["ticker"]), q, num(r["total_sar_cash_effect"])))
        elif st.startswith("PENDING"):
            pending.append({k: r[k] for k in ("transaction_id", "portfolio_id", "action", "ticker", "quantity", "order_type", "limit_price", "recommendation_timestamp", "total_sar_cash_effect")})

    def value_at(pid, d, use_latest=False):
        cash = CFG["start_capital_sar"]; hold = defaultdict(float)
        for (ed, kind, tk, q, ce) in events[pid]:
            if ed <= d:
                cash += ce
                if kind == "FILL": hold[tk] += q
        total = cash; lines = []
        for tk, q in hold.items():
            if abs(q) < 1e-9: continue
            if use_latest: p, asof, src = latest_price(tk)
            else: p, asof = price_on(tk, d); src = "close"
            if p is None: continue
            ccy = CFG["instruments"].get(tk, {}).get("ccy", "USD")
            fx = fx_now if use_latest else (price_on("SAR=X", d)[0] or CFG["fx_ref"])
            if ccy == "SAR": fx = 1.0
            mv = q * p * fx; total += mv
            lines.append(dict(ticker=tk, name=CFG["instruments"].get(tk, {}).get("name", tk), qty=q, price=p, ccy=ccy, price_asof=asof, price_source=src, fx=fx, value_sar=round(mv, 2)))
        return total, cash, lines

    dates = sorted({d for tk in prices for d in prices[tk] if d >= START_DATE} | {START_DATE, dt.date.today().isoformat()})
    out = dict(generated_at_utc=NOW, start_capital_sar=CFG["start_capital_sar"], fx=dict(rate=fx_now, as_of=fx_asof, source=fx_src),
               labels=CFG["labels"], targets=CFG["targets"], portfolios={}, history={}, pending_orders=pending,
               data_freshness={tk: (max(prices[tk]) if prices[tk] else None) for tk in prices})
    for pid in pids:
        total, cash, lines = value_at(pid, "9999-12-31", use_latest=True)
        contrib = sum(ce for (_, k, _, _, ce) in events[pid] if k == "CASH")
        invested = CFG["start_capital_sar"] + contrib
        w = {l["ticker"]: round(l["value_sar"] / total, 4) for l in lines}; w["CASH"] = round(cash / total, 4)
        out["portfolios"][pid] = dict(label=CFG["labels"][pid], total_sar=round(total, 2), cash_sar=round(cash, 2), contributions_sar=contrib,
                                      net_invested_sar=invested, pnl_sar=round(total - invested, 2), return_pct=round((total / invested - 1) * 100, 3),
                                      holdings=lines, weights=w)
        out["history"][pid] = [dict(date=d, total_sar=round(value_at(pid, d)[0], 2)) for d in dates]
    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, "docs", "state.json"), "w"), indent=1)
    print("state.json written:", {p: out["portfolios"][p]["total_sar"] for p in pids}, "pending", len(pending))

if __name__ == "__main__":
    main()
