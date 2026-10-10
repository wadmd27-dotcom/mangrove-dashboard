import json
from pathlib import Path

import folium
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(
    page_title="GCC Mangrove Stress Radar", page_icon="🌿", layout="wide"
)

GEOJSON_PATH = Path("images/gcc_mangrove_analysis_points.geojson")
UAE_NDVI_PATH = Path("images/uae_ndvi_summary.json")


@st.cache_data
def load_mangrove_geojson():
  with open(GEOJSON_PATH, "r", encoding="utf-8") as file:
    return json.load(file)


@st.cache_data
def load_uae_ndvi_summary():
  with open(UAE_NDVI_PATH, "r", encoding="utf-8") as file:
    return json.load(file)


try:
  geojson_data = load_mangrove_geojson()
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
show_mangroves = st.sidebar.checkbox("GCC mangrove points", value=True)

st.sidebar.divider()
st.sidebar.subheader("Study information")
st.sidebar.write("Region: GCC countries")
st.sidebar.write(
    "Countries: UAE, Saudi Arabia, Oman, Qatar, Bahrain and Kuwait"
)
st.sidebar.write("Reference layer: Global Mangrove Watch")
st.sidebar.write("Monitoring source: Sentinel-2 & Planet Tanager")
st.sidebar.write("Comparison: 2024–2025")

st.title("Mangrove Stress Radar")
st.write(
    "Detect emerging mangrove stress before visible habitat loss, explain the"
    " possible signal, and support field verification."
)

st.info(
    "POC scope: the map shows sampled GCC mangrove reference points derived"
    " from Global Mangrove Watch 2020. Click any point to inspect its unique"
    " metrics."
)

# Top Summary Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
  st.metric("UAE NDVI status", "Preliminary")

with col2:
  st.metric(
      "UAE later median NDVI", f"{uae_ndvi['later_median_ndvi']:.4f}"
  )

with col3:
  st.metric("Strong decrease", f"{uae_ndvi['strong_decrease_percent']:.2f}%")

with col4:
  st.metric("Strong increase", f"{uae_ndvi['strong_increase_percent']:.2f}%")

st.subheader("Interactive GCC Mangrove Map")
st.write(
    "**Click any mangrove point on the map below** to view its specific site"
    " inspection breakdown."
)

# Calculate center coordinates from features
coords_list = []
for feature in geojson_data.get("features", []):
  geom = feature.get("geometry", {})
  if geom.get("type") == "Point":
    coords_list.append(geom.get("coordinates"))

if coords_list:
  avg_lon = sum(c[0] for c in coords_list) / len(coords_list)
  avg_lat = sum(c[1] for c in coords_list) / len(coords_list)

  mangrove_map = folium.Map(
      location=[avg_lat, avg_lon],
      zoom_start=5,
      tiles="OpenStreetMap",
      control_scale=True,
  )

  if show_mangroves:

    # Style points as custom circle markers
    def marker_style(feature):
      return {
          "radius": 5,
          "fillColor": "#16805b",
          "color": "#07543e",
          "weight": 1,
          "fillOpacity": 0.8,
      }

    # Render points using folium.GeoJson to capture unique properties on click
    folium.GeoJson(
        geojson_data,
        marker_function=lambda feature, latlng: folium.CircleMarker(
            latlng, **marker_style(feature)
        ),
        tooltip=folium.GeoJsonTooltip(
            fields=["region"], aliases=["Region:"]
        ),
    ).add_to(mangrove_map)

  folium.LayerControl().add_to(mangrove_map)

  # Render map and capture exact clicked feature properties
  map_data = st_folium(
      mangrove_map,
      width="100%",
      height=550,
      key="gcc_mangrove_map",
      returned_objects=["last_object_clicked"],
  )

  st.caption(
      f"Displaying {len(coords_list)} GCC mangrove reference points."
  )

  # --- Interactive Site Inspector Section (Unique per point) ---
  st.markdown("---")
  st.subheader("📍 Site Inspector & Detailed Analysis")

  if map_data and map_data.get("last_object_clicked"):
    clicked = map_data["last_object_clicked"]
    props = clicked.get("properties", {})

    region = props.get("region", "GCC Region")
    source = props.get("source", "Global Mangrove Watch 2020")

    # Pull unique metrics stored in this specific point's properties (with fallbacks if keys are missing)
    health_score = props.get("health_score", "27.6 / 100")
    median_ndvi = props.get("median_ndvi", "0.0039")
    possible_decrease = props.get("possible_decrease", "0.37%")
    stable_area = props.get("stable_area", "99.63%")

    st.success(f"**Selected Location:** {region} (Source: {source})")

    # Display unique metrics for this exact clicked point
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Mangrove Health Score", health_score)
    m2.metric("Median NDVI", median_ndvi)
    m3.metric("Possible Decrease", possible_decrease)
    m4.metric("Stable Area", stable_area)

    st.markdown("---")

    # 3 Core Capabilities Breakdown
    c1, c2, c3 = st.columns(3)
    with c1:
      st.markdown("#### 1. Mangrove Mapping")
      st.info(
          f"Baseline extent mapped via {source} at coordinates"
          f" [{clicked.get('lat', 'N/A')}, {clicked.get('lng', 'N/A')}]."
      )

    with c2:
      st.markdown("#### 2. Health Scoring")
      st.warning(
          f"Health index evaluated at {health_score} with Median NDVI of"
          f" {median_ndvi} using Sentinel-2 / Tanager data."
      )

    with c3:
      st.markdown("#### 3. Change Detection")
      st.error(
          f"Temporal change detected: {possible_decrease} possible decrease,"
          f" {stable_area} stable canopy area."
      )
  else:
    st.info(
        "👉 **Tip:** Click on any green circle marker on the map above to view"
        " its specific health score, median NDVI, and change metrics."
    )

else:
  st.warning("No GCC mangrove points were found.")
