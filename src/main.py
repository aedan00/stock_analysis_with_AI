from data import get_stock_data
from fundamentals.display_fundamental import display_fundamental_report
from fundamentals.fundamental_analysis import analyze_fundamentals
from technical.charts import plot_stock
from report import create_report
from display_report import display_report
from technical.analysis import analyze_stock
import yfinance as yf


def main():

    ticker: str = input(
        "Enter ticker: "
    ).upper()

    raw_data = get_stock_data(ticker)

    analysis_data, metrics = analyze_stock(raw_data)

    fundamental_metrics = analyze_fundamentals(
        yf.Ticker(ticker).info
    )

    chart = plot_stock(
        analysis_data,
        ticker
    )

    report = create_report(
        ticker,
        metrics,
        chart
    )

    display_report(
        report
    )

    display_fundamental_report(
        fundamental_metrics
    )

if __name__ == "__main__":
    main()