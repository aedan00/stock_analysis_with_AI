from models.fundamental import FundamentalMetrics
from models.valuation import ValuationMetrics

from fundamentals.valuation import (
    calculate_valuation,
)


def analyze_fundamentals(
    info: dict,
) -> FundamentalMetrics:


    valuation_data = calculate_valuation(
        info
    )

    valuation_metrics = ValuationMetrics(
        market_cap=valuation_data["market_cap"],

        pe_ratio=valuation_data["pe_ratio"],
        pe_signal=valuation_data["pe_signal"],

        peg_ratio=valuation_data["peg_ratio"],
        peg_signal=valuation_data["peg_signal"],

        price_to_book=valuation_data["price_to_book"],
        pb_signal=valuation_data["pb_signal"],
    )


    return FundamentalMetrics(
        valuation=valuation_metrics
    )