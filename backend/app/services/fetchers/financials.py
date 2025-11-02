import yfinance as yf
import datetime
import math
import time
from app.utils.sanitizer_util import sanitize




def fetch_stock_financials(symbol: str) -> dict:
    """
    Fetch a clean, GPT-ready financial profile for a company.
    Includes only essential fundamentals, valuation ratios,
    analyst sentiment, and limited historical context.
    Automatically retries if Yahoo Finance returns empty or fails.
    """

    max_retries = 3

    # --- Helper to trim long time series ---
    def trim_dict(d: dict, n=7):
        if not isinstance(d, dict):
            return d
        items = list(d.items())
        return dict(items[:n])  # Yahoo lists most recent first

    for attempt in range(max_retries):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.get_info()

            # if info is empty, Yahoo is likely down — retry
            if not info:
                print(f"[WARN] Empty data from Yahoo for {symbol}, retry {attempt + 1}/{max_retries}")
                time.sleep(2 ** attempt)
                continue

            # --- Basics / Valuation ---
            info_filtered = {
                k: info.get(k)
                for k in [
                    "shortName", "sector", "industry", "country", "currency",
                    "marketCap", "sharesOutstanding",
                    "trailingPE", "forwardPE", "pegRatio",
                    "priceToBook", "priceToSalesTrailing12Months",
                    "dividendYield", "payoutRatio", "beta"
                ]
            }

            stock_data = {
                "symbol": symbol,
                "info": info_filtered,
                "isin": ticker.get_isin(),
                "calendar": ticker.get_calendar(),
            }

            # --- Income Statement (trimmed) ---
            income_annual = trim_dict(ticker.get_income_stmt(as_dict=True, freq="yearly"))
            income_quarter = trim_dict(ticker.get_income_stmt(as_dict=True, freq="quarterly"), 8)

            income_filtered = {
                "annual": {
                    date: {k: v for k, v in row.items() if k in [
                        "TotalRevenue", "GrossProfit", "OperatingIncome", "NetIncome",
                        "EBIT", "EBITDA", "BasicEPS", "DilutedEPS"
                    ]}
                    for date, row in income_annual.items()
                },
                "quarterly": {
                    date: {k: v for k, v in row.items() if k in [
                        "TotalRevenue", "GrossProfit", "OperatingIncome", "NetIncome",
                        "EBIT", "EBITDA", "BasicEPS", "DilutedEPS"
                    ]}
                    for date, row in income_quarter.items()
                },
            }

            # --- Balance Sheet (trimmed) ---
            balance_annual = trim_dict(ticker.get_balance_sheet(as_dict=True, freq="yearly"))
            balance_quarter = trim_dict(ticker.get_balance_sheet(as_dict=True, freq="quarterly"), 8)

            balance_filtered = {
                "annual": {
                    date: {k: v for k, v in row.items() if k in [
                        "TotalAssets", "TotalLiabilitiesNetMinorityInterest",
                        "TotalEquityGrossMinorityInterest", "CashAndCashEquivalents",
                        "CurrentAssets", "CurrentLiabilities",
                        "ShortTermDebt", "LongTermDebt"
                    ]}
                    for date, row in balance_annual.items()
                },
                "quarterly": {
                    date: {k: v for k, v in row.items() if k in [
                        "TotalAssets", "TotalLiabilitiesNetMinorityInterest",
                        "TotalEquityGrossMinorityInterest", "CashAndCashEquivalents",
                        "CurrentAssets", "CurrentLiabilities",
                        "ShortTermDebt", "LongTermDebt"
                    ]}
                    for date, row in balance_quarter.items()
                },
            }

            # --- Cash Flow (trimmed) ---
            cash_annual = trim_dict(ticker.get_cash_flow(as_dict=True, freq="yearly"))
            cash_quarter = trim_dict(ticker.get_cash_flow(as_dict=True, freq="quarterly"), 8)

            cash_filtered = {
                "annual": {
                    date: {k: v for k, v in row.items() if k in [
                        "OperatingCashFlow", "FreeCashFlow",
                        "CapitalExpenditures", "DepreciationAndAmortization"
                    ]}
                    for date, row in cash_annual.items()
                },
                "quarterly": {
                    date: {k: v for k, v in row.items() if k in [
                        "OperatingCashFlow", "FreeCashFlow",
                        "CapitalExpenditures", "DepreciationAndAmortization"
                    ]}
                    for date, row in cash_quarter.items()
                },
            }

            # --- Analyst / Sentiment Data ---
            analyst_data = {
                "recommendations_summary": ticker.get_recommendations_summary(as_dict=True),
                "price_targets": ticker.get_analyst_price_targets(),
                "growth_estimates": ticker.get_growth_estimates(as_dict=True),
                "earnings_estimate": ticker.get_earnings_estimate(as_dict=True),
            }

            # --- Insider sentiment (optional) ---
            insider_tx = ticker.get_insider_transactions(as_dict=True)
            if isinstance(insider_tx, list):
                insider_tx = insider_tx[:10]  # limit to 10 latest

            # --- Dividends (5y) ---
            dividends = ticker.get_dividends(period="5y").to_dict()

            # --- Assemble final clean dict ---
            stock_data.update({
                "income_statement": income_filtered,
                "balance_sheet": balance_filtered,
                "cash_flow": cash_filtered,
                "analyst_data": analyst_data,
                "insider_transactions": insider_tx,
                "dividends": dividends,
            })

            return sanitize(stock_data)

        except Exception as e:
            print(f"[ERROR] Yahoo fetch failed for {symbol} (attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(2 ** attempt)

    # --- If all retries failed ---
    print(f"[ERROR] Yahoo consistently failed for {symbol} after {max_retries} retries.")
    return {"symbol": symbol, "error": "Yahoo Finance unavailable"}

def summarize_financials(stock_data: dict) -> dict:
    """
    Lightweight summary of essential financial metrics for GPT analysis and dashboards.
    Keeps only the most recent and meaningful values for fast AI scoring and display.
    """

    try:
        def latest(d: dict, key: str):
            """Safely get the most recent entry from annual/quarterly data."""
            section = d.get(key, {})
            if not section or not isinstance(section, dict):
                return None
            return next(iter(section.values()), None)

        info = stock_data.get("info", {})
        income = stock_data.get("income_statement", {})
        balance = stock_data.get("balance_sheet", {})
        cash_flow = stock_data.get("cash_flow", {})
        analyst = stock_data.get("analyst_data", {})

        summary = {
            "symbol": stock_data.get("symbol"),
            "company": {
                "name": info.get("shortName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "country": info.get("country"),
                "currency": info.get("currency"),
                "market_cap": info.get("marketCap"),
            },
            "valuation": { 
                "trailing_pe": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
                "price_to_book": info.get("priceToBook"),
                "price_to_sales": info.get("priceToSalesTrailing12Months"),
                "dividend_yield": info.get("dividendYield"),
                "beta": info.get("beta"),
            },
            "income_statement": {
                "ttm": income.get("ttm"),
                "latest_annual": latest(income, "annual"),
                "latest_quarter": latest(income, "quarterly"),
            },
            "balance_sheet": {
                "latest_annual": latest(balance, "annual"),
                "latest_quarter": latest(balance, "quarterly"),
            },
            "cash_flow": {
                "latest_annual": latest(cash_flow, "annual"),
                "latest_quarter": latest(cash_flow, "quarterly"),
            },
            "balance_summary": {
                "total_assets": (latest(balance, "annual") or {}).get("TotalAssets"),
                "total_liabilities": (latest(balance, "annual") or {}).get("TotalLiabilitiesNetMinorityInterest"),
                "cash": (latest(balance, "annual") or {}).get("CashAndCashEquivalents"),
                "debt": (
                    ((latest(balance, "annual") or {}).get("ShortTermDebt") or 0)
                    + ((latest(balance, "annual") or {}).get("LongTermDebt") or 0)
                ),
            },
            "analyst_data": {
                "recommendations_summary": analyst.get("recommendations_summary"),
                "price_targets": analyst.get("price_targets"),
                "earnings_estimate": analyst.get("earnings_estimate"),
                "growth_estimates": analyst.get("growth_estimates"),
            },
        }

        return summary

    except Exception as e:
        return {"error": str(e)}
