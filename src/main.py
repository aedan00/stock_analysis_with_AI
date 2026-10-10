from data import get_fundamental_data, get_stock_data
from fundamentals.display_fundamental import display_fundamental_report
from fundamentals.fundamental_analysis import analyze_fundamentals, build_biotech_comparison_metrics
from technical.charts import plot_stock
from report import create_report
from display_report import display_report
from technical.analysis import analyze_stock


DEFAULT_BIOTECH_TICKERS = [
    "VRTX",
    "REGN",
    # "GILD",
    # "AMGN",
    # "BMRN",
    # "EXEL",
    # "ALNY",
    # "INCY",
    # "NTLA",
    # "SGEN",
]


def biotech_score(comparison_metrics: dict) -> float:
    """
    Lightweight biotech comparison score using a few normalized inputs.
    Free-cash-flow margin contributes up to +/-25 points, with its value
    capped to the range from -50% to +50%.
    """
    score = 0.0

    balance_sheet = comparison_metrics.get("balance_sheet", {})
    cash_position = comparison_metrics.get("cash_position", {})
    profitability = comparison_metrics.get("profitability", {})
    growth = comparison_metrics.get("growth", {})

    current_ratio = balance_sheet.get("current_ratio")
    if current_ratio is not None:
        score += min(current_ratio, 3.0) * 10

    free_cash_flow_margin = cash_position.get("free_cash_flow_margin")
    if free_cash_flow_margin is not None:
        score += min(max(free_cash_flow_margin, -0.5), 0.5) * 50

    net_margin = profitability.get("net_margin")
    if net_margin is not None:
        score += min(max(net_margin, -0.5), 0.5) * 100

    revenue_growth = growth.get("revenue_growth")
    if revenue_growth is not None:
        score += min(max(revenue_growth, -0.5), 0.5) * 100

    return round(score, 2)


def format_currency(value: float | int | None) -> str:
    if value is None:
        return "N/A"

    absolute_value = abs(value)
    if absolute_value >= 1_000_000_000:
        return f"${value / 1_000_000_000:,.1f}B"
    if absolute_value >= 1_000_000:
        return f"${value / 1_000_000:,.1f}M"
    return f"${value:,.0f}"


def format_percentage(value: float | None) -> str:
    return "N/A" if value is None else f"{value:.1%}"


def compare_biotech_tickers(comparison_metrics_by_ticker: dict[str, dict]):
    ranked_rows = []

    for ticker, comparison_metrics in comparison_metrics_by_ticker.items():
        score = biotech_score(comparison_metrics)
        ranked_rows.append({
            "ticker": ticker,
            "company": comparison_metrics.get("company"),
            "score": score,
            "market_cap": comparison_metrics.get("market_cap"),
            "free_cash_flow": comparison_metrics.get("cash_position", {}).get("free_cash_flow"),
            "free_cash_flow_margin": comparison_metrics.get("cash_position", {}).get("free_cash_flow_margin"),
            "revenue_growth": comparison_metrics.get("growth", {}).get("revenue_growth"),
            "net_margin": comparison_metrics.get("profitability", {}).get("net_margin"),
        })

    ranked_rows.sort(key=lambda row: row["score"], reverse=True)

    print("\n=== Ranked biotech comparison ===")
    print("Score is a project-specific heuristic, not an official financial metric.")
    if not ranked_rows:
        print("No companies could be ranked: no comparison metrics were available.")
        return

    print("{:<6} {:<22} {:>8} {:>12} {:>12} {:>12} {:>10} {:>10}".format(
        "Ticker",
        "Company",
        "Score",
        "Mkt Cap",
        "FCF",
        "FCF Margin",
        "Rev Grw",
        "Net Margin",
    ))
    print("-" * 102)

    for row in ranked_rows:
        company = row["company"] or "N/A"
        market_cap = format_currency(row["market_cap"])
        free_cash_flow = format_currency(row["free_cash_flow"])
        free_cash_flow_margin = format_percentage(row["free_cash_flow_margin"])
        revenue_growth = format_percentage(row["revenue_growth"])
        net_margin = format_percentage(row["net_margin"])

        print(
            "{:<6} {:<22} {:>8.2f} {:>12} {:>12} {:>12} {:>10} {:>10}".format(
                row["ticker"],
                company[:22],
                row["score"],
                market_cap,
                free_cash_flow,
                free_cash_flow_margin,
                revenue_growth,
                net_margin,
            )
        )


def analyze_one_ticker(ticker: str) -> dict | None:
    raw_data = get_stock_data(ticker)

    if raw_data.empty:
        print(f"Skipping {ticker}: no valid price history returned by Yahoo Finance.")
        return None

    analysis_data, metrics = analyze_stock(raw_data)
    fundamental_data = get_fundamental_data(ticker)
    fundamental_metrics = analyze_fundamentals(fundamental_data)
    comparison_metrics = build_biotech_comparison_metrics(ticker, fundamental_data)

    print(f"\n=== {ticker} ===")
    print("Technical summary:")
    print(metrics)
    print("\nFundamental summary:")
    print(fundamental_metrics)
    print("\nBiotech comparison metrics:")
    print(comparison_metrics)

    chart = plot_stock(analysis_data, ticker)
    report = create_report(ticker, metrics, chart)
    display_report(report)
    display_fundamental_report(fundamental_metrics)
    return comparison_metrics


def get_comparison_metrics_for_tickers(tickers: list[str]) -> dict[str, dict]:
    comparison_metrics_by_ticker = {}

    for ticker in tickers:
        fundamental_data = get_fundamental_data(ticker)
        comparison_metrics_by_ticker[ticker] = build_biotech_comparison_metrics(
            ticker,
            fundamental_data,
        )

    return comparison_metrics_by_ticker


def main():
    raw_input = input(
        "Enter ticker(s), or press Enter to use the default biotech basket: "
    ).strip()

    if raw_input:
        tickers = [symbol.strip().upper() for symbol in raw_input.split(",") if symbol.strip()]
    else:
        tickers = DEFAULT_BIOTECH_TICKERS

    comparison_only = input(
        "Comparison only (skip technical analysis and charts)? [Y/n]: "
    ).strip().lower() not in {"n", "no"}

    if comparison_only:
        comparison_metrics_by_ticker = get_comparison_metrics_for_tickers(tickers)
    else:
        comparison_metrics_by_ticker = {}
        for ticker in tickers:
            comparison_metrics = analyze_one_ticker(ticker)
            if comparison_metrics is not None:
                comparison_metrics_by_ticker[ticker] = comparison_metrics

    compare_biotech_tickers(comparison_metrics_by_ticker)


if __name__ == "__main__":
    main()