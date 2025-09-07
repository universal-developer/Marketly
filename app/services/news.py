import os
import json
import datetime
import yfinance as yf
import finnhub
from dotenv import load_dotenv, find_dotenv
from app.services.utils import tickers_to_concept_uris

# --- Load API keys ---
load_dotenv(find_dotenv())
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")  # match .env key name exactly
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)


def get_news(symbol: str, days: int = 3, max_items: int = 8, output_file: str | None = None):
    """
    Fetch news for a single company based on its ticker symbol using Finnhub.
    Optionally saves results to a JSON file if output_file is provided.
    """
    date_start = (datetime.date.today() -
                  datetime.timedelta(days=days)).isoformat()
    date_end = datetime.date.today().isoformat()

    articles = finnhub_client.company_news(
        symbol, _from=date_start, to=date_end)

    if max_items:
        articles = articles[:max_items]

    # Save results if requested
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        print(f"✅ Saved {len(articles)} articles for {symbol} → {output_file}")

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
    """
    Fetch grouped news for multiple tickers.
    Returns a dict: { "AAPL": [...articles], "NVDA": [...articles] }
    """
    if isinstance(symbols, str):
        symbols = [s.strip().upper() for s in symbols.split(",")]

    grouped = {}
    for symbol in symbols:
        url = f"{BASE_URL}/news/stock"
        params = {
            "symbols": symbol,
            "limit": limit,
            "from": date_start,
            "to": date_end,
            "apikey": FMP_API_KEY,
        }
        r = requests.get(url, params=params)
        r.raise_for_status()
        grouped[symbol] = r.json()

    return grouped


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
