from dataclasses import dataclass
from src.solar_insight import SolarInsight


@dataclass
class AddressInsight:
    address: str
    solar_insight: SolarInsight
