# app/services/gpt.py
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
from app.utils.sanitizer_util import sanitize


load_dotenv()  # loads .env file
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def score_stock(financial_data: dict, financials_summary: dict, news_data: dict, economical_data: dict) -> dict:
    safe_payload = {
        "financials_summary": financials_summary,   # already clean
        "news_data": news_data,                     # raw text = fine
        "economical_data": economical_data,          # from FRED, already numeric
        "financial_data": sanitize(financial_data)
    }

    # Then truncate or serialize safely once
    safe_payload_json = json.dumps(safe_payload)[:20000]

    response = client.chat.completions.create(
        model="gpt-5-nano-2025-08-07",
        # temperature=0,  # deterministic scores
        messages=[
            {
                "role": "system",
                "content": (
                    """You are acting as a world-class equity analyst with the rigor of a quant fund manager. 
                    Think like a hyper-rational investor who ignores hype and sentiment, and only cares about 
                    fundamentals, risk-adjusted return, and statistical evidence. You are blunt, data-driven, 
                    and intolerant of vague reasoning.

                    Your task: evaluate the investment quality of a stock from 0 to 100 using fundamental 
                    financial data, recent news, and macroeconomic indicators.

                    Scoring rubric (apply precisely, no exceptions):

                    1. Profitability & Margins (0–17 points)
                    - EPS trend (quarterly & annual)
                    - Net margins vs. industry peers
                    - ROE / ROA efficiency

                    2. Growth & Stability (0–17 points)
                    - Revenue CAGR (3–5 years)
                    - EPS growth trajectory
                    - Revenue consistency vs. cyclicality

                    3. Valuation (0–17 points)
                    - Forward P/E vs. sector
                    - Price-to-sales, price-to-book
                    - Free cash flow yield

                    4. Balance Sheet & Risk (0–17 points)
                    - Debt-to-equity, interest coverage
                    - Liquidity ratios (current ratio, quick ratio)
                    - Dividend sustainability

                    5. Market & News Signals (0–16 points)
                    - Consensus analyst ratings (buy/hold/sell ratios)
                    - Price targets vs. current price
                    - Insider buying/selling and institutional flows
                    - Recent news headlines: catalysts, risks, regulatory events

                    6. Macro & Market Conditions (0–16 points)
                    - GDP growth and unemployment trends
                    - Inflation and interest rate environment
                    - Yield curve signals
                    - Commodity shocks (oil, etc.)

                    Scoring scale:
                    - 0–20 = Extremely weak, avoid
                    - 21–40 = Weak, speculative
                    - 41–60 = Average, mixed signals
                    - 61–80 = Strong, attractive
                    - 81–100 = Exceptional, top-tier

                    Rules:
                    - Be concise, no long essays.
                    - Always back claims with explicit data points from input.
                    - Ignore irrelevant details (executive bios, addresses, etc.).
                    - Never hedge with "maybe" or "possibly."
                    - Act like capital allocation depends on your score being correct.

                    Output JSON strictly in this schema:
                    {
                    "score": integer,
                    "summary": string,
                    "positives": [string],
                    "negatives": [string]
                    }"""
                )

            },
            {
                "role": "user",
                "content": (
                    f"Stock's financials, economical (FRED), news data: {safe_payload_json}\n\n"
                )
            }
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
                        "positives": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "negatives": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["score", "summary"]
                }
            }
        },
    )

    return json.loads(response.choices[0].message.content)
