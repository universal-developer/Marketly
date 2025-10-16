from fastapi import APIRouter, HTTPException
from app.services.financials import fetch_stock_financials, summarize_financials
from app.services.economics import fetch_macro_indicators
from app.services.news import get_news
from app.services.gpt import score_stock

router = APIRouter()


@router.get("/score/{symbol}")
def stock_score_financials(symbol: str):
    """
    Fetches all data (financial, macro, and news) for a stock symbol,
    summarizes it, and generates an AI-based investment score.
    """

    try:
        # --- Step 1: Fetch all raw data ---
        financial_data = fetch_stock_financials(symbol)
        financials_summary = summarize_financials(financial_data)
        economical_data = fetch_macro_indicators()
        news_data = get_news(symbol)

        # --- Step 2: Score the stock with GPT ---
        analysis = score_stock(financials_summary, news_data, economical_data)

        # --- Step 3: Return structured response ---
        return {
            "symbol": symbol.upper(),
            "score": analysis["score"],
            "summary": analysis["summary"],
            "positives": analysis.get("positives", []),
            "negatives": analysis.get("negatives", []),
            "company": financials_summary.get("company"),
            "valuation": financials_summary.get("valuation"),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Analysis failed: {str(e)}")
