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
    current_volume: int
    average_volume: float
    relative_volume: float
    volume_signal: str

@dataclass
class Report:
    ticker: str
    metrics: StockMetrics
    chart: str