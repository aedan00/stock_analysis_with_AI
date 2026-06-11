import yfinance as yf


def get_stock_data(ticker_symbol):
    """
    Download stock price data.
    """
    stock = yf.Ticker(ticker_symbol)

    data = stock.history(period="1y")

    return stock, data


def show_company_profile(ticker_symbol, stock, data):
    """
    Display company information.
    """

    info = stock.info

    print("\n========== Company Profile ==========\n")

    print(f"Ticker: {ticker_symbol}")

    print(f"Company: {info.get('longName', 'N/A')}")

    print(f"Sector: {info.get('sector', 'N/A')}")

    print(f"Industry: {info.get('industry', 'N/A')}")

    print(
        f"Market Cap: "
        f"${info.get('marketCap', 0):,}"
    )

    latest_price = data["Close"].iloc[-1]

    print(
        f"Current Price: "
        f"${latest_price:.2f}"
    )

    high = data["High"].max()
    low = data["Low"].min()

    print(
        f"52-week High: "
        f"${high:.2f}"
    )

    print(
        f"52-week Low: "
        f"${low:.2f}"
    )

    print(
        f"Website: "
        f"{info.get('website', 'N/A')}"
    )

    print("\n====================================")


def main():

    ticker_symbol = input(
        "Enter stock ticker: "
    ).upper()

    stock, data = get_stock_data(ticker_symbol)

    if data.empty:
        print("Invalid ticker.")
        return

    show_company_profile(
        ticker_symbol,
        stock,
        data
    )


if __name__ == "__main__":
    main()