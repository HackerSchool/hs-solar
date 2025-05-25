from dataclasses import dataclass
from src.building_insight import BuildingInsight


@dataclass
class PanelInsight:
    building: BuildingInsight
    has_panel: bool
    detection_image_url: str
