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
