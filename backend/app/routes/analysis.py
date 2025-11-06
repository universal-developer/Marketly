from fastapi import APIRouter, HTTPException
from app.integrations.financials import fetch_stock_financials
from app.integrations.economics import fetch_macro_indicators
from app.integrations.news import get_news
from app.integrations.gpt import score_stock

router = APIRouter()


@router.get("/score/{symbol}")
def stock_score(symbol: str):
    """
    Fetch financial, macro, and news data for a stock symbol,
    and generate an AI-based investment score.
    """

    symbol = symbol.upper()

    try:
        # --- Step 1: Fetch all raw data ---
        financial_data = fetch_stock_financials(symbol)
        if "error" in financial_data:
            raise ValueError(financial_data["error"])

        economical_data = fetch_macro_indicators()
        news_data = get_news(symbol)

        # --- Step 2: Score the stock with GPT ---
        analysis = score_stock(financial_data, news_data, economical_data)
        if "error" in analysis:
            raise ValueError(analysis["error"])

        # --- Step 3: Return structured response ---
        return {
            "symbol": symbol,
            "score": analysis.get("score"),
            "summary": analysis.get("summary"),
            "positives": analysis.get("positives", []),
            "negatives": analysis.get("negatives", []),
            "company": financial_data.get("info", {}).get("shortName"),
            "valuation": {
                "trailingPE": financial_data["info"].get("trailingPE"),
                "forwardPE": financial_data["info"].get("forwardPE"),
                "priceToBook": financial_data["info"].get("priceToBook"),
                "priceToSales": financial_data["info"].get("priceToSalesTrailing12Months"),
                "dividendYield": financial_data["info"].get("dividendYield"),
                "marketCap": financial_data["info"].get("marketCap"),
            },
        }

    except ValueError as ve:
        raise HTTPException(status_code=502, detail=f"Data error: {ve}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")
