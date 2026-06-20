from dataclasses import dataclass
from candlestick import CandlestickMetrics
from price_levels import PriceLevelMetrics
from volatility import VolatilityMetrics
from volume import VolumeMetrics
from momentum import MomentumMetrics
from trend import TrendMetrics
from performance import PerformanceMetrics

@dataclass
class TechnicalMetrics:
    performance: PerformanceMetrics
    trend: TrendMetrics
    momentum: MomentumMetrics
    volume: VolumeMetrics
    volatility: VolatilityMetrics
    price_levels: PriceLevelMetrics
    candlesticks: CandlestickMetrics