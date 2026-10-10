import json
import os

import folium
import streamlit as st
from streamlit_folium import st_folium

geojson_path = "images/gcc_mangrove_analysis_points.geojson"
st.set_page_config(
    page_title="Mangrove Stress Radar",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)


# -----------------------------
# GMW-inspired visual style
# -----------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f4f8f5;
        color: #173b35;
    }

    section[data-testid="stSidebar"] {
        background-color: #e1eee8;
        border-right: 1px solid #b7d2c5;
    }

    h1, h2, h3 {
        color: #145c4a;
        font-family: Arial, sans-serif;
    }

    .dashboard-subtitle {
        color: #55756d;
        font-size: 1.05rem;
        margin-bottom: 1rem;
    }

    .section-label {
        color: #145c4a;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        font-size: 0.82rem;
        margin-top: 1rem;
    }

    .info-box {
        background-color: #e5f2ec;
        border-left: 5px solid #16805b;
        padding: 1rem;
        border-radius: 6px;
        color: #244d43;
        margin-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# Load GMW GeoJSON
# -----------------------------
geojson_path = "images/gmw_uae_extent.geojson"

gmw_data = None

if os.path.exists(geojson_path):
    with open(geojson_path, "r") as file:
        gmw_data = json.load(file)
        analysis_path = "images/gcc_mangrove_analysis_points.geojson"

analysis_data = None

if os.path.exists(analysis_path):
    with open(analysis_path, "r") as file:
        analysis_data = json.load(file)


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("🌿 Mangrove Stress Radar")
st.sidebar.markdown(
    "Explore mangrove extent, preliminary health, and change indicators."
)

st.sidebar.markdown("---")

st.sidebar.subheader("Map layers")

show_gmw = st.sidebar.checkbox(
    "GMW mangrove extent",
    value=True
)

st.sidebar.markdown("---")

st.sidebar.subheader("Study information")
st.sidebar.write("Region: UAE / Gulf coast")
st.sidebar.write("Reference layer: Global Mangrove Watch")
st.sidebar.write("Monitoring source: Sentinel-2")
st.sidebar.write("Comparison: 2024–2025")


# -----------------------------
# Main title
# -----------------------------
st.title("Mangrove Stress Radar")

st.markdown(
    """
    <div class="dashboard-subtitle">
    Detect emerging mangrove stress before visible habitat loss,
    explain the possible signal, and support field verification.
    </div>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# Summary metrics
# -----------------------------
st.markdown(
    '<div class="section-label">Current satellite indicators</div>',
    unsafe_allow_html=True
)

metric_1, metric_2, metric_3, metric_4 = st.columns(4)

with metric_1:
    st.metric(
        "Mangrove health score",
        "27.6 / 100"
    )

with metric_2:
    st.metric(
        "Median NDVI",
        "0.0039"
    )

with metric_3:
    st.metric(
        "Possible decrease",
        "0.37%"
    )

with metric_4:
    st.metric(
        "Stable area",
        "99.63%"
    )


# -----------------------------
# Interactive map
# -----------------------------
st.markdown(
    '<div class="section-label">Interactive mangrove map</div>',
    unsafe_allow_html=True
)

st.write(
    "Click anywhere on the map to inspect coordinates. "
    "Click a green mangrove area to view its reference information."
)

mangrove_map = folium.Map(
    location=[24.5, 54.5],
    zoom_start=6,
    tiles="OpenStreetMap",
    control_scale=True
)

if show_gmw and gmw_data is not None:
    folium.GeoJson(
        gmw_data,
        name="GMW Mangrove Extent",
        style_function=lambda feature: {
            "fillColor": "#16805b",
            "color": "#07543e",
            "weight": 1,
            "fillOpacity": 0.75
        },
        highlight_function=lambda feature: {
            "fillColor": "#f2b134",
            "color": "#8a5a00",
            "weight": 2,
            "fillOpacity": 0.9
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["region", "source"],
            aliases=["Region", "Source"],
            sticky=True
        ),
        popup=folium.GeoJsonPopup(
            fields=["region", "source"],
            aliases=["Region", "Source"]
        )
    ).add_to(mangrove_map)

if analysis_data is not None:
    folium.GeoJson(
        analysis_data,
        name="Mangrove analysis points",
        marker=folium.CircleMarker(
            radius=5,
            color="#f2b134",
            fill=True,
            fill_color="#f2b134",
            fill_opacity=0.85
        ),
        tooltip=folium.GeoJsonTooltip(
            fields=[
                "ndvi",
                "ndvi_change",
                "health_score",
                "change_status"
            ],
            aliases=[
                "NDVI",
                "NDVI change",
                "Health score",
                "Status"
            ]
        ),
        popup=folium.GeoJsonPopup(
            fields=[
                "ndvi",
                "ndvi_change",
                "health_score",
                "change_status",
                "recommended_action"
            ],
            aliases=[
                "NDVI",
                "NDVI change",
                "Health score",
                "Change status",
                "Recommended action"
            ]
        )
    ).add_to(mangrove_map)
folium.LatLngPopup().add_to(mangrove_map)
folium.LayerControl().add_to(mangrove_map)

map_result = st_folium(
    mangrove_map,
    width="100%",
    height=720,
    returned_objects=[
        "last_clicked",
        "last_object_clicked"
    ]
)


# -----------------------------
# -----------------------------
# -----------------------------
# Selected analysis point report
# -----------------------------
if map_result and map_result.get("last_object_clicked"):
    clicked_point = map_result["last_object_clicked"]
    properties = clicked_point.get("properties", {})

    latitude = clicked_point.get("lat")
    longitude = clicked_point.get("lng")

    st.success(
        f"Selected point: {latitude:.5f}, {longitude:.5f}"
    )

    st.markdown(
        '<div class="section-label">Selected area report</div>',
        unsafe_allow_html=True
    )

    report_1, report_2, report_3, report_4 = st.columns(4)

    with report_1:
        st.metric(
            "Health score",
            f"{properties.get('health_score', 'N/A')} / 100"
        )

    with report_2:
        st.metric(
            "NDVI",
            properties.get("ndvi", "N/A")
        )

    with report_3:
        st.metric(
            "NDVI change",
            properties.get("ndvi_change", "N/A")
        )

    with report_4:
        st.metric(
            "Change status",
            properties.get("change_status", "N/A")
        )

    st.info(
        f"Recommended action: "
        f"{properties.get('recommended_action', 'Review in the field.')}"
    )

else:
    st.info(
        "Click an orange analysis point to view location-specific results."
    )
    # -----------------------------
if map_result and map_result.get("last_clicked"):
    selected_location = map_result["last_clicked"]

    latitude = selected_location["lat"]
    longitude = selected_location["lng"]

    st.success(
        f"Selected location: "
        f"{latitude:.5f}, {longitude:.5f}"
    )

    st.markdown(
        '<div class="section-label">Selected area report</div>',
        unsafe_allow_html=True
    )

    report_1, report_2, report_3, report_4 = st.columns(4)

    with report_1:
        st.metric("Health score", "27.6 / 100")

    with report_2:
        st.metric("Median NDVI", "0.0039")

    with report_3:
        st.metric("Possible change", "Stable")

    with report_4:
        st.metric("Confidence", "Preliminary")

    st.info(
        "This location is within the GMW mangrove reference extent. "
        "Sentinel-2 indicators show mostly stable conditions. "
        "Field or UAV inspection is recommended before taking action."
    )

else:
    st.info("Click anywhere on the map to select a location.")
# -----------------------------
# Interpretation
# -----------------------------
st.markdown(
    """
    <div class="info-box">
    <b>Initial interpretation:</b><br>
    The selected mangrove area shows a preliminary satellite health score
    of 27.6/100. NDVI change between the two dates is small, with 99.63%
    of the mapped mangrove pixels classified as stable.
    These are satellite indicators and require field or UAV validation.
    </div>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# Possible actions
# -----------------------------
st.markdown(
    '<div class="section-label">Recommended next action</div>',
    unsafe_allow_html=True
)

action_1, action_2, action_3 = st.columns(3)

with action_1:
    st.markdown("### 🔍 Inspect")
    st.write("Check the location using UAV or a field team.")

with action_2:
    st.markdown("### 💧 Validate")
    st.write("Measure salinity and water quality if stress is suspected.")

with action_3:
    st.markdown("### 🌱 Track")
    st.write("Compare the health indicator again after 30–90 days.")
