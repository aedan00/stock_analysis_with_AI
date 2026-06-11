import pandas as pd
from config import (
    RSI_PERIOD,
    MACD_FAST_PERIOD,
    MACD_SLOW_PERIOD,
    MACD_SIGNAL_PERIOD
)

def calculate_rsi(
    data: pd.DataFrame,
    period: int = RSI_PERIOD
) -> pd.Series:

    delta = data["Close"].diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = (
        gain.rolling(period)
        .mean()
    )

    avg_loss = (
        loss.rolling(period)
        .mean()
    )

    rs = avg_gain / avg_loss

    return 100 - (
        100 / (1 + rs)
    )


def calculate_macd(
    data: pd.DataFrame,
    fast_period: int = MACD_FAST_PERIOD,
    slow_period: int = MACD_SLOW_PERIOD,
    signal_period: int = MACD_SIGNAL_PERIOD,
) -> pd.DataFrame:
    
    """
    Calculate MACD, signal line, and histogram.

    Args:
        data: DataFrame containing a 'Close' column.

    Returns:
        DataFrame with columns:
        - MACD
        - MACD_SIGNAL
        - MACD_HISTOGRAM
    """
        
    #create empty DataFrame with the same rows (index) as your original stock data.
    macd_data = pd.DataFrame(index=data.index)

    ema_fast = (
        data["Close"]
        .ewm(
            span=fast_period,
            adjust=False)
        .mean()
    )

    ema_slow = (
        data["Close"]
        .ewm(slow_period)
        .mean()
    )

    macd_data["MACD"] = ema_fast - ema_slow

    macd_data["MACD_SIGNAL"] = (
        macd_data["MACD"]
        .ewm(signal_period)
        .mean()
    )

    macd_data["MACD_HISTOGRAM"] = (
        macd_data["MACD"] - macd_data["MACD_SIGNAL"]
    )

    return macd_data