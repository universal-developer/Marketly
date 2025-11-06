from pydantic import BaseModel
from typing import List, Optional, Literal

class StockInput(BaseModel):
    symbol: str
    shares: float

class PortfolioItem(BaseModel):
    symbol: str
    shares: float
    current_price: float
    value: float
    source: Literal["manual"] = "manual"

class PortfolioResponse(BaseModel):
    total_value: float
    assets: List[PortfolioItem]
