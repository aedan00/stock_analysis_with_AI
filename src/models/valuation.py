from dataclasses import dataclass

@dataclass
class ValuationMetrics:
    market_cap: float | None

    pe_ratio: float | None
    pe_signal: str

    peg_ratio: float | None
    peg_signal: str

    price_to_book: float | None
    pb_signal: str