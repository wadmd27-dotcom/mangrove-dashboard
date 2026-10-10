import json
from pathlib import Path

import folium
import streamlit as st
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium


st.set_page_config(
    page_title="GCC Mangrove Stress Radar",
    page_icon="🌿",
    layout="wide"
)


GEOJSON_PATH = Path(
    "images/gcc_mangrove_analysis_points.geojson"
)
UAE_NDVI_PATH = Path(
    "images/uae_ndvi_summary.json"
)

@st.cache_data
def load_mangrove_points():
    with open(GEOJSON_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    points = []

    for feature in data.get("features", []):
        geometry = feature.get("geometry", {})
        properties = feature.get("properties", {})
        coordinates = geometry.get("coordinates", [])

        if (
            geometry.get("type") == "Point"
            and len(coordinates) >= 2
        ):
            points.append({
                "latitude": float(coordinates[1]),
                "longitude": float(coordinates[0]),
                "region": properties.get("region", "GCC"),
                "source": properties.get(
                    "source",
                    "Global Mangrove Watch 2020"
                )
            })

    return points
@st.cache_data
def load_uae_ndvi_summary():
    with open(
        UAE_NDVI_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)

try:
    mangrove_points = load_mangrove_points()
except Exception as error:
    st.error(f"Could not load GCC mangrove data: {error}")
    st.stop()
try:
    uae_ndvi = load_uae_ndvi_summary()
except Exception as error:
    st.error(f"Could not load UAE NDVI summary: {error}")
    st.stop()

st.sidebar.title("🌿 Mangrove Stress Radar")

st.sidebar.write(
    "Explore GCC mangrove locations and preliminary health indicators."
)

st.sidebar.divider()

st.sidebar.subheader("Map layers")

show_mangroves = st.sidebar.checkbox(
    "GCC mangrove points",
    value=True
)

st.sidebar.divider()

st.sidebar.subheader("Study information")

st.sidebar.write("Region: GCC countries")
st.sidebar.write(
    "Countries: UAE, Saudi Arabia, Oman, Qatar, Bahrain and Kuwait"
)
st.sidebar.write(
    "Reference layer: Global Mangrove Watch"
)
st.sidebar.write(
    "Monitoring source: Sentinel-2"
)
st.sidebar.write(
    "Comparison: 2024–2025"
)


st.title("Mangrove Stress Radar")

st.write(
    "Detect emerging mangrove stress before visible habitat loss, "
    "explain the possible signal, and support field verification."
)

st.info(
    "POC scope: the map shows 475 sampled GCC mangrove reference "
    "points derived from Global Mangrove Watch 2020. Health and "
    "change indicators are preliminary and require multi-tile "
    "Sentinel-2 processing and field validation for full GCC coverage."
)


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "UAE NDVI status",
        "Preliminary"
    )

with col2:
    st.metric(
        "UAE later median NDVI",
        f"{uae_ndvi['later_median_ndvi']:.4f}"
    )

with col3:
    st.metric(
        "Strong decrease",
        f"{uae_ndvi['strong_decrease_percent']:.2f}%"
    )

with col4:
    st.metric(
        "Strong increase",
        f"{uae_ndvi['strong_increase_percent']:.2f}%"
    )

st.subheader("Interactive GCC Mangrove Map")

st.write(
    "Click a mangrove point to view its reference information."
)


if mangrove_points:

    average_latitude = sum(
        point["latitude"]
        for point in mangrove_points
    ) / len(mangrove_points)

    average_longitude = sum(
        point["longitude"]
        for point in mangrove_points
    ) / len(mangrove_points)

    mangrove_map = folium.Map(
        location=[
            average_latitude,
            average_longitude
        ],
        zoom_start=5,
        tiles="OpenStreetMap",
        control_scale=True
    )

    marker_cluster = MarkerCluster(
        name="GCC Mangrove Points"
    )

    if show_mangroves:

        for point in mangrove_points:

            popup_text = (
                f"<b>Region:</b> {point['region']}<br>"
                f"<b>Source:</b> {point['source']}<br>"
                f"<b>Latitude:</b> {point['latitude']:.5f}<br>"
                f"<b>Longitude:</b> {point['longitude']:.5f}<br><br>"

                "<b>Stress fingerprint</b><br>"
                "NDVI: Preliminary<br>"
                "NDWI: Planned<br>"
                "Turbidity/NDCI: Planned<br>"
                "Fragmentation: Planned<br>"
                "Planet Tanager anomaly: Planned<br><br>"

                "<b>Possible cause</b><br>"
                "Requires field validation<br><br>"

                "<b>Confidence and uncertainty</b><br>"
                "Preliminary reference point; "
                "multi-date validation required<br><br>"

                "<b>Recommended action</b><br>"
                "Inspect by UAV or field team<br>"
                "Test salinity and water quality<br>"
                "Prioritize protection<br><br>"

                "<b>Outcome tracking</b><br>"
                "Verification: Pending<br>"
                "Intervention: Not recorded<br>"
                "Recovery after 30/60/90 days: Pending"
            )

            folium.CircleMarker(
                location=[
                    point["latitude"],
                    point["longitude"]
                ],
                radius=5,
                color="#07543e",
                fill=True,
                fill_color="#16805b",
                fill_opacity=0.8,
                weight=1,
                popup=folium.Popup(
                    popup_text,
                    max_width=320
                )
            ).add_to(marker_cluster)

    marker_cluster.add_to(mangrove_map)

    folium.LayerControl().add_to(mangrove_map)

    st_folium(
        mangrove_map,
        width="100%",
        height=650,
        key="gcc_mangrove_map"
    )

    st.caption(
        f"Displaying {len(mangrove_points)} "
        "GCC mangrove reference points."
    )

else:
    st.warning(
        "No GCC mangrove points were found."
    )
