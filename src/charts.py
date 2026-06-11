from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

def plot_stock(
    data: pd.DataFrame,
    ticker: str,
) -> str:
    """
    Create stock price chart.

    Args:
        data: Analysis DataFrame containing moving averages.
        ticker: Stock ticker symbol.

    Returns:
        Path to saved chart.
    """
    required_columns = [
        "Close",
        "MA50",
        "MA200",
        "RSI",
        "MACD",
        "MACD_SIGNAL",
        "MACD_HISTOGRAM",
    ]

    missing = set(required_columns) - set(data.columns)

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    fig, axes = plt.subplots(
        nrows=3,
        ncols=1,
        figsize=(14, 10),
        sharex=True,
)

    #price, MA50, MA200
    axes[0].plot(
        data.index,
        data["Close"],
        label="Close Price",
        linewidth=2,
    )

    axes[0].plot(
        data.index,
        data["MA50"],
        label="50-Day MA",
    )

    axes[0].plot(
        data.index,
        data["MA200"],
        label="200-Day MA",
    )

    axes[0].set_title(f"{ticker} Stock Price")
    axes[0].set_ylabel("Price ($)")
    axes[0].grid(True)
    axes[0].legend()


    #RSI
    axes[1].plot(
        data.index,
        data["RSI"],
        label="RSI",
        linewidth=2,
    )

    axes[1].axhline(
        y=30,
        color="green",
        linestyle="--",
        label="Oversold (30)",
    )

    axes[1].axhline(
        y=70,
        color="red",
        linestyle="--",
        label="Overbought (70)",
    )

    axes[1].set_title("RSI")
    axes[1].set_ylabel("RSI")
    axes[1].set_ylim(0, 100)
    axes[1].grid(True)
    axes[1].legend()


    #MACD, MACD_SIGNAL, MACD_HISTOGRAM
    axes[2].plot(
        data.index,
        data["MACD"],
        label="MACD",
        linewidth=2,
    )

    axes[2].plot(
        data.index,
        data["MACD_SIGNAL"],
        label="MACD SIGNAL",
    )

    axes[2].bar(
        data.index,
        data["MACD_HISTOGRAM"],
        label="MACD HISTOGRAM",
    )

    axes[2].axhline(
        y=0,
        color="black",
        linestyle="--",
        linewidth=1,
    )

    axes[2].set_title(f"{ticker} MACD, MACD SIGNAL and MACD HISTOGRAM")
    axes[2].set_xlabel("Date")
    axes[2].set_ylabel("Price ($)")
    axes[2].grid(True)
    axes[2].legend()


    filename = REPORT_DIR / f"{ticker}_chart.png"

    #prevent tight layout between charts
    fig.tight_layout()
    fig.savefig(filename)
    plt.close()

    return str(filename)