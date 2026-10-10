import pandas as pd
import yfinance as yf

from config import DATA_PERIOD


def get_stock_data(
    ticker: str
) -> pd.DataFrame:

    stock = yf.Ticker(ticker)
    data = stock.history(
        period=DATA_PERIOD
    )

    if data.empty or "Close" not in data.columns:
        return pd.DataFrame()

    return data


def get_fundamental_data(ticker: str) -> dict:
    stock = yf.Ticker(ticker)

    return {
        "info": stock.info,
        "income_statement": stock.income_stmt,
        "balance_sheet": stock.balance_sheet,
        "cash_flow": stock.cashflow,
    }