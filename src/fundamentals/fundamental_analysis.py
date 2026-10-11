import math

import pandas as pd


def _safe_divide(
    numerator,
    denominator,
):
    """
    Return a safe ratio, or None if either side is missing or the denominator is zero.
    """
    if numerator is None or denominator is None or denominator == 0:
        return None

    try:
        return numerator / denominator
    except TypeError:
        return None


def _get_value(
    statement: pd.DataFrame,
    field: str,
    column=None
):
    """
    Safely retrieve a value from a Yahoo Finance financial statement.
    Returns None if the field does not exist.
    """

    if statement is None or field not in statement.index:
        return None

    values = statement.loc[field]

    if column is not None:
        if column not in values.index:
            return None

        return values[column]

    return values


def _latest_value(
    statement: pd.DataFrame,
    field: str
):
    """
    Get the most recent value for a financial statement field.
    """

    values = _get_value(statement, field)

    if values is None or len(values) == 0:
        return None

    return values.iloc[0]


def _recent_finite_values(
    statement: pd.DataFrame,
    field: str,
    limit: int = 3,
) -> list[tuple[object, float]]:
    """Return recent finite statement periods and values, newest first."""
    values = _get_value(statement, field)
    if values is None or len(values) == 0:
        return []

    recent_values = []
    for period, value in values.iloc[:limit].items():
        try:
            if math.isfinite(value):
                recent_values.append((period, value))
        except (TypeError, ValueError):
            continue

    return recent_values


def build_biotech_comparison_metrics(
    ticker: str,
    fundamental_data: dict,
) -> dict:
    """
    Build a normalized metric dictionary for biotech peer comparison.
    This keeps the same fields across all names and makes ranking easier.
    """
    info = fundamental_data.get("info", {})
    income = fundamental_data.get("income_statement")
    balance = fundamental_data.get("balance_sheet")
    cash_flow = fundamental_data.get("cash_flow")

    total_cash = _latest_value(balance, "Cash And Cash Equivalents At Carrying Value")
    if total_cash is None:
        total_cash = _latest_value(balance, "Cash")
    if total_cash is None:
        total_cash = _latest_value(balance, "Cash And Cash Equivalents")

    total_debt = _latest_value(balance, "Total Debt")
    net_cash = None
    if total_cash is not None and total_debt is not None:
        try:
            if math.isfinite(total_cash) and math.isfinite(total_debt):
                net_cash = total_cash - total_debt
        except (TypeError, ValueError):
            pass
    current_assets = _latest_value(balance, "Current Assets")
    current_liabilities = _latest_value(balance, "Current Liabilities")
    total_assets = _latest_value(balance, "Total Assets")
    equity = _latest_value(balance, "Stockholders Equity")

    revenue = _latest_value(income, "Total Revenue")
    research_and_development = _latest_value(income, "Research And Development")
    if research_and_development is not None:
        try:
            if not math.isfinite(research_and_development):
                research_and_development = None
        except (TypeError, ValueError):
            research_and_development = None
    research_and_development_intensity = _safe_divide(
        research_and_development,
        revenue,
    )
    if research_and_development_intensity is not None:
        try:
            if not math.isfinite(research_and_development_intensity):
                research_and_development_intensity = None
        except (TypeError, ValueError):
            research_and_development_intensity = None

    gross_profit = _latest_value(income, "Gross Profit")
    operating_income = _latest_value(income, "Operating Income")
    net_income = _latest_value(income, "Net Income")

    operating_cash_flow = _latest_value(cash_flow, "Operating Cash Flow")
    recent_operating_cash_flows = _recent_finite_values(
        cash_flow,
        "Operating Cash Flow",
    )
    average_operating_cash_flow = (
        sum(value for _, value in recent_operating_cash_flows)
        / len(recent_operating_cash_flows)
        if recent_operating_cash_flows
        else None
    )
    balance_sheet_as_of = (
        balance.columns[0]
        if balance is not None and len(balance.columns) > 0
        else None
    )
    operating_cash_flow_periods = [
        period for period, _ in recent_operating_cash_flows
    ]
    capital_expenditure = _latest_value(cash_flow, "Capital Expenditure")
    free_cash_flow = None
    if operating_cash_flow is not None and capital_expenditure is not None:
        free_cash_flow = operating_cash_flow + capital_expenditure

    cash_runway_years = None
    if average_operating_cash_flow is not None and average_operating_cash_flow < 0:
        cash_runway_years = _safe_divide(
            total_cash,
            abs(average_operating_cash_flow),
        )

    return {
        "ticker": ticker,
        "company": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "market_cap": info.get("marketCap"),
        "enterprise_value": info.get("enterpriseValue"),
        "cash_position": {
            "total_cash": total_cash,
            "net_cash": net_cash,
            "operating_cash_flow": operating_cash_flow,
            "average_operating_cash_flow": average_operating_cash_flow,
            "cash_runway_periods": len(recent_operating_cash_flows),
            "free_cash_flow": free_cash_flow,
            "cash_runway_years": cash_runway_years,
            "free_cash_flow_margin": _safe_divide(free_cash_flow, revenue),
        },
        "statement_periods": {
            "balance_sheet_as_of": balance_sheet_as_of,
            "operating_cash_flow_periods": operating_cash_flow_periods,
        },
        "research_and_development": {
            "expense": research_and_development,
            "intensity": research_and_development_intensity,
        },
        "balance_sheet": {
            "total_debt": total_debt,
            "current_ratio": _safe_divide(current_assets, current_liabilities),
            "debt_to_equity": _safe_divide(total_debt, equity),
        },
        "profitability": {
            "gross_margin": _safe_divide(gross_profit, revenue),
            "operating_margin": _safe_divide(operating_income, revenue),
            "net_margin": _safe_divide(net_income, revenue),
            "roe": _safe_divide(net_income, equity),
            "roa": _safe_divide(net_income, total_assets),
        },
        "growth": {
            "revenue_growth": info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsGrowth"),
        },
        "valuation": {
            "trailing_pe": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "price_to_sales": info.get("priceToSalesTrailing12Months"),
            "price_to_book": info.get("priceToBook"),
            "enterprise_to_ebitda": info.get("enterpriseToEbitda"),
        },
    }


def analyze_fundamentals(
    fundamental_data: dict
) -> dict:

    info = fundamental_data["info"]
    income = fundamental_data["income_statement"]
    balance = fundamental_data["balance_sheet"]
    cash_flow = fundamental_data["cash_flow"]

    # --------------------------------------------------
    # Basic company information
    # --------------------------------------------------

    market_cap = info.get("marketCap")
    enterprise_value = info.get("enterpriseValue")

    # --------------------------------------------------
    # Income statement
    # --------------------------------------------------

    revenue =  _latest_value(
        income,
        "Total Revenue"
    )

    gross_profit =  _latest_value(
        income,
        "Gross Profit"
    )

    operating_income =  _latest_value(
        income,
        "Operating Income"
    )

    net_income =  _latest_value(
        income,
        "Net Income"
    )

    # --------------------------------------------------
    # Balance sheet
    # --------------------------------------------------

    total_assets =  _latest_value(
        balance,
        "Total Assets"
    )

    equity =  _latest_value(
        balance,
        "Stockholders Equity"
    )

    total_debt =  _latest_value(
        balance,
        "Total Debt"
    )

    current_assets =  _latest_value(
        balance,
        "Current Assets"
    )

    current_liabilities =  _latest_value(
        balance,
        "Current Liabilities"
    )

    # --------------------------------------------------
    # Cash flow
    # --------------------------------------------------

    operating_cash_flow =  _latest_value(
        cash_flow,
        "Operating Cash Flow"
    )

    capital_expenditure =  _latest_value(
        cash_flow,
        "Capital Expenditure"
    )

    # --------------------------------------------------
    # Profitability
    # --------------------------------------------------

    gross_margin = _safe_divide(
        gross_profit,
        revenue,
    )
    operating_margin = _safe_divide(
        operating_income,
        revenue,
    )
    net_margin = _safe_divide(
        net_income,
        revenue,
    )

    # --------------------------------------------------
    # Free cash flow
    # --------------------------------------------------

    free_cash_flow = None

    if (
        operating_cash_flow is not None
        and capital_expenditure is not None
    ):
        free_cash_flow = (
            operating_cash_flow
            + capital_expenditure
        )

    # --------------------------------------------------
    # ROA
    # --------------------------------------------------

    roa = _safe_divide(
        net_income,
        total_assets,
    )

    # --------------------------------------------------
    # ROE
    # --------------------------------------------------

    roe = _safe_divide(
        net_income,
        equity,
    )

    # --------------------------------------------------
    # Debt / Equity
    # --------------------------------------------------

    debt_to_equity = _safe_divide(
        total_debt,
        equity,
    )

    # --------------------------------------------------
    # Current ratio
    # --------------------------------------------------

    current_ratio = _safe_divide(
        current_assets,
        current_liabilities,
    )

    # --------------------------------------------------
    # Growth
    # --------------------------------------------------

    revenue_growth = info.get(
        "revenueGrowth"
    )

    earnings_growth = info.get(
        "earningsGrowth"
    )

    # --------------------------------------------------
    # Valuation
    # --------------------------------------------------

    trailing_pe = info.get(
        "trailingPE"
    )

    forward_pe = info.get(
        "forwardPE"
    )

    price_to_sales = info.get(
        "priceToSalesTrailing12Months"
    )

    price_to_book = info.get(
        "priceToBook"
    )

    enterprise_to_ebitda = info.get(
        "enterpriseToEbitda"
    )

    # --------------------------------------------------
    # Return results
    # --------------------------------------------------

    return {

        "company": info.get(
            "longName"
        ),

        "sector": info.get(
            "sector"
        ),

        "industry": info.get(
            "industry"
        ),

        "market_cap": market_cap,

        "enterprise_value": enterprise_value,

        "growth": {
            "revenue_growth": revenue_growth,
            "earnings_growth": earnings_growth,
        },

        "profitability": {
            "gross_margin": gross_margin,
            "operating_margin": operating_margin,
            "net_margin": net_margin,
            "roe": roe,
            "roa": roa,
        },

        "cash_flow": {
            "operating_cash_flow": (
                _latest_value(
                    cash_flow,
                    "Operating Cash Flow"
                )
            ),
            "capital_expenditure": (
                _latest_value(
                    cash_flow,
                    "Capital Expenditure"
                )
            ),
            "free_cash_flow": free_cash_flow,
        },

        "financial_health": {
            "total_debt": (
                _latest_value(
                    balance,
                    "Total Debt"
                )
            ),
            "current_ratio": current_ratio,
            "debt_to_equity": debt_to_equity,
        },

        "valuation": {
            "trailing_pe": trailing_pe,
            "forward_pe": forward_pe,
            "price_to_sales": price_to_sales,
            "price_to_book": price_to_book,
            "enterprise_to_ebitda": (
                enterprise_to_ebitda
            ),
        },
    }