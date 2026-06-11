from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf


# Constants
TRADING_DAYS_PER_YEAR = 252
SHORT_MA_WINDOW = 50
LONG_MA_WINDOW = 200
DATA_PERIOD = "1y"

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)


def get_stock_data(ticker: str) -> pd.DataFrame:
    """
    Download historical stock price data.

    Args:
        ticker: Stock ticker symbol.

    Returns:
        DataFrame containing historical price data.
    """

    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=DATA_PERIOD)

        if data.empty:
            raise ValueError(
                f"No data found for ticker {ticker}"
            )

        return data

    except Exception as error:
        print(f"Error downloading data: {error}")
        return pd.DataFrame()


def calculate_metrics(
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

    # Moving averages
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

    # Determine trend
    if analysis["MA50"].iloc[-1] > analysis["MA200"].iloc[-1]:
        trend = "Bullish"
    else:
        trend = "Bearish"

    metrics = {
        "latest_price": end_price,
        "total_return": total_return,
        "annualized_volatility": annualized_volatility,
        "trend": trend,
    }

    return analysis, metrics


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

    plt.figure(figsize=(12, 6))

    plt.plot(
        data.index,
        data["Close"],
        label="Close Price",
        linewidth=2,
    )

    plt.plot(
        data.index,
        data["MA50"],
        label="50-Day MA",
    )

    plt.plot(
        data.index,
        data["MA200"],
        label="200-Day MA",
    )

    plt.title(f"{ticker} Stock Price")
    plt.xlabel("Date")
    plt.ylabel("Price ($)")
    plt.grid(True)
    plt.legend()

    filename = REPORT_DIR / f"{ticker}_chart.png"

    plt.savefig(filename)
    plt.close()

    return str(filename)


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
        "latest_price": metrics["latest_price"],
        "total_return": metrics["total_return"],
        "volatility": metrics["annualized_volatility"],
        "trend": metrics["trend"],
        "chart": chart_file,
    }


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
        f"\nChart saved to:\n"
        f"{report['chart']}"
    )

    print("\n======================================")


def main() -> None:
    """
    Main program workflow.
    """

    ticker: str = input(
        "Enter ticker: "
    ).upper()

    raw_data = get_stock_data(ticker)

    if raw_data.empty:
        return

    analysis_data, metrics = calculate_metrics(
        raw_data
    )

    chart_file = plot_stock(
        analysis_data,
        ticker,
    )

    report = create_report(
        ticker,
        metrics,
        chart_file,
    )

    display_report(report)


if __name__ == "__main__":
    main()