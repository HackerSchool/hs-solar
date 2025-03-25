import folium

# Example data from the API response
roof_segment_stats = [
        {
          "pitchDegrees": 22.439005,
          "azimuthDegrees": 250.22649,
          "stats": {
            "areaMeters2": 89.60426,
            "sunshineQuantiles": [
              390.82538,
              1301.5073,
              1603.2637,
              1648.0955,
              1658.9692,
              1666.9606,
              1673.8635,
              1679.4534,
              1685.8224,
              1698.3386,
              1850.5
            ],
            "groundAreaMeters2": 82.82
          },
          "center": {
            "latitude": 38.6739075,
            "longitude": -9.1603
          },
          "boundingBox": {
            "sw": {
              "latitude": 38.6738223,
              "longitude": -9.1603617
            },
            "ne": {
              "latitude": 38.6739783,
              "longitude": -9.1602406
            }
          },
          "planeHeightAtCenterMeters": 44.012238
        },
        {
          "pitchDegrees": 18.696873,
          "azimuthDegrees": 71.59903,
          "stats": {
            "areaMeters2": 60.513428,
            "sunshineQuantiles": [
              334.9688,
              1019.9205,
              1400.106,
              1485.6339,
              1509.8466,
              1530.8905,
              1545.5643,
              1557.4309,
              1566.7742,
              1578.7771,
              1709.7036
            ],
            "groundAreaMeters2": 57.32
          },
          "center": {
            "latitude": 38.6739275,
            "longitude": -9.1601839
          },
          "boundingBox": {
            "sw": {
              "latitude": 38.6738567,
              "longitude": -9.160218
            },
            "ne": {
              "latitude": 38.6739983,
              "longitude": -9.160143
            }
          },
          "planeHeightAtCenterMeters": 43.425343
        },
        {
          "pitchDegrees": 20.507782,
          "azimuthDegrees": 162.01596,
          "stats": {
            "areaMeters2": 51.354618,
            "sunshineQuantiles": [
              713.8026,
              1370.2897,
              1635.2384,
              1741.9159,
              1789.975,
              1809.289,
              1820.9626,
              1826.669,
              1831.6864,
              1835.8367,
              1851.929
            ],
            "groundAreaMeters2": 48.1
          },
          "center": {
            "latitude": 38.6738526,
            "longitude": -9.160219399999999
          },
          "boundingBox": {
            "sw": {
              "latitude": 38.6738206,
              "longitude": -9.1602775
            },
            "ne": {
              "latitude": 38.6738883,
              "longitude": -9.1601567
            }
          },
          "planeHeightAtCenterMeters": 43.707867
        },
        {
          "pitchDegrees": 0.13742384,
          "azimuthDegrees": 0,
          "stats": {
            "areaMeters2": 26.980078,
            "sunshineQuantiles": [
              700.42426,
              1216.813,
              1379.0452,
              1566.2931,
              1652.0249,
              1685.7611,
              1693.4371,
              1696.4717,
              1698.8926,
              1701.1249,
              1842.633
            ],
            "groundAreaMeters2": 26.98
          },
          "center": {
            "latitude": 38.6739184,
            "longitude": -9.1602494
          },
          "boundingBox": {
            "sw": {
              "latitude": 38.6738809,
              "longitude": -9.1602833999999991
            },
            "ne": {
              "latitude": 38.673948599999996,
              "longitude": -9.1602177
            }
          },
          "planeHeightAtCenterMeters": 46.132687
        },
        {
          "pitchDegrees": 23.48352,
          "azimuthDegrees": 70.68997,
          "stats": {
            "areaMeters2": 25.207848,
            "sunshineQuantiles": [
              604.88367,
              1182.1499,
              1359.7009,
              1440.0596,
              1480.9227,
              1505.7933,
              1517.6927,
              1526.5887,
              1537.5552,
              1606.2843,
              1836.5134
            ],
            "groundAreaMeters2": 23.12
          },
          "center": {
            "latitude": 38.6739652,
            "longitude": -9.160245
          },
          "boundingBox": {
            "sw": {
              "latitude": 38.6739287,
              "longitude": -9.1602778
            },
            "ne": {
              "latitude": 38.6739937,
              "longitude": -9.160217900000001
            }
          },
          "planeHeightAtCenterMeters": 44.925087
        },
        {
          "pitchDegrees": 23.77646,
          "azimuthDegrees": 71.43615,
          "stats": {
            "areaMeters2": 7.8787017,
            "sunshineQuantiles": [
              822.7384,
              1362.4119,
              1423.7831,
              1477.1418,
              1493.1534,
              1504.4225,
              1511.63,
              1519.8577,
              1553.4728,
              1632.0829,
              1758.7306
            ],
            "groundAreaMeters2": 7.21
          },
          "center": {
            "latitude": 38.6738941,
            "longitude": -9.160207999999999
          },
          "boundingBox": {
            "sw": {
              "latitude": 38.6738837,
              "longitude": -9.160235
            },
            "ne": {
              "latitude": 38.6739063,
              "longitude": -9.160188999999999
            }
          },
          "planeHeightAtCenterMeters": 44.73378
        }
      ]

# Function to calculate the best solar exposure
def get_best_segment(segments):
    best_segment = None
    best_solar_value = 0

    for segment in segments:
        # Use the maximum value in sunshineQuantiles as the metric
        max_solar = max(segment["stats"]["sunshineQuantiles"])
        if max_solar > best_solar_value:
            best_solar_value = max_solar
            best_segment = segment

    return best_segment

# Find the roof segment with the best solar exposure
best_segment = get_best_segment(roof_segment_stats)

# Create a map centered at the best roof segment's center
center_lat = best_segment["center"]["latitude"]
center_lon = best_segment["center"]["longitude"]
m = folium.Map(location=[center_lat, center_lon], zoom_start=18)

# Draw bounding boxes and add markers for each roof segment
for segment in roof_segment_stats:
    sw_lat, sw_lon = segment["boundingBox"]["sw"]["latitude"], segment["boundingBox"]["sw"]["longitude"]
    ne_lat, ne_lon = segment["boundingBox"]["ne"]["latitude"], segment["boundingBox"]["ne"]["longitude"]
    bounding_box_coords = [[sw_lat, sw_lon], [ne_lat, ne_lon]]

    # Check if this is the best segment
    if segment == best_segment:
        color = "#00ff00"  # Green for the best segment
        fill_color = "#00ff00"
        popup = f"Best Solar Exposure: {max(segment['stats']['sunshineQuantiles'])} kWh/m²/year<br>Area: {segment['stats']['areaMeters2']} m²"
    else:
        color = "#ff7800"  # Orange for other segments
        fill_color = "#ffff00"
        popup = f"Solar Exposure: {max(segment['stats']['sunshineQuantiles'])} kWh/m²/year<br>Area: {segment['stats']['areaMeters2']} m²"

    # Draw the bounding box
    folium.Rectangle(
        bounds=bounding_box_coords,
        color=color,
        fill=True,
        fill_color=fill_color,
        fill_opacity=0.2,
        popup=popup
    ).add_to(m)

    # Add a marker at the center of the roof segment
    #folium.Marker(
    #    location=[segment["center"]["latitude"], segment["center"]["longitude"]],
    #    popup=f"Pitch: {segment['pitchDegrees']}°<br>Azimuth: {segment['azimuthDegrees']}°"
    #).add_to(m)

# Save the map to an HTML file
m.save("best_roof_segment_map.html")

# Display the map in a web browser
import webbrowser
webbrowser.open("best_roof_segment_map.html")