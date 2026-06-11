import yfinance as yf
import pandas as pd


def get_stock_data(ticker_symbol):
    """
    Download one year of stock data.
    """

    stock = yf.Ticker(ticker_symbol)

    data = stock.history(period="1y")

    return stock, data


def calculate_return(data):
    """
    Calculate one-year return.
    """

    start_price = data["Close"].iloc[0]
    end_price = data["Close"].iloc[-1]

    stock_return = (
        (end_price - start_price)
        / start_price
        * 100
    )

    return stock_return


def calculate_volatility(data):
    """
    Calculate daily return volatility.
    """

    daily_returns = (
        data["Close"]
        .pct_change()
        .dropna()
    )

    volatility = (
        daily_returns.std()
        * (252 ** 0.5)
        * 100
    )

    return volatility


def calculate_trend(data):
    """
    Compare 50-day and 200-day moving averages.
    """

    data["MA50"] = (
        data["Close"]
        .rolling(50)
        .mean()
    )

    data["MA200"] = (
        data["Close"]
        .rolling(200)
        .mean()
    )

    latest_ma50 = data["MA50"].iloc[-1]
    latest_ma200 = data["MA200"].iloc[-1]

    if latest_ma50 > latest_ma200:
        return "Bullish"
    else:
        return "Bearish"


def generate_report(ticker, data):

    stock_return = calculate_return(data)

    volatility = calculate_volatility(data)

    trend = calculate_trend(data)


    print("\n========== Investment Analysis ==========\n")

    print(f"Ticker: {ticker}")

    print(
        f"1-Year Return: "
        f"{stock_return:.2f}%"
    )

    print(
        f"Annualized Volatility: "
        f"{volatility:.2f}%"
    )

    print(
        f"Trend Signal: "
        f"{trend}"
    )


    print("\nAnalyst Summary:")

    if stock_return > 0:
        print(
            "- The stock gained value over the past year."
        )
    else:
        print(
            "- The stock declined over the past year."
        )


    if volatility > 40:
        print(
            "- The stock shows high price volatility."
        )
    else:
        print(
            "- The stock shows moderate volatility."
        )


    print(
        f"- Current trend appears {trend.lower()}."
    )


    print(
        "\n========================================"
    )


def main():

    ticker = input(
        "Enter stock ticker: "
    ).upper()


    stock, data = get_stock_data(ticker)


    if data.empty:
        print(
            "Could not find stock data."
        )
        return


    generate_report(
        ticker,
        data
    )


if __name__ == "__main__":
    main()