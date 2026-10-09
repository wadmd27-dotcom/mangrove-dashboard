import json

import folium
import streamlit as st
from streamlit_folium import st_folium


# -----------------------------
# Page configuration
# -----------------------------

st.set_page_config(
    page_title="UAE Mangrove Watch",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)


# -----------------------------
# GMW-inspired styling
# -----------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', Arial, sans-serif;
    }

    .stApp {
        background-color: #f4f8f7;
    }

    h1, h2, h3 {
        color: #006f73;
        font-weight: 700;
    }

    .gmw-banner {
        background: linear-gradient(135deg, #007f82, #00a6a6);
        color: white;
        padding: 24px 32px;
        border-radius: 16px;
        margin-bottom: 20px;
    }

    .gmw-banner h1 {
        color: white;
        margin: 0;
        font-size: 34px;
    }

    .gmw-banner p {
        color: #e7ffff;
        margin-top: 8px;
        font-size: 16px;
    }

    .info-card {
        background: white;
        border-left: 5px solid #00a6a6;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0, 80, 80, 0.08);
        margin-bottom: 18px;
    }

    [data-testid="stSidebar"] {
        background-color: #e8f3f1;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #006f73;
    }

    .stButton button {
        background-color: #008c8c;
        color: white;
        border-radius: 8px;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# Header
# -----------------------------

st.markdown(
    """
    <div class="gmw-banner">
        <h1>🌿 UAE Mangrove Watch</h1>
        <p>
            Interactive mangrove habitat mapping and satellite-based
            ecosystem monitoring.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# Sidebar controls
# -----------------------------

st.sidebar.markdown("## Map Controls")

show_gmw = st.sidebar.checkbox(
    "Mangrove habitat extent",
    value=True
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    """
    **Reference dataset**

    Global Mangrove Watch habitat extent

    **Reference year**

    2020

    **Study area**

    United Arab Emirates
    """
)


# -----------------------------
# Load GMW GeoJSON
# -----------------------------

with open("images/gmw_uae_extent.geojson", "r") as file:
    gmw_data = json.load(file)


# -----------------------------
# Create interactive map
# -----------------------------

interactive_map = folium.Map(
    location=[24.5, 54.5],
    zoom_start=6,
    tiles="OpenStreetMap",
    control_scale=True
)


# Add GMW layer
if show_gmw:
    folium.GeoJson(
        gmw_data,
        name="Mangrove Habitat Extent",
        style_function=lambda feature: {
            "fillColor": "#00a6a6",
            "color": "#006f73",
            "weight": 1,
            "fillOpacity": 0.75
        },
        highlight_function=lambda feature: {
            "fillColor": "#f2c94c",
            "color": "#9b7200",
            "weight": 3,
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
    ).add_to(interactive_map)


# Add map controls
folium.LayerControl(collapsed=False).add_to(interactive_map)
folium.LatLngPopup().add_to(interactive_map)


# -----------------------------
# Display map
# -----------------------------

st.markdown(
    """
    <div class="info-card">
        <b>Explore the UAE mangrove habitat</b><br>
        Zoom, pan, and click the green mangrove areas to inspect
        the reference layer.
    </div>
    """,
    unsafe_allow_html=True
)

map_result = st_folium(
    interactive_map,
    width=1600,
    height=850
)


# -----------------------------
# Selected location information
# -----------------------------

if map_result and map_result.get("last_clicked"):
    clicked = map_result["last_clicked"]

    latitude = clicked["lat"]
    longitude = clicked["lng"]

    st.markdown("### Selected Location")

    location_col1, location_col2, location_col3 = st.columns(3)

    with location_col1:
        st.metric("Latitude", f"{latitude:.4f}")

    with location_col2:
        st.metric("Longitude", f"{longitude:.4f}")

    with location_col3:
        st.metric("Reference layer", "GMW 2020")

    st.info(
        "This location has been selected on the map. "
        "The next version will connect the selected location "
        "to Sentinel-2 health indicators and change alerts."
    )
else:
    st.info(
        "Click anywhere on the map to select a location. "
        "Click a green polygon to view its GMW information."
    )


# -----------------------------
# Footer
# -----------------------------

st.markdown("---")

st.caption(
    "Reference: Global Mangrove Watch. "
    "Satellite-derived indicators are preliminary and require validation."
)
