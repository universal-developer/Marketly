from fastapi import APIRouter
from app.services.financials import fetch_stock_financials

router = APIRouter()


@router.get("/financials/{symbol}")
def get_stock(symbol: str):
    return fetch_stock_financials(symbol)
