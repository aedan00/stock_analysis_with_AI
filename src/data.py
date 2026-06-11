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