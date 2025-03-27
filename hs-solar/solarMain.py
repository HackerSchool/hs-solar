import requests
import time

from src import map as mp
from src import building as bd

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"

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

if __name__ == "__main__":
    # Example bounding box for Lisbon, Portugal
    bbox_lisbon = (38.67341041544132, -9.161527409275678, 38.67855145901363, -9.158915586575736) 
    #bbox_lisbon = (38.71335969833295, -9.144428411236115, 38.72609494053631, -9.139108746002357)

    buldings = bd.Buildings(*bbox_lisbon, filename="buildings_lisbon.json")
    m = mp.Map(bbox_lisbon[0], bbox_lisbon[1]) # TODO center of the bounding box

    b = buldings.getBuildings()
    for building in b:
        m.placeBoundingBox(building.getBoundingBox())

    # TODO: iterate over building to see eligible buildings for solar panels

    ########################################################################################
    # Quick example on how to load solar API info,
    # what needs to happen is that we parse which bildings are eligible for the solar panels
    # and then request the JSON data to the API

    # TODO: request solar API info for each building
    b[0].loadSolarInfo("predio1.json")
    b[1].loadSolarInfo("predio2.json")

    m.placeSolarPanels(b[0].getSolarPanels(), limit=250)
    m.placeSolarPanels(b[1].getSolarPanels(), limit=250)
    ########################################################################################

    m.save("buildings_map.html")
