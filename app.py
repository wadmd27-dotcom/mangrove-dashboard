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


# ---------------------------------------------------------
# Custom styling
# ---------------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background:
            linear-gradient(
                rgba(10, 30, 20, 0.86),
                rgba(15, 35, 25, 0.84)
            ),
            url("https://images.unsplash.com/photo-1584551246679-0daf3d275d0f?auto=format&fit=crop&w=1920&q=80");

        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    h1, h2, h3, h4, h5, h6,
    p, span, label, .stMarkdown {
        color: #e2ede5 !important;
    }

    [data-testid="stMetric"] {
        background-color: rgba(20, 50, 35, 0.78);
        border: 1px solid rgba(50, 150, 100, 0.45);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    [data-testid="stSidebar"] {
        background-color: rgba(10, 25, 18, 0.96);
        border-right: 1px solid rgba(50, 150, 100, 0.25);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: rgba(20, 50, 35, 0.65);
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(30, 90, 60, 0.9) !important;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# File paths
# ---------------------------------------------------------

GEOJSON_PATH = Path(
    "images/gcc_mangrove_analysis_points.geojson"
)

UAE_NDVI_PATH = Path(
    "images/uae_ndvi_summary.json"
)


# ---------------------------------------------------------
# Data loaders
# ---------------------------------------------------------

@st.cache_data
def load_mangrove_points():
    with open(
        GEOJSON_PATH,
        "r",
        encoding="utf-8"
    ) as file:
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
            country_or_region = properties.get(
                "country",
                properties.get("region", "GCC")
            )

            points.append({
                "latitude": float(coordinates[1]),
                "longitude": float(coordinates[0]),
                "region": str(country_or_region),
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


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

try:
    mangrove_points = load_mangrove_points()
except Exception as error:
    st.error(
        f"Could not load GCC mangrove data: {error}"
    )
    st.stop()


try:
    uae_ndvi = load_uae_ndvi_summary()
except Exception as error:
    st.error(
        f"Could not load UAE NDVI summary: {error}"
    )
    st.stop()


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.title("🌿 Mangrove Stress Radar")

st.sidebar.write(
    "Explore GCC mangrove locations and preliminary "
    "health indicators."
)

st.sidebar.divider()

st.sidebar.subheader("Map and region filters")

show_mangroves = st.sidebar.checkbox(
    "Show GCC mangrove points",
    value=True
)

selected_region = st.sidebar.selectbox(
    "Filter by sub-region",
    [
        "All GCC Regions",
        "UAE",
        "Saudi Arabia",
        "Oman",
        "Qatar",
        "Bahrain",
        "Kuwait"
    ]
)

st.sidebar.divider()

st.sidebar.subheader("Study information")

st.sidebar.markdown(
    "**Region:** GCC countries"
)

st.sidebar.markdown(
    "**Countries:** UAE, Saudi Arabia, Oman, Qatar, Bahrain and Kuwait"
)

st.sidebar.markdown(
    "**Reference layer:** Global Mangrove Watch 2020"
)

st.sidebar.markdown(
    "**Monitoring source:** Sentinel-2 & Planet Tanager"
)

st.sidebar.markdown(
    "**Comparison:** 2024–2025"
)


# ---------------------------------------------------------
# Main header
# ---------------------------------------------------------

st.title(
    "🌿 GCC Mangrove Stress Radar & Blue Carbon Monitor"
)

st.write(
    "Detect emerging mangrove stress before visible "
    "habitat loss, explain the possible signal, and "
    "support field verification."
)

st.info(
    "POC scope: the map shows 475 sampled GCC mangrove "
    "reference points derived from Global Mangrove Watch "
    "2020. Health and change indicators are preliminary "
    "and require multi-tile Sentinel-2 processing and "
    "field validation for full GCC coverage."
)


# ---------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "UAE NDVI status",
        uae_ndvi.get(
            "status",
            "Preliminary"
        )
    )

with col2:
    st.metric(
        "UAE later median NDVI",
        f"{uae_ndvi.get('later_median_ndvi', 0.0):.4f}"
    )

with col3:
    st.metric(
        "Strong decrease",
        f"{uae_ndvi.get('strong_decrease_percent', 0.0):.2f}%"
    )

with col4:
    st.metric(
        "Strong increase",
        f"{uae_ndvi.get('strong_increase_percent', 0.0):.2f}%"
    )


# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(
    [
        "🗺️ Interactive Map Explorer",
        "📊 Regional Ecosystem Insights"
    ]
)


# ---------------------------------------------------------
# Tab 1: Interactive map
# ---------------------------------------------------------

with tab1:

    st.subheader("Interactive GCC Mangrove Map")

    st.write(
        "Click a mangrove point to view its stress "
        "fingerprint, possible causes, and recommended actions."
    )

    if mangrove_points:

        filtered_points = mangrove_points

        if selected_region != "All GCC Regions":

            filtered_points = [
                point
                for point in mangrove_points
                if selected_region.lower()
                in point["region"].lower()
            ]

            if not filtered_points:

                st.warning(
                    f"No points are labeled specifically as "
                    f"{selected_region}. The current GeoJSON "
                    "uses GCC as the region label, so all points "
                    "remain available under All GCC Regions."
                )

        if filtered_points:

            average_latitude = sum(
                point["latitude"]
                for point in filtered_points
            ) / len(filtered_points)

            average_longitude = sum(
                point["longitude"]
                for point in filtered_points
            ) / len(filtered_points)

            # OpenStreetMap does not require an API key
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

                for point in filtered_points:

                    popup_text = f"""
                    <div style="
                        font-family: Arial, sans-serif;
                        font-size: 13px;
                        width: 280px;
                        line-height: 1.45;
                        color: #222;
                    ">

                        <div style="
                            color: #07543e;
                            font-size: 16px;
                            font-weight: bold;
                            margin-bottom: 6px;
                        ">
                            🌿 Mangrove Stress Inspection
                        </div>

                        <b>Region:</b>
                        {point["region"]}<br>

                        <b>Source:</b>
                        {point["source"]}<br>

                        <b>Latitude:</b>
                        {point["latitude"]:.5f}<br>

                        <b>Longitude:</b>
                        {point["longitude"]:.5f}

                        <hr>

                        <b>Stress fingerprint</b><br>
                        NDVI: Preliminary UAE indicator<br>
                        NDWI: Planned<br>
                        Turbidity/NDCI: Planned<br>
                        Fragmentation or canopy thinning: Planned<br>
                        Planet Tanager anomaly: Planned

                        <hr>

                        <b>Possible cause</b><br>
                        Possible water stress, sediment or pollution,
                        clearing, construction, storm damage, or
                        restoration failure. This is not a proven diagnosis.

                        <hr>

                        <b>Confidence and uncertainty</b><br>
                        Imagery quality: To be assessed<br>
                        Affected area: To be assessed<br>
                        Agreement between indices: Pending<br>
                        Persistence across dates: Pending

                        <hr>

                        <b>Recommended action</b><br>
                        • Inspect by UAV or field team<br>
                        • Test salinity and water quality<br>
                        • Check restoration plots<br>
                        • Prioritize protection<br>
                        • Replant only if suitable

                        <hr>

                        <b>Outcome tracking</b><br>
                        Alert verification: Pending<br>
                        Intervention: Not recorded<br>
                        Recovery after 30/60/90 days: Pending<br>
                        Carbon, biodiversity, and coastal-protection
                        value at risk: To be estimated

                    </div>
                    """

                    folium.CircleMarker(
                        location=[
                            point["latitude"],
                            point["longitude"]
                        ],
                        radius=5,
                        color="#07543e",
                        fill=True,
                        fill_color="#16805b",
                        fill_opacity=0.85,
                        weight=1,
                        popup=folium.Popup(
                            popup_text,
                            max_width=360
                        )
                    ).add_to(marker_cluster)

            marker_cluster.add_to(mangrove_map)

            folium.LayerControl().add_to(mangrove_map)

            st_folium(
                mangrove_map,
                width="100%",
                height=600,
                key="gcc_mangrove_map"
            )

            st.caption(
                f"Displaying {len(filtered_points)} "
                "GCC mangrove reference points."
            )

        else:
            st.warning(
                "No points are available for this filter."
            )

    else:
        st.warning(
            "No GCC mangrove points were found."
        )


# ---------------------------------------------------------
# Tab 2: Regional insights
# ---------------------------------------------------------

with tab2:

    st.subheader(
        "📊 Regional Ecosystem Health Summary"
    )

    st.write(
        "Overview of preliminary monitoring indicators "
        "across Arabian Gulf and Red Sea mangrove areas."
    )

    t_col1, t_col2 = st.columns(2)

    with t_col1:

        st.markdown("### 🌿 Key observations")

        st.success(
            "Baseline mapping uses Global Mangrove Watch "
            "2020 reference data."
        )

        st.info(
            "Sentinel-2 comparisons provide a preliminary "
            "view of vegetation-condition change."
        )

        st.warning(
            "NDWI, turbidity, fragmentation, hyperspectral "
            "anomalies, and field verification are planned "
            "for the next POC stage."
        )

    with t_col2:

        st.markdown("### 🛰️ Technology stack")

        st.write(
            "• Satellite source: Sentinel-2 L2A"
        )

        st.write(
            "• Hyperspectral source: Planet Tanager"
        )

        st.write(
            "• Reference layer: Global Mangrove Watch 2020"
        )

        st.write(
            "• Target area: UAE, Saudi Arabia, Oman, "
            "Qatar, Bahrain and Kuwait"
        )

        st.write(
            "• POC reference points: "
            f"{len(mangrove_points)}"
        )
