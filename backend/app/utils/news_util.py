import yfinance as yf
from eventregistry import EventRegistry
import os
from dotenv import load_dotenv, find_dotenv
import pandas as pd


load_dotenv(find_dotenv())
NEWS_API_KEY = os.getenv("EVENT_REGISTERY_API_KEY")
er = EventRegistry(apiKey=NEWS_API_KEY, allowUseOfArchive=False)


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

    tickers = [yf.Ticker(symbol) for symbol in symbols_clean]

    company_names, concept_uris = [], []

    for ticker in tickers:
        info = ticker.info or {}
        # ✅ Always fallback to ticker symbol if no names
        company_name = (
            info.get("shortName")
            or info.get("longName")
            or info.get("displayName")
            or ticker.ticker
        )
        company_names.append(company_name)

        # Map to Event Registry concept
        uri = er.getConceptUri(company_name)
        if not uri:
            print(
                f"⚠️ Could not resolve EventRegistry concept for '{company_name}'")
        concept_uris.append(uri)

    # Filter out None values so queries don’t break
    company_names = [n for n, u in zip(company_names, concept_uris) if u]
    concept_uris = [u for u in concept_uris if u]

    return company_names, concept_uris
