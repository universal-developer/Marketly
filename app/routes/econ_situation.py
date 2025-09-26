from fastapi import APIRouter
from app.services.economics import fetch_macro_indicators

router = APIRouter()


@router.get("/economics")
def macro_indicators():
    return fetch_macro_indicators()
