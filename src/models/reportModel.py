from dataclasses import dataclass
from models.fundamental import FundamentalMetrics
from models.technical import TechnicalMetrics

@dataclass
class Report:
    ticker: str
    metrics: TechnicalMetrics
 #   fundamental: FundamentalMetrics
    chart: str



