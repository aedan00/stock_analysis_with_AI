import pandas as pd
from typing import Any
from indicators import (calculate_rsi, calculate_macd,)
from models import StockMetrics
from config import (
    TRADING_DAYS_PER_YEAR,
    SHORT_MA_WINDOW,
    LONG_MA_WINDOW,
)

def analyze_stock(
    data: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Calculate stock performance metrics and indicators.

    Args:
        data: Raw stock price DataFrame.

    Returns:
        A copy of the data with indicators and a metrics dictionary.
    """

    # Create independent analysis dataframe
    analysis = data.copy()

    start_price: float = analysis["Close"].iloc[0]
    end_price: float = analysis["Close"].iloc[-1]

    total_return: float = (
        (end_price - start_price)
        / start_price
    )

    daily_returns: pd.Series = (
        analysis["Close"]
        .pct_change()
        .dropna()
    )

    annualized_volatility: float = (
        daily_returns.std()
        * (TRADING_DAYS_PER_YEAR ** 0.5)
    )

    # Moving averages - MA50 & MA200
    analysis["MA50"] = (
        analysis["Close"]
        .rolling(SHORT_MA_WINDOW)
        .mean()
    )

    analysis["MA200"] = (
        analysis["Close"]
        .rolling(LONG_MA_WINDOW)
        .mean()
    )

    # Determine trend -RSI
    if analysis["MA50"].iloc[-1] > analysis["MA200"].iloc[-1]:
        trend = "Bullish"
    else:
        trend = "Bearish"

    analysis["RSI"] = calculate_rsi(analysis)

    currentRsi = analysis["RSI"].iloc[-1]
    if currentRsi > 70:
        rsi_signal = "Overbought"
    elif currentRsi < 30:
        rsi_signal = "Oversold"
    else:
        rsi_signal = "Neutral"



    # MACD
    macd_data = calculate_macd(analysis)

    analysis["MACD"] = (
        macd_data["MACD"]
    )

    analysis["MACD_SIGNAL"] = (
        macd_data["MACD_SIGNAL"]
    )

    analysis["MACD_HISTOGRAM"] = (
        macd_data["MACD_HISTOGRAM"]
    )

    current_macd = analysis["MACD"].iloc[-1]

    current_signal = analysis["MACD_SIGNAL"].iloc[-1]


    if current_macd > current_signal:
        macd_signal = "Bullish"
    else:
        macd_signal = "Bearish"

    metrics = StockMetrics(
    latest_price=end_price,
    total_return=total_return,
    annualized_volatility=annualized_volatility,
    trend=trend,
    rsi=currentRsi,
    rsi_signal=rsi_signal,
    macd_signal=macd_signal,
    )

    #validation
    print(
        analysis[
            [
            "Close",
            "MA50",
            "MA200",
            "RSI",
            "MACD",
            "MACD_SIGNAL",
            "MACD_HISTOGRAM"
            ]
        ].tail(30)
    )

    return analysis, metrics