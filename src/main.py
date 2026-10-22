import math

from data import get_fundamental_data, get_stock_data
from fundamentals.display_fundamental import display_fundamental_report
from fundamentals.fundamental_analysis import analyze_fundamentals, build_biotech_comparison_metrics
from technical.charts import plot_stock
from report import create_report
from display_report import display_report
from technical.analysis import analyze_stock
from clinical_trials import (
    SPONSOR_ALIASES,
    display_clinical_trial_summary,
    fetch_clinical_trial_summary,
)


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


def _metric_is_available(value) -> bool:
    if value is None:
        return False

    try:
        return math.isfinite(value)
    except (TypeError, ValueError):
        return False


def biotech_score_breakdown(comparison_metrics: dict) -> dict[str, float | None]:
    """
    Return the weighted point contribution from each available input.
    """
    balance_sheet = comparison_metrics.get("balance_sheet", {})
    cash_position = comparison_metrics.get("cash_position", {})
    profitability = comparison_metrics.get("profitability", {})
    growth = comparison_metrics.get("growth", {})

    current_ratio = balance_sheet.get("current_ratio")
    free_cash_flow_margin = cash_position.get("free_cash_flow_margin")
    net_margin = profitability.get("net_margin")
    revenue_growth = growth.get("revenue_growth")

    return {
        "liquidity": min(current_ratio, 3.0) * 10
        if _metric_is_available(current_ratio) else None,
        "free_cash_flow_margin": min(max(free_cash_flow_margin, -0.5), 0.5) * 50
        if _metric_is_available(free_cash_flow_margin) else None,
        "net_margin": min(max(net_margin, -0.5), 0.5) * 100
        if _metric_is_available(net_margin) else None,
        "revenue_growth": min(max(revenue_growth, -0.5), 0.5) * 100
        if _metric_is_available(revenue_growth) else None,
    }


def biotech_score(comparison_metrics: dict) -> float:
    breakdown = biotech_score_breakdown(comparison_metrics)
    return round(
        sum(points for points in breakdown.values() if points is not None),
        2,
    )


def format_currency(value: float | int | None) -> str:
    if not _metric_is_available(value):
        return "N/A"

    absolute_value = abs(value)
    if absolute_value >= 1_000_000_000:
        return f"${value / 1_000_000_000:,.2f}B"
    if absolute_value >= 1_000_000:
        return f"${value / 1_000_000:,.1f}M"
    return f"${value:,.0f}"


def format_percentage(value: float | None) -> str:
    return "N/A" if not _metric_is_available(value) else f"{value:.1%}"


def format_cash_runway(
    runway_years: float | None,
    average_operating_cash_flow: float | None,
    periods: int,
) -> str:
    if not _metric_is_available(average_operating_cash_flow):
        return "N/A"
    period_label = f" ({periods}yr avg)"
    if average_operating_cash_flow >= 0:
        return f"No burn{period_label}"
    if not _metric_is_available(runway_years):
        return "N/A"
    return f"{runway_years:.1f} yrs{period_label}"


def format_statement_period(period) -> str:
    if period is None:
        return "N/A"
    if hasattr(period, "strftime"):
        return period.strftime("%Y-%m-%d")
    return str(period)


def print_comparison_section(title: str, rows: list[dict]) -> None:
    if not rows:
        return

    print(f"\n=== {title} ===")
    print("{:<6} {:<22} {:>8} {:>9} {:>12} {:>12} {:>12} {:>12} {:>12} {:>12} {:>20} {:>12} {:>10} {:>10}".format(
        "Ticker",
        "Company",
        "Score",
        "Coverage",
        "Mkt Cap",
        "FCF",
        "Cash",
        "Debt",
        "Net Cash",
        "Avg OpCF",
        "Cash Runway",
        "FCF Margin",
        "Rev Grw",
        "Net Margin",
    ))
    print("-" * 184)

    for row in rows:
        company = row["company"] or "N/A"
        market_cap = format_currency(row["market_cap"])
        free_cash_flow = format_currency(row["free_cash_flow"])
        total_cash = format_currency(row["total_cash"])
        total_debt = format_currency(row["total_debt"])
        net_cash = format_currency(row["net_cash"])
        average_operating_cash_flow = format_currency(row["average_operating_cash_flow"])
        cash_runway = format_cash_runway(
            row["cash_runway_years"],
            row["average_operating_cash_flow"],
            row["cash_runway_periods"],
        )
        free_cash_flow_margin = format_percentage(row["free_cash_flow_margin"])
        revenue_growth = format_percentage(row["revenue_growth"])
        net_margin = format_percentage(row["net_margin"])

        print(
            "{:<6} {:<22} {:>8.2f} {:>9} {:>12} {:>12} {:>12} {:>12} {:>12} {:>12} {:>20} {:>12} {:>10} {:>10}".format(
                row["ticker"],
                company[:22],
                row["score"],
                f"{row['coverage']}/4",
                market_cap,
                free_cash_flow,
                total_cash,
                total_debt,
                net_cash,
                average_operating_cash_flow,
                cash_runway,
                free_cash_flow_margin,
                revenue_growth,
                net_margin,
            )
        )

    print("\nStatement periods (balance sheet as-of; operating cash flow periods averaged):")
    print("{:<6} {:<20} {}".format("Ticker", "Balance sheet", "OpCF periods"))
    for row in rows:
        operating_cash_flow_periods = row["operating_cash_flow_periods"]
        periods_label = (
            ", ".join(format_statement_period(period) for period in operating_cash_flow_periods)
            if operating_cash_flow_periods
            else "N/A"
        )
        print("{:<6} {:<20} {}".format(
            row["ticker"],
            format_statement_period(row["balance_sheet_as_of"]),
            periods_label,
        ))

    print("\nR&D investment context (informational only; not scored):")
    print("{:<6} {:>14} {:>14}".format("Ticker", "R&D expense", "R&D / Revenue"))
    for row in rows:
        print("{:<6} {:>14} {:>14}".format(
            row["ticker"],
            format_currency(row["research_and_development_expense"]),
            format_percentage(row["research_and_development_intensity"]),
        ))

    print("\nScore breakdown (points; N/A means unavailable):")
    print("{:<6} {:>10} {:>12} {:>12} {:>16}".format(
        "Ticker",
        "Liquidity",
        "FCF Margin",
        "Net Margin",
        "Revenue Growth",
    ))
    print("-" * 60)
    for row in rows:
        breakdown = row["score_breakdown"]
        print("{:<6} {:>10} {:>12} {:>12} {:>16}".format(
            row["ticker"],
            format_score_points(breakdown["liquidity"]),
            format_score_points(breakdown["free_cash_flow_margin"]),
            format_score_points(breakdown["net_margin"]),
            format_score_points(breakdown["revenue_growth"]),
        ))


def compare_biotech_tickers(comparison_metrics_by_ticker: dict[str, dict]):
    ranked_rows = []
    skipped_tickers = []

    for ticker, comparison_metrics in comparison_metrics_by_ticker.items():
        score_breakdown = biotech_score_breakdown(comparison_metrics)
        coverage = sum(points is not None for points in score_breakdown.values())
        if coverage == 0:
            skipped_tickers.append(ticker)
            continue

        score = round(
            sum(points for points in score_breakdown.values() if points is not None),
            2,
        )
        ranked_rows.append({
            "ticker": ticker,
            "company": comparison_metrics.get("company"),
            "score": score,
            "market_cap": comparison_metrics.get("market_cap"),
            "free_cash_flow": comparison_metrics.get("cash_position", {}).get("free_cash_flow"),
            "total_cash": comparison_metrics.get("cash_position", {}).get("total_cash"),
            "net_cash": comparison_metrics.get("cash_position", {}).get("net_cash"),
            "total_debt": comparison_metrics.get("balance_sheet", {}).get("total_debt"),
            "cash_runway_years": comparison_metrics.get("cash_position", {}).get("cash_runway_years"),
            "average_operating_cash_flow": comparison_metrics.get("cash_position", {}).get("average_operating_cash_flow"),
            "cash_runway_periods": comparison_metrics.get("cash_position", {}).get("cash_runway_periods"),
            "balance_sheet_as_of": comparison_metrics.get("statement_periods", {}).get("balance_sheet_as_of"),
            "operating_cash_flow_periods": comparison_metrics.get("statement_periods", {}).get("operating_cash_flow_periods", []),
            "research_and_development_expense": comparison_metrics.get("research_and_development", {}).get("expense"),
            "research_and_development_intensity": comparison_metrics.get("research_and_development", {}).get("intensity"),
            "free_cash_flow_margin": comparison_metrics.get("cash_position", {}).get("free_cash_flow_margin"),
            "revenue_growth": comparison_metrics.get("growth", {}).get("revenue_growth"),
            "net_margin": comparison_metrics.get("profitability", {}).get("net_margin"),
            "coverage": coverage,
            "score_breakdown": score_breakdown,
        })

    ranked_rows.sort(key=lambda row: row["score"], reverse=True)

    print("\n=== Ranked biotech comparison ===")
    print("Score is a project-specific heuristic, not an official financial metric.")
    print("Cash runway uses average annual operating cash flow over up to 3 recent periods; it is not scored.")
    for ticker in skipped_tickers:
        print(f"Skipping {ticker}: no score metrics were available from Yahoo Finance.")

    if not ranked_rows:
        print("No companies could be ranked: no comparison metrics were available.")
        return

    complete_rows = [row for row in ranked_rows if row["coverage"] == 4]
    partial_rows = [row for row in ranked_rows if row["coverage"] < 4]

    print_comparison_section("Complete data (4/4)", complete_rows)
    if partial_rows:
        print("\nWarning: incomplete scores use fewer metrics and are not directly comparable to complete scores.")
        print_comparison_section("Partial data (<4/4)", partial_rows)


def format_score_points(value: float | None) -> str:
    return "N/A" if value is None else f"{value:+.1f}"


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

    trial_tickers = [ticker for ticker in tickers if ticker in SPONSOR_ALIASES]
    if trial_tickers:
        include_trial_lookup = input(
            "Fetch ClinicalTrials.gov activity for mapped companies "
            f"({', '.join(trial_tickers)})? [y/N]: "
        ).strip().lower() in {"y", "yes"}
        if include_trial_lookup:
            for ticker in trial_tickers:
                display_clinical_trial_summary(fetch_clinical_trial_summary(ticker))


if __name__ == "__main__":
    main()