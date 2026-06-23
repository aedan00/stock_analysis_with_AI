from typing import Any
from models.reportModel import Report

def display_report(
    report: Report,
) -> None:
    """
    Display report for the user.
    """

    print(f"\n============={report.ticker} Investment Report =============\n")

    print(
        "\n============= Technical Analysis ==============\n"
    )

    print(f"Ticker: {report.ticker}")

    print(
        f"Latest Price: "
        f"${report.metrics.performanceMetrics.latest_price:.2f}"
    )

    print(
        f"1-Year Return: "
        f"{report.metrics.performanceMetrics.total_return:.2%}"
    )

    print(
        f"Annualized Volatility: "
        f"{report.metrics.performanceMetrics.annualized_volatility:.2%}\n"
    )

    #Trend
    print(
        f"Trend: "
        f"{report.metrics.trendMetrics.trend}\n"
    )

    # RSI
    print(
        f"RSI (Relative Strength Index): {report.metrics.momentumMetrics.rsi:.2f} "
        f"({report.metrics.momentumMetrics.rsi_signal})"
    )

    print(
        f"MACD Trend: "
        f"{report.metrics.momentumMetrics.macd_signal}\n"
    )

    print(
        f"Current Volume: "
        f"{report.metrics.volumeMetrics.current_volume:,}"
    )

    print(
        f"20-Day Avg Volume: "
        f"{report.metrics.volumeMetrics.average_volume:,.0f}"
    )

    print(
        f"Relative Volume: "
        f"{report.metrics.volumeMetrics.relative_volume:.2f}"
    )

    print(
        f"Volume Signal: "
        f"{report.metrics.volumeMetrics.volume_signal}\n"
    )

    #ATR
    print(
        f"ATR (Average True Range): "
        f"{report.metrics.volatilityMetrics.atr:.2f}"
    )

    print(
        f"ATR Percent: "
        f"{report.metrics.volatilityMetrics.atr_percent:.2f}"
    )

    print(
        f"ATR Volatility: "
        f"{report.metrics.volatilityMetrics.volatility}\n"
    )

    #BB
    print(
        f"Bollinger Bands Upper Bound: "
        f"{report.metrics.volatilityMetrics.bb_upper:.2f}"
    )
    print(
        f"Bollinger Bands Lower Bound: "
        f"{report.metrics.volatilityMetrics.bb_lower:.2f}"
    )
    print(
        f"Bollinger Bands Signal: "
        f"{report.metrics.volatilityMetrics.bb_signal}"
    )
    print(
        f"Bollinger Bands Width: "
        f"{report.metrics.volatilityMetrics.bb_bandwidth:.2f}\n"
    )

    #adx
    print(
        f"Current ADX (Average Directional Index): "
        f"{report.metrics.trendMetrics.current_adx:.2f}"
    )
    print(
        f"ADX Signal: "
        f"{report.metrics.trendMetrics.adx_signal}"
    )
    print(
        f"Positive DI (Directional Indicator): "
        f"{report.metrics.trendMetrics.plus_di:.2f}"
    )
    print(
        f"Negative DI (Directional Indicator): "
        f"{report.metrics.trendMetrics.minus_di:.2f}"
    )
    print(
        f"DI Signal: "
        f"{report.metrics.trendMetrics.di_signal}\n"
    )

    #obv
    print(
        f"OBV (On-Balance Volume): "
        f"{report.metrics.volumeMetrics.obv:.2f}"
    )
    print(
        f"OBV Signal: "
        f"{report.metrics.volumeMetrics.obv_signal}\n"
    )

    #Support & Resistance
    print(
        f"Support & Resistance Signal: "
        f"{report.metrics.priceLevelMetrics.sr_signal}\n"
    )

    #Stochastic
    print(
        f"Stochastic K: "
        f"{report.metrics.momentumMetrics.stochastic_k:.2f}"
    )
    print(
        f"Stochastic D: "
        f"{report.metrics.momentumMetrics.stochastic_d:.2f}"
    )
    print(
        f"Stochastic Signal: "
        f"{report.metrics.momentumMetrics.stochastic_signal}\n"
    )

    # candlestick
    print(
        "Candlestick Patterns:"
    )
    if report.metrics.candlesticksMetrics.patterns:

        for pattern in report.metrics.candlesticksMetrics.patterns:
            print(f"- {pattern}\n")

    else:
        print("- None detected\n")
    

    # pivot
    print(
        f"Pivot: "
        f"{report.metrics.priceLevelMetrics.pivot:.2f}"
    )
    print(
        f"Pivot R1: "
        f"{report.metrics.priceLevelMetrics.pivot_r1:.2f}"
    )
    print(
        f"Pivot R2: "
        f"{report.metrics.priceLevelMetrics.pivot_r2:.2f}"
    )
    print(
        f"Pivot R3: "
        f"{report.metrics.priceLevelMetrics.pivot_r3:.2f}"
    )
    print(
        f"Pivot S1: "
        f"{report.metrics.priceLevelMetrics.pivot_s1:.2f}"
    )
    print(
        f"Pivot S2: "
        f"{report.metrics.priceLevelMetrics.pivot_s2:.2f}"
    )
    print(
        f"Pivot S3: "
        f"{report.metrics.priceLevelMetrics.pivot_s3:.2f}"
    )
    print(
        f"Pivot Signal: "
        f"{report.metrics.priceLevelMetrics.pivot_signal}\n"
    )


    #fib
    print(
        f"23.6%: "
        f"{report.metrics.priceLevelMetrics.fib_23_6:.2f}"
    )
    print(
        f"38.2%: "
        f"{report.metrics.priceLevelMetrics.fib_38_2:.2f}"
    )
    print(
        f"50%: "
        f"{report.metrics.priceLevelMetrics.fib_50:.2f}"
    )
    print(
        f"61.8%: "
        f"{report.metrics.priceLevelMetrics.fib_61_8:.2f}"
    )
    print(
        f"78.6%: "
        f"{report.metrics.priceLevelMetrics.fib_78_6:.2f}"
    )
    print(
        f"Fib Signal: "
        f"{report.metrics.priceLevelMetrics.fib_signal}\n"
    )


    print(
        f"\nChart saved to:\n"
        f"{report.chart}"
    )

    print("\n=================================================")