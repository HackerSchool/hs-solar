import folium
import json

from src import building as bd
from src import map as mp

MAX_PANELS = 300

# Load the building insight data
p1 = bd.BuildingInsight("predio1.json")
p2 = bd.BuildingInsight("predio2.json")

# Create the map centered at the building insight's center
center_lat, center_lon = p1.getLatLon()
m = mp.Map(center_lat, center_lon)

# Place solar panels on the map
m.placeSolarPanels(p1.getSolarPanels(), MAX_PANELS)
m.placeSolarPanels(p2.getSolarPanels(), MAX_PANELS)

# Save the map to an HTML file
m.save("solar_panels_map.html")