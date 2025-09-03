# app/services/gpt.py

def analyze_with_gpt(stock_data: dict) -> str:
    """
    Placeholder GPT analysis function.
    Later you can connect OpenAI API here.
    """
    # For now just return a summary string
    return f"Analysis for {stock_data.get('symbol', 'UNKNOWN')} with {len(stock_data.keys())} data points."
