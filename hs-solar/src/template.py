from jinja2 import Template
from src.address_insight import AddressInsight
from src.pipeline import Config

template_str = """
<!DOCTYPE html>
<html>
<head>
    <title>Ranking</title>
    <style>
        table, th, td {
            text-align: center;
            vertical-align: middle;
        }
</style>
</head>
<body>
    <table border="1">
        <thead>
          <tr>
            <th>Address</th>
            <th>Latitude</th>
            <th>Longitude</th>
            <th>Configuration Panel Count</th>
            <th>Yearly Energy DC (kWh)</th>
            <th>Aerial Detection Image</th>
          </tr>
        </thead>
        <tbody>
        {% for addr in address_insights %}
          <tr>
            <td>{{ addr.address }}</td>
            <td>{{ addr.solar_insight.panel_insight.building.centroid.lat }}</td>
            <td>{{ addr.solar_insight.panel_insight.building.centroid.lon }}</td>
            {% set configs = addr.solar_insight.solar_potential.solar_panel_configs %}
              {% if configs and configs|length > 0 %}
                  <td>{{ configs[0].panels_count }}</td>
                  <td>{{ configs[0].yearly_energy_dc_kwh }}</td>
              {% else %}
                  <td>N/A</td>
                  <td>N/A</td>
              {% endif %}
            <td>
                <a href="{{ config.panel_detection_service }}/{{ addr.solar_insight.panel_insight.detection_image_url }}" target="_blank">
                    {{ addr.solar_insight.panel_insight.detection_image_url.lstrip("results/") }}
                </a>
            </td>
          </tr>
        {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""


def render_ranking_template(config: Config, address_insights: list[AddressInsight], html_file: str) -> str:
    template = Template(template_str)
    output = template.render(config=config, address_insights=address_insights)

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(output)


def render_csv_template(config: Config, address_insights: list[AddressInsight], csv_file: str) -> str:
    with open(csv_file, "w", encoding="utf-8") as f:
        f.write("Address,Latitude,Longitude,Configuration Panel Count,Yearly Energy DC (kWh),Aerial Detection Image\n")
        for addr in address_insights:
            lat = addr.solar_insight.panel_insight.building.centroid.lat
            lon = addr.solar_insight.panel_insight.building.centroid.lon
            configs = addr.solar_insight.solar_potential.solar_panel_configs
            if configs and len(configs) > 0:
                panels_count = configs[0].panels_count
                yearly_energy_dc_kwh = configs[0].yearly_energy_dc_kwh
            else:
                panels_count = "N/A"
                yearly_energy_dc_kwh = "N/A"
            detection_image_url = addr.solar_insight.panel_insight.detection_image_url.lstrip("results/")
            f.write(
                f"{addr.address},{lat},{lon},{panels_count},{yearly_energy_dc_kwh},{config.panel_detection_service}/{detection_image_url}\n"
            )
