import pandas as pd


def prepare_financials_for_gpt(financial_data):
    try:
        income = financial_data.get("income_statement", {}).get("ttm", {})
        balance = financial_data.get("balance_sheet", {}).get("annual", {})
        cashflow = financial_data.get("cash_flow", {}).get("ttm", {})

        return {
            "revenue": float(income.get("TotalRevenue", 0)) if income else None,
            "net_income": float(income.get("NetIncome", 0)) if income else None,
            "gross_profit": float(income.get("GrossProfit", 0)) if income else None,
            "total_assets": float(balance.get("TotalAssets", 0)) if balance else None,
            "total_liabilities": float(balance.get("TotalLiabilitiesNetMinorityInterest", 0)) if balance else None,
            "operating_cashflow": float(cashflow.get("OperatingCashFlow", 0)) if cashflow else None,
            "free_cashflow": float(cashflow.get("FreeCashFlow", 0)) if cashflow else None,
        }
    except Exception as e:
        return {"error": str(e)}


def safe_ratio(a, b):
    try:
        if not a or not b or b == 0:
            return None
        return round(a / b, 3)
    except Exception:
        return None
