from typing import Any

def display_report(
    report: dict[str, Any],
) -> None:
    """
    Display report for the user.
    """

    print("\n========== Investment Report ==========\n")

    print(f"Ticker: {report['ticker']}")

    print(
        f"Latest Price: "
        f"${report['latest_price']:.2f}"
    )

    print(
        f"1-Year Return: "
        f"{report['total_return']:.2%}"
    )

    print(
        f"Annualized Volatility: "
        f"{report['volatility']:.2%}"
    )

    print(
        f"Trend: "
        f"{report['trend']}"
    )

    print(
        f"RSI: "
        f"RSI: {report['rsi']:.2f} "
        f"({report['rsi_signal']})"
    )

    print(
        f"MACD Trend: "
        f"{report['macd_signal']}"
    )

    print(
        f"\nChart saved to:\n"
        f"{report['chart']}"
    )

    print("\n======================================")