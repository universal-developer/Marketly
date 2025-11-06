import csv

import yfinance as yf
from app.schemas.portfolio import StockInput, PortfolioItem, PortfolioResponse

def compute_manual_portfolio(stocks: list[StockInput]) -> PortfolioResponse:
  total = 0
  assets = []
  
  for stock in stocks:
    ticker = yf.Ticker(stock.symbol)
    hist = ticker.history(period="1d")
    