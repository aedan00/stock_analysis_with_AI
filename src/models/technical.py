from dataclasses import dataclass

from models.performance import PerformanceMetrics
from models.trend import TrendMetrics
from models.momentum import MomentumMetrics
from models.volume import VolumeMetrics
from models.volatility import VolatilityMetrics
from models.price_levels import PriceLevelMetrics
from models.candlestick import CandlestickMetrics

@dataclass
class TechnicalMetrics:

    performanceMetrics: PerformanceMetrics
    trendMetrics: TrendMetrics
    momentumMetrics: MomentumMetrics
    volumeMetrics: VolumeMetrics
    volatilityMetrics: VolatilityMetrics
    priceLevelMetrics: PriceLevelMetrics
    candlesticksMetrics: CandlestickMetrics