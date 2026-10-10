import base64
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
# Paths
# ---------------------------------------------------------

BG_IMAGE_PATH = Path(
    "images/mangrove_bg.jpg"
)

GEOJSON_PATH = Path(
    "images/gcc_mangrove_analysis_points.geojson"
)

UAE_INDICES_PATH = Path(
    "images/uae_indices_summary.json"
)


# ---------------------------------------------------------
# Background
# ---------------------------------------------------------

if BG_IMAGE_PATH.exists():

    with open(
        BG_IMAGE_PATH,
        "rb"
    ) as image_file:
        encoded_image = base64.b64encode(
            image_file.read()
        ).decode("utf-8")

    background_css = f"""
    .stApp {{
        background:
            linear-gradient(
                rgba(10, 30, 20, 0.84),
                rgba(15, 35, 25, 0.82)
            ),
            url("data:image/jpeg;base64,{encoded_image}");

        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-color: #0a1e14;
    }}
    """

else:

    background_css = """
    .stApp {
        background-color: #0a1e14;
    }
    """


st.markdown(
    f"""
    <style>
    {background_css}

    h1, h2, h3, h4, h5, h6,
    p, span, label, .stMarkdown {{
        color: #e2ede5 !important;
    }}

    [data-testid="stMetric"] {{
        background-color: rgba(20, 50, 35, 0.85) !important;
        border: 1px solid rgba(50, 150, 100, 0.5) !important;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    }}

    [data-testid="stSidebar"] {{
        background-color: rgba(10, 25, 18, 0.96) !important;
        border-right: 1px solid rgba(50, 150, 100, 0.3) !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
    }}

    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(20, 50, 35, 0.7);
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: rgba(30, 90, 60, 0.95) !important;
        font-weight: bold;
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# Approximate GCC boundaries
# ---------------------------------------------------------

GCC_COUNTRY_BOUNDS = {
    "UAE": {
        "lat": (22.5, 26.5),
        "lon": (51.5, 56.5)
    },
    "Saudi Arabia": {
        "lat": (16.0, 31.5),
        "lon": (34.0, 50.0)
    },
    "Oman": {
        "lat": (16.5, 26.5),
        "lon": (56.5, 60.0)
    },
    "Qatar": {
        "lat": (24.4, 26.2),
        "lon": (50.6, 51.7)
    },
    "Bahrain": {
        "lat": (25.7, 26.4),
        "lon": (50.3, 50.8)
    },
    "Kuwait": {
        "lat": (28.4, 30.2),
        "lon": (46.5, 48.5)
    }
}


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
            geometry.get("type") != "Point"
            or len(coordinates) < 2
        ):
            continue

        longitude = float(coordinates[0])
        latitude = float(coordinates[1])

        detected_country = "GCC"

        for country, bounds in GCC_COUNTRY_BOUNDS.items():

            inside_latitude = (
                bounds["lat"][0]
                <= latitude
                <= bounds["lat"][1]
            )

            inside_longitude = (
                bounds["lon"][0]
                <= longitude
                <= bounds["lon"][1]
            )

            if inside_latitude and inside_longitude:
                detected_country = country
                break

        points.append({
            "latitude": latitude,
            "longitude": longitude,
            "region": detected_country,
            "source": properties.get(
                "source",
                "Global Mangrove Watch 2020"
            )
        })

    return points


@st.cache_data
def load_uae_indices_summary():

    with open(
        UAE_INDICES_PATH,
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
    uae_indices = load_uae_indices_summary()
except Exception as error:
    st.error(
        f"Could not load UAE indices summary: {error}"
    )
    st.stop()


ndvi_data = uae_indices.get(
    "ndvi",
    {}
)

ndwi_data = uae_indices.get(
    "ndwi",
    {}
)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.title(
    "🌿 Mangrove Stress Radar"
)

st.sidebar.write(
    "Explore GCC mangrove locations and preliminary "
    "health indicators."
)

st.sidebar.divider()

st.sidebar.subheader(
    "Map layers"
)

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

st.sidebar.subheader(
    "Study information"
)

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
    "**Comparison:** "
    f"{uae_indices.get('baseline_date', '2024')} "
    "to "
    f"{uae_indices.get('later_date', '2025')}"
)


# ---------------------------------------------------------
# Header
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
    "POC scope: the map shows sampled GCC mangrove "
    "reference points derived from Global Mangrove Watch "
    "2020. Calculated NDVI and NDWI indicators are "
    "currently available only for UAE."
)


# ---------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "UAE NDVI status",
        uae_indices.get(
            "status",
            "Preliminary"
        )
    )

with col2:

    st.metric(
        "UAE later median NDVI",
        f"{ndvi_data.get('later_median', 0.0):.4f}"
    )

with col3:

    st.metric(
        "UAE NDVI scene change",
        f"{ndvi_data.get('scene_level_change', 0.0):.4f}"
    )

with col4:

    st.metric(
        "UAE NDWI scene change",
        f"{ndwi_data.get('scene_level_change', 0.0):.4f}"
    )


# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------

st.markdown(
    "<br>",
    unsafe_allow_html=True
)

tab1, tab2 = st.tabs(
    [
        "🗺️ Interactive Map Explorer",
        "📊 Regional Ecosystem Insights"
    ]
)


# ---------------------------------------------------------
# Interactive map
# ---------------------------------------------------------

with tab1:

    st.subheader(
        "Interactive GCC Mangrove Map"
    )

    st.write(
        "Click any mangrove point on the map below "
        "to view its stress inspection details."
    )

    if mangrove_points:

        if selected_region == "All GCC Regions":

            filtered_points = mangrove_points

        else:

            filtered_points = [
                point
                for point in mangrove_points
                if point["region"] == selected_region
            ]

        if not filtered_points:

            st.warning(
                f"No points were classified as {selected_region}. "
                "The country assignment is approximate."
            )

            filtered_points = mangrove_points

        average_latitude = sum(
            point["latitude"]
            for point in filtered_points
        ) / len(filtered_points)

        average_longitude = sum(
            point["longitude"]
            for point in filtered_points
        ) / len(filtered_points)

        zoom_level = (
            7
            if selected_region != "All GCC Regions"
            else 5
        )

        mangrove_map = folium.Map(
            location=[
                average_latitude,
                average_longitude
            ],
            zoom_start=zoom_level,
            tiles="OpenStreetMap",
            control_scale=True
        )

        marker_cluster = MarkerCluster(
            name="GCC Mangrove Points"
        )

        if show_mangroves:

            for point in filtered_points:

                tooltip_text = (
                    f"Region: {point['region']} | "
                    "Click to inspect"
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
                    fill_opacity=0.85,
                    weight=1,
                    tooltip=tooltip_text
                ).add_to(marker_cluster)

        marker_cluster.add_to(
            mangrove_map
        )

        folium.LayerControl().add_to(
            mangrove_map
        )

        map_data = st_folium(
            mangrove_map,
            width="100%",
            height=550,
            key="gcc_mangrove_map",
            returned_objects=[
                "last_object_clicked"
            ]
        )

        st.caption(
            f"Displaying {len(filtered_points)} "
            "mangrove reference points."
        )

        # -------------------------------------------------
        # Stress inspection panel
        # -------------------------------------------------

        st.markdown("---")

        st.subheader(
            "🔍 Mangrove Stress Inspection Panel"
        )

        last_clicked = None

        if map_data:
            last_clicked = map_data.get(
                "last_object_clicked"
            )

        if last_clicked:

            clicked_latitude = last_clicked.get(
                "lat"
            )

            clicked_longitude = last_clicked.get(
                "lng"
            )

            matched_point = None

            if (
                clicked_latitude is not None
                and clicked_longitude is not None
            ):

                matched_point = min(
                    filtered_points,
                    key=lambda point: (
                        abs(
                            point["latitude"]
                            - clicked_latitude
                        )
                        +
                        abs(
                            point["longitude"]
                            - clicked_longitude
                        )
                    )
                )

            if matched_point:

                selected_country = matched_point[
                    "region"
                ]

                st.success(
                    "Selected location — "
                    f"Latitude: "
                    f"{matched_point['latitude']:.5f}, "
                    f"Longitude: "
                    f"{matched_point['longitude']:.5f}"
                )

                panel_col1, panel_col2 = st.columns(2)

                with panel_col1:

                    st.markdown(
                        "### 📍 Location and baseline"
                    )

                    st.write(
                        f"**Region:** "
                        f"{selected_country}"
                    )

                    st.write(
                        f"**Source:** "
                        f"{matched_point['source']}"
                    )

                    if selected_country == "UAE":

                        st.write(
                            f"**Baseline date:** "
                            f"{uae_indices.get('baseline_date', 'N/A')}"
                        )

                        st.write(
                            f"**Later date:** "
                            f"{uae_indices.get('later_date', 'N/A')}"
                        )

                        st.write(
                            f"**Common tile:** "
                            f"{uae_indices.get('common_tile', 'N/A')}"
                        )

                    st.markdown(
                        "### 🧬 Stress fingerprint"
                    )

                    if selected_country == "UAE":

                        st.success(
                            "Calculated UAE numerical indicators"
                        )

                        st.write(
                            "• **NDVI classification:** "
                            f"{ndvi_data.get('interpretation', 'Preliminary')}"
                        )

                        st.write(
                            f"• **NDVI baseline median:** "
                            f"{ndvi_data.get('baseline_median', 0.0):.4f}"
                        )

                        st.write(
                            f"• **NDVI later median:** "
                            f"{ndvi_data.get('later_median', 0.0):.4f}"
                        )

                        st.write(
                            f"• **NDVI change:** "
                            f"{ndvi_data.get('scene_level_change', 0.0):.4f}"
                        )

                        st.write(
                            "• **NDVI strong decrease:** "
                            f"{ndvi_data.get('strong_decrease_percent', 0.0):.2f}%"
                        )

                        st.write(
                            "• **NDWI classification:** "
                            f"{ndwi_data.get('interpretation', 'Preliminary')}"
                        )

                        st.write(
                            f"• **NDWI baseline median:** "
                            f"{ndwi_data.get('baseline_median', 0.0):.4f}"
                        )

                        st.write(
                            f"• **NDWI later median:** "
                            f"{ndwi_data.get('later_median',
