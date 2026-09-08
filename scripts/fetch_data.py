#!/usr/bin/env python3
"""Sentinel daily data pull. Writes append-only CSVs under data/.
Sources: Yahoo Finance via yfinance (primary), stooq (fallback for US tickers),
US Treasury daily par yield curve CSV, optional FRED (needs FRED_API_KEY secret).
Every row carries the source and the UTC fetch time so the agent can classify freshness.
The script never raises on a single failure; failures are written to data/fetch_log.csv."""
import csv, json, os, sys, io, datetime as dt, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

US_TICKERS = ["VTI", "ITOT", "VOO", "IVV", "SPYM", "SCHB", "SGOV", "BIL", "USFR", "SHV", "KSA"]
SA_TICKERS = ["9412.SR", "9413.SR", "9400.SR", "9402.SR", "9403.SR", "9404.SR", "9408.SR", "^TASI.SR",
              "2222.SR", "1120.SR", "7010.SR", "4013.SR", "2280.SR", "4190.SR"]
OTHER = ["SAR=X", "BZ=F", "CL=F", "^TNX", "^IRX"]
WATCH_US = ["MSFT", "V", "ISRG", "COST", "NVDA", "LLY"]

NOW = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
os.makedirs("data", exist_ok=True)
PRICES = "data/prices_daily.csv"; LOG = "data/fetch_log.csv"; LATEST = "data/latest.json"

def log(ticker, status, detail=""):
    new = not os.path.exists(LOG)
    with open(LOG, "a", newline="") as f:
        w = csv.writer(f)
        if new: w.writerow(["fetched_at_utc", "ticker", "status", "detail"])
        w.writerow([NOW, ticker, status, detail[:200]])

def load_existing():
    seen = set()
    if os.path.exists(PRICES):
        with open(PRICES) as f:
            for r in csv.DictReader(f): seen.add((r["date"], r["ticker"]))
    return seen

def append_rows(rows):
    new = not os.path.exists(PRICES)
    with open(PRICES, "a", newline="") as f:
        w = csv.writer(f)
        if new: w.writerow(["date", "ticker", "open", "high", "low", "close", "adj_close", "volume", "source", "fetched_at_utc"])
        for r in rows: w.writerow(r)

def yf_pull(tickers, seen):
    import yfinance as yf
    out = []
    for t in tickers:
        try:
            h = yf.Ticker(t).history(period="10d", interval="1d", auto_adjust=False)
            if h is None or h.empty: log(t, "EMPTY"); continue
            n = 0
            for idx, row in h.iterrows():
                d = idx.strftime("%Y-%m-%d")
                if (d, t) in seen: continue
                out.append([d, t, round(float(row["Open"]), 4), round(float(row["High"]), 4), round(float(row["Low"]), 4),
                            round(float(row["Close"]), 4), round(float(row.get("Adj Close", row["Close"])), 4),
                            int(row["Volume"]) if row["Volume"] == row["Volume"] else "", "yahoo", NOW])
                seen.add((d, t)); n += 1
            log(t, "OK", f"{n} new rows")
        except Exception as e:
            log(t, "ERROR", repr(e))
    return out

def stooq_pull(tickers, seen):
    out = []
    for t in tickers:
        try:
            url = f"https://stooq.com/q/d/l/?s={t.lower()}.us&i=d"
            txt = urllib.request.urlopen(url, timeout=30).read().decode()
            rows = list(csv.DictReader(io.StringIO(txt)))[-10:]
            n = 0
            for r in rows:
                d = r["Date"]
                if (d, t) in seen: continue
                out.append([d, t, r["Open"], r["High"], r["Low"], r["Close"], r["Close"], r.get("Volume", ""), "stooq", NOW])
                seen.add((d, t)); n += 1
            log(t, "OK-stooq", f"{n} new rows")
        except Exception as e:
            log(t, "ERROR-stooq", repr(e))
    return out

def treasury_pull(seen):
    out = []
    y = dt.date.today().year
    url = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/"
           f"{y}/all?type=daily_treasury_yield_curve&field_tdr_date_value={y}&page&_format=csv")
    try:
        txt = urllib.request.urlopen(url, timeout=30).read().decode()
        rows = list(csv.DictReader(io.StringIO(txt)))[:10]
        for r in rows:
            d = dt.datetime.strptime(r["Date"], "%m/%d/%Y").strftime("%Y-%m-%d")
            for col, tk in [("3 Mo", "UST3M"), ("2 Yr", "UST2Y"), ("10 Yr", "UST10Y")]:
                if (d, tk) in seen or not r.get(col): continue
                out.append([d, tk, "", "", "", r[col], r[col], "", "us_treasury", NOW]); seen.add((d, tk))
        log("UST", "OK", f"{len(out)} rows")
    except Exception as e:
        log("UST", "ERROR", repr(e))
    return out

def fred_pull(seen):
    key = os.environ.get("FRED_API_KEY")
    if not key: log("FRED", "SKIPPED", "no FRED_API_KEY"); return []
    out = []
    for sid in ["DFEDTARU", "DGS10", "DTB3", "DCOILBRENTEU", "CPIAUCSL"]:
        try:
            url = f"https://api.stlouisfed.org/fred/series/observations?series_id={sid}&api_key={key}&file_type=json&sort_order=desc&limit=10"
            js = json.load(urllib.request.urlopen(url, timeout=30))
            for o in js["observations"]:
                if o["value"] == "." or (o["date"], sid) in seen: continue
                out.append([o["date"], sid, "", "", "", o["value"], o["value"], "", "fred", NOW]); seen.add((o["date"], sid))
            log(sid, "OK")
        except Exception as e:
            log(sid, "ERROR", repr(e))
    return out

def quotes_pull(tickers):
    """Delayed intraday quotes (Yahoo, typically 15-min delayed) for the dashboard's 'live' view.
    Never used for paper fills - fills use dated session opens only."""
    import yfinance as yf
    out = {}
    for t in tickers:
        try:
            fi = yf.Ticker(t).fast_info
            p = fi.get("last_price") or fi.get("lastPrice")
            if p: out[t] = dict(price=round(float(p), 4), as_of_utc=NOW, source="yahoo fast_info (delayed)",
                                prev_close=fi.get("previous_close") or fi.get("previousClose"))
        except Exception as e:
            log(t, "QUOTE-ERROR", repr(e))
    json.dump({"generated_at_utc": NOW, "quotes": out}, open("data/latest_quotes.json", "w"), indent=1)
    return out

def main():
    seen = load_existing()
    quotes_pull(["VTI", "SGOV", "SAR=X", "9412.SR", "9413.SR", "^TASI.SR", "BZ=F"])
    rows = []
    rows += yf_pull(US_TICKERS + SA_TICKERS + OTHER + WATCH_US, seen)
    # stooq fallback only for US tickers that yielded nothing today
    got = {r[1] for r in rows}
    rows += stooq_pull([t for t in US_TICKERS if t not in got], seen)
    rows += treasury_pull(seen)
    rows += fred_pull(seen)
    append_rows(rows)
    # latest snapshot per ticker for quick reads
    latest = {}
    if os.path.exists(PRICES):
        with open(PRICES) as f:
            for r in csv.DictReader(f):
                if r["ticker"] not in latest or r["date"] > latest[r["ticker"]]["date"]:
                    latest[r["ticker"]] = {k: r[k] for k in ("date", "open", "close", "source", "fetched_at_utc")}
    json.dump({"generated_at_utc": NOW, "latest": latest}, open(LATEST, "w"), indent=1)
    print(f"appended {len(rows)} rows; {len(latest)} tickers in latest.json")

if __name__ == "__main__":
    main()
