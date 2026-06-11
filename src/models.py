from dataclasses import dataclass

@dataclass
class StockMetrics:
    latest_price: float
    total_return: float
    annualized_volatility: float
    trend: str
    rsi: float
    rsi_signal: str
    macd_signal: str