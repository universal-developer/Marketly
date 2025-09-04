import yfinance as yf
import datetime
import math


def sanitize(obj):
    """Recursively replace NaN/Inf with None for JSON safety."""
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize(v) for v in obj]
    elif isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    return obj


def fetch_stock_financials(symbol: str) -> dict:
    try:
        ticker = yf.Ticker(symbol)
        stock_data = {"symbol": symbol}

        # --- Basics ---
        stock_data["info"] = ticker.get_info()
        stock_data["calendar"] = ticker.get_calendar()
        stock_data["isin"] = ticker.get_isin()

        # --- Financials ---
        stock_data["income_statement"] = {
            "annual": ticker.get_income_stmt(as_dict=True, freq="yearly"),
            "quarterly": ticker.get_income_stmt(as_dict=True, freq="quarterly"),
            "ttm": ticker.get_income_stmt(as_dict=True, freq="trailing"),
        }
        stock_data["balance_sheet"] = {
            "annual": ticker.get_balance_sheet(as_dict=True, freq="yearly"),
            "quarterly": ticker.get_balance_sheet(as_dict=True, freq="quarterly"),
        }
        stock_data["cash_flow"] = {
            "annual": ticker.get_cash_flow(as_dict=True, freq="yearly"),
            "quarterly": ticker.get_cash_flow(as_dict=True, freq="quarterly"),
            # "ttm": ticker.get_ttm_cash_flow(as_dict=True),
        }

        # --- Dividends, Splits, Actions ---
        stock_data["dividends"] = ticker.get_dividends(period="max").to_dict()
        stock_data["splits"] = ticker.get_splits(period="max").to_dict()
        stock_data["actions"] = ticker.get_actions(period="max").to_dict()

        # --- Earnings ---
        stock_data["earnings_dates"] = (
            ticker.get_earnings_dates(limit=12).to_dict()
            if ticker.get_earnings_dates(limit=12) is not None
            else {}
        )
        stock_data["earnings_estimate"] = ticker.get_earnings_estimate(
            as_dict=True)
        stock_data["earnings_history"] = ticker.get_earnings_history(
            as_dict=True)
        stock_data["eps_trend"] = ticker.get_eps_trend(as_dict=True)
        stock_data["eps_revisions"] = ticker.get_eps_revisions(as_dict=True)

        # --- Holders & Insiders ---
        stock_data["institutional_holders"] = ticker.get_institutional_holders(
            as_dict=True)
        stock_data["mutualfund_holders"] = ticker.get_mutualfund_holders(
            as_dict=True)
        stock_data["major_holders"] = ticker.get_major_holders(as_dict=True)
        stock_data["insider_transactions"] = ticker.get_insider_transactions(
            as_dict=True)
        stock_data["insider_roster"] = ticker.get_insider_roster_holders(
            as_dict=True)
        stock_data["insider_purchases"] = ticker.get_insider_purchases(
            as_dict=True)

        # --- Recommendations & Ratings ---
        stock_data["recommendations"] = ticker.get_recommendations(
            as_dict=True)
        stock_data["recommendations_summary"] = ticker.get_recommendations_summary(
            as_dict=True)
        stock_data["upgrades_downgrades"] = ticker.get_upgrades_downgrades(
            as_dict=True)
        stock_data["analyst_price_targets"] = ticker.get_analyst_price_targets()

        # --- Estimates & Growth ---
        stock_data["revenue_estimate"] = ticker.get_revenue_estimate(
            as_dict=True)
        stock_data["growth_estimates"] = ticker.get_growth_estimates(
            as_dict=True)

        # --- SEC & Sustainability ---
        stock_data["sec_filings"] = ticker.get_sec_filings()
        stock_data["sustainability"] = ticker.get_sustainability(as_dict=True)

        # --- News ---
        stock_data["news"] = ticker.get_news(count=10, tab="all")

        return sanitize(stock_data)

    except Exception as e:
        return {"symbol": symbol, "error": str(e)}
