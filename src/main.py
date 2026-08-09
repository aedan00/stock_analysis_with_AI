from data import get_fundamental_data, get_stock_data
from fundamentals.display_fundamental import display_fundamental_report
from fundamentals.fundamental_analysis import analyze_fundamentals
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

    fundamental_data = get_fundamental_data(
        ticker
    )

    fundamental_metrics = analyze_fundamentals(
        fundamental_data
    )


    print("Got fundamental metrics")

    print(fundamental_metrics)

    print("After print")


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