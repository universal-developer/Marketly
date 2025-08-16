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


def get_news(symbol: str, days: int = 3, max_items: int = 8):
    instrument = yf.Ticker(symbol)
    info = instrument.info or {}
    company_name = info.get("shortName") or info.get(
        "longName") or info.get("displayName") or symbol

    company_uri = er.getConceptUri(company_name)

    finance_sources = ["Reuters", "Bloomberg", "CNBC",
                       "Yahoo Finance", "Financial Times", "The Wall Street Journal"]
    source_uris = [er.getSourceUri(s)
                   for s in finance_sources if er.getSourceUri(s)]

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    date_end = now_utc.date().isoformat()
    date_start = (now_utc - datetime.timedelta(days=days)).date().isoformat()

    q = QueryArticlesIter(
        conceptUri=company_uri,
        lang=["eng"],
        isDuplicateFilter="skipDuplicates",
        startSourceRankPercentile=70,
        endSourceRankPercentile=100,
        sourceUri=QueryItems.OR(source_uris) if source_uris else None,
        dateStart=date_start,
        dateEnd=date_end,
        keywordsLoc="title"   # <-- corrected
    )

    retinfo = ReturnInfo(articleInfo=ArticleInfoFlags(
        concepts=False, categories=False, location=False, image=True
    ))

    articles = []
    for article in q.execQuery(er, sortBy="date", sortByAsc=False, returnInfo=retinfo, maxItems=max_items):
        articles.append({
            "title": article.get("title"),
            "url": article.get("url"),
            "source": article.get("source", {}).get("title"),
            "dateTime": article.get("dateTime"),
            "image": article.get("image"),
            "body": article.get("body")
        })
    return articles


print(get_news("AAPL"))
