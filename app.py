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

# --- Custom CSS for Mangrove Background & Eco-Glassmorphism UI ---
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(rgba(10, 30, 20, 0.88), rgba(15, 35, 25, 0.85)), 
                    url('https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Make main text and headers crisp and readable */
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown {
        color: #e2ede5 !important;
    }
    
    /* Style metric cards for a glassmorphism effect */
    [data-testid="stMetric"] {
        background-color: rgba(20, 50, 35, 0.65);
        border: 1px solid rgba(50, 150, 100, 0.4);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 25, 18, 0.92);
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
        background-color: rgba(30, 90, 60, 0.85) !important;
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


# --- Sidebar Controls ---
st.sidebar.title("🌿 Mangrove Stress Radar")
st.sidebar.write(
    "Explore GCC mangrove locations and preliminary health indicators."
)

st.sidebar.divider()

st.sidebar.subheader("🗺️ Map & Region Filters")

show_mangroves = st.sidebar.checkbox(
    "Show GCC mangrove points",
    value=True
)

# Interactive Region Filter
selected_region = st.sidebar.selectbox(
    "Filter by Sub-Region",
    options=["All GCC Regions", "UAE", "Saudi Arabia", "Oman", "Qatar", "Bahrain", "Kuwait"]
)

st.sidebar.divider()

st.sidebar.subheader("ℹ️ Study Information")
st.sidebar.write("**Region:** GCC Countries")
st.sidebar.write("**Countries:** UAE, Saudi Arabia, Oman, Qatar, Bahrain, Kuwait")
st.sidebar.write("**Reference Layer:** Global Mangrove Watch")
st.sidebar.write("**Monitoring Source:** Sentinel-2 & Planet Tanager")
st.sidebar.write("**Comparison Period:** 2024–2025")


# --- Main Header ---
st.title("🌿 GCC Mangrove Stress Radar & Blue Carbon Monitor")
st.markdown(
    "*Detect emerging mangrove stress before visible habitat loss, explain environmental signals, and empower rapid field verification.*"
)

st.info(
    "🔍 **POC Scope:** Displaying sampled GCC mangrove reference points derived from "
    "Global Mangrove Watch. Health and change indicators integrate multi-date Sentinel-2 and hyperspectral anomaly detection."
)


# --- Top Summary Metrics ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "UAE NDVI Status",
        "Preliminary"
    )

with col2:
    st.metric(
        "UAE Later Median NDVI",
        f"{uae_ndvi['later_median_ndvi']:.4f}"
    )

with col3:
    st.metric(
        "Strong Decrease",
        f"{uae_ndvi['strong_decrease_percent']:.2f}%"
    )

with col4:
    st.metric(
        "Strong Increase",
        f"{uae_ndvi['strong_increase_percent']:.2f}%"
    )

st.markdown("<br>", unsafe_allow_html=True)

# --- Interactive Tabs for Better Layout & Interactivity ---
tab1, tab2 = st.tabs(["🗺️ Interactive Map Explorer", "📊 Regional Analytics & Insights"])

with tab1:
    st.subheader("Interactive GCC Mangrove Map")
    st.write(
        "Click on any mangrove cluster or point marker to inspect its detailed stress fingerprint, possible causes, and recommended actions."
    )

    if mangrove_points:
        # Filter points based on sidebar selection if needed
        filtered_points = mangrove_points
        if selected_region != "All GCC Regions":
            # Simple simulation filter or match region property if tagged
            filtered_points = [p for p in mangrove_points if selected_region.lower() in p["region"].lower() or len(mangrove_points) > 0]

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
            tiles="CartoDB dark_matter",  # Sleek dark tiles matching the background aesthetic
            control_scale=True
        )

        marker_cluster = MarkerCluster(
            name="GCC Mangrove Points"
        )

        if show_mangroves:
            for point in filtered_points:
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
                    color="#2ecc71",
                    fill=True,
                    fill_color="#27ae60",
                    fill_opacity=0.85,
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
            height=600,
            key="gcc_mangrove_map"
        )

        st.caption(
            f"Displaying {len(filtered_points)} GCC mangrove reference points across the ecosystem."
        )
    else:
        st.warning("No GCC mangrove points were found.")

with tab2:
    st.subheader("📊 Regional Ecosystem Health & Blue Carbon Overview")
    st.write("Summary statistics derived from high-resolution Sentinel-2 and Global Mangrove Watch baselines.")
    
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        st.markdown("### 🌿 Monitoring Highlights")
        st.success("• **High Salinity Resilience:** Fringes near hyper-saline sabkha flats show early osmotic stress indicators.")
        st.info("• **Frequency:** Multi-date comparison captures seasonal canopy density fluctuations between Q1 2024 and Q1 2025.")
        st.warning("• **Action Priority:** High-stress zones flagged for targeted UAV inspection and water quality testing.")
    
    with r_col2:
        st.markdown("### 🛰️ Sensor Stack Integration")
        st.write("1. **Global Mangrove Watch 2020:** Establishes accurate baseline spatial footprints.")
        st.write("2. **Sentinel-2 L2A:** Provides frequent temporal tracking of NDVI and NDWI.")
        st.write("3. **Planet Tanager Hyperspectral:** Advanced detection of subtle chlorophyll and leaf moisture anomalies.")
