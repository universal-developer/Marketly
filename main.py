import datetime
import os
from dotenv import load_dotenv, find_dotenv
import yfinance as yf
from eventregistry import *

# --- Load API keys ---
load_dotenv(find_dotenv())
NEWS_API_KEY = os.getenv("EVENT_REGISTERY_API_KEY")

# Initialize Event Registry client
er = EventRegistry(apiKey=NEWS_API_KEY, allowUseOfArchive=False)


# --- Helper functions ---

def get_instrument_metadata(symbol: str):
    """
    Fetch metadata for a single instrument (ticker).
    """
    instrument = yf.Ticker(symbol)
    metadata = [instrument.info]
    return metadata


def get_news(symbol: str, days: int = 3, max_items: int = 8):
    """
    Fetch news for a single company based on its ticker symbol.
    """
    instrument = yf.Ticker(symbol)
    info = instrument.info or {}

    company_name = info.get("shortName") or \
        info.get("longName") or \
        info.get("displayName") or \
        symbol

    company_uri = er.getConceptUri(company_name)

    query = {
        "$query": {
            "$and": [
                {"conceptUri": company_uri},   # disambiguated company concept
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

    return articles


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


def get_news_combined(symbols, max_items=50, days=7):
    """
    Returns a combined list of articles across ALL symbols.
    """

    # Step 1 — normalize input
    symbols_clean = normalize_symbols(symbols)

    if not symbols_clean:
        return []
    print("Symbols:", symbols_clean)

    # Step 2 — get ticker objects
    tickers = [yf.Ticker(symbol) for symbol in symbols_clean]

    # Step 3 — resolve company names
    company_names = []

    for ticker in tickers:
        info = ticker.info or {}
        company_name = info.get("shortName") or \
            info.get("longName") or \
            info.get("displayName")

        if company_name:
            company_names.append(company_name)

    print("Company names:", company_names)

    # Step 4 — map names to concept URIs
    concept_uris = []

    for name in company_names:
        uri = er.getConceptUri(name)
        if uri:
            concept_uris.append(uri)

    print("Concept URIs:", concept_uris)

    # Step 5 — (TODO) Fetch articles for all concept URIs

    query = {
        "$query": {
            "$and": [
                {"conceptUri": concept_uris},   # disambiguated company concept
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

    return articles
    print(articles)


# --- Run example ---
get_news_combined(input("Enter tickers (e.g., AAPL, NVDA): "))
