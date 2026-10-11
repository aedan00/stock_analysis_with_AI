import math

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
     "SGEN",
]


def _metric_is_available(value) -> bool:
    if value is None:
        return False

    try:
        return math.isfinite(value)
    except (TypeError, ValueError):
        return False


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
    if _metric_is_available(current_ratio):
        score += min(current_ratio, 3.0) * 10

    free_cash_flow_margin = cash_position.get("free_cash_flow_margin")
    if _metric_is_available(free_cash_flow_margin):
        score += min(max(free_cash_flow_margin, -0.5), 0.5) * 50

    net_margin = profitability.get("net_margin")
    if _metric_is_available(net_margin):
        score += min(max(net_margin, -0.5), 0.5) * 100

    revenue_growth = growth.get("revenue_growth")
    if _metric_is_available(revenue_growth):
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
    return "N/A" if not _metric_is_available(value) else f"{value:.1%}"


def compare_biotech_tickers(comparison_metrics_by_ticker: dict[str, dict]):
    ranked_rows = []
    skipped_tickers = []

    for ticker, comparison_metrics in comparison_metrics_by_ticker.items():
        balance_sheet = comparison_metrics.get("balance_sheet", {})
        cash_position = comparison_metrics.get("cash_position", {})
        profitability = comparison_metrics.get("profitability", {})
        growth = comparison_metrics.get("growth", {})
        score_inputs = (
            balance_sheet.get("current_ratio"),
            cash_position.get("free_cash_flow_margin"),
            profitability.get("net_margin"),
            growth.get("revenue_growth"),
        )
        coverage = sum(_metric_is_available(value) for value in score_inputs)
        if coverage == 0:
            skipped_tickers.append(ticker)
            continue

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
            "coverage": coverage,
        })

    ranked_rows.sort(key=lambda row: row["score"], reverse=True)

    print("\n=== Ranked biotech comparison ===")
    print("Score is a project-specific heuristic, not an official financial metric.")
    for ticker in skipped_tickers:
        print(f"Skipping {ticker}: no score metrics were available from Yahoo Finance.")

    if not ranked_rows:
        print("No companies could be ranked: no comparison metrics were available.")
        return

    if any(row["coverage"] < 4 for row in ranked_rows):
        print("Warning: incomplete scores use fewer metrics; compare those scores cautiously.")

    print("{:<6} {:<22} {:>8} {:>9} {:>12} {:>12} {:>12} {:>10} {:>10}".format(
        "Ticker",
        "Company",
        "Score",
        "Coverage",
        "Mkt Cap",
        "FCF",
        "FCF Margin",
        "Rev Grw",
        "Net Margin",
    ))
    print("-" * 112)

    for row in ranked_rows:
        company = row["company"] or "N/A"
        market_cap = format_currency(row["market_cap"])
        free_cash_flow = format_currency(row["free_cash_flow"])
        free_cash_flow_margin = format_percentage(row["free_cash_flow_margin"])
        revenue_growth = format_percentage(row["revenue_growth"])
        net_margin = format_percentage(row["net_margin"])

        print(
            "{:<6} {:<22} {:>8.2f} {:>9} {:>12} {:>12} {:>12} {:>10} {:>10}".format(
                row["ticker"],
                company[:22],
                row["score"],
                f"{row['coverage']}/4",
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