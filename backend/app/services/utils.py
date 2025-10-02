import yfinance as yf
from eventregistry import EventRegistry
import os
from dotenv import load_dotenv, find_dotenv
import math
import datetime
import pandas as pd


load_dotenv(find_dotenv())
NEWS_API_KEY = os.getenv("EVENT_REGISTERY_API_KEY")
er = EventRegistry(apiKey=NEWS_API_KEY, allowUseOfArchive=False)

YF_TO_FMP_EXCHANGE = {
    "NMS": "NASDAQ", "NasdaqGS": "NASDAQ", "NasdaqCM": "NASDAQ", "NasdaqGM": "NASDAQ",
    "NYQ": "NYSE", "NYE": "NYSE", "ASE": "AMEX", "PCX": "NYSEARCA", "BATS": "BATS",
    "TOR": "TSX", "VAN": "TSXV",
    "PAR": "EURONEXT", "AMS": "EURONEXT", "BRU": "EURONEXT", "LIS": "EURONEXT", "OSL": "OSLO",
    "LSE": "LSE", "IOB": "LSE",
    "GER": "XETRA", "FRA": "FRA",
    "SWX": "SIX",
    "JPX": "JPX", "TSE": "TSE",
    "HKG": "HKEX", "SHH": "SSE", "SHZ": "SZSE",
    "BSE": "BSE", "NSE": "NSE",
    "ASX": "ASX", "NZX": "NZX",
    "MIL": "MILAN", "MAD": "BME", "SAO": "B3", "JNB": "JSE"
}


def normalize_symbols(symbols):
    if isinstance(symbols, list):
        return [s.strip().upper() for s in symbols]
    if isinstance(symbols, str):
        parts = symbols.split(",") if "," in symbols else symbols.split()
        return [p.strip().upper() for p in parts]
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


def map_exchange(info: dict) -> str:
    yf_code, full_name = info.get("exchange"), info.get("fullExchangeName")
    if yf_code in YF_TO_FMP_EXCHANGE:
        return YF_TO_FMP_EXCHANGE[yf_code]
    if full_name in YF_TO_FMP_EXCHANGE:
        return YF_TO_FMP_EXCHANGE[full_name]
    return "UNKNOWN"


def sanitize(obj):
    """Recursively clean data for JSON serialization (NaN, Inf, Timestamps, Dates)."""
    if isinstance(obj, dict):
        clean = {}
        for k, v in obj.items():
            # ensure key is string
            if isinstance(k, (datetime.date, datetime.datetime, pd.Timestamp)):
                k = k.isoformat()
            else:
                k = str(k)
            clean[k] = sanitize(v)
        return clean

    elif isinstance(obj, (list, tuple)):
        return [sanitize(v) for v in obj]

    elif isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None

    elif isinstance(obj, (datetime.date, datetime.datetime, pd.Timestamp)):
        return obj.isoformat()

    return obj
