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
        f"{report.metrics.annualized_volatility:.2%}"
    )
    print(
        "\n"
    )


    print(
        f"Trend: "
        f"{report.metrics.trend}"
    )
    print(
        "\n"
    )

    print(
        f"RSI: {report.metrics.rsi:.2f} "
        f"({report.metrics.rsi_signal})"
    )

    print(
        f"MACD Trend: "
        f"{report.metrics.macd_signal}"
    )
    print(
        "\n"
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
        f"{report.metrics.volume_signal}"
    )
    print(
        "\n"
    )

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
        f"{report.metrics.volatility}"
    )
    print(
        "\n"
    )

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
        f"{report.metrics.bb_bandwidth:.2f}"
    )
    print(
        "\n"
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
        f"{report.metrics.di_signal}"
    )

    print(
        f"\nChart saved to:\n"
        f"{report.chart}"
    )

    print("\n=================================================")