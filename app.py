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

# --- Custom CSS for Lush Coastal Mangroves Background & Info-Bubble UI ---
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(rgba(10, 30, 20, 0.85), rgba(15, 35, 25, 0.82)), 
                    url('https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Readable text styling */
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown {
        color: #e2ede5 !important;
    }
    
    /* Glassmorphism metric cards */
    [data-testid="stMetric"] {
        background-color: rgba(20, 50, 35, 0.75);
        border: 1px solid rgba(50, 150, 100, 0.4);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 25, 18, 0.95);
        border-right: 1px solid rgba(50, 150, 100, 0.2);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(20, 50, 35, 0.6);
        border-radius: 8px 8px 0px 0px;
        color: #e2ede5;
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


GEOJSON_PATH = Path(
    "images/gcc_mangrove_analysis_points.geojson"
)
UAE_NDVI_PATH = Path(
    "images/uae_ndvi_summary.json"
)


# Bounding boxes for spatial filtering of GCC countries[cite: 3]
GCC_COUNTRY_BOUNDS = {
    "UAE": {"lat": (22.5, 26.5), "lon": (51.5, 56.5)},
    "Saudi Arabia": {"lat": (16.0, 31.5), "lon": (34.0, 50.0)},
    "Oman": {"lat": (16.5, 26.5), "lon": (56.5, 60.0)},
    "Qatar": {"lat": (24.4, 26.2), "lon": (50.6, 51.7)},
    "Bahrain": {"lat": (25.7, 26.4), "lon": (50.3, 50.8)},
    "Kuwait": {"lat": (28.4, 30.2), "lon": (46.5, 48.5)},
}


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
            lon = float(coordinates[0])
            lat = float(coordinates[1])

            # Determine specific country based on coordinates[cite: 3]
            detected_country = "GCC"
            for country, bounds in GCC_COUNTRY_BOUNDS.items():
                if (
                    bounds["lat"][0] <= lat <= bounds["lat"][1]
                    and bounds["lon"][0] <= lon <= bounds["lon"][1]
                ):
                    detected_country = country
                    break

            points.append({
                "latitude": lat,
                "longitude": lon,
                "region": detected_country,
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


# --- Sidebar Controls ---
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

selected_region = st.sidebar.selectbox(
    "Filter by Sub-Region",
    options=["All GCC Regions", "UAE", "Saudi Arabia", "Oman", "Qatar", "Bahrain", "Kuwait"]
)

st.sidebar.divider()

st.sidebar.subheader("Study information")

st.sidebar.write("**Region:** GCC countries")
st.sidebar.write("**Countries:** UAE, Saudi Arabia, Oman, Qatar, Bahrain, Kuwait")
st.sidebar.write("**Reference layer:** Global Mangrove Watch")
st.sidebar.write("**Monitoring source:** Sentinel-2")
st.sidebar.write("**Comparison:** 2024–2025")


# --- Main Header ---
st.title("🌿 GCC Mangrove Stress Radar & Blue Carbon Monitor")
st.write(
    "Detect emerging mangrove stress before visible habitat loss, "
    "explain the possible signal, and support field verification."
)

st.info(
    "POC scope: the map shows sampled GCC mangrove reference "
    "points derived from Global Mangrove Watch 2020. Health and "
    "change indicators are preliminary and require multi-tile "
    "Sentinel-2 processing and field validation for full GCC coverage."
)


# --- Top Summary Metrics ---
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

st.markdown("<br>", unsafe_allow_html=True)

# --- Interactive Tabs ---
tab1, tab2 = st.tabs(["🗺️ Interactive Map Explorer", "📊 Regional Ecosystem Insights"])

with tab1:
    st.subheader("Interactive GCC Mangrove Map")
    st.write("Click any mangrove point to view its stress fingerprint bubble.")

    if mangrove_points:
        # Filter points dynamically based on spatial region match[cite: 3]
        if selected_region == "All GCC Regions":
            filtered_points = mangrove_points
        else:
            filtered_points = [
                p for p in mangrove_points if p["region"] == selected_region
            ]

        if filtered_points:
            average_latitude = sum(
                point["latitude"] for point in filtered_points
            ) / len(filtered_points)

            average_longitude = sum(
                point["longitude"] for point in filtered_points
            ) / len(filtered_points)
            zoom_lvl = 7 if selected_region != "All GCC Regions" else 5
        else:
            average_latitude, average_longitude, zoom_lvl = 24.0, 52.0, 5

        mangrove_map = folium.Map(
            location=[average_latitude, average_longitude],
            zoom_start=zoom_lvl,
            tiles="OpenStreetMap",
            control_scale=True
        )

        marker_cluster = MarkerCluster(name="GCC Mangrove Points")

        if show_mangroves and filtered_points:
            for point in filtered_points:
                popup_text = f"""
                    <div style="background: white; padding: 12px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); font-family: sans-serif; font-size: 12px; width: 230px; line-height: 1.4; border-left: 4px solid #16805b; color: #333;">
                        <b style="color: #07543e; font-size: 13px;">🌿 Mangrove Stress Inspection</b><br>
                        <hr style="margin: 5px 0; border: 0; border-top: 1px solid #eee;">
                        <b>Region:</b> {point['region']}<br>
                        <b>Source:</b> {point['source']}<br>
                        <b>Latitude:</b> {point['latitude']:.4f}<br>
                        <b>Longitude:</b> {point['longitude']:.4f}<br><br>
                        <b>Stress fingerprint:</b><br>
                        • NDVI: Preliminary<br>
                        • NDWI: Planned<br>
                        • Turbidity/NDCI: Planned<br>
                        • Planet Tanager: Planned<br><br>
                        <b>Action:</b> Inspect by UAV or field team
                    </div>
                """

                folium.CircleMarker(
                    location=[point["latitude"], point["longitude"]],
                    radius=5,
                    color="#07543e",
                    fill=True,
                    fill_color="#16805b",
                    fill_opacity=0.85,
                    weight=1,
                    popup=folium.Popup(popup_text, max_width=270)
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
            f"Displaying {len(filtered_points)} mangrove reference points for {selected_region}."
        )

    else:
        st.warning("No GCC mangrove points were found.")

with tab2:
    st.subheader("📊 Regional Ecosystem Health Summary")
    st.write("Overview of monitoring indices across the Arabian Gulf and Red Sea coasts.")
    
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        st.markdown("### 🌿 Key Observations")
        st.success("• **Baseline Mapping:** Leverages Global Mangrove Watch to establish robust spatial boundaries.")
        st.info("• **Temporal Tracking:** Sentinel-2 comparisons highlight seasonal vegetation health shifts.")
    with t_col2:
        st.markdown("### 🛰️ Technology Stack")
        st.write("• **Satellite Source:** Sentinel-2 L2A & Planet Tanager")
        st.write("• **Target Area:** UAE, Saudi Arabia, Oman, Qatar, Bahrain, Kuwait")
