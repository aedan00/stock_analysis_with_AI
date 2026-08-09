def format_money(value):
    """Format large monetary values."""

    if value is None:
        return "N/A"

    if abs(value) >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"

    if abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"

    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"

    if abs(value) >= 1_000:
        return f"${value / 1_000:.2f}K"

    return f"${value:,.2f}"


def format_percentage(value):
    """Convert decimal percentage to readable percentage."""

    if value is None:
        return "N/A"

    return f"{value * 100:.2f}%"


def format_ratio(value):
    """Format a ratio."""

    if value is None:
        return "N/A"

    return f"{value:.2f}"


def format_number(value):
    """Format a normal number."""

    if value is None:
        return "N/A"

    return f"{value:,.2f}"


def display_fundamental_report(
    fundamental_metrics: dict
) -> None:

    company = fundamental_metrics.get(
        "company"
    )

    sector = fundamental_metrics.get(
        "sector"
    )

    industry = fundamental_metrics.get(
        "industry"
    )

    market_cap = fundamental_metrics.get(
        "market_cap"
    )

    enterprise_value = fundamental_metrics.get(
        "enterprise_value"
    )

    growth = fundamental_metrics.get(
        "growth",
        {}
    )

    profitability = fundamental_metrics.get(
        "profitability",
        {}
    )

    cash_flow = fundamental_metrics.get(
        "cash_flow",
        {}
    )

    financial_health = fundamental_metrics.get(
        "financial_health",
        {}
    )

    valuation = fundamental_metrics.get(
        "valuation",
        {}
    )

    print()
    print("=" * 55)
    print("             FUNDAMENTAL ANALYSIS")
    print("=" * 55)

    # --------------------------------------------------
    # Company
    # --------------------------------------------------

    print()
    print(f"Company:   {company or 'N/A'}")
    print(f"Sector:    {sector or 'N/A'}")
    print(f"Industry:  {industry or 'N/A'}")

    # --------------------------------------------------
    # Valuation
    # --------------------------------------------------

    print()
    print("-" * 55)
    print("VALUATION")
    print("-" * 55)

    print(
        f"Market Cap:       "
        f"{format_money(market_cap)}"
    )

    print(
        f"Enterprise Value: "
        f"{format_money(enterprise_value)}"
    )

    print(
        f"P/E Ratio:        "
        f"{format_number(valuation.get('trailing_pe'))}"
    )

    print(
        f"Forward P/E:      "
        f"{format_number(valuation.get('forward_pe'))}"
    )

    print(
        f"Price / Sales:    "
        f"{format_number(valuation.get('price_to_sales'))}"
    )

    print(
        f"Price / Book:     "
        f"{format_number(valuation.get('price_to_book'))}"
    )

    print(
        f"EV / EBITDA:      "
        f"{format_number(valuation.get('enterprise_to_ebitda'))}"
    )

    # --------------------------------------------------
    # Growth
    # --------------------------------------------------

    print()
    print("-" * 55)
    print("GROWTH")
    print("-" * 55)

    print(
        f"Revenue Growth:   "
        f"{format_percentage(growth.get('revenue_growth'))}"
    )

    print(
        f"Earnings Growth:  "
        f"{format_percentage(growth.get('earnings_growth'))}"
    )

    # --------------------------------------------------
    # Profitability
    # --------------------------------------------------

    print()
    print("-" * 55)
    print("PROFITABILITY")
    print("-" * 55)

    print(
        f"Gross Margin:     "
        f"{format_percentage(profitability.get('gross_margin'))}"
    )

    print(
        f"Operating Margin: "
        f"{format_percentage(profitability.get('operating_margin'))}"
    )

    print(
        f"Net Margin:       "
        f"{format_percentage(profitability.get('net_margin'))}"
    )

    print(
        f"ROE:              "
        f"{format_percentage(profitability.get('roe'))}"
    )

    print(
        f"ROA:              "
        f"{format_percentage(profitability.get('roa'))}"
    )

    # --------------------------------------------------
    # Cash Flow
    # --------------------------------------------------

    print()
    print("-" * 55)
    print("CASH FLOW")
    print("-" * 55)

    print(
        f"Operating Cash Flow: "
        f"{format_money(cash_flow.get('operating_cash_flow'))}"
    )

    print(
        f"Capital Expenditure: "
        f"{format_money(cash_flow.get('capital_expenditure'))}"
    )

    print(
        f"Free Cash Flow:      "
        f"{format_money(cash_flow.get('free_cash_flow'))}"
    )

    # --------------------------------------------------
    # Financial Health
    # --------------------------------------------------

    print()
    print("-" * 55)
    print("FINANCIAL HEALTH")
    print("-" * 55)

    print(
        f"Total Debt:       "
        f"{format_money(financial_health.get('total_debt'))}"
    )

    print(
        f"Debt / Equity:    "
        f"{format_ratio(financial_health.get('debt_to_equity'))}"
    )

    print(
        f"Current Ratio:    "
        f"{format_ratio(financial_health.get('current_ratio'))}"
    )

    print()
    print("=" * 55)
    print()