from typing import Any
from models import Report

def display_report(
    report: Report,
) -> None:
    """
    Display report for the user.
    """

    print(f"\n============={report.ticker} Investment Report =============\n")

    print(f"Ticker: {report.ticker}")

    print(
        f"Latest Price: "
        f"${report.metrics.latest_price:.2f}"
    )

    print(
        f"1-Year Return: "
        f"{report.metrics.total_return:.2%}"
    )

    print(
        f"Annualized Volatility: "
        f"{report.metrics.annualized_volatility:.2%}\n"
    )

    #Trend
    print(
        f"Trend: "
        f"{report.metrics.trend}\n"
    )

    # RSI
    print(
        f"RSI (Relative Strength Index): {report.metrics.rsi:.2f} "
        f"({report.metrics.rsi_signal})"
    )

    print(
        f"MACD Trend: "
        f"{report.metrics.macd_signal}\n"
    )

    print(
        f"Current Volume: "
        f"{report.metrics.current_volume:,}"
    )

    print(
        f"20-Day Avg Volume: "
        f"{report.metrics.average_volume:,.0f}"
    )

    print(
        f"Relative Volume: "
        f"{report.metrics.relative_volume:.2f}"
    )

    print(
        f"Volume Signal: "
        f"{report.metrics.volume_signal}\n"
    )

    #ATR
    print(
        f"ATR (Average True Range): "
        f"{report.metrics.atr:.2f}"
    )

    print(
        f"ATR Percent: "
        f"{report.metrics.atr_percent:.2f}"
    )

    print(
        f"ATR Volatility: "
        f"{report.metrics.volatility}\n"
    )

    #BB
    print(
        f"Bollinger Bands Upper Bound: "
        f"{report.metrics.bb_upper:.2f}"
    )
    print(
        f"Bollinger Bands Lower Bound: "
        f"{report.metrics.bb_lower:.2f}"
    )
    print(
        f"Bollinger Bands Signal: "
        f"{report.metrics.bb_signal}"
    )
    print(
        f"Bollinger Bands Width: "
        f"{report.metrics.bb_bandwidth:.2f}\n"
    )

    #adx
    print(
        f"Current ADX (Average Directional Index): "
        f"{report.metrics.current_adx:.2f}"
    )
    print(
        f"ADX Signal: "
        f"{report.metrics.adx_signal}"
    )
    print(
        f"Positive DI (Directional Indicator): "
        f"{report.metrics.plus_di:.2f}"
    )
    print(
        f"Negative DI (Directional Indicator): "
        f"{report.metrics.minus_di:.2f}"
    )
    print(
        f"DI Signal: "
        f"{report.metrics.di_signal}\n"
    )

    #obv
    print(
        f"OBV (On-Balance Volume): "
        f"{report.metrics.obv:.2f}"
    )
    print(
        f"OBV Signal: "
        f"{report.metrics.obv_signal}\n"
    )

    #Support & Resistance
    print(
        f"Support & Resistance Signal: "
        f"{report.metrics.sr_signal}\n"
    )

    #Stochastic
    print(
        f"Stochastic K: "
        f"{report.metrics.stochastic_k:.2f}"
    )
    print(
        f"Stochastic D: "
        f"{report.metrics.stochastic_d:.2f}"
    )
    print(
        f"Stochastic Signal: "
        f"{report.metrics.stochastic_signal}\n"
    )

    # candlestick
    print(
        "Candlestick Patterns:"
    )
    if report.metrics.candlestick_patterns:

        for pattern in report.metrics.candlestick_patterns:
            print(f"- {pattern}")

    else:
        print("- None detected")
    


    print(
        f"\nChart saved to:\n"
        f"{report.chart}"
    )

    print("\n=================================================")