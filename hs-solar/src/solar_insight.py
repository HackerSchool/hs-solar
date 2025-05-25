from dataclasses import dataclass
from src.building_insight import Coordinate
from src.panel_insight import PanelInsight

# https://developers.google.com/maps/documentation/solar/reference/rest/v1/buildingInsights/findClosest#SolarPotential


@dataclass
class RoofSegmentSummary:
    panels_count: int
    yearly_energy_dc_kwh: float
    pitch_degrees: float
    azimuth_degrees: float
    segment_index: int


@dataclass
class SolarPanelConfig:
    panels_count: int
    yearly_energy_dc_kwh: int
    roof_segment_summaries: list[RoofSegmentSummary]


@dataclass
class SolarPanel:
    center: Coordinate
    yearly_energy_dc_kwh: float
    orientation: str
    segment_index: int


@dataclass
class SizeAndSunshineStats:
    area: float
    sunshine_quantiles: list[float]


@dataclass
class RoofSegmentStats:
    center: Coordinate
    stats: SizeAndSunshineStats
    pitch_degrees: float
    azimuth_degrees: float
    panel_height_at_center_meters: float


@dataclass
class SolarPotential:
    max_panels: int
    panel_capacity: float
    panel_height_meters: float
    panel_width_meters: float
    panel_lifetime_years: int
    max_array_area_meters_2: float
    max_sunshine_hours_year: float
    carbon_offset_kg: float
    whole_roof_stats: SizeAndSunshineStats
    roof_segments_stats: list[RoofSegmentStats]
    solar_panels: list[SolarPanel]
    solar_panel_configs: list[SolarPanelConfig]

    @staticmethod
    def from_json(json_data):
        # should probably look for a library that can do this automaticall
        return SolarPotential(
            max_panels=json_data.get("solarPotential", {}).get("maxArrayPanelsCount", None),
            panel_capacity=json_data.get("solarPotential", {}).get("panelCapacityWatts", None),
            panel_height_meters=json_data.get("solarPotential", {}).get("panelHeightMeters", None),
            panel_width_meters=json_data.get("solarPotential", {}).get("panelWidthMeters", None),
            panel_lifetime_years=json_data.get("solarPotential", {}).get("panelLifetimeYears", None),
            max_array_area_meters_2=json_data.get("solarPotential", {}).get("maxArrayAreaMeters2", None),
            max_sunshine_hours_year=json_data.get("solarPotential", {}).get("maxSunshineHoursYear", None),
            carbon_offset_kg=json_data.get("solarPotential", {}).get("carbonOffsetFactorKgPerMwh", None),
            whole_roof_stats=SizeAndSunshineStats(
                area=json_data.get("solarPotential", {}).get("wholeRoofStats", {}).get("areaMeters2", None),
                sunshine_quantiles=[
                    q
                    for q in json_data.get("solarPotential", {}).get("wholeRoofStats", {}).get("sunshineQuantiles", [])
                ],
            ),
            roof_segments_stats=[
                RoofSegmentStats(
                    center=Coordinate(
                        lat=rs.get("center", {}).get("latitude", None), lon=rs.get("center", {}).get("longitude", None)
                    ),
                    stats=SizeAndSunshineStats(
                        area=rs.get("stats", {}).get("areaMeters2", None),
                        sunshine_quantiles=[q for q in rs.get("stats", {}).get("sunshineQuantiles", [])],
                    ),
                    pitch_degrees=rs.get("pitchDegrees", None),
                    azimuth_degrees=rs.get("azimuthDegrees", None),
                    panel_height_at_center_meters=rs.get(
                        "panelHeightAtCenterMeters",
                    ),
                )
                for rs in json_data.get("solarPotential", {}).get("roofSegmentStats", [])
            ],
            solar_panels=[
                SolarPanel(
                    center=Coordinate(
                        lat=sp.get("center", {}).get("latitude", None), lon=sp.get("center", {}).get("longitude", None)
                    ),
                    yearly_energy_dc_kwh=sp.get("yearlyEnergyDcKwh", None),
                    orientation=sp.get("orientation", ""),
                    segment_index=sp.get("segmentIndex", None),
                )
                for sp in json_data.get("solarPotential", {}).get("solarPanels", [])
            ],
            solar_panel_configs=[
                SolarPanelConfig(
                    panels_count=spc.get("panelsCount", None),
                    yearly_energy_dc_kwh=spc.get("yearlyEnergyDcKwh", None),
                    roof_segment_summaries=[
                        RoofSegmentSummary(
                            panels_count=rss.get("panelsCount", None),
                            yearly_energy_dc_kwh=rss.get("yearlyEnergyDcKwh", None),
                            pitch_degrees=rss.get("pitchDegrees", None),
                            azimuth_degrees=rss.get("azimuthDegrees", None),
                            segment_index=rss.get("segmentIndex", None),
                        )
                        for rss in spc.get("roofSegmentSummaries", [])
                    ],
                )
                for spc in json_data.get("solarPotential", {}).get("solarPanelConfigs", [])
            ],
        )


@dataclass
class SolarInsight:
    panel_insight: PanelInsight
    solar_potential: SolarPotential
