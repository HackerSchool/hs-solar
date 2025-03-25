import requests
import folium, json, time
from shapely.geometry import shape, Point

class Buildings:
    boundingBox = None
    buildings = []

    def __init__(self, min_lat, min_lon, max_lat, max_lon, filename = None):
        self.boundingBox = (min_lat, min_lon, max_lat, max_lon)
        self.buildings = self.init_buildings(filename=filename)

    def init_buildings(self, filename = None):
        """
        Fetches buildings from OpenStreetMap using Overpass API within the given bounding box.
        :param bbox: Tuple (min_lat, min_lon, max_lat, max_lon)
        :return: List of building coordinates (centroids)
        """
        bbox = self.boundingBox
        overpass_url = "https://overpass-api.de/api/interpreter"
        query = f"""
        [out:json];
        (
        way["building"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
        );
        out geom;
        """
        
        response = requests.get(overpass_url, params={"data": query})
        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            return []
        data = response.json()
        if filename:
            print("Saving buildings to file...")
            json.dump(data, open(filename, "w"), indent=2)
        buildings = []
        for element in data["elements"]:
            if "nodes" in element:
                coords = [(node["lat"], node["lon"]) for node in element.get("geometry", [])]
                if coords:
                    centroid = Point(shape({"type": "Polygon", "coordinates": [coords]}).centroid)
                    b = BuildingInsight(centroid.x, centroid.y)
                    b.setInfo(element)
                    buildings.append(b)
        return buildings
    
    def getBuildings(self):
        return self.buildings

class BuildingInsight:
    # TODO add address support
    # TODO add solar info support
    json_file = None
    info = None
    center_lat = None
    center_lon = None

    adress = None
    solar_info = None

    #def __init__(self, json_file):
    #    self.json_file = json_file
    #    self.info = json.load(open(json_file))
    #    self.center_lat = self.info["solarPotential"]["solarPanels"][0]["center"]["latitude"]
    #    self.center_lon = self.info["solarPotential"]["solarPanels"][0]["center"]["longitude"]

    def __init__(self, center_lat, center_lon):
        self.center_lat = center_lat
        self.center_lon = center_lon

    def getSolarPanels(self):
        return self.solar_info["solarPotential"]["solarPanels"]
    
    def getLatLon(self):
        return self.center_lat, self.center_lon
    
    def getBoundingBox(self):
        element = self.info
        coords = []
        if "geometry" in element:
            coords = [(point["lat"], point["lon"]) for point in element["geometry"]]
        return coords
    
    def getCenter(self):
        return self.info["center"]
    
    def setInfo(self, info: dict):
        self.info = info

    def getInfo(self):
        return self.info
    
    def setAdress(self, adress):
        self.adress = adress

    def getAdress(self):
        return self.adress

    def loadSolarInfo(self, filename):
        try:
            with open(filename, "r") as f:
                self.solar_info = json.load(f)
        except Exception as e:
            print("Error loading solar info from file.")
            print(e)
            return None