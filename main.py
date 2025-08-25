import datetime
import os
import typing
import yfinance as yf
import fmpsdk
import json
from eventregistry import *
from dotenv import load_dotenv, find_dotenv

# --- Load API keys ---
load_dotenv(find_dotenv())
NEWS_API_KEY = os.getenv("EVENT_REGISTERY_API_KEY")
FINANCIALS_API_KEY = os.getenv("FMPSDK_API_KEY")

# Initialize Event Registry client
er = EventRegistry(apiKey=NEWS_API_KEY, allowUseOfArchive=False)

# --- fmpsdk API consts ---

YF_TO_FMP_EXCHANGE = {
    # --- United States ---
    "NMS": "NASDAQ",          # NASDAQ Stock Market
    "NasdaqGS": "NASDAQ",     # NASDAQ Global Select
    "NasdaqCM": "NASDAQ",     # NASDAQ Capital Market
    "NasdaqGM": "NASDAQ",     # NASDAQ Global Market
    "NYQ": "NYSE",            # New York Stock Exchange
    "NYE": "NYSE",            # NYSE (alt code)
    "ASE": "AMEX",            # American Stock Exchange
    "PCX": "NYSEARCA",        # NYSE Arca (ETFs)
    "BATS": "BATS",           # BATS Global Markets

    # --- Canada ---
    "TOR": "TSX",             # Toronto Stock Exchange
    "VAN": "TSXV",            # TSX Venture Exchange

    # --- Europe: Euronext (multi-country) ---
    "PAR": "EURONEXT",        # Euronext Paris
    "AMS": "EURONEXT",        # Euronext Amsterdam
    "BRU": "EURONEXT",        # Euronext Brussels
    "LIS": "EURONEXT",        # Euronext Lisbon
    "OSL": "OSLO",            # Oslo Børs (Euronext-owned)

    # --- United Kingdom ---
    "LSE": "LSE",             # London Stock Exchange
    "IOB": "LSE",             # London Intl Order Book

    # --- Germany ---
    "GER": "XETRA",           # Deutsche Börse XETRA
    "FRA": "FRA",             # Frankfurt Stock Exchange

    # --- Switzerland ---
    "SWX": "SIX",             # SIX Swiss Exchange

    # --- Asia: Japan ---
    "JPX": "JPX",             # Japan Exchange Group
    "TSE": "TSE",             # Tokyo Stock Exchange

    # --- Asia: Hong Kong / China ---
    "HKG": "HKEX",            # Hong Kong Stock Exchange
    "SHH": "SSE",             # Shanghai Stock Exchange
    "SHZ": "SZSE",            # Shenzhen Stock Exchange

    # --- Asia: India ---
    "BSE": "BSE",             # Bombay Stock Exchange
    "NSE": "NSE",             # National Stock Exchange of India

    # --- Australia & Oceania ---
    "ASX": "ASX",             # Australian Securities Exchange
    "NZX": "NZX",             # New Zealand Exchange

    # --- Other ---
    "MIL": "MILAN",           # Borsa Italiana (Milan)
    "MAD": "BME",             # Madrid Stock Exchange (BME)
    "SAO": "B3",              # B3 Brazil
    "JNB": "JSE",             # Johannesburg Stock Exchange
}

time_delta_5min: str = "5min"
time_delta_15min: str = "15min"
time_delta_daily: str = "daily"

# --- Helper functions ---


def normalize_symbols(symbols):
    """
    Normalize user input into a clean list of uppercase ticker symbols.
    Accepts either:
      - A string: "AAPL, NVDA" or "AAPL NVDA"
      - A list: ["AAPL", "NVDA"]
    """
    if isinstance(symbols, list):
        clean = []
        for symbol in symbols:
            clean.append(symbol.strip().upper())
        return clean

    if isinstance(symbols, str):
        if "," in symbols:
            parts = symbols.split(",")
        else:
            parts = symbols.split()
        clean = []
        for part in parts:
            clean.append(part.strip().upper())
        return clean

    raise ValueError("Symbols must be a list or string")


def tickers_to_concept_uris(symbols):
    """
    Given a list/string of symbols, return (company_names, concept_uris).
    Example:
        (["Apple Inc.", "NVIDIA Corporation"],
        ["http://en.wikipedia.org/wiki/Apple_Inc.", "http://en.wikipedia.org/wiki/Nvidia"])
    """
    # Normalize input
    symbols_clean = normalize_symbols(symbols)
    if not symbols_clean:
        return [], []

    # Get ticker objects
    tickers = [yf.Ticker(symbol) for symbol in symbols_clean]

    # Resolve company names
    company_names = []
    for ticker in tickers:
        info = ticker.info or {}
        company_name = info.get("shortName") or \
            info.get("longName") or \
            info.get("displayName")
        if company_name:
            company_names.append(company_name)

    # Map names to concept URIs
    concept_uris = []
    for name in company_names:
        uri = er.getConceptUri(name)
        if uri:
            concept_uris.append(uri)

    return company_names, concept_uris


def map_exchange(info: dict) -> str:
    yf_code = info.get("exchange")
    full_name = info.get("fullExchangeName")

    # Try short code first, then full name
    if yf_code in YF_TO_FMP_EXCHANGE:
        return YF_TO_FMP_EXCHANGE[yf_code]
    if full_name in YF_TO_FMP_EXCHANGE:
        return YF_TO_FMP_EXCHANGE[full_name]

    return "UNKNOWN"


def fetch_stock_financials(symbol: str) -> dict:
    """Fetch essential data for a single stock from FMP."""
    try:
        # --- Core financial data package ---
        stock_data = {
            "symbol": symbol,

            # --- Company basics ---
            "profile": fmpsdk.company_profile(apikey=FINANCIALS_API_KEY, symbol=symbol),
            "quote": fmpsdk.quote(apikey=FINANCIALS_API_KEY, symbol=symbol),
            "executives": fmpsdk.key_executives(apikey=FINANCIALS_API_KEY, symbol=symbol),

            # --- Financials ---
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
            "income_statement_as_reported": fmpsdk.income_statement_as_reported(
                apikey=FINANCIALS_API_KEY, symbol=symbol, period="annual"
            ),

            # --- Valuation & Ratings ---
            "rating": fmpsdk.rating(apikey=FINANCIALS_API_KEY, symbol=symbol),
            "dcf": fmpsdk.discounted_cash_flow(apikey=FINANCIALS_API_KEY, symbol=symbol),

            # --- Ownership ---
            "institutional_holders": fmpsdk.institutional_holders(apikey=FINANCIALS_API_KEY, symbol=symbol),
            "insider_trading": fmpsdk.insider_trading(apikey=FINANCIALS_API_KEY, symbol=symbol, limit=10),

            # --- News & Sentiment ---
            "news": fmpsdk.stock_news(apikey=FINANCIALS_API_KEY, tickers=symbol, limit=10),
            "press_releases": fmpsdk.press_releases(apikey=FINANCIALS_API_KEY, symbol=symbol),
            "social_sentiment": fmpsdk.social_sentiments(apikey=FINANCIALS_API_KEY, symbol=symbol),

            # --- Calendar events ---
            "earnings_surprises": fmpsdk.earnings_surprises(apikey=FINANCIALS_API_KEY, symbol=symbol),
            "dividends_history": fmpsdk.historical_stock_dividend(apikey=FINANCIALS_API_KEY, symbol=symbol),
            "splits_history": fmpsdk.historical_stock_split(apikey=FINANCIALS_API_KEY, symbol=symbol),
        }

        # --- Upcoming dividends (bulk → filter for symbol) ---
        upcoming_dividends = fmpsdk.dividend_calendar(
            apikey=FINANCIALS_API_KEY,
            from_date=datetime.date.today().isoformat(),
            to_date=(datetime.date.today() +
                     datetime.timedelta(days=365)).isoformat()
        )
        if isinstance(upcoming_dividends, list):
            stock_data["dividends_upcoming"] = [
                d for d in upcoming_dividends if d.get("symbol") == symbol]
        else:
            stock_data["dividends_upcoming"] = []

        # --- Upcoming earnings (bulk → filter for symbol) ---
        upcoming_earnings = fmpsdk.earning_calendar(
            apikey=FINANCIALS_API_KEY,
            from_date=datetime.date.today().isoformat(),
            to_date=(datetime.date.today() +
                     datetime.timedelta(days=365)).isoformat()
        )
        if isinstance(upcoming_earnings, list):
            stock_data["earnings_calendar_next"] = [
                e for e in upcoming_earnings if e.get("symbol") == symbol]
        else:
            stock_data["earnings_calendar_next"] = []

        return stock_data

    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return {"symbol": symbol, "error": str(e)}

# --- Get instruments important data ---


def get_instrument_metadata(symbol: str):
    """
    Fetch metadata for a single instrument (ticker).
    """
    instrument = yf.Ticker(symbol)
    metadata = [instrument.info]
    return metadata


def get_instrument_financials(symbol):
    dat = yf.Ticker(symbol)
    print(dat.option_chain(dat.options[0]).calls)
    return dat.option_chain(dat.options[0]).calls

# --- News fetrching functions ---


def get_news(symbol: str, days: int = 3, max_items: int = 8, output_file="single_company_articles.json"):
    """
    Fetch news for a single company based on its ticker symbol.
    Saves results to a JSON file.
    """

    # Resolve company name from Yahoo Finance
    ticker = yf.Ticker(symbol)
    info = ticker.info or {}
    company_name = info.get("shortName") or info.get(
        "longName") or info.get("displayName") or symbol

    # Map to Event Registry concept
    company_uri = er.getConceptUri(company_name)
    if not company_uri:
        print(f"⚠️ Could not resolve concept for {symbol} ({company_name})")
        return []

    query = {
        "$query": {
            "$and": [
                {"conceptUri": company_uri},  # single company concept
                {"lang": "eng"},
                {"$or": [
                    {"sourceUri": "reuters.com"},
                    {"sourceUri": "bloomberg.com"},
                    {"sourceUri": "cnbc.com"},
                    {"sourceUri": "finance.yahoo.com"},
                    {"sourceUri": "wsj.com"},
                    {"sourceUri": "ft.com"}
                ]}
            ]
        },
        "$filter": {"forceMaxDataTimeWindow": str(days)}
    }

    # Collect articles
    articles = []
    q = QueryArticlesIter.initWithComplexQuery(query)

    for article in q.execQuery(er, maxItems=max_items):
        articles.append({
            "company_name": company_name,
            "title": article.get("title"),
            "url": article.get("url"),
            "source": article.get("source", {}).get("title"),
            "dateTime": article.get("dateTime"),
            "image": article.get("image"),
            "body": article.get("body")
        })

    # Save results to JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    print(
        f"✅ Saved {len(articles)} articles for {company_name} → {output_file}")
    return articles


def get_news_grouped(symbols, max_items=50, days=7, output_file="grouped_articles.json"):
    """
    Returns a dict of articles grouped by company name,
    and writes it to a JSON file.
    """
    company_names, concept_uris = tickers_to_concept_uris(symbols)

    grouped_articles = {}

    for name, concept_uri in zip(company_names, concept_uris):
        query = {
            "$query": {
                "$and": [
                    {"conceptUri": concept_uri},
                    {"lang": "eng"},
                    {"$or": [
                        {"sourceUri": "reuters.com"},
                        {"sourceUri": "bloomberg.com"},
                        {"sourceUri": "cnbc.com"},
                        {"sourceUri": "finance.yahoo.com"},
                        {"sourceUri": "wsj.com"},
                        {"sourceUri": "ft.com"}
                    ]}
                ]
            },
            "$filter": {
                "forceMaxDataTimeWindow": str(days)
            }
        }

        company_articles = []
        q = QueryArticlesIter.initWithComplexQuery(query)

        for article in q.execQuery(er, maxItems=max_items):
            company_articles.append({
                "title": article.get("title"),
                "url": article.get("url"),
                "source": article.get("source", {}).get("title"),
                "dateTime": article.get("dateTime"),
                "image": article.get("image"),
                "body": article.get("body")
            })

        grouped_articles[name] = company_articles

    # --- Write output to JSON ---
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(grouped_articles, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved grouped articles to {output_file}")
    return grouped_articles


def get_news_mixed(symbols, max_items=10, days=3):
    """
    Returns a combined list of articles across ALL symbols.
    """

    company_names, concept_uris = tickers_to_concept_uris(symbols)

    # print("Concept URIs:", concept_uris)

    query = {
        "$query": {
            "$and": [
                # disambiguated company concept
                {"conceptUri": {"$or": concept_uris}},
                {"lang": "eng"},
                {"$or": [
                    {"sourceUri": "reuters.com"},
                    {"sourceUri": "bloomberg.com"},
                    {"sourceUri": "cnbc.com"},
                    {"sourceUri": "finance.yahoo.com"},
                    {"sourceUri": "wsj.com"},
                    {"sourceUri": "ft.com"}
                ]}
            ]
        },
        "$filter": {
            "forceMaxDataTimeWindow": str(days)   # e.g., "3" → last 3 days
        }
    }

    articles = []

    q = QueryArticlesIter.initWithComplexQuery(query)

    for article in q.execQuery(er, maxItems=max_items):
        articles.append({
            "title": article.get("title"),
            "url": article.get("url"),
            "source": article.get("source", {}).get("title"),
            "dateTime": article.get("dateTime"),
            "image": article.get("image"),
            "body": article.get("body")
        })

    # --- Write to file ---
    with open("mixed_articles.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    return articles


# --- Run example ---
# get_instrument_financials("AAPL")
fetch_stock_financials("AAPL")
# get_news(input("Enter tickers (e.g., AAPL): "))
# get_news_mixed(input("Enter tickers (e.g., AAPL, NVDA): "))
# get_news_grouped(input("Enter tickers (e.g., AAPL, NVDA): "))
