from dataclasses import dataclass

@dataclass
class StockMetrics:
    #Performance
    latest_price: float
    total_return: float
    annualized_volatility: float

    #Trend
    trend: str

    #Momentum
    rsi: float
    rsi_signal: str
    macd_signal: str

    #Volume
    current_volume: int
    average_volume: float
    relative_volume: float
    volume_signal: str

    #Volatility: Average True Range
    atr: float
    atr_percent: float
    volatility: str

    # Bollinger Bands
    bb_upper: float
    bb_middle: float
    bb_lower: float
    bb_signal: str
    bb_bandwidth: float

    #adx
    current_adx: float
    plus_di: float
    minus_di: float
    adx_signal: str
    di_signal: str

    #obv
    obv: float
    obv_signal: str

    # support & resistance
    support: float | None
    resistance: float | None
    sr_signal: str

    #stochastic
    stochastic_k: float
    stochastic_d: float
    stochastic_signal: str

    #candlesticks
    candlestick_patterns: list[str]


@dataclass
class Report:
    ticker: str
    metrics: StockMetrics
    chart: str