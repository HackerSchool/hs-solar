import streamlit as st
import json
import yaml
from pathlib import Path
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
import pandas as pd
import plotly.express as px
from src.pipeline import SolarPipeline, Config
from src.building_insight import BuildingInsight
from src.panel_insight import PanelInsight
from src.solar_insight import SolarInsight
from src.encoder import load_stage_result, dump_stage_result

# Set page config
st.set_page_config(
    page_title="HS-Solar Dashboard",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'config' not in st.session_state:
    st.session_state.config = None
if 'pipeline' not in st.session_state:
    st.session_state.pipeline = None
if 'buildings' not in st.session_state:
    st.session_state.buildings = None
if 'panels' not in st.session_state:
    st.session_state.panels = None
if 'solar' not in st.session_state:
    st.session_state.solar = None
if 'points' not in st.session_state:
    st.session_state.points = []

def update_coords():
    """Update coordinates when manual inputs change"""
    st.session_state.config.update({
        'top_corner': [st.session_state.top_lat, st.session_state.top_lon],
        'bot_corner': [st.session_state.bot_lat, st.session_state.bot_lon]
    })
    save_config(st.session_state.config)
    st.rerun()

def load_config():
    """Load configuration from config.yaml"""
    try:
        with open('config.yaml', 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        st.error("config.yaml not found! Please create it first.")
        return None

def save_config(config):
    """Save configuration to config.yaml"""
    with open('config.yaml', 'w') as f:
        yaml.dump(config, f)

def create_selection_map():
    """Create a map with synchronized rectangle and markers"""
    m = folium.Map(
        location=[0, 0],
        zoom_start=2,
        tiles="OpenStreetMap"
    )
    
    draw = Draw(
        draw_options={
            'polyline': False,
            'polygon': False,
            'circle': False,
            'circlemarker': False,
            'marker': False,  # Disable markers for cleaner rectangle handling
            'rectangle': {
                'shapeOptions': {
                    'color': 'red',
                    'fillColor': 'red',
                    'fillOpacity': 0.1
                }
            }
        },
        edit_options={'edit': True}
    )
    draw.add_to(m)

    # Add rectangle from current config if exists
    if st.session_state.config and st.session_state.config['top_corner'] != [0, 0]:
        folium.Rectangle(
            bounds=[
                [st.session_state.config['bot_corner'][0], st.session_state.config['bot_corner'][1]],
                [st.session_state.config['top_corner'][0], st.session_state.config['top_corner'][1]]
            ],
            color='red',
            fill=True,
            fill_opacity=0.1
        ).add_to(m)
    
    return m

def create_analysis_map(buildings, center_lat=None, center_lon=None):
    """Create a map for displaying building analysis results"""
    if center_lat is None or center_lon is None:
        center_lat = (st.session_state.config['top_corner'][0] + st.session_state.config['bot_corner'][0]) / 2
        center_lon = (st.session_state.config['top_corner'][1] + st.session_state.config['bot_corner'][1]) / 2
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=15,
        tiles="OpenStreetMap"
    )
    
    # Add rectangle for the region of interest
    folium.Rectangle(
        bounds=[
            [st.session_state.config['bot_corner'][0], st.session_state.config['bot_corner'][1]],
            [st.session_state.config['top_corner'][0], st.session_state.config['top_corner'][1]]
        ],
        color='red',
        fill=True,
        fill_opacity=0.1
    ).add_to(m)
    
    # Add markers for buildings
    for building in buildings:
        if isinstance(building, PanelInsight):
            lat = building.building.centroid.lat
            lon = building.building.centroid.lon
            has_panel = building.has_panel
            building_id = building.building.building_id
        else:  # BuildingInsight
            lat = building.centroid.lat
            lon = building.centroid.lon
            has_panel = False
            building_id = building.building_id
        
        color = 'green' if has_panel else 'blue'
        folium.CircleMarker(
            location=[lat, lon],
            radius=5,
            color=color,
            fill=True,
            popup=f"Building ID: {building_id}<br>Has Panel: {has_panel if isinstance(building, PanelInsight) else 'Unknown'}"
        ).add_to(m)
    
    return m

def main():
    st.title("☀️ HS-Solar Dashboard")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Load or create config
        if st.session_state.config is None:
            st.session_state.config = load_config()
        
        if st.session_state.config:
            # Display current config
            st.subheader("Current Configuration")
            st.json(st.session_state.config)
            
            # Edit config
            st.subheader("Edit Configuration")
            new_config = st.session_state.config.copy()
            
            new_config['google_cloud_key'] = st.text_input("Google Cloud API Key", value=new_config['google_cloud_key'], type="password")
            new_config['panel_detection_service'] = st.text_input("Panel Detection Service URL", value=new_config['panel_detection_service'])
            new_config['confidence_threshold'] = st.slider("Confidence Threshold", 0.0, 1.0, value=new_config['confidence_threshold'], step=0.05)
            
            if st.button("Save Configuration"):
                save_config(new_config)
                st.session_state.config = new_config
                st.session_state.pipeline = SolarPipeline(Config(**new_config))
                st.success("Configuration saved!")
        
        # Pipeline controls
        st.header("Pipeline Controls")
        if st.session_state.pipeline is None and st.session_state.config:
            st.session_state.pipeline = SolarPipeline(Config(**new_config))
        
        if st.session_state.pipeline:
            if st.button("1. Fetch Buildings"):
                with st.spinner("Fetching buildings..."):
                    st.session_state.buildings = st.session_state.pipeline.fetch_buildings()
                    st.success(f"Found {len(st.session_state.buildings)} buildings!")
            
            if st.session_state.buildings:
                if st.button("2. Detect Solar Panels"):
                    with st.spinner("Detecting solar panels..."):
                        st.session_state.panels = st.session_state.pipeline.filter_solar_panels(st.session_state.buildings)
                        panel_count = len([p for p in st.session_state.panels if p.has_panel])
                        st.success(f"Detected {panel_count} buildings with solar panels!")
                
                if st.session_state.panels:
                    if st.button("3. Get Solar Data"):
                        with st.spinner("Fetching solar data..."):
                            st.session_state.solar = st.session_state.pipeline.fetch_solar_data(st.session_state.panels)
                            st.success(f"Got solar data for {len(st.session_state.solar)} buildings!")
                    
                    if st.session_state.solar:
                        if st.button("4. Rank Buildings"):
                            with st.spinner("Ranking buildings..."):
                                st.session_state.solar = st.session_state.pipeline.rank(st.session_state.solar)
                                st.success("Buildings ranked by solar potential!")
    
    # Main content area
    if st.session_state.config:
        # Region Selection Section
        st.header("Region Selection")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selection_map = create_selection_map()
            map_data = st_folium(selection_map, width=700, height=500, 
                            returned_objects=["last_active_drawing", "all_drawings"])
            
            # Handle map drawings
            if map_data.get("last_active_drawing"):
                drawing = map_data["last_active_drawing"]
                if drawing["geometry"]["type"] == "Polygon":
                    coords = drawing["geometry"]["coordinates"][0]
                    lats = [c[1] for c in coords]
                    lons = [c[0] for c in coords]
                    
                    new_top = [max(lats), max(lons)]
                    new_bot = [min(lats), min(lons)]
                    
                    # Update config and points
                    st.session_state.config.update({
                        'top_corner': new_top,
                        'bot_corner': new_bot
                    })
                    save_config(st.session_state.config)
                    st.rerun()
        
        with col2:
            # Manual coordinate input
            st.subheader("Manual Coordinates")
            
            # Get current values
            current_top = st.session_state.config['top_corner']
            current_bot = st.session_state.config['bot_corner']
            
            # Create number inputs with update callbacks
            new_top_lat = st.number_input("Top Latitude", value=current_top[0], format="%.6f",
                                        key="top_lat", on_change=update_coords)
            new_top_lon = st.number_input("Top Longitude", value=current_top[1], format="%.6f",
                                        key="top_lon", on_change=update_coords)
            new_bot_lat = st.number_input("Bottom Latitude", value=current_bot[0], format="%.6f",
                                        key="bot_lat", on_change=update_coords)
            new_bot_lon = st.number_input("Bottom Longitude", value=current_bot[1], format="%.6f",
                                        key="bot_lon", on_change=update_coords)
            
            # Add reset button
            if st.button("Reset to Default"):
                st.session_state.config.update({
                    'top_corner': [0, 0],
                    'bot_corner': [0, 0]
                })
                save_config(st.session_state.config)
                st.rerun()
    
    # Analysis Results Section
    if st.session_state.buildings:
        st.header("Analysis Results")
        
        # Building Map
        st.subheader("Building Map")
        m = create_analysis_map(st.session_state.buildings)
        st_folium(m, width=1200, height=600)
        
        # Building Statistics
        st.subheader("Building Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Buildings", len(st.session_state.buildings))
        
        if st.session_state.panels:
            with col2:
                panel_count = len([p for p in st.session_state.panels if p.has_panel])
                st.metric("Buildings with Panels", panel_count)
        
        if st.session_state.solar:
            with col3:
                avg_potential = sum(s.solar_potential.yearly_energy_dc_kwh for s in st.session_state.solar) / len(st.session_state.solar)
                st.metric("Average Yearly Energy (kWh)", f"{avg_potential:.1f}")
            
            # Solar potential visualization
            st.subheader("Solar Potential Analysis")
            
            # Create DataFrame for visualization
            solar_data = []
            for insight in st.session_state.solar:
                if insight.solar_potential.solar_panel_configs:
                    config = insight.solar_potential.solar_panel_configs[0]  # Get best configuration
                    solar_data.append({
                        'Building ID': insight.panel_insight.building.id,
                        'Yearly Energy (kWh)': config.yearly_energy_dc_kwh,
                        'Panel Count': config.panels_count,
                        'Carbon Offset (kg)': insight.solar_potential.carbon_offset_kg
                    })
            
            if solar_data:
                df = pd.DataFrame(solar_data)
                
                # Energy potential chart
                fig = px.bar(df, x='Building ID', y='Yearly Energy (kWh)',
                           title='Yearly Energy Potential by Building',
                           labels={'Building ID': 'Building', 'Yearly Energy (kWh)': 'Energy (kWh/year)'})
                st.plotly_chart(fig, use_container_width=True)
                
                # Panel count vs energy scatter plot
                fig = px.scatter(df, x='Panel Count', y='Yearly Energy (kWh)',
                               title='Panel Count vs Energy Potential',
                               labels={'Panel Count': 'Number of Panels', 'Yearly Energy (kWh)': 'Energy (kWh/year)'})
                st.plotly_chart(fig, use_container_width=True)
                
                # Export options
                st.subheader("Export Results")
                if st.button("Export to CSV"):
                    df.to_csv('solar_analysis.csv', index=False)
                    st.success("Results exported to solar_analysis.csv!")
                
                if st.button("Export to JSON"):
                    dump_stage_result("ranked_solar", "solar_analysis.json", st.session_state.solar)
                    st.success("Results exported to solar_analysis.json!")

if __name__ == "__main__":
    main() 