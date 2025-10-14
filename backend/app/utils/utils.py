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
