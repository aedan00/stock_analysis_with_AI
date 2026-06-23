from data import get_stock_data
from technical.charts import plot_stock
from report import create_report
from display_report import display_report
from technical.analysis import analyze_stock


def main():

    ticker: str = input(
        "Enter ticker: "
    ).upper()

    raw_data = get_stock_data(ticker)

    analysis_data, metrics = analyze_stock(raw_data)

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


if __name__ == "__main__":
    main()