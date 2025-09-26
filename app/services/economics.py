from fredapi import Fred
import os


def fetch_macro_indicators():
    """
    Fetch macroeconomic indicators from FRED.
    If resample_freq is provided (e.g. 'M' for monthly), each series
    will be resampled (via .last()) to that freq and aligned.
    """

    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise RuntimeError("FRED_API_KEY not set in environment")

    fred = Fred(api_key=api_key)

    # (Updated) indicators dictionary
    indicators = {
        "GDP (Real)": "GDPC1",
        "GDP Growth Rate": "A191RL1Q225SBEA",
        "Industrial Production": "INDPRO",
        "CPI (All Items)": "CPIAUCSL",
        "Core CPI": "CPILFESL",
        "PPI": "PPIACO",
        "Unemployment Rate": "UNRATE",
        "Nonfarm Payrolls": "PAYEMS",
        "Job Openings (JOLTS)": "JTSJOL",  # updated from JOLTSJOL
        "Fed Funds Rate": "FEDFUNDS",
        "10Y Treasury Yield": "DGS10",
        "Yield Curve (10Y-2Y)": "T10Y2Y",
        "Trade Balance": "NETEXP",
        "US Dollar Index": "DTWEXBGS",
        "Oil Prices": "DCOILWTICO",
        # "Gold Prices": "GOLDAMGBD228NLBM",  # deprecated / removed
        "Consumer Confidence": "UMCSENT",
        "Leading Index": "USSLIND"
        # "ISM PMI": "NAPM"  # no known valid replacement currently
    }

    data = {}

    for label, code in indicators.items():
        try:
            series = fred.get_series(code)
            # convert to JSON-safe format: list of {date, value}
            records = [
                {"date": d.strftime("%Y-%m-%d"),
                 "value": float(v) if v == v else None}
                for d, v in series.items()
            ]
            data[label] = records
        except Exception as e:
            print(f"❌ Failed {label}: {e}")

    return data
