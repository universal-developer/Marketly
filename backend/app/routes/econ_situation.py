import time
from fastapi import APIRouter
from app.services.economics import fetch_macro_indicators

router = APIRouter()


@router.get("/economics")
def macro_indicators():
    """
    Fetch macroeconomic indicators from FRED.
    If resample_freq is provided (e.g. 'M' for monthly), each series
    will be resampled (via .last()) to that freq and aligned.
    """
    start_time = time.time()
    result = fetch_macro_indicators()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")
    return result
