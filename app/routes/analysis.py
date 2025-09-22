from fastapi import APIRouter
from app.services.financials import fetch_stock_financials
from app.services.gpt import score_stock

router = APIRouter()


"""@router.get("/analysis/{symbol}")
def analyze_stock(symbol: str):
    data = fetch_stock_financials(symbol)
    analysis = analyze_with_gpt(data)
    return {"symbol": symbol, "analysis": analysis, "raw_data": data}
"""


@router.get("/score/{symbol}")
def stock_score_financials(symbol: str):
    data = fetch_stock_financials(symbol)
    analysis = score_stock(data)
    return {
        "symbol": symbol,
        "score": analysis["score"],
        "summary": analysis["summary"],
        "positives": analysis.get("positives", []),
        "negatives": analysis.get("negatives", []),
        "raw_data": data
    }
