import datetime
import os
from dotenv import load_dotenv, find_dotenv
import yfinance as yf
from eventregistry import *


load_dotenv(find_dotenv())
NEWS_API_KEY = os.getenv("EVENT_REGISTERY_API_KEY")


er = EventRegistry(apiKey=NEWS_API_KEY, allowUseOfArchive=False)


def get_instrument_metadata(symbol: str):
    instrument = yf.Ticker(symbol)
    metadata = [instrument.info]

    return metadata


def get_news(symbol: list, days: int = 3, max_items: int = 8):
    instrument = yf.Ticker(symbol)
    info = instrument.info or {}
    company_name = info.get("shortName") or info.get(
        "longName") or info.get("displayName") or symbol

    company_uri = er.getConceptUri(company_name)

    query = {
        "$query": {
            "$and": [
                {"conceptUri": company_uri},   # <-- disambiguated Apple Inc.
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
            "forceMaxDataTimeWindow": "7"   # last 7 days
        }
    }

    articles = []

    q = QueryArticlesIter.initWithComplexQuery(query)
    for article in q.execQuery(er, maxItems=20):
        articles.append({
            "title": article.get("title"),
            "url": article.get("url"),
            "source": article.get("source", {}).get("title"),
            "dateTime": article.get("dateTime"),
            "image": article.get("image"),
            "body": article.get("body")
        })

    return articles


def get_news_combined(symbols, max_items=50, days=7):
    """
    Returns a single list of articles across ALL symbols (mixed river).
    """
    symbols_clean = [symbol.strip().upper()
                     for symbol in symbols if symbol.strip()]
    if not symbols_clean:
        return []

    instrument = yf.Ticker(" ".join(symbols_clean))


print(get_news(input("What instruments are you interested in? ")))
