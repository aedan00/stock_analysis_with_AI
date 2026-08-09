import pandas as pd
import yfinance as yf

from config import DATA_PERIOD


def get_stock_data(
    ticker: str
) -> pd.DataFrame:

    stock = yf.Ticker(ticker)

    return stock.history(
        period=DATA_PERIOD
    )


def get_fundamental_data(ticker: str) -> dict:
    stock = yf.Ticker(ticker)

    return {
        "info": stock.info,
        "income_statement": stock.income_stmt,
        "balance_sheet": stock.balance_sheet,
        "cash_flow": stock.cashflow,
    }