import yfinance as yf

from models.valuation import ValuationMetrics


def calculate_valuation(
    info: dict,
):

    market_cap = info.get(
        "marketCap"
    )

    pe = info.get(
        "trailingPE"
    )

    peg = info.get(
        "pegRatio"
    )

    pb = info.get(
        "priceToBook"
    )


    return {
        "market_cap": market_cap,

        "pe_ratio": pe,
        "pe_signal": get_pe_signal(pe),

        "peg_ratio": peg,
        "peg_signal": get_peg_signal(peg),

        "price_to_book": pb,
        "pb_signal": get_pb_signal(pb),
    }


def get_pe_signal(
    pe: float | None,
) -> str:

    if pe is None:
        return "Unavailable"

    if pe <= 0:
        return "Negative Earnings"

    if pe < 15:
        return "Potentially Undervalued"

    if pe < 25:
        return "Fairly Valued"

    return "Expensive"


def get_peg_signal(
    peg: float | None,
) -> str:

    if peg is None:
        return "Unavailable"

    if peg < 1:
        return "Undervalued Growth"

    if peg <= 2:
        return "Reasonable"

    return "Expensive Growth"


def get_pb_signal(
    pb: float | None,
) -> str:

    if pb is None:
        return "Unavailable"

    if pb < 1:
        return "Below Book Value"

    if pb < 3:
        return "Fair Value"

    return "Premium Valuation"