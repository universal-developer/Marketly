import pandas as pd

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


def map_exchange(info: dict) -> str:
    yf_code, full_name = info.get("exchange"), info.get("fullExchangeName")
    if yf_code in YF_TO_FMP_EXCHANGE:
        return YF_TO_FMP_EXCHANGE[yf_code]
    if full_name in YF_TO_FMP_EXCHANGE:
        return YF_TO_FMP_EXCHANGE[full_name]
    return "UNKNOWN"
