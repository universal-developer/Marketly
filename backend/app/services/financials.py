import yfinance as yf
import datetime
import math
from app.services.utils import sanitize


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
        stock_data["dividends"] = ticker.get_dividends(period="10y").to_dict()
        stock_data["splits"] = ticker.get_splits(period="10y").to_dict()
        stock_data["actions"] = ticker.get_actions(period="10y").to_dict()

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


def summarize_financials(stock_data: dict) -> dict:
    """
    Summarize and organize financial data for AI analysis.
    Keep only the most meaningful, structured, and human-readable parts.
    """

    try:
        info = stock_data.get("info", {})
        income = stock_data.get("income_statement", {})
        balance = stock_data.get("balance_sheet", {})
        cash_flow = stock_data.get("cash_flow", {})
        recs = stock_data.get("recommendations_summary", {})
        targets = stock_data.get("analyst_price_targets", {})
        earnings = stock_data.get("earnings_estimate", {})
        revenue_est = stock_data.get("revenue_estimate", {})
        growth = stock_data.get("growth_estimates", {})

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
                "dividend_yield": info.get("dividendYield"),
                "beta": info.get("beta"),
            },
            "income_statement": {
                "ttm": income.get("ttm"),
                "latest_annual": next(iter(income.get("annual", {}).values()), None),
                "latest_quarter": next(iter(income.get("quarterly", {}).values()), None),
            },
            "balance_sheet": {
                "latest_annual": next(iter(balance.get("annual", {}).values()), None),
                "latest_quarter": next(iter(balance.get("quarterly", {}).values()), None),
            },
            "cash_flow": {
                "latest_annual": next(iter(cash_flow.get("annual", {}).values()), None),
                "latest_quarter": next(iter(cash_flow.get("quarterly", {}).values()), None),
            },
            "analyst_data": {
                "recommendations_summary": recs,
                "price_targets": targets,
                "earnings_estimate": earnings,
                "revenue_estimate": revenue_est,
                "growth_estimates": growth,
            },
        }

        return sanitize(summary)

    except Exception as e:
        return {"error": str(e)}
