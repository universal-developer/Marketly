# app/services/gpt.py
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
from app.services.utils import sanitize


load_dotenv()  # loads .env file
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# def analyze_with_gpt(stock_data: dict) -> str:
"""
    Placeholder GPT analysis function.
    Later you can connect OpenAI API here.
    """
# For now just return a summary string
# return f"Analysis for {stock_data.get('symbol', 'UNKNOWN')} with {len(stock_data.keys())} data points."


def score_stock(data: dict) -> dict:

    safe_data = sanitize(data)
    safe_json = json.dumps(safe_data)[:5000]

    response = client.chat.completions.create(
        model="gpt-5-nano-2025-08-07",
        messages=[
            {"role": "system", "content": "You are a financial analyst. Score stocks 0-100."},
            {"role": "user",
                "content": f"Analyze this stock data: {safe_json}"}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "stock_score",
                "schema": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "integer"},
                        "summary": {"type": "string"},
                        "positives": {"type": "array", "items": {"type": "string"}},
                        "negatives": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["score", "summary"]
                }
            }
        }
    )
    return json.loads(response.choices[0].message.content)

    return json.loads(response.text)
