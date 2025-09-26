from fredapi import Fred
import os
import pandas as pd


def fetch_macro_indicators():
    # Lo/*************  ✨ Windsurf Command ⭐  *************/
    """
    Fetch macroeconomic indicators from FRED.

    Returns a Pandas DataFrame with the following columns:
        - GDP (Real)
        - GDP Growth Rate
        - Industrial Production
        - CPI (All Items)
        - Core CPI
        - PPI
        - Unemployment Rate
        - Nonfarm Payrolls
        - Job Openings (JOLTS)
        - Fed Funds Rate
        - 10Y Treasury Yield
        - Yield Curve (10Y-2Y)
        - Trade Balance
        - US Dollar Index

        - Oil Prices
        - Gold Prices
        - Consumer Confidence
        - Leading Index
        - ISM PMI

    Each column is a separate FRED series, aligned by date.
    """

    fred = Fred(api_key=os.getenv("FRED_API_KEY"))

    # Define indicators (FRED codes + labels)
    indicators = {
        "GDP (Real)": "GDPC1",
        "GDP Growth Rate": "A191RL1Q225SBEA",
        "Industrial Production": "INDPRO",
        "CPI (All Items)": "CPIAUCSL",
        "Core CPI": "CPILFESL",
        "PPI": "PPIACO",
        "Unemployment Rate": "UNRATE",
        "Nonfarm Payrolls": "PAYEMS",
        "Job Openings (JOLTS)": "JOLTSJOL",
        "Fed Funds Rate": "FEDFUNDS",
        "10Y Treasury Yield": "DGS10",
        "Yield Curve (10Y-2Y)": "T10Y2Y",
        "Trade Balance": "NETEXP",
        "US Dollar Index": "DTWEXBGS",
        "Oil Prices": "DCOILWTICO",
        "Gold Prices": "GOLDAMGBD228NLBM",
        "Consumer Confidence": "UMCSENT",
        "Leading Index": "USSLIND",
        "ISM PMI": "NAPM"
    }

    data = {}
    for label, code in indicators.items():
        try:
            series = fred.get_series(code)
            data[label] = series
        except Exception as e:
            print(f"Failed to fetch {label} ({code}): {e}")

    # Combine into one DataFrame (align by date)
    df = pd.DataFrame(data)
    return df


df = fetch_macro_indicators()
print(df.tail())
