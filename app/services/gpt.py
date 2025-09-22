# app/services/gpt.py
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

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
    response = client.responses.create(
        model="gpt-5",
        input="How much gold would it take to coat the Statue of Liberty in a 1mm layer?",
        reasoning={
            "effort": "minimal"
        }
    )

    return json.loads(response.text)
