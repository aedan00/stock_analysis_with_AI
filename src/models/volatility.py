from dataclasses import dataclass

@dataclass
class VolatilityMetrics:
    atr: float
    atr_percent: float
    volatility: str

    bb_upper: float
    bb_middle: float
    bb_lower: float
    bb_bandwidth: float
    bb_signal: str