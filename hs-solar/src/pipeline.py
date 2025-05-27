from typing import List

import requests
import json
from json import JSONEncoder

from dataclasses import dataclass, asdict, is_dataclass
from datetime import datetime
import logging

from functools import cmp_to_key

from src.building_insight import BuildingInsight, Bounds, Coordinate
from src.panel_insight import PanelInsight
from src.solar_insight import SolarInsight, SolarPotential
from src.address_insight import AddressInsight

from src.encoder import dump_stage_result
from src.decorator import rate_limiter
from src.map import Map


@dataclass
class Config:
    google_cloud_key: str
    panel_detection_service: str
    bot_corner: List[float]
    top_corner: List[float]
    confidence_threshold: float


class SolarPipeline:
    def __init__(self, config: Config):
        for key, value in config.__dict__.items():
            setattr(self, key, value)

    def fetch_buildings(self, filename="buildings.json") -> List[BuildingInsight]:
        """
        Fetches buildings from OpenStreetMap using Overpass API within the given bounding box.
        :param filename: Optional filename to save the response
        :return: List of BuildingInsights coordinates (centroids)
        """
        logging.info("Running buildings stage")

        bbox = (*self.bot_corner, *self.top_corner)
        query = f"""
        [out:json];
        (
        way["building"]({",".join(str(x) for x in bbox)});
        );
        out geom;
        """

        logging.info("Requesting Overpass API for buildings insights")
        resp = requests.get("https://overpass-api.de/api/interpreter", params={"data": query})
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            logging.error("Failed requesting Overpass API: %d Error:\n %s", resp.status_code, resp.text)
            raise ValueError(f"Failed requesting Overpass API: Error {resp.status_code}\n {resp.text}")

        if resp.status_code != 200:
            logging.error("Non 200 return code from Overpass API: %d Error:\n %s", resp.status_code, resp.text)
            raise ValueError(f"Non 200 return code from Overpass API: Error {resp.status_code}\n {resp.text}")

        try:
            data = resp.json()
        except json.JSONDecodeError as e:
            logging.error("Failed to decode Overpass API JSON response:\n %s", e)
            raise ValueError(f"Failed to decode Overpass API JSON response:\n {e}")

        buildings = []
        for el in data["elements"]:
            if "nodes" in el:
                b = BuildingInsight(
                    building_id=el.get("id", ""),
                    bounds=Bounds(**el.get("bounds", {"minlat": 0, "minlon": 0, "maxlat": 0, "maxlon": 0})),
                    geometry=[Coordinate(**c) for c in el.get("geometry", [])],
                    tags=el.get("tags", {}),
                )
                buildings.append(b)

        if filename:
            logging.info("Saving buildings insights to %s", filename)
            dump_stage_result("buildings", filename, buildings)

        m = Map(self.top_corner[0], self.top_corner[1])
        for b in buildings:
            m.placeBoundingBox([(c.lat, c.lon) for c in b.geometry])
        m.save("buildings.html")
        logging.info("Saved map with buildings to buildings.html")

        return buildings

    def filter_solar_panels(self, buildings: List[BuildingInsight], filename="panels.json") -> List[PanelInsight]:
        """
        Filters buildings to only include those with solar panels.
        :param buildings: List of BuildingInsights
        :return: List of PanelInsight
        """
        logging.info("Running panels stage")
        # return buildings

        def has_panel(detection: dict, building: BuildingInsight) -> bool:
            # get center point of the detection
            center_lat = 0
            center_lon = 0
            for corner in detection["corners"]:
                center_lat += corner[0]
                center_lon += corner[1]
            center_lat /= len(detection["corners"])
            center_lon /= len(detection["corners"])

            # check if detection center is inside building bounds
            if (building.bounds.minlat <= center_lat <= building.bounds.maxlat) and (
                building.bounds.minlon <= center_lon <= building.bounds.maxlon
            ):
                return True
            return False

        @rate_limiter(calls=300, period=60)
        def request_detection(b: BuildingInsight) -> requests.Response:
            return requests.get(
                f"{self.panel_detection_service}/predict_coordinates?lat={b.centroid.lat}&long={b.centroid.lon}"
            )

        panel_insights = []
        for b in buildings:
            # get solar panel detections for each building
            rsp = request_detection(b)
            try:
                rsp.raise_for_status()
                rsp_json = rsp.json()
            except requests.exceptions.HTTPError as e:
                logging.error(
                    "Failed requesting panel detection service for %s %s: %d Error:\n %s",
                    b.centroid.lat,
                    b.centroid.lon,
                    rsp.status_code,
                    e,
                )
                continue
            except json.JSONDecodeError as e:
                logging.error("Failed to decode panel detection service JSON response:\n %s", e)
                continue

            detection_image_url = rsp_json["image"]

            w_panel = False
            for detection in rsp_json["detections"]:
                if detection["confidence"] < self.confidence_threshold:
                    continue

                if has_panel(detection, b):
                    w_panel = True
                    break

            panel_insights.append(
                PanelInsight(
                    building=b,
                    has_panel=w_panel,
                    detection_image_url=detection_image_url,
                )
            )

        if filename:
            logging.info("Saving panel buildings insights to %s", filename)
            dump_stage_result("panels", filename, panel_insights)

        return panel_insights

    def fetch_solar_data(self, buildings: List[PanelInsight], filename="solar.json") -> List[PanelInsight]:
        """
        Fetches solar data for each building with solar panels.
        :param buildings: List of PanelInsights
        :return: List of SolarInsights
        """
        logging.info("Running solar stage")
        # return buildings

        @rate_limiter(calls=60, period=60)
        def request_solar(b: PanelInsight) -> requests.Response:
            return requests.get(
                "https://solar.googleapis.com/v1/buildingInsights:findClosest?"
                f"location.latitude={b.building.centroid.lat}"
                f"&location.longitude={b.building.centroid.lon}"
                f"&requiredQuality=MEDIUM&key={self.google_cloud_key}"
            )

        solar_insights = []
        for b in buildings:
            if b.has_panel:
                continue

            rsp = request_solar(b)
            try:
                rsp.raise_for_status()
            except requests.exceptions.HTTPError:
                logging.error(
                    "Failed requesting Google Solar API API for %s %s: %d Error:\n %s",
                    b.building.centroid.lat,
                    b.building.centroid.lon,
                    rsp.status_code,
                    rsp.text,
                )
                continue

            if rsp.status_code != 200:
                logging.error("Non 200 return code from Google Solar API: %d Error:\n %s", rsp.status_code, rsp.text)
                continue

            try:
                rsp_json = rsp.json()
            except json.JSONDecodeError as e:
                logging.error("Failed to decode Google Solar API JSON response:\n %s", e)
                continue

            solar_insight = SolarInsight(
                panel_insight=b,
                solar_potential=SolarPotential.from_json(rsp_json),
            )

            solar_insights.append(solar_insight)

        if filename:
            logging.info("Saving solar data insights to %s", filename)
            dump_stage_result("solar", filename, solar_insights)

        return solar_insights

    def rank(self, solar_insights: List[SolarInsight], filename="rank.json") -> List[SolarInsight]:
        """
        Ranks the solar insights based on the yearly energy DC kWh.
        :param solar_insights: List of SolarInsights
        :return: List of SolarInsights sorted by yearly energy DC kWh
        """

        def cmp_insights(insight1: SolarInsight, insight2: SolarInsight) -> int:
            first = insight1.solar_potential.solar_panel_configs
            second = insight2.solar_potential.solar_panel_configs
            if len(first) == 0 and len(second) == 0:
                return 0
            if len(first) == 0:
                return -1
            if len(second) == 0:
                return 1

            energy1 = first[0].yearly_energy_dc_kwh
            energy2 = second[0].yearly_energy_dc_kwh
            if energy1 > energy2:
                return 1
            elif energy1 < energy2:
                return -1
            else:
                return 0

        logging.info("Ranking insights")
        ranked_solar_insights = sorted(solar_insights, key=cmp_to_key(cmp_insights), reverse=True)

        if filename:
            logging.info("Saving ranked solar data insights to %s", filename)
            dump_stage_result("ranked_solar", filename, ranked_solar_insights)

        # for e in ranked_solar_insights:
        #     rsp = requests.get()

        return ranked_solar_insights

    def get_addresses(self, solar_insights: List[SolarInsight], filename="addresses.json") -> List[AddressInsight]:
        """
        Fetches addresses for each building using Google Maps API.
        :param solar_insights: List of SolarInsights
        :return: List of SolarInsights with addresses
        """
        logging.info("Running address stage")
        # return solar_insights

        @rate_limiter(calls=300, period=60)
        def request_geocode(lat: float, lon: float) -> requests.Response:
            return requests.get(
                f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={self.google_cloud_key}"
            )

        addresses = []
        for s in solar_insights:
            rsp = request_geocode(s.panel_insight.building.centroid.lat, s.panel_insight.building.centroid.lon)
            try:
                rsp.raise_for_status()
            except requests.exceptions.HTTPError:
                logging.error(
                    "Failed requesting Google Maps Geocode API for %s %s: %d Error:\n %s",
                    s.panel_insight.building.centroid.lat,
                    s.panel_insight.building.centroid.lon,
                    rsp.status_code,
                    rsp.text,
                )
                continue

            if rsp.status_code != 200:
                logging.error("Non 200 return code from Google Solar API: %d Error:\n %s", rsp.status_code, rsp.text)
                continue

            try:
                rsp_json = rsp.json()
            except json.JSONDecodeError as e:
                logging.error("Failed to decode Google Solar API JSON response:\n %s", e)
                continue

            if (
                "results" not in rsp_json
                or len(rsp_json["results"]) == 0
                or "formatted_address" not in rsp_json["results"][0]
            ):
                addresses.append(AddressInsight(solar_insight=s, address=""))
                continue

            addresses.append(AddressInsight(solar_insight=s, address=rsp_json["results"][0]["formatted_address"]))

        if filename:
            logging.info("Saving address data insights to %s", filename)
            dump_stage_result("addresses", filename, addresses)

        return addresses
