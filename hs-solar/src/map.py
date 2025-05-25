import folium

DEFAULT_N_PANELS = 15


class Map:
    m = None

    def __init__(self, center_lat, center_lon):
        self.m = folium.Map(
            location=[center_lat, center_lon], zoom_start=18, max_zoon=100
        )

    def placeSolarPanels(self, solar_panels: dict, limit=DEFAULT_N_PANELS):
        count = 0
        for panel in solar_panels:
            if count >= limit:
                break
            lat, lon = panel["center"]["latitude"], panel["center"]["longitude"]
            yearly_energy = panel["yearlyEnergyDcKwh"]
            orientation = panel["orientation"]
            segment_index = panel["segmentIndex"]

            if yearly_energy > 700:
                color = "green"
            elif yearly_energy > 650:
                color = "orange"
            else:
                color = "red"

            folium.CircleMarker(
                location=[lat, lon],
                radius=3,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                popup=f"Yearly Energy: {yearly_energy} kWh<br>Orientation: {orientation}<br>Segment: {segment_index}",
            ).add_to(self.m)

            count += 1

    def addPoint(self, lat, lon):
        folium.CircleMarker(
            location=[lat, lon],
            radius=3,
            fill_opacity=0.7,
        ).add_to(self.m)

    def placeBoundingBox(self, bbox: list):
        folium.Polygon(
            locations=bbox, color="blue", fill=True, fill_opacity=0.5
        ).add_to(self.m)

    def save(self, filename):
        self.m.save(filename)
