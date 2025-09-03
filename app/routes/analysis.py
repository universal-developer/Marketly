from fastapi import APIRouter
from app.services.financials import fetch_stock_financials
from app.services.gpt import analyze_with_gpt

router = APIRouter()


@router.get("/analysis/{symbol}")
def analyze_stock(symbol: str):
    data = fetch_stock_financials(symbol)
    analysis = analyze_with_gpt(data)
    return {"symbol": symbol, "analysis": analysis, "raw_data": data}
