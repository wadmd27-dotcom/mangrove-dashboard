import json

import folium
import streamlit as st
from streamlit_folium import st_folium


# Page configuration must come before any Streamlit commands
st.set_page_config(
    page_title="Mangrove Health Dashboard",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Sidebar
st.sidebar.title("🌿 Mangrove Monitoring")
st.sidebar.markdown(
    "Use the map to explore the GMW mangrove reference extent "
    "for the UAE."
)


# Main title
st.title("🌿 Mangrove Health and Blue Carbon Dashboard")

st.write(
    "An interactive mangrove monitoring dashboard combining "
    "Global Mangrove Watch reference data with Sentinel-2 analysis."
)


# Load GMW GeoJSON
with open("images/gmw_uae_extent.geojson", "r") as file:
    gmw_data = json.load(file)


# Create interactive map
interactive_map = folium.Map(
    location=[24.5, 54.5],
    zoom_start=6,
    tiles="OpenStreetMap",
    control_scale=True
)


# Add GMW mangrove layer
gmw_layer = folium.GeoJson(
    gmw_data,
    name="GMW Mangrove Extent — 2020",
    style_function=lambda feature: {
        "fillColor": "#16823B",
        "color": "#0B5D2A",
        "weight": 1,
        "fillOpacity": 0.75
    },
    highlight_function=lambda feature: {
        "fillColor": "#F4C542",
        "color": "#8A6500",
        "weight": 2,
        "fillOpacity": 0.9
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["layer", "year", "class"],
        aliases=["Layer", "Year", "Class"],
        sticky=True
    ),
    popup=folium.GeoJsonPopup(
        fields=["layer", "year", "class"],
        aliases=["Layer", "Year", "Class"]
    )
)

gmw_layer.add_to(interactive_map)


# Add map controls
folium.LayerControl(collapsed=False).add_to(interactive_map)
folium.LatLngPopup().add_to(interactive_map)


# Display full-width interactive map
st.subheader("Interactive Mangrove Map")

map_result = st_folium(
    interactive_map,
    width=1600,
    height=850
)


# Display clicked location information
if map_result and map_result.get("last_clicked"):
    clicked = map_result["last_clicked"]

    st.success(
        f"Selected location — "
        f"Latitude: {clicked['lat']:.4f}, "
        f"Longitude: {clicked['lng']:.4f}"
    )
else:
    st.info(
        "Click anywhere on the map to select a location. "
        "Click a green mangrove polygon to view its GMW information."
    )


st.divider()


# Degradation alert summary
st.header("Possible Mangrove Degradation Alerts")

st.image(
    "images/possible_mangrove_degradation_alerts.png",
    caption=(
        "Possible degradation hotspots based on NDVI change "
        "between February 2024 and February 2025"
    ),
    use_container_width=True
)

st.info(
    "Red areas indicate possible vegetation decline. "
    "These areas require further validation or field inspection."
)

metric_col1, metric_col2 = st.columns(2)

with metric_col1:
    st.metric("Possible decrease", "1.99%")

with metric_col2:
    st.metric("Possible increase", "1.53%")


st.divider()


# Satellite analysis maps
st.header("Satellite Analysis Maps")

map_col1, map_col2 = st.columns(2)

with map_col1:
    st.subheader("Ecosystem Health Indices")
    st.image(
        "images/image 4.png",
        use_container_width=True
    )

with map_col2:
    st.subheader("RGB and Coastal Indicators")
    st.image(
        "images/image 3.png",
        use_container_width=True
    )


st.divider()


# Spectral analysis
st.header("Spectral Analysis")

spectral_col1, spectral_col2 = st.columns(2)

with spectral_col1:
    st.subheader("Spectral Signatures")
    st.image(
        "images/image 1.png",
        use_container_width=True
    )

with spectral_col2:
    st.subheader("Mean Spectrum")
    st.image(
        "images/image 2.png",
        use_container_width=True
    )


st.divider()


# Indicator summary
st.header("Indicator Summary")

indicator_col1, indicator_col2, indicator_col3 = st.columns(3)

with indicator_col1:
    st.metric("Vegetation indicator", "NDVI")

with indicator_col2:
    st.metric("Water indicator", "NDWI")

with indicator_col3:
    st.metric("Chlorophyll indicator", "NDCI")


st.info(
    "These indicators are preliminary remote-sensing proxies. "
    "They are not confirmed measurements of carbon storage or "
    "mangrove health and require additional validation."
)
