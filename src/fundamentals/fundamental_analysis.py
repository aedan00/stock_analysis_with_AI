import pandas as pd


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

    gross_margin = None
    operating_margin = None
    net_margin = None

    if revenue is not None:

        gross_margin = gross_profit / revenue

        operating_margin = operating_income / revenue

        net_margin = net_income / revenue

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

    roa = None

    if (
        net_income is not None
        and total_assets is not None
    ):
        roa = net_income / total_assets

    # --------------------------------------------------
    # ROE
    # --------------------------------------------------

    roe = None

    if (
        net_income is not None
        and equity is not None
    ):
        roe = net_income / equity

    # --------------------------------------------------
    # Debt / Equity
    # --------------------------------------------------

    debt_to_equity = None

    if (
        total_debt is not None
        and equity is not None
    ):
        debt_to_equity = total_debt / equity

    # --------------------------------------------------
    # Current ratio
    # --------------------------------------------------

    current_ratio = None

    if (
        current_assets is not None
        and current_liabilities is not None
    ):
        current_ratio = (
            current_assets
            / current_liabilities
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