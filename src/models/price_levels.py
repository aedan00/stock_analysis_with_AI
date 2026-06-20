from dataclasses import dataclass

@dataclass
class PriceLevelMetrics:
    support: float | None
    resistance: float | None
    sr_signal: str

    pivot: float
    pivot_r1: float
    pivot_r2: float
    pivot_r3: float
    pivot_s1: float
    pivot_s2: float
    pivot_s3: float
    pivot_signal: str

    fib_23_6: float
    fib_38_2: float
    fib_50: float
    fib_61_8: float
    fib_78_6: float
    fib_signal: str