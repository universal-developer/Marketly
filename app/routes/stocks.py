from fastapi import APIRouter
from app.services.financials import fetch_stock_financials

router = APIRouter()


@router.get("/stocks/{symbol}")
def get_stock(symbol: str):
    return fetch_stock_financials(symbol)
