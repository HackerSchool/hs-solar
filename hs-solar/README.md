# ☀️ HS-Solar 

A command-line tool to gather, analyze, and render solar panel insights for buildings in a specified geographical area.

## 📦 Features

- Fetch buildings within a specified region.
- Detect buildings with solar panels via an external detection service.
- Retrieve solar information and ranking.
- Fetch building addresses.
- Render an HTML report from ranked results.

---

## 🔧 Configuration

Before running any commands, configure the script using the config file. Here's an example:

```yaml
google_cloud_key: "" # GCP API key for project with Solar API, Maps Static API and Geocoding API services activated
panel_detection_service: "http://localhost:5000"     # root URL of the detection service
top_corner: [38.69999341381147, -9.301351421573495]  # northeast corner of the bounding box
bot_corner: [38.687996467877966, -9.314670765744175] # southwest corner of the bounding box
confidence_threshold: 0.95  # confidence threshold for panel detection
```

## 🚀 Usage
Run the CLI using:

```bash
python main.py <command> [--options]
```
Replace `main.py` with your entry point file if named differently.

## 📚 Commands

### `buildings`

Fetch geographic building information within the defined region.

    python main.py buildings --file buildings.json

- `--file`: Path to save the resulting building data.

Additionally, generates a `buildings.html` file with an interactive map preview of the buildings in the specified region.

---

### `panels`

Filters buildings with solar panels.

    python main.py panels --file panels.json --buildings buildings.json

- `--file`: Path to save results.
- `--buildings`: Optional. Use a local buildings file. If not provided, data is fetched.

---

### `solar`

Get solar information for detected buildings.

    python main.py solar --file solar.json --panels panels.json

- `--file`: Path to save results.
- `--panels`: Optional. Use a local panels file. If not provided, data is fetched.

---

### `rank`

Rank buildings based on solar potential.

    python main.py rank --file rank.json --solar solar.json

- `--file`: Path to save ranked data.
- `--solar`: Optional. Use a local solar info file. If not provided, data is fetched.

---

### `address`

Get human-readable addresses for buildings.

    python main.py address --file addresses.json --solar solar.json

- `--file`: Path to save addresses.
- `--solar`: Optional. Use a local solar info file. If not provided, data is fetched.

---

### `render`

Render a report from ranked address data.

    python main.py render --html_file report.html --addresses addresses.json

- `--html_file`: Output file for the HTML report.
- `--addresses`: Optional. Use local address data. If not provided, data is fetched.

## 📝 Observations


- This tool is currently **only a proof of concept**, and some shortcuts were made during development.
- The most important enhancement needed is implementing **client-side rate limiting and retries** on external API calls. At present, the tool takes a very modest approach to consuming external services, which makes it unnecessarily slow.
- Other less critical improvements might include:
  - Storing run results in a NoSQL database for better data management.
  - Packaging the script for easier distribution and installation.
  - Implementing external Google Cloud Platform (GCP) user authentication.
  - Creating a more user-friendly graphical user interface (UI).