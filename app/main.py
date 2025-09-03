from fastapi import FastAPI
from app.routes import stocks, news, analysis

app = FastAPI(title="Marketly Backend 🚀")

# Include routers
app.include_router(stocks.router)
app.include_router(news.router)
app.include_router(analysis.router)


@app.get("/")
def root():
    return {"message": "Marketly backend is running"}
