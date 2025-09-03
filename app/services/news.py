import json
import yfinance as yf
from eventregistry import EventRegistry, QueryArticlesIter
from dotenv import load_dotenv, find_dotenv
import os
from app.services.utils import tickers_to_concept_uris

# --- Load API keys ---
load_dotenv(find_dotenv())
NEWS_API_KEY = os.getenv("EVENT_REGISTERY_API_KEY")

# Initialize Event Registry client
er = EventRegistry(apiKey=NEWS_API_KEY, allowUseOfArchive=False)


def get_news(symbol: str, days: int = 3, max_items: int = 8, output_file: str | None = None):
    """
    Fetch news for a single company based on its ticker symbol.
    Optionally saves results to a JSON file if output_file is provided.
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
                {"conceptUri": company_uri},
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

    # Save results if requested
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        print(
            f"✅ Saved {len(articles)} articles for {company_name} → {output_file}")

    return articles


"""def get_news_grouped(symbols, max_items: int = 50, days: int = 7, output_file: str | None = None):
    
Returns a dict of articles grouped by company name.
Optionally saves results to a JSON file if output_file is provided.

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
            "$filter": {"forceMaxDataTimeWindow": str(days)}
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

    # Save results if requested
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(grouped_articles, f, ensure_ascii=False, indent=2)
        print(f"✅ Saved grouped articles to {output_file}")

    return grouped_articles"""


def get_news_grouped(symbols, max_items: int = 50, days: int = 7, output_file: str | None = None):
    """
    Returns a dict of articles grouped by company name.
    Optionally saves results to a JSON file if output_file is provided.
    """
    company_names, concept_uris = tickers_to_concept_uris(symbols)

    grouped_articles = {}

    for name, concept_uri in zip(company_names, concept_uris):
        if not concept_uri:
            print(f"⚠️ Skipping {name}, no conceptUri found")
            continue

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
            "$filter": {"forceMaxDataTimeWindow": str(days)}
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

    # Save results if requested
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(grouped_articles, f, ensure_ascii=False, indent=2)
        print(f"✅ Saved grouped articles to {output_file}")

    return grouped_articles


def get_news_mixed(symbols, max_items: int = 10, days: int = 3, output_file: str | None = None):
    """
    Returns a combined list of articles across ALL symbols.
    Optionally saves results to a JSON file if output_file is provided.
    """
    _, concept_uris = tickers_to_concept_uris(symbols)

    query = {
        "$query": {
            "$and": [
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
        "$filter": {"forceMaxDataTimeWindow": str(days)}
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

    # Save results if requested
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        print(f"✅ Saved mixed articles to {output_file}")

    return articles
