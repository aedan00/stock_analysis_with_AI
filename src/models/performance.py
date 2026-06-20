from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    latest_price: float
    total_return: float
    annualized_volatility: float