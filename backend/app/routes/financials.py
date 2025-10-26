from fastapi import APIRouter
from app.services.fetchers.financials import fetch_stock_financials
from app.utils.sanitizer_util import sanitize
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/financials/{symbol}")
def get_financials(symbol: str):
    data = fetch_stock_financials(symbol)
    return JSONResponse(content=sanitize(data))
