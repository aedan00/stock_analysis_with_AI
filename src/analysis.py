import pandas as pd
from typing import Any
from indicators import (calculate_rsi, calculate_macd, calculate_atr, 
                        calculate_bollinger_bands, calculate_adx, 
                        calculate_obv, calculate_support_resistance, 
                        calculate_stochastic, calculate_pivot_points, calculate_fibonacci_levels)
from candlesticks import detect_candlestick_patterns
from models.technical import TechnicalMetrics
from models.performance import PerformanceMetrics
from models.trend import TrendMetrics
from models.momentum import MomentumMetrics
from models.volume import VolumeMetrics
from models.volatility import VolatilityMetrics
from models.price_levels import PriceLevelMetrics
from models.candlestick import CandlestickMetrics

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


    # Volume
    analysis["AVG_VOLUME20"] = (
        analysis["Volume"]
        .rolling(20)
        .mean()
    )

    current_volume = analysis["Volume"].iloc[-1]
    average_volume = analysis["AVG_VOLUME20"].iloc[-1]
    relative_volume = (
        current_volume
        / average_volume
    )

    if relative_volume > 1.5:
        volume_signal = "Very High"
    elif relative_volume > 1.1:
        volume_signal = "Above Average"
    elif relative_volume < 0.8:
        volume_signal = "Below Average"
    else:
        volume_signal = "Average"


    # volatile 
    analysis["ATR"] = calculate_atr(analysis)
    current_atr = analysis["ATR"].iloc[-1]
    atr_percent = (
        current_atr
        / end_price
    ) * 100
    if atr_percent < 1:
        volatility = "Low"
    elif atr_percent < 3:
        volatility = "Moderate"
    elif atr_percent < 5:
        volatility = "High"
    else:
        volatility = "Very High"

    # Bollinger Bands
    bb_data = calculate_bollinger_bands(analysis)
    analysis["BB_UPPER"] = bb_data["BB_UPPER"]
    analysis["BB_MIDDLE"] = bb_data["BB_MIDDLE"]
    analysis["BB_LOWER"] = bb_data["BB_LOWER"]
    analysis["BB_BANDWIDTH"] = bb_data["BB_BANDWIDTH"]

    current_price = analysis["Close"].iloc[-1]
    upper = analysis["BB_UPPER"].iloc[-1]
    middle = analysis["BB_MIDDLE"].iloc[-1]
    lower = analysis["BB_LOWER"].iloc[-1]
    if current_price > upper:
        bb_signal = "Above Upper Band"
    elif current_price < lower:
        bb_signal = "Below Lower Band"
    elif current_price > middle:
        bb_signal = "Upper Half of Band"
    else:
        bb_signal = "Lower Half of Band"
    bb_bandwidth = (
        (upper - lower)
        / middle
    ) * 100





    # ADX
    adx_data = calculate_adx(analysis)
    analysis["ADX"] = adx_data["ADX"]
    analysis["PLUS_DI"] = adx_data["PLUS_DI"]
    analysis["MINUS_DI"] = adx_data["MINUS_DI"]

    current_adx = analysis["ADX"].iloc[-1]
    plus_di = analysis["PLUS_DI"].iloc[-1]
    minus_di = analysis["MINUS_DI"].iloc[-1]


    if current_adx < 20:
        adx_signal = "Weak Trend"
    elif current_adx < 25:
        adx_signal = "Developing Trend"
    elif current_adx < 50:
        adx_signal = "Strong Trend"
    elif current_adx < 75:
        adx_signal = "Very Strong Trend"
    else:
        adx_signal = "Extreme Trend"
    if plus_di > minus_di:
        di_signal = "Bullish"
    else:
        di_signal = "Bearish"


    # OBV
    analysis["OBV"] = calculate_obv(analysis)
    current_obv = analysis["OBV"].iloc[-1]
    previous_obv = analysis["OBV"].iloc[-2]
    if current_obv > previous_obv:
        obv_signal = "Accumulation"
    elif current_obv < previous_obv:
        obv_signal = "Distribution"
    else:
        obv_signal = "Neutral"


    #S&R
    sr_signal = "Between Levels"

    support, resistance = calculate_support_resistance(analysis)

    current_price = analysis["Close"].iloc[-1]

    if resistance is not None:
        if current_price >= resistance * 0.98:
            sr_signal = "Near Resistance"

    elif support is not None:
        if current_price <= support * 1.02:
            sr_signal = "Near Support"



    stochastic = calculate_stochastic(analysis)

    analysis["STOCHASTIC_K"] = stochastic["STOCHASTIC_K"]
    analysis["STOCHASTIC_D"] = stochastic["STOCHASTIC_D"]

    current_k = analysis["STOCHASTIC_K"].iloc[-1]
    current_d = analysis["STOCHASTIC_D"].iloc[-1]

    if current_k > 80:
        stochastic_signal = "Overbought"

    elif current_k < 20:
        stochastic_signal = "Oversold"

    elif current_k > current_d:
        stochastic_signal = "Bullish"

    else:
        stochastic_signal = "Bearish"


    # candlesticks
    candlestick_patterns = detect_candlestick_patterns(
        analysis
    )
    candlestickMetrics = CandlestickMetrics(
        candlestick_patterns
    )

    #pivot
    pivot_data = calculate_pivot_points(
        analysis
    )

    analysis[
        [
            "PIVOT",
            "R1",
            "R2",
            "R3",
            "S1",
            "S2",
            "S3",
        ]
    ] = pivot_data


    current_price = analysis["Close"].iloc[-1]

    pivot = analysis["PIVOT"].iloc[-1]
    r1 = analysis["R1"].iloc[-1]
    s1 = analysis["S1"].iloc[-1]


    if current_price > r1:
        pivot_signal = "Above Resistance"

    elif current_price < s1:
        pivot_signal = "Below Support"

    elif current_price > pivot:
        pivot_signal = "Bullish Above Pivot"

    else:
        pivot_signal = "Bearish Below Pivot"



    fib = calculate_fibonacci_levels(
        analysis
    )

    # append fib columns to analysis columns
    analysis[
        [
            "FIB_HIGH",
            "FIB_LOW",
            "FIB_23_6",
            "FIB_38_2",
            "FIB_50",
            "FIB_61_8",
            "FIB_78_6",
        ]
    ] = fib

    current_price = analysis["Close"].iloc[-1]

    levels = {
        "23.6%": analysis["FIB_23_6"].iloc[-1],
        "38.2%": analysis["FIB_38_2"].iloc[-1],
        "50%": analysis["FIB_50"].iloc[-1],
        "61.8%": analysis["FIB_61_8"].iloc[-1],
        "78.6%": analysis["FIB_78_6"].iloc[-1],
    }

    closest_level = min(
        levels,
        key=lambda level: abs(current_price - levels[level])
    )
    fib_signal = f"Near {closest_level} retracement"

    performanceMetrics=PerformanceMetrics(
        latest_price=end_price,
        total_return=total_return,
        annualized_volatility=annualized_volatility,       
    )

    trendMetrics = TrendMetrics(
        trend=trend,
        current_adx=current_adx,
        plus_di=plus_di,
        minus_di=minus_di,
        adx_signal=adx_signal,
        di_signal=di_signal,
    )   

    momentumMetrics=MomentumMetrics(
        rsi=currentRsi,
        rsi_signal=rsi_signal,
        macd_signal=macd_signal,
        stochastic_k=current_k,
        stochastic_d=current_d,
        stochastic_signal=stochastic_signal,
    )
    
    volumeMetrics = VolumeMetrics(
        current_volume=current_volume,
        average_volume=average_volume,
        relative_volume=relative_volume,
        volume_signal=volume_signal,
        obv=current_obv,
        obv_signal=obv_signal,
    )

    volatilityMetrics = VolatilityMetrics(
        atr=current_atr,
        atr_percent=atr_percent,
        volatility=volatility,
        bb_upper=upper,
        bb_middle=middle,
        bb_lower=lower,
        bb_signal=bb_signal,
        bb_bandwidth=bb_bandwidth,
    )

    priceLevelMetrics = PriceLevelMetrics(
        support=support,
        resistance=resistance,
        sr_signal=sr_signal,

        pivot=pivot,
        pivot_r1=r1,
        pivot_r2=analysis["R2"].iloc[-1],
        pivot_r3=analysis["R3"].iloc[-1],
        pivot_s1=s1,
        pivot_s2=analysis["S2"].iloc[-1],
        pivot_s3=analysis["S3"].iloc[-1],
        pivot_signal=pivot_signal,
        fib_23_6=levels["23.6%"],
        fib_38_2=levels["38.2%"],
        fib_50=levels["50%"],
        fib_61_8=levels["61.8%"],
        fib_78_6=levels["78.6%"],
        fib_signal=fib_signal,
    )

    metrics = TechnicalMetrics(
        performanceMetrics,
        trendMetrics, 
        momentumMetrics,
        volumeMetrics,
        volatilityMetrics,
        priceLevelMetrics,
        candlestickMetrics,
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
            "MACD_HISTOGRAM",
            ]
        ].tail(30)
    )

    return analysis, metrics




