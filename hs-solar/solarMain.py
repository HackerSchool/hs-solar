import requests
import time

from src import map as mp
from src import building as bd

import json

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"

PANELS_API = "http://192.168.1.140:5003/"
CONFIDENCE_THRESHOLD = 0.8

SOLAR_API = "https://solar.googleapis.com/v1/buildingInsights"
SOLAR_KEY = "yourKey"

########################################################################################
# Quick example on how to get the address of a building
# TODO: take addresses of the buildings
def get_address(lat, lon):
    """ Fetch address from Nominatim Reverse Geocoding API """
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "addressdetails": 1
    }
    headers = {
        "User-Agent": "HS-Solar/1.0 (filipepicarra@tecnico.ulisboa.pt)"  # Replace with your details
    }
    response = requests.get(NOMINATIM_URL, params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("display_name")
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def get_addresses(buildings):
    """ Get addresses for a list of building coordinates """
    addresses = {}
    for lat, lon in buildings:
        address = get_address(lat, lon)
        if address:
            addresses[(lat, lon)] = address
        print(f"Address for ({lat}, {lon}):\n{address}\n")
        # Sleep for 250 ms to avoid rate limiting
        time.sleep(0.250)
    return addresses
########################################################################################

def hasPanel(building: bd.BuildingInsight):
    lat, lon = building.getCenter()
    call = PANELS_API + "predict_coordinates?lat=" + str(lat) + "&long=" + str(lon)

    response = requests.get(call)
    if(response.status_code != 200):
        print(f"Error {response.status_code}: {response.text}")
        return False
    
    bounds = building.getMaxBounds()
    center_lat, center_lon = 0, 0
    data = response.json()
    data = data["detections"]
    for detection in data:
        if(detection["confidence"] >= CONFIDENCE_THRESHOLD):
            for corner in detection["corners"]:
                center_lat += corner[0]
                center_lon += corner[1]
            center_lat /= len(detection["corners"])
            center_lon /= len(detection["corners"])

            # Check if the center of the building is within the bounding box
            if (bounds[0] <= center_lat <= bounds[2]) and (bounds[1] <= center_lon <= bounds[3]):
                return True
    return False

def getSolar(building: bd.BuildingInsight):
    lat, lon = building.getCenter()
    call = SOLAR_API + ":findClosest?location.latitude=" + str(lat) + "&location.longitude=" + \
        str(lon) + "&requiredQuality=LOW&key=" + SOLAR_KEY
    
    response = requests.get(call)
    if(response.status_code != 200):
        print(f"Error {response.status_code}: {response.text}")
        return None
    return response.json()

if __name__ == "__main__":
    # Example bounding box for Lisbon, Portugal
    #bbox_lisbon = (38.67341041544132, -9.161527409275678, 38.67855145901363, -9.158915586575736) 
    #bbox_lisbon = (38.71335969833295, -9.144428411236115, 38.72609494053631, -9.139108746002357)
    bbox_lisbon = (38.67184023283974, -9.157275666592053, 38.673366872623156, -9.15525042856257)
    bbox_lisbon = (38.68908225615068, -9.312777615027736, 38.689884345213294, -9.31200646480284)
    
    buldings = bd.Buildings(*bbox_lisbon, filename="buildings_lisbon.json")
    m = mp.Map(bbox_lisbon[0], bbox_lisbon[1]) # TODO center of the bounding box

    b = buldings.getBuildings()
    #for building in b:
    #    m.placeBoundingBox(building.getBoundingBox())

    ########################################################################################
    # Quick example on how to load solar API info,
    # what needs to happen is that we parse which bildings are eligible for the solar panels
    # and then request the JSON data to the API

    # TODO: request solar API info for each building
    # b[0].loadSolarInfo("predio1.json")
    # b[1].loadSolarInfo("predio2.json")

    # m.placeSolarPanels(b[0].getSolarPanels(), limit=250)
    # m.placeSolarPanels(b[1].getSolarPanels(), limit=250)
    ########################################################################################

    # Remove buildings with sonal panels
    b_wo_panels = []
    for building in b:
        if(not hasPanel(building)):
            b_wo_panels.append(building)

    for building in b_wo_panels:
        m.placeBoundingBox(building.getBoundingBox())

    # Pass buildings through the Solar API
    for building in b_wo_panels:
        building.setSolarInfo(getSolar(building))

    # Save all info a json object
    out = {"buildings": []}
    for building in b_wo_panels:
        entry = {}
        entry["info"] = building.getInfo()
        entry["solar"] = building.getSolarInfo()
        out["buildings"].append(entry)
    with open("buildings.json", "w") as f:
        json.dump(out, f, indent=2)

    m.save("buildings_map.html")
