import streamlit as st
st.sidebar.header("Map Layers")
selected_map = st.sidebar.selectbox(
    "Choose a map to view",
    [
        "Mangrove Indicators",
        "Possible Degradation Alerts",
        "RGB Coastal Overview"    ]
)

if selected_map == "Mangrove Indicators":
    st.image(
        "images/image 4.png",
        caption="Mangrove and ecosystem indicators",
        use_container_width=True
    )

elif selected_map == "Possible Degradation Alerts":
    st.image(
        "images/possible_mangrove_degradation_alerts.png",
        caption="Possible mangrove degradation hotspots",
        use_container_width=True
    )

elif selected_map == "RGB Coastal Overview":
    st.image(
        "images/image 3.png",
        caption="RGB coastal overview",
        use_container_width=True
    )

st.set_page_config(
    page_title="Mangrove Health Dashboard",
    page_icon="🌿",
    layout="wide"
)

st.title("🌿 Mangrove Health and Blue Carbon Dashboard")

st.write(
    "This dashboard explores mangrove and coastal ecosystem health "
    "using Tanager hyperspectral satellite indicators."
)

st.header("Satellite Analysis Maps")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Ecosystem Health Indices")
    st.image("images/image 4.png", use_container_width=True)

with col2:
    st.subheader("RGB and Coastal Indicators")
    st.image("images/image 3.png", use_container_width=True)
st.subheader("Possible Mangrove Degradation Alerts")

st.image(
    "images/possible_mangrove_degradation_alerts.png",
    caption="Areas with a strong NDVI decrease between February 2024 and February 2025",
    use_container_width=True
)

st.info(
    "This map shows possible degradation hotspots. "
    "The red areas require further validation or field inspection."
)

col1, col2 = st.columns(2)

with col1:
    st.metric("Possible decrease", "1.99%")

with col2:
    st.metric("Possible increase", "1.53%")
st.header("Spectral Analysis")

col3, col4 = st.columns(2)

with col3:
    st.subheader("Spectral Signatures")
    st.image("images/image 1.png", use_container_width=True)

with col4:
    st.subheader("Mean Spectrum")
    st.image("images/image 2.png", use_container_width=True)

st.header("Initial Interpretation")

a, b, c = st.columns(3)

with a:
    st.metric("Vegetation indicator", "NDVI")

with b:
    st.metric("Water indicator", "NDWI")

with c:
    st.metric("Chlorophyll indicator", "NDCI")

st.info(
    "These maps are indicators, not confirmed measurements of carbon storage "
    "or mangrove health. Further validation with reference data is required."
)
import folium
from streamlit_folium import st_folium

st.subheader("Interactive GCC Map")

gcc_map = folium.Map(
    location=[25.5, 51.5],
    zoom_start=5,
    tiles="CartoDB positron"
)

folium.LatLngPopup().add_to(gcc_map)

map_result = st_folium(
    gcc_map,
    width= "100%",
    height=600
)

if map_result and map_result.get("last_clicked"):
    clicked = map_result["last_clicked"]

    st.success(
        f"Selected location: "
        f"{clicked['lat']:.4f}, {clicked['lng']:.4f}"
    )
else:
    st.info("Click anywhere on the GCC map to select a location.")
import json
import folium
from streamlit_folium import st_folium

st.subheader("Interactive GMW Mangrove Map")

with open("images/gmw_uae_extent.geojson", "r") as file:
    gmw_data = json.load(file)

interactive_map = folium.Map(
    location=[24.5, 54.5],
    zoom_start=6,
    tiles="OpenStreetMap"
)

folium.GeoJson(
    gmw_data,
    name="GMW Mangrove Extent",
    style_function=lambda feature: {
        "fillColor": "#16823B",
        "color": "#0B5D2A",
        "weight": 1,
        "fillOpacity": 0.7
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["layer", "year", "class"],
        aliases=["Layer", "Year", "Class"]
    ),
    popup=folium.GeoJsonPopup(
        fields=["layer", "year", "class"],
        aliases=["Layer", "Year", "Class"]
    )
).add_to(interactive_map)

folium.LayerControl().add_to(interactive_map)
folium.LatLngPopup().add_to(interactive_map)

map_result = st_folium(
    interactive_map,
    width="100%",
    height=650
)

if map_result and map_result.get("last_clicked"):
    clicked = map_result["last_clicked"]

    st.success(
        f"Selected location: "
        f"{clicked['lat']:.4f}, {clicked['lng']:.4f}"
    )
