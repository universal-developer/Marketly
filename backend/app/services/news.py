import os
import json
import datetime
import yfinance as yf
import finnhub
from dotenv import load_dotenv, find_dotenv
from fastapi.encoders import jsonable_encoder
from app.services.utils import tickers_to_concept_uris

# --- Load API keys ---
load_dotenv(find_dotenv())
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")  # match .env key name exactly
finnhub_client = finnhub.Client(
    api_key=FINNHUB_API_KEY)


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
        # show first 2 articles
        print(">>> RAW RESPONSE:", symbol, articles[:2])

    return articles


def get_news_grouped(symbols, max_items: int = 50, days: int = 30, output_file: str | None = None):
    date_start = (datetime.date.today() -
                  datetime.timedelta(days=days)).isoformat()
    date_end = datetime.date.today().isoformat()

    if isinstance(symbols, str):
        symbols = [s.strip().upper() for s in symbols.split(",")]

    grouped = {}

    for symbol in symbols:
        articles = finnhub_client.company_news(
            symbol, _from=date_start, to=date_end)
        print(f"{symbol}: {len(articles)} articles")
        print(f"{symbol}: type={type(articles)}, sample={articles[:1]}")

        if max_items:
            articles = articles[:max_items]

        grouped[symbol] = articles

    # print(grouped)
    return grouped


def get_news_mixed(symbols, max_items: int = 10, days: int = 3, output_file: str | None = None):
    """
    Returns a combined list of articles across ALL symbols.
    Optionally saves results to a JSON file if output_file is provided.
    """
    date_start = (datetime.date.today() -
                  datetime.timedelta(days=days)).isoformat()
    date_end = datetime.date.today().isoformat()

    if isinstance(symbols, str):
        symbols = [s.strip().upper() for s in symbols.split(",")]

    mixed_articles = []

    for symbol in symbols:
        articles = finnhub_client.company_news(
            symbol, _from=date_start, to=date_end)
        if max_items:
            articles = articles[:max_items]
        mixed_articles.extend(articles)

    mixed_articles.sort(key=lambda x: x['datetime'])

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(mixed_articles, f, ensure_ascii=False, indent=2)
        print(f"✅ Saved {len(mixed_articles)} articles → {output_file}")

    return mixed_articles
