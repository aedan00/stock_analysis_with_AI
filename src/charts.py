from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

from chart_helpers import (
    plot_price_chart,
    plot_momentum,
    plot_macd,
    plot_volume,
    plot_trend_strength,
)
from candlestick_helper import plot_candlestick

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)


def plot_stock(
    data: pd.DataFrame,
    ticker: str,
) -> str:
    """
    Create technical analysis dashboard.

    Automatically plots available indicators.
    """

    panels = []

    panels.append(
        plot_candlestick
    )

    # Always include price
    panels.append(
        plot_price_chart
    )


    # Add momentum if available
    if (
        "RSI" in data.columns
        or "STOCH_K" in data.columns
    ):
        panels.append(
            plot_momentum
        )


    # Add MACD if available
    if (
        "MACD" in data.columns
        and "MACD_SIGNAL" in data.columns
    ):
        panels.append(
            plot_macd
        )


    # Add volume if available
    if (
        "Volume" in data.columns
    ):
        panels.append(
            plot_volume
        )


    # Add ADX if available
    if (
        "ADX" in data.columns
    ):
        panels.append(
            plot_trend_strength
        )


    fig, axes = plt.subplots(
        nrows=len(panels),
        figsize=(16, 24),
        gridspec_kw={
            "height_ratios": [
                3,  # candlestick
                2,  # existing price chart
                1,  # RSI
                1,  # MACD
                1,  # Volume
                1,  # ADX
            ]
        }
    )


    # Handle single chart case
    if len(panels) == 1:
        axes = [axes]


    for ax, panel in zip(
        axes,
        panels,
    ):
        panel(
            ax,
            data,
            ticker,
        )


    fig.tight_layout()


    filename = (
        REPORT_DIR
        / f"{ticker}_technical_dashboard.png"
    )


    fig.savefig(
        filename,
        dpi=300,
        bbox_inches="tight",
    )


    plt.close()


    return str(filename)