from typing import Any
from models import Report

def create_report(
    ticker: str,
    metrics: dict[str, Any],
    chart_file: str,
) -> Report:
    """
    Create structured investment report.

    Returns:
        Dictionary containing report information.
    """

    return Report(
        ticker=ticker,
        metrics=metrics,
        chart=chart_file,
    )