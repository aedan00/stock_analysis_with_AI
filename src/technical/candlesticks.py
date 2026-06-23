import pandas as pd


def detect_candlestick_patterns(
    data: pd.DataFrame,
) -> list[str]:

    patterns = []

    candle = data.iloc[-1]

    open_price = candle["Open"]
    high = candle["High"]
    low = candle["Low"]
    close = candle["Close"]

    body = abs(close - open_price)

    upper_wick = (
        high - max(open_price, close)
    )

    lower_wick = (
        min(open_price, close) - low
    )

    candle_range = high - low


    # Doji
    if body <= candle_range * 0.1:
        patterns.append("Doji")


    # Hammer
    if (
        lower_wick >= body * 2
        and upper_wick <= body * 0.5
    ):
        patterns.append("Hammer")


    # Shooting Star
    if (
        upper_wick >= body * 2
        and lower_wick <= body * 0.5
    ):
        patterns.append("Shooting Star")


    return patterns