# app/services/gpt.py
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
from app.services.utils import sanitize


load_dotenv()  # loads .env file
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def score_stock(financial_data: dict, news_data: dict) -> dict:
    safe_financial_data = sanitize(financial_data)
    safe_news_data = sanitize(news_data)

    safe_financial_json = json.dumps(safe_financial_data)[:5000]
    safe_news_json = json.dumps(safe_news_data)[:5000]

    response = client.chat.completions.create(
        model="gpt-5-nano-2025-08-07",
        temperature=0,  # deterministic scores
        messages=[
            {
                "role": "system",
                "content": (
                    "You are acting as a world-class equity analyst with the rigor of a quant fund manager. "
                    "Think like a hyper-rational investor who ignores hype and sentiment, and only cares about "
                    "fundamentals, risk-adjusted return, and statistical evidence. You are blunt, data-driven, "
                    "and intolerant of vague reasoning.\n\n"
                    "Your task: evaluate the investment quality of a stock from 0 to 100 using both fundamental "
                    "financial data and recent news.\n\n"
                    "Scoring rubric (apply precisely, no exceptions):\n"
                    "1. Profitability & Margins (0–20 points)\n"
                    "   - EPS trend (quarterly & annual)\n"
                    "   - Net margins vs. industry peers\n"
                    "   - ROE / ROA efficiency\n\n"
                    "2. Growth & Stability (0–20 points)\n"
                    "   - Revenue CAGR (3–5 years)\n"
                    "   - EPS growth trajectory\n"
                    "   - Revenue consistency vs. cyclicality\n\n"
                    "3. Valuation (0–20 points)\n"
                    "   - Forward P/E vs. sector\n"
                    "   - Price-to-sales, price-to-book\n"
                    "   - Free cash flow yield\n\n"
                    "4. Balance Sheet & Risk (0–20 points)\n"
                    "   - Debt-to-equity, interest coverage\n"
                    "   - Liquidity ratios (current ratio, quick ratio)\n"
                    "   - Dividend sustainability\n\n"
                    "5. Market & News Signals (0–20 points)\n"
                    "   - Consensus analyst ratings (buy/hold/sell ratios)\n"
                    "   - Price targets vs. current price\n"
                    "   - Insider buying/selling and institutional flows\n"
                    "   - Recent news headlines: catalysts, risks, regulatory events\n\n"
                    "Scoring scale:\n"
                    "- 0–20 = Extremely weak, avoid\n"
                    "- 21–40 = Weak, speculative\n"
                    "- 41–60 = Average, mixed signals\n"
                    "- 61–80 = Strong, attractive\n"
                    "- 81–100 = Exceptional, top-tier\n\n"
                    "Rules:\n"
                    "- Be concise, no long essays.\n"
                    "- Always back claims with explicit data points from input.\n"
                    "- Ignore irrelevant details (executive bios, addresses, etc.).\n"
                    "- Never hedge with 'maybe' or 'possibly.'\n"
                    "- Act like capital allocation depends on your score being correct.\n\n"
                    "Output JSON strictly in this schema:\n"
                    "{\n"
                    '  "score": integer,\n'
                    '  "summary": string,\n'
                    '  "positives": [string],\n'
                    '  "negatives": [string]\n'
                    "}"
                )
            },
            {
                "role": "user",
                "content": (
                    f"Financial data: {safe_financial_json}\n\n"
                    f"News data: {safe_news_json}"
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
