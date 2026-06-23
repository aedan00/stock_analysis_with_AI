from dataclasses import dataclass

@dataclass
class MomentumMetrics:
    rsi: float
    rsi_signal: str
    macd_signal: str

    stochastic_k: float
    stochastic_d: float
    stochastic_signal: str
