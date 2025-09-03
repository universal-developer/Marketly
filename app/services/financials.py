import fmpsdk
import datetime
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
FINANCIALS_API_KEY = os.getenv("FMPSDK_API_KEY")


def fetch_stock_financials(symbol: str) -> dict:
    try:
        stock_data = {
            "symbol": symbol,
            "profile": fmpsdk.company_profile(apikey=FINANCIALS_API_KEY, symbol=symbol),
            "quote": fmpsdk.quote(apikey=FINANCIALS_API_KEY, symbol=symbol),
            "executives": fmpsdk.key_executives(apikey=FINANCIALS_API_KEY, symbol=symbol),
            "income_statement": {
                "annual": fmpsdk.income_statement(apikey=FINANCIALS_API_KEY, symbol=symbol, period="annual"),
                "quarterly": fmpsdk.income_statement(apikey=FINANCIALS_API_KEY, symbol=symbol, period="quarter"),
            },
            "balance_sheet": fmpsdk.balance_sheet_statement(apikey=FINANCIALS_API_KEY, symbol=symbol, period="quarter"),
            "cash_flow": fmpsdk.cash_flow_statement(apikey=FINANCIALS_API_KEY, symbol=symbol, period="quarter"),
            "ratios": fmpsdk.financial_ratios_ttm(apikey=FINANCIALS_API_KEY, symbol=symbol),
            "key_metrics": fmpsdk.key_metrics_ttm(apikey=FINANCIALS_API_KEY, symbol=symbol),
            "enterprise_values": fmpsdk.enterprise_values(apikey=FINANCIALS_API_KEY, symbol=symbol, period="quarter"),
            "financial_growth": fmpsdk.financial_growth(apikey=FINANCIALS_API_KEY, symbol=symbol, period="annual"),
            "rating": fmpsdk.rating(apikey=FINANCIALS_API_KEY, symbol=symbol),
            "dcf": fmpsdk.discounted_cash_flow(apikey=FINANCIALS_API_KEY, symbol=symbol),
            "institutional_holders": fmpsdk.institutional_holders(apikey=FINANCIALS_API_KEY, symbol=symbol),
            "insider_trading": fmpsdk.insider_trading(apikey=FINANCIALS_API_KEY, symbol=symbol, limit=10),
            "news": fmpsdk.stock_news(apikey=FINANCIALS_API_KEY, tickers=symbol, limit=10),
            "press_releases": fmpsdk.press_releases(apikey=FINANCIALS_API_KEY, symbol=symbol),
            "social_sentiment": fmpsdk.social_sentiments(apikey=FINANCIALS_API_KEY, symbol=symbol),
            "earnings_surprises": fmpsdk.earnings_surprises(apikey=FINANCIALS_API_KEY, symbol=symbol),
            "dividends_history": fmpsdk.historical_stock_dividend(apikey=FINANCIALS_API_KEY, symbol=symbol),
            "splits_history": fmpsdk.historical_stock_split(apikey=FINANCIALS_API_KEY, symbol=symbol),
        }

        upcoming_dividends = fmpsdk.dividend_calendar(
            apikey=FINANCIALS_API_KEY,
            from_date=datetime.date.today().isoformat(),
            to_date=(datetime.date.today() +
                     datetime.timedelta(days=365)).isoformat()
        )
        stock_data["dividends_upcoming"] = [d for d in upcoming_dividends if d.get(
            "symbol") == symbol] if isinstance(upcoming_dividends, list) else []

        upcoming_earnings = fmpsdk.earning_calendar(
            apikey=FINANCIALS_API_KEY,
            from_date=datetime.date.today().isoformat(),
            to_date=(datetime.date.today() +
                     datetime.timedelta(days=365)).isoformat()
        )
        stock_data["earnings_calendar_next"] = [e for e in upcoming_earnings if e.get(
            "symbol") == symbol] if isinstance(upcoming_earnings, list) else []

        return stock_data
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}
