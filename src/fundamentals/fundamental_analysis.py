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

    total_cash = (
        _latest_value(balance, "Cash And Cash Equivalents At Carrying Value")
        or _latest_value(balance, "Cash")
        or _latest_value(balance, "Cash And Cash Equivalents")
    )

    total_debt = _latest_value(balance, "Total Debt")
    current_assets = _latest_value(balance, "Current Assets")
    current_liabilities = _latest_value(balance, "Current Liabilities")
    total_assets = _latest_value(balance, "Total Assets")
    equity = _latest_value(balance, "Stockholders Equity")

    revenue = _latest_value(income, "Total Revenue")
    gross_profit = _latest_value(income, "Gross Profit")
    operating_income = _latest_value(income, "Operating Income")
    net_income = _latest_value(income, "Net Income")

    operating_cash_flow = _latest_value(cash_flow, "Operating Cash Flow")
    capital_expenditure = _latest_value(cash_flow, "Capital Expenditure")
    free_cash_flow = None
    if operating_cash_flow is not None and capital_expenditure is not None:
        free_cash_flow = operating_cash_flow + capital_expenditure

    return {
        "ticker": ticker,
        "company": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "market_cap": info.get("marketCap"),
        "enterprise_value": info.get("enterpriseValue"),
        "cash_position": {
            "total_cash": total_cash,
            "free_cash_flow": free_cash_flow,
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