from typing import Any

def create_report(
    ticker: str,
    metrics: dict[str, Any],
    chart_file: str,
) -> dict[str, Any]:
    """
    Create structured investment report.

    Returns:
        Dictionary containing report information.
    """

    return {
        "ticker": ticker,
        "latest_price": metrics.latest_price,
        "total_return": metrics.total_return,
        "volatility": metrics.annualized_volatility,
        "trend": metrics.trend,
        "rsi": metrics.rsi,
        "rsi_signal": metrics.rsi_signal,
        "macd_signal": metrics.macd_signal,
        "chart": chart_file,
    }