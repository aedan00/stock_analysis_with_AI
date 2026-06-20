from dataclasses import dataclass

@dataclass
class VolumeMetrics:
    current_volume: int
    average_volume: float
    relative_volume: float
    volume_signal: str

    obv: float
    obv_signal: str