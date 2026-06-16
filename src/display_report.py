from typing import Any
from models import Report

def display_report(
    report: Report,
) -> None:
    """
    Display report for the user.
    """

    print("\n========== Investment Report ==========\n")

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
        f"Trend: "
        f"{report.metrics.trend}"
    )

    print(
        f"RSI: "
        f"RSI: {report.metrics.rsi:.2f} "
        f"({report.metrics.rsi_signal})"
    )

    print(
        f"MACD Trend: "
        f"{report.metrics.macd_signal}"
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
        f"ATR: "
        f"{report.metrics.atr}"
    )

    print(
        f"ATR Percent: "
        f"{report.metrics.atr_percent}"
    )

    print(
        f"ATR Volatility: "
        f"{report.metrics.volatility}"
    )

    print(
        f"\nChart saved to:\n"
        f"{report.chart}"
    )

    print("\n======================================")