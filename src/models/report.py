from dataclasses import dataclass
from fundamental import FundamentalMetrics
from technical import TechnicalMetrics

@dataclass
class Report:
    ticker: str
    technical: TechnicalMetrics
    fundamental: FundamentalMetrics
    chart: str