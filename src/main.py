from data import get_fundamental_data, get_stock_data
from fundamentals.display_fundamental import display_fundamental_report
from fundamentals.fundamental_analysis import analyze_fundamentals
from technical.charts import plot_stock
from report import create_report
from display_report import display_report
from technical.analysis import analyze_stock


DEFAULT_BIOTECH_TICKERS = [
    "VRTX",
    "REGN",
    "GILD",
    "AMGN",
    "BMRN",
    "EXEL",
    "ALNY",
    "INCY",
    "NTLA",
    "SGEN",
]


def analyze_one_ticker(ticker: str):
    raw_data = get_stock_data(ticker)

    if raw_data.empty:
        print(f"Skipping {ticker}: no valid price history returned by Yahoo Finance.")
        return

    analysis_data, metrics = analyze_stock(raw_data)
    fundamental_data = get_fundamental_data(ticker)
    fundamental_metrics = analyze_fundamentals(fundamental_data)

    print(f"\n=== {ticker} ===")
    print("Technical summary:")
    print(metrics)
    print("\nFundamental summary:")
    print(fundamental_metrics)

    chart = plot_stock(analysis_data, ticker)
    report = create_report(ticker, metrics, chart)
    display_report(report)
    display_fundamental_report(fundamental_metrics)


def main():
    # Step 1: keep single-ticker support, but default to a biotech basket
    raw_input = input(
        "Enter ticker(s), or press Enter to use the default biotech basket: "
    ).strip()

    if raw_input:
        tickers = [symbol.strip().upper() for symbol in raw_input.split(",") if symbol.strip()]
    else:
        tickers = DEFAULT_BIOTECH_TICKERS

    for ticker in tickers:
        analyze_one_ticker(ticker)


if __name__ == "__main__":
    main()