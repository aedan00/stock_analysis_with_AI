from dataclasses import dataclass

@dataclass
class TrendMetrics:
    trend: str

    current_adx: float
    plus_di: float
    minus_di: float
    adx_signal: str
    di_signal: str