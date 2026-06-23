from dataclasses import dataclass

from models.valuation import ValuationMetrics

@dataclass
class FundamentalMetrics:
    valuation: ValuationMetrics