# app/services/fetchers/financials.py

import os
import json
import requests
import yfinance as yf
from dotenv import load_dotenv
from app.core.cache import CacheManager

# === Load environment variables ===
load_dotenv()

# === API Base URLs ===
FINNHUB = "https://finnhub.io/api/v1"
FMP = "https://financialmodelingprep.com/api/v3"
TWELVE = "https://api.twelvedata.com"
RAPIDAPI_HOST = "yh-finance.p.rapidapi.com"  # YH Finance by SteadyAPI (RapidAPI)

# === API Keys ===
FINNHUB_KEY = os.getenv("FINNHUB_API_KEY")
FMP_KEY = os.getenv("FMPSDK_API_KEY")
TWELVE_KEY = os.getenv("TWELVE_API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")


# =====================================================================
# 🧩 Generic Safe GET Wrapper
# =====================================================================
def safe_get(url, params=None, source_name=""):
    """Perform a safe GET request that never raises; logs minimal info."""
    try:
        r = requests.get(url, params=params or {}, timeout=10)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict) and data.get("status") == "error":
            print(f"⚠️  {source_name}: {data.get('message', 'API returned error')}")
            return None
        return data
    except Exception as e:
        print(f"⚠️  {source_name} failed: {e}")
        return None


# =====================================================================
# 🧩 YH Finance (RapidAPI SteadyAPI) — Reliable Yahoo Alternative
# =====================================================================
def fetch_yahoo_summary(symbol: str) -> dict:
    """Fetches stock data from YH Finance (RapidAPI by SteadyAPI)."""
    if not RAPIDAPI_KEY:
        print("⚠️  RAPIDAPI_KEY missing — skipping YH Finance block")
        return {}

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }

    try:
        # --- 1️⃣ Profile (sector, industry, country)
        prof = requests.get(
            f"https://{RAPIDAPI_HOST}/v1/stock/profile",
            headers=headers,
            params={"symbol": symbol},
            timeout=10,
        ).json()
        profile_data = prof.get("quoteSummary", {}).get("result", [{}])[0].get("assetProfile", {})

        # --- 2️⃣ Financial data (current price, margins, debt)
        fin = requests.get(
            f"https://{RAPIDAPI_HOST}/v1/stock/financial-data",
            headers=headers,
            params={"symbol": symbol},
            timeout=10,
        ).json()
        fin_data = fin.get("quoteSummary", {}).get("result", [{}])[0].get("financialData", {})

        # --- 3️⃣ Statistics (valuation ratios)
        stat = requests.get(
            f"https://{RAPIDAPI_HOST}/v1/stock/statistics",
            headers=headers,
            params={"symbol": symbol},
            timeout=10,
        ).json()
        stat_data = stat.get("quoteSummary", {}).get("result", [{}])[0].get("defaultKeyStatistics", {})

        # --- ✅ Merge everything ---
        return {
            "symbol": symbol,
            "info": {
                "shortName": profile_data.get("longBusinessSummary"),
                "sector": profile_data.get("sector"),
                "industry": profile_data.get("industry"),
                "country": profile_data.get("country"),
                "marketCap": fin_data.get("marketCap", {}).get("raw"),
                "trailingPE": stat_data.get("trailingPE", {}).get("raw"),
                "forwardPE": stat_data.get("forwardPE", {}).get("raw"),
                "priceToBook": stat_data.get("priceToBook", {}).get("raw"),
                "dividendYield": fin_data.get("dividendYield", {}).get("raw"),
                "beta": stat_data.get("beta", {}).get("raw"),
            },
            "quote": {
                "currentPrice": fin_data.get("currentPrice", {}).get("raw"),
                "targetMeanPrice": fin_data.get("targetMeanPrice", {}).get("raw"),
                "recommendationMean": fin_data.get("recommendationMean", {}).get("raw"),
            },
            "source": "yh-finance-rapidapi-basic"
        }

    except Exception as e:
        print(f"⚠️  YH Finance fetch failed for {symbol}: {e}")
        return {}


# =====================================================================
# 🧩 Main Aggregator (Redis-cached)
# =====================================================================
def fetch_stock_financials(symbol: str, force_refresh: bool = False) -> dict:
    """
    Robust hybrid financial fetcher combining Finnhub, TwelveData, FMP, yfinance, and YH Finance.
    Cached in Redis for 24h (from CacheManager presets).
    """
    symbol = symbol.upper()
    cache_key = CacheManager.make_key("stocks", symbol)

    # --- Cache logic ---
    if not force_refresh:
        cached = CacheManager.get(cache_key)
        if cached:
            print(f"💾  Loaded {symbol} from Redis cache.")
            try:
                return json.loads(cached)
            except Exception:
                pass
    else:
        print(f"🔄  Force-refreshing {symbol} cache...")

    # --- Fetch fresh data ---
    merged = {
        "symbol": symbol,
        "info": {},
        "quote": {},
        "analyst_data": None,
        "financials": {},
        "dividends": {},
        "sources": {},
    }

    # ------------------------------
    # 1️⃣ Finnhub — Profile / Quote / Metrics / Recommendations
    # ------------------------------
    if FINNHUB_KEY:
        profile = safe_get(f"{FINNHUB}/stock/profile2", {"symbol": symbol, "token": FINNHUB_KEY}, "Finnhub profile")
        quote = safe_get(f"{FINNHUB}/quote", {"symbol": symbol, "token": FINNHUB_KEY}, "Finnhub quote")
        metrics = safe_get(f"{FINNHUB}/stock/metric", {"symbol": symbol, "token": FINNHUB_KEY}, "Finnhub metrics")
        recs = safe_get(f"{FINNHUB}/stock/recommendation", {"symbol": symbol, "token": FINNHUB_KEY}, "Finnhub recs")

        if profile:
            merged["info"].update({
                "shortName": profile.get("name"),
                "sector": profile.get("finnhubIndustry"),
                "country": profile.get("country"),
                "currency": profile.get("currency"),
            })
            merged["sources"]["profile"] = "finnhub"

        if metrics:
            m = metrics.get("metric", {})
            merged["info"].update({
                "marketCap": m.get("marketCapitalization"),
                "trailingPE": m.get("peBasicExclExtraTTM"),
                "priceToBook": m.get("pbAnnual"),
                "roe": m.get("roeTTM"),
                "grossMargin": m.get("grossMarginTTM"),
            })
            merged["sources"]["metrics"] = "finnhub"

        if quote:
            merged["quote"] = quote
            merged["sources"]["quote"] = "finnhub"

        if recs:
            merged["analyst_data"] = recs
            merged["sources"]["analyst_data"] = "finnhub"
    else:
        print("⚠️  FINNHUB_API_KEY missing — skipping Finnhub block")

    # ------------------------------
    # 2️⃣ TwelveData — fallback for quote
    # ------------------------------
    if TWELVE_KEY:
        td_quote = safe_get(f"{TWELVE}/quote", {"symbol": symbol, "apikey": TWELVE_KEY}, "TwelveData quote")
        if td_quote and not merged["quote"]:
            merged["quote"] = td_quote
            merged["sources"]["quote"] = "twelvedata"
    else:
        print("⚠️  TWELVE_API_KEY missing — skipping TwelveData block")

    # ------------------------------
    # 3️⃣ FMP — supplemental ratios + financials
    # ------------------------------
    if FMP_KEY:
        fmp_ratios = safe_get(f"{FMP}/ratios/{symbol}", {"apikey": FMP_KEY}, "FMP ratios")
        if fmp_ratios and isinstance(fmp_ratios, list):
            latest = fmp_ratios[0]
            merged["info"].update({
                "priceToSales": latest.get("priceToSalesRatio"),
                "debtToEquity": latest.get("debtEquityRatio"),
                "dividendYield": latest.get("dividendYield"),
            })
            merged["sources"]["ratios"] = "fmp"

        fmp_income = safe_get(f"{FMP}/income-statement/{symbol}", {"limit": 1, "apikey": FMP_KEY}, "FMP income")
        if fmp_income and isinstance(fmp_income, list):
            merged["financials"]["income_statement"] = fmp_income[0]
            merged["sources"]["financials"] = "fmp"
    else:
        print("⚠️  FMPSDK_API_KEY missing — skipping FMP block")

    # ------------------------------
    # 4️⃣ yfinance — dividends fallback
    # ------------------------------
    try:
        ticker = yf.Ticker(symbol)
        divs = getattr(ticker, "dividends", None)
        if divs is not None and hasattr(divs, "tail"):
            dividends = divs.tail(10).to_dict()
            if dividends:
                merged["dividends"] = dividends
                merged["sources"]["dividends"] = "yfinance"
    except Exception as e:
        print(f"⚠️  yfinance failed for {symbol}: {e}")

    # ------------------------------
    # 5️⃣ YH Finance (RapidAPI) — final fallback
    # ------------------------------
    yahoo_summary = fetch_yahoo_summary(symbol)
    if yahoo_summary:
        merged["info"].update(yahoo_summary.get("info", {}))
        merged["quote"].update(yahoo_summary.get("quote", {}))
        merged["financials"].update(yahoo_summary.get("financials", {}))
        merged["sources"]["yahoo"] = "rapidapi"

    # ------------------------------
    # ✅ Final summary
    # ------------------------------
    filled_fields = sum(1 for v in merged["info"].values() if v)
    print(f"✅  {symbol}: fetched with {filled_fields} info fields filled.")

    # --- Save in Redis ---
    CacheManager.set(cache_key, json.dumps(merged))
    return merged
