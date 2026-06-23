import pandas as pd
from config import (
    RSI_PERIOD,
    MACD_FAST_PERIOD,
    MACD_SLOW_PERIOD,
    MACD_SIGNAL_PERIOD,
    ATR_PERIOD,
    STOCHASTIC_PERIOD,
    STOCHASTIC_SIGNAL,
    LOOKBACK_PERIOD,
)

def calculate_rsi(
    data: pd.DataFrame,
    period: int = RSI_PERIOD
) -> pd.Series:

    delta = data["Close"].diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

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
        .ewm(slow_period,
             adjust=False)
        .mean()
    )

    macd_data["MACD"] = ema_fast - ema_slow

    macd_data["MACD_SIGNAL"] = (
        macd_data["MACD"]
        .ewm(signal_period,
             adjust=False)
        .mean()
    )

    macd_data["MACD_HISTOGRAM"] = (
        macd_data["MACD"] - macd_data["MACD_SIGNAL"]
    )

    return macd_data

def calculate_atr(
    data: pd.DataFrame,
    period: int = ATR_PERIOD,
) -> pd.Series:
    high = data["High"]
    low = data["Low"]
    close = data["Close"]

    previous_close = close.shift(1)

    true_range = pd.concat(
        [
            high - low,
            (high - previous_close).abs(),
            (low - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    atr = (
        true_range.ewm(alpha=1/period, adjust=False).mean() 
    )

    return atr


def calculate_bollinger_bands(
    data: pd.DataFrame,
    period: int = 20,
    std_dev: float = 2.0,
) -> pd.DataFrame:
    """
    Calculate Bollinger Bands.

    Args:
        data: DataFrame containing a 'Close' column.
        period: Moving average window length.
        std_dev: Number of standard deviations for the bands.

    Returns:
        DataFrame containing:
        - BB_UPPER
        - BB_MIDDLE
        - BB_LOWER
        - BB_BANDWIDTH
    """

    close = data["Close"]

    # Middle Band = Simple Moving Average
    middle_band = (
        close
        .rolling(period)
        .mean()
    )

    # Standard deviation of price
    standard_deviation = (
        close
        .rolling(period)
        .std()
    )

    # Upper and lower bands
    upper_band = (
        middle_band
        + (std_dev * standard_deviation)
    )

    lower_band = (
        middle_band
        - (std_dev * standard_deviation)
    )

    # Band width shows volatility expansion/contraction
    bandwidth = (
        (upper_band - lower_band)
        / middle_band
    ) * 100

    bollinger_data = pd.DataFrame(
        index=data.index
    )

    bollinger_data["BB_UPPER"] = upper_band
    bollinger_data["BB_MIDDLE"] = middle_band
    bollinger_data["BB_LOWER"] = lower_band
    bollinger_data["BB_BANDWIDTH"] = bandwidth

    return bollinger_data




def calculate_adx(
    data: pd.DataFrame,
    period: int = 14,
) -> pd.DataFrame:
    """
    Calculate Average Directional Index (ADX).

    Args:
        data: DataFrame containing High, Low, Close columns.
        period: Smoothing period.

    Returns:
        DataFrame containing:
        - ADX
        - PLUS_DI
        - MINUS_DI
    """

    high = data["High"]
    low = data["Low"]
    close = data["Close"]

    # Previous values
    previous_high = high.shift(1)
    previous_low = low.shift(1)
    previous_close = close.shift(1)

    # True Range
    true_range = pd.concat(
        [
            high - low,
            (high - previous_close).abs(),
            (low - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    # Directional Movement
    up_move = high - previous_high
    down_move = previous_low - low

    plus_dm = pd.Series(
        0.0,
        index=data.index
    )

    minus_dm = pd.Series(
        0.0,
        index=data.index
    )

    plus_dm[
        (up_move > down_move) &
        (up_move > 0)
    ] = up_move[
        (up_move > down_move) &
        (up_move > 0)
    ]

    minus_dm[
        (down_move > up_move) &
        (down_move > 0)
    ] = down_move[
        (down_move > up_move) &
        (down_move > 0)
    ]

    # Wilder smoothing
    atr = (
        true_range
        .rolling(period)
        .mean()
    )

    plus_di = (
        plus_dm
        .rolling(period)
        .mean()
        / atr
    ) * 100

    minus_di = (
        minus_dm
        .rolling(period)
        .mean()
        / atr
    ) * 100

    # Directional Index
    dx = (
        (plus_di - minus_di).abs()
        /
        (plus_di + minus_di)
    ) * 100

    # ADX
    adx = (
        dx
        .rolling(period)
        .mean()
    )

    adx_data = pd.DataFrame(
        index=data.index
    )

    adx_data["ADX"] = adx
    adx_data["PLUS_DI"] = plus_di
    adx_data["MINUS_DI"] = minus_di

    return adx_data


#OBV
def calculate_obv(
    data: pd.DataFrame,
) -> pd.Series:
    """
    Calculate On-Balance Volume (OBV).

    Args:
        data: DataFrame containing Close and Volume columns.

    Returns:
        A pandas Series containing OBV values.
    """

    obv = [0]

    for i in range(1, len(data)):
        previous_close = data["Close"].iloc[i - 1]
        current_close = data["Close"].iloc[i]
        current_volume = data["Volume"].iloc[i]

        if current_close > previous_close:
            obv.append(obv[-1] + current_volume)

        elif current_close < previous_close:
            obv.append(obv[-1] - current_volume)

        else:
            obv.append(obv[-1])

    return pd.Series(
        obv,
        index=data.index,
    )



def calculate_support_resistance(
    data: pd.DataFrame,
    lookback: int = 2,
) -> tuple[float | None, float | None]:

    highs = data["High"]
    lows = data["Low"]

    resistance = None
    support = None

    for i in range(
        lookback,
        len(data) - lookback,
    ):

        current_high = highs.iloc[i]

        if (
            current_high == highs.iloc[
                i - lookback:i + lookback + 1
            ].max()
        ):
            resistance = current_high

        current_low = lows.iloc[i]

        if (
            current_low == lows.iloc[
                i - lookback:i + lookback + 1
            ].min()
        ):
            support = current_low

    return support, resistance




def calculate_stochastic(
    data: pd.DataFrame,
    period: int = STOCHASTIC_PERIOD,
    signal_period: int = STOCHASTIC_SIGNAL,
) -> pd.DataFrame:
    """
    Calculate the Stochastic Oscillator.

    Returns:
        DataFrame containing:
        - STOCHASTIC_K
        - STOCHASTIC_D
    """

    lowest_low = (
        data["Low"]
        .rolling(period)
        .min()
    )

    highest_high = (
        data["High"]
        .rolling(period)
        .max()
    )

    price_range = (highest_high - lowest_low).replace(0, pd.NA)
    percent_k = (
        (data["Close"] - lowest_low)
        / price_range
    ) * 100

    percent_d = (
        percent_k
        .rolling(signal_period)
        .mean()
    )

    stochastic = pd.DataFrame(index=data.index)

    stochastic["STOCHASTIC_K"] = percent_k
    stochastic["STOCHASTIC_D"] = percent_d

    return stochastic




def calculate_pivot_points(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate standard pivot points.

    Uses previous trading day's High, Low, Close.

    Returns:
        DataFrame with:
        PIVOT
        R1, R2, R3
        S1, S2, S3
    """

    previous_high = data["High"].shift(1)
    previous_low = data["Low"].shift(1)
    previous_close = data["Close"].shift(1)

    pivot = (
        previous_high
        + previous_low
        + previous_close
    ) / 3


    pivots = pd.DataFrame(
        index=data.index
    )

    pivots["PIVOT"] = pivot

    pivots["R1"] = (
        2 * pivot
        - previous_low
    )

    pivots["S1"] = (
        2 * pivot
        - previous_high
    )

    pivots["R2"] = (
        pivot
        + (previous_high - previous_low)
    )

    pivots["S2"] = (
        pivot
        - (previous_high - previous_low)
    )

    pivots["R3"] = (
        previous_high
        + 2 * (pivot - previous_low)
    )

    pivots["S3"] = (
        previous_low
        - 2 * (previous_high - pivot)
    )

    return pivots



#fibonacci
def calculate_fibonacci_levels(
    data: pd.DataFrame,
    lookback: int = LOOKBACK_PERIOD,
) -> pd.DataFrame:
    """
    Calculate Fibonacci retracement levels over a lookback window.
    """

    highest_high = (
        data["High"]
        .rolling(lookback)
        .max()
    )

    lowest_low = (
        data["Low"]
        .rolling(lookback)
        .min()
    )

    price_range = highest_high - lowest_low

    fibonacci = pd.DataFrame(index=data.index)

    fibonacci["FIB_HIGH"] = highest_high
    fibonacci["FIB_LOW"] = lowest_low

    fibonacci["FIB_23_6"] = (
        highest_high
        - price_range * 0.236
    )

    fibonacci["FIB_38_2"] = (
        highest_high
        - price_range * 0.382
    )

    fibonacci["FIB_50"] = (
        highest_high
        - price_range * 0.500
    )

    fibonacci["FIB_61_8"] = (
        highest_high
        - price_range * 0.618
    )

    fibonacci["FIB_78_6"] = (
        highest_high
        - price_range * 0.786
    )
    # return a new dataFrame that has the same index as the original dataFrame with these columns
    return fibonacci