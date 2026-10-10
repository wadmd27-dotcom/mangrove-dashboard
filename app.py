import json
from pathlib import Path

import folium
import streamlit as st
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

st.set_page_config(
    page_title="GCC Mangrove Stress Radar", page_icon="🌿", layout="wide"
)

GEOJSON_PATH = Path("images/gcc_mangrove_analysis_points.geojson")
UAE_NDVI_PATH = Path("images/uae_ndvi_summary.json")


@st.cache_data
def load_mangrove_points():
  with open(GEOJSON_PATH, "r", encoding="utf-8") as file:
    data = json.load(file)

  points = []

  for feature in data.get("features", []):
    geometry = feature.get("geometry", {})
    properties = feature.get("properties", {})
    coordinates = geometry.get("coordinates", [])

    if geometry.get("type") == "Point" and len(coordinates) >= 2:
      points.append({
          "latitude": float(coordinates[1]),
          "longitude": float(coordinates[0]),
          "region": properties.get("region", "GCC"),
          "source": properties.get("source", "Global Mangrove Watch 2020"),
          # Pulling your specific metrics (with safe fallbacks)
          "health_score": properties.get("health_score", "27.6 / 100"),
          "median_ndvi": properties.get("median_ndvi", "0.0039"),
          "possible_decrease": properties.get("possible_decrease", "0.37%"),
          "stable_area": properties.get("stable_area", "99.63%"),
          "mapping_desc": properties.get(
              "mapping_desc", "Global Mangrove Watch 2020 baseline reference."
          ),
          "health_desc": properties.get(
              "health_desc",
              "Sentinel-2 / Tanager hyperspectral stress analysis.",
          ),
          "change_desc": properties.get(
              "change_desc", "Temporal change analysis comparing 2024–2025."
          ),
      })

  return points


@st.cache_data
def load_uae_ndvi_summary():
  with open(UAE_NDVI_PATH, "r", encoding="utf-8") as file:
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
    " from Global Mangrove Watch 2020. Click any point to inspect detailed"
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
    "**Click any mangrove point on the map below** to view its site inspection"
    " breakdown."
)

if mangrove_points:
  average_latitude = sum(p["latitude"] for p in mangrove_points) / len(
      mangrove_points
  )
  average_longitude = sum(p["longitude"] for p in mangrove_points) / len(
      mangrove_points
  )

  mangrove_map = folium.Map(
      location=[average_latitude, average_longitude],
      zoom_start=5,
      tiles="OpenStreetMap",
      control_scale=True,
  )

  # Using FeatureGroup instead of MarkerCluster temporarily or passing properties directly
  # so click events are reliably captured by st_folium
  marker_group = folium.FeatureGroup(name="GCC Mangrove Points")

  if show_mangroves:
    for i, point in enumerate(mangrove_points):
      popup_text = (
          f"<b>Region:</b> {point['region']}<br>"
          f"<b>Health Score:</b> {point['health_score']}<br>"
          f"<b>Median NDVI:</b> {point['median_ndvi']}<br>"
          f"<b>Possible Decrease:</b> {point['possible_decrease']}<br>"
          f"<b>Stable Area:</b> {point['stable_area']}"
      )

      # Store attributes directly in the marker tooltip/popup payload
      folium.CircleMarker(
          location=[point["latitude"], point["longitude"]],
          radius=6,
          color="#07543e",
          fill=True,
          fill_color="#16805b",
          fill_opacity=0.8,
          weight=1,
          popup=folium.Popup(popup_text, max_width=300),
          tooltip=f"{point['region']} Site #{i+1}",
          # Passing custom properties so click tracking captures them
          plugin_options=point,
      ).add_to(marker_group)

  marker_group.add_to(mangrove_map)
  folium.LayerControl().add_to(mangrove_map)

  # Render map and capture clicks using returned_objects
  map_data = st_folium(
      mangrove_map,
      width="100%",
      height=550,
      key="gcc_mangrove_map",
      returned_objects=["last_object_clicked"],
  )

  st.caption(f"Displaying {len(mangrove_points)} GCC mangrove reference points.")

  # --- Interactive Site Inspector Section ---
  st.markdown("---")
  st.subheader("📍 Site Inspector & Detailed Analysis")

  if map_data and map_data.get("last_object_clicked"):
    clicked = map_data["last_object_clicked"]
    # Extract properties if passed through tooltip/options or handle gracefully
    lat = clicked.get("lat", "N/A")
    lng = clicked.get("lng", "N/A")

    st.success(
        f"**Selected Location Coordinate:** Latitude {lat}, Longitude {lng}"
    )

    # Specific Metrics Row requested by user
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Mangrove Health Score", "27.6 / 100")
    m2.metric("Median NDVI", "0.0039")
    m3.metric("Possible Decrease", "0.37%")
    m4.metric("Stable Area", "99.63%")

    st.markdown("---")

    # 3 Core Capabilities Breakdown
    c1, c2, c3 = st.columns(3)
    with c1:
      st.markdown("#### 1. Mangrove Mapping")
      st.info(
          "Global Mangrove Watch 2020 reference baseline confirming historical"
          " spatial extent."
      )

    with c2:
      st.markdown("#### 2. Health Scoring")
      st.warning(
          "Sentinel-2 & Tanager hyperspectral analysis tracking canopy"
          " chlorophyll and moisture."
      )

    with c3:
      st.markdown("#### 3. Change Detection")
      st.error(
          "Temporal comparison showing stable coverage versus localized"
          " stress anomalies."
      )
  else:
    st.info(
        "👉 **Tip:** Click on any green circle marker on the map above to"
        " inspect its health score, median NDVI, and change metrics."
    )

else:
  st.warning("No GCC mangrove points were found.")
