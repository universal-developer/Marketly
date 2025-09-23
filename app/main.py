from fastapi import FastAPI
from app.routes import financials, news, analysis
from rich.traceback import install

# Make all tracebacks pretty in the console
install(show_locals=True)

app = FastAPI(title="Marketly Backend 🚀")

# Include routers
app.include_router(financials.router)
app.include_router(news.router)
app.include_router(analysis.router)


@app.get("/")
def root():
    return {"message": "Marketly backend is running"}
