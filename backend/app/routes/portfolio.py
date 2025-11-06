from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/portfolio/manual")
def get_portfolio_manual(file):
  pass

